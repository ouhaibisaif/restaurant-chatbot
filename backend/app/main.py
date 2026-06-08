from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database.db import init_db
from app.routes import chat, menu, reservations


load_dotenv()

app = FastAPI(title="Restaurant Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):517[3-9]$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "restaurant-chatbot"}


app.include_router(chat.router)
app.include_router(menu.router)
app.include_router(reservations.router)
