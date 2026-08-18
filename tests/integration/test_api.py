from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Barrier

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.integration
BOOK = {
    "serial_number": "000123",
    "title": "The Hobbit",
    "author": "J. R. R. Tolkien",
}


def test_health_checks_the_database(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_complete_book_lifecycle(client: TestClient) -> None:
    created = client.post("/books", json=BOOK)
    assert created.status_code == 201
    assert created.json() == {
        **BOOK,
        "is_borrowed": False,
        "borrower_card_number": None,
        "borrowed_at": None,
    }

    duplicate = client.post("/books", json=BOOK)
    assert duplicate.status_code == 409

    listed = client.get("/books")
    assert listed.status_code == 200
    assert listed.json() == [created.json()]

    borrowed = client.patch(
        "/books/000123/status",
        json={"is_borrowed": True, "borrower_card_number": "000001"},
    )
    assert borrowed.status_code == 200
    assert borrowed.json()["is_borrowed"] is True
    assert borrowed.json()["borrower_card_number"] == "000001"
    borrowed_at = datetime.fromisoformat(
        borrowed.json()["borrowed_at"].replace("Z", "+00:00")
    )
    assert borrowed_at.utcoffset() is not None

    repeated_borrow = client.patch(
        "/books/000123/status",
        json={"is_borrowed": True, "borrower_card_number": "000002"},
    )
    assert repeated_borrow.status_code == 409

    delete_borrowed = client.delete("/books/000123")
    assert delete_borrowed.status_code == 409

    returned = client.patch(
        "/books/000123/status",
        json={"is_borrowed": False},
    )
    assert returned.status_code == 200
    assert returned.json()["is_borrowed"] is False
    assert returned.json()["borrower_card_number"] is None
    assert returned.json()["borrowed_at"] is None

    repeated_return = client.patch(
        "/books/000123/status",
        json={"is_borrowed": False},
    )
    assert repeated_return.status_code == 409

    deleted = client.delete("/books/000123")
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get("/books").json() == []


def test_books_are_ordered_by_serial_number(client: TestClient) -> None:
    later_book = {**BOOK, "serial_number": "900000"}
    earlier_book = {**BOOK, "serial_number": "000001"}

    assert client.post("/books", json=later_book).status_code == 201
    assert client.post("/books", json=earlier_book).status_code == 201

    serial_numbers = [book["serial_number"] for book in client.get("/books").json()]
    assert serial_numbers == ["000001", "900000"]


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("delete", "/books/999999", None),
        ("patch", "/books/999999/status", {"is_borrowed": False}),
    ],
)
def test_missing_book_returns_404(
    client: TestClient,
    method: str,
    path: str,
    json_body: dict[str, bool] | None,
) -> None:
    response = client.request(method, path, json=json_body)

    assert response.status_code == 404


def test_invalid_requests_return_422(client: TestClient) -> None:
    invalid_create = client.post(
        "/books",
        json={**BOOK, "serial_number": "12345"},
    )
    invalid_path = client.delete("/books/not-a-number")
    missing_card = client.patch(
        "/books/000123/status",
        json={"is_borrowed": True},
    )

    assert invalid_create.status_code == 422
    assert invalid_path.status_code == 422
    assert missing_card.status_code == 422


def test_concurrent_checkout_allows_only_one_borrower(
    client: TestClient,
) -> None:
    assert client.post("/books", json=BOOK).status_code == 201
    barrier = Barrier(2)

    def checkout(card_number: str) -> int:
        barrier.wait()
        with TestClient(app) as concurrent_client:
            response = concurrent_client.patch(
                "/books/000123/status",
                json={
                    "is_borrowed": True,
                    "borrower_card_number": card_number,
                },
            )
        return response.status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        status_codes = list(executor.map(checkout, ["000001", "000002"]))

    assert sorted(status_codes) == [200, 409]
