from fastapi import FastAPI

from app.api.routes import books, health

app = FastAPI(
    title="Library API",
    description="API for managing a library's book inventory and borrowing state.",
    version="1.0.0",
)
app.include_router(health.router)
app.include_router(books.router)
