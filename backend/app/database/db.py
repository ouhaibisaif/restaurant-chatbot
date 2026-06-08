from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "restaurant.db"


def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = dict_factory
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                reservation_date TEXT NOT NULL,
                reservation_time TEXT NOT NULL,
                people INTEGER NOT NULL,
                notes TEXT,
                source TEXT NOT NULL DEFAULT 'form',
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_reservations_created_at
            ON reservations(created_at DESC)
            """
        )


def create_reservation(payload: dict) -> dict:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO reservations
            (name, phone, reservation_date, reservation_time, people, notes, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["name"],
                payload["phone"],
                payload["reservation_date"],
                payload["reservation_time"],
                payload["people"],
                payload.get("notes", ""),
                payload.get("source", "form"),
            ),
        )
        reservation_id = cursor.lastrowid
        return conn.execute(
            "SELECT * FROM reservations WHERE id = ?",
            (reservation_id,),
        ).fetchone()


def list_reservations() -> list[dict]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM reservations ORDER BY created_at DESC, id DESC"
        ).fetchall()
