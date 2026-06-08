from __future__ import annotations

import re
from datetime import date, time
from typing import Literal

from pydantic import BaseModel, Field, field_validator


SAFE_TEXT_RE = re.compile(r"^[\w\s.,'’()+\-:/@!?]{1,1200}$", re.UNICODE)
PHONE_RE = re.compile(r"^[0-9+\-\s()]{6,30}$")


def validate_safe_text(value: str, field_name: str = "text") -> str:
    cleaned = value.strip()
    if not SAFE_TEXT_RE.fullmatch(cleaned):
        raise ValueError(f"{field_name} contains unsupported characters")
    return cleaned


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1200)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    session_id: str | None = Field(default=None, max_length=80)
    language: Literal["en", "fr", "ar", "auto"] = "auto"
    history: list[ChatMessage] = Field(default_factory=list, max_length=12)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        return validate_safe_text(value, "message")


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    reservation_saved: bool = False


class ReservationRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    phone: str = Field(min_length=6, max_length=30)
    reservation_date: date
    reservation_time: time
    people: int = Field(ge=1, le=30)
    notes: str | None = Field(default="", max_length=500)
    source: Literal["form", "chat"] = "form"

    @field_validator("name", "notes")
    @classmethod
    def strip_text(cls, value: str | None) -> str:
        return validate_safe_text(value or "", "text") if value else ""

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        cleaned = value.strip()
        if not PHONE_RE.fullmatch(cleaned):
            raise ValueError("phone must contain only digits, spaces, +, -, or parentheses")
        return cleaned


class ReservationResponse(BaseModel):
    id: int
    name: str
    phone: str
    reservation_date: str
    reservation_time: str
    people: int
    notes: str | None
    source: str
    status: str
    created_at: str
