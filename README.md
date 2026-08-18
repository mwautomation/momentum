# Library API

Small FastAPI service for tracking a library's books and their current borrowing
state. Data is stored in PostgreSQL and the complete local environment is managed
with Docker Compose through a Makefile.

## Requirements

- Docker with the Compose plugin
- GNU Make

No local Python or PostgreSQL installation is required.

## Start the application

```console
make up
```

This builds the API image, starts PostgreSQL, applies Alembic migrations, and
starts the API in the background. Wait until the API is healthy, then use:

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

The equivalent direct command is:

```console
docker compose up --build --detach
```

Operational commands:

```console
make ps       # show service state
make logs     # follow API logs
make down     # stop containers and preserve database data
```

Copying `.env.example` to `.env` is optional. The application has local-only
defaults, and the file can be used to override the API port or PostgreSQL values.
PostgreSQL is available only on the internal Compose network. The unauthenticated
API is bound to the host loopback interface.

## API workflow

Serial numbers and library card numbers are strings containing exactly six ASCII
digits, including leading zeroes.

Add an available book:

```console
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{"serial_number":"000123","title":"The Hobbit","author":"J. R. R. Tolkien"}'
```

List all books, ordered by serial number:

```console
curl http://localhost:8000/books
```

Borrow the book. The server records the current UTC time:

```console
curl -X PATCH http://localhost:8000/books/000123/status \
  -H "Content-Type: application/json" \
  -d '{"is_borrowed":true,"borrower_card_number":"000001"}'
```

Return the book:

```console
curl -X PATCH http://localhost:8000/books/000123/status \
  -H "Content-Type: application/json" \
  -d '{"is_borrowed":false}'
```

Delete the available book:

```console
curl -X DELETE http://localhost:8000/books/000123
```

Deleting a borrowed book or repeating a state transition returns `409 Conflict`.
Unknown books return `404 Not Found`, and malformed input returns
`422 Unprocessable Entity`.

## Tests

```console
make test
```

The target creates an isolated Compose project and PostgreSQL volume, applies the
migration, runs Ruff lint and formatting checks, and runs all unit and integration
tests. Test containers and their volume are removed afterward, including after a
failed test. The development database used by `make up` is not modified.

## Project structure

- `app/api/routes` contains the HTTP layer.
- `app/schemas.py` defines request and response validation.
- `app/services.py` implements transactional business rules.
- `app/models.py` and `alembic` define the PostgreSQL schema and migrations.
- `compose.yaml` and `Makefile` provide the local deployment interface.
