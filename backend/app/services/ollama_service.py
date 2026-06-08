from __future__ import annotations

import os
import uuid

import httpx

from app.database.db import create_reservation
from app.database.sample_data import restaurant_context
from app.models.schemas import ChatMessage
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.services.reservation_parser import missing_reservation_fields, parse_reservation_details
from app.services.security import looks_like_prompt_injection, sanitize_text


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

SESSION_MEMORY: dict[str, list[dict[str, str]]] = {}
RESERVATION_MEMORY: dict[str, dict] = {}


def get_or_create_session(session_id: str | None) -> str:
    return session_id or str(uuid.uuid4())


def _safe_redirect(language: str) -> str:
    if language == "fr":
        return "Je peux vous aider avec le menu, les horaires, la livraison ou une reservation au Jardin Bleu."
    if language == "ar":
        return "يمكنني مساعدتك في قائمة الطعام أو أوقات العمل أو التوصيل أو حجز طاولة في مطعم Le Jardin Bleu."
    return "I can help with Le Jardin Bleu's menu, opening hours, delivery, allergens, or table reservations."


async def generate_chat_reply(
    message: str,
    session_id: str | None,
    language: str,
    history: list[ChatMessage],
) -> tuple[str, str, bool]:
    clean_message = sanitize_text(message)
    current_session = get_or_create_session(session_id)

    if looks_like_prompt_injection(clean_message):
        return _safe_redirect(language), current_session, False

    reservation_saved = _merge_reservation_details(current_session, clean_message)

    memory = SESSION_MEMORY.setdefault(current_session, [])
    compact_history = [{"role": item.role, "content": sanitize_text(item.content)} for item in history[-6:]]
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": (
                "Restaurant context. Use this as the only factual source:\n"
                f"{restaurant_context()}"
            ),
        },
        *compact_history,
        *memory[-8:],
        {"role": "user", "content": clean_message},
    ]

    if reservation_saved:
        messages.append(
            {
                "role": "system",
                "content": "A reservation request was saved as pending. Tell the user the restaurant received it and may call to confirm.",
            }
        )
    elif _reservation_intent(clean_message):
        missing = missing_reservation_fields(RESERVATION_MEMORY.get(current_session, {}))
        if missing:
            messages.append(
                {
                    "role": "system",
                    "content": f"The user is making a reservation. Ask only for these missing fields: {', '.join(missing)}.",
                }
            )

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_ctx": 4096},
                },
            )
            response.raise_for_status()
            reply = response.json()["message"]["content"].strip()
    except httpx.HTTPError:
        reply = (
            "I am having trouble reaching the local Qwen model through Ollama. "
            "Please make sure Ollama is running and the model is pulled."
        )

    memory.extend(
        [
            {"role": "user", "content": clean_message},
            {"role": "assistant", "content": reply},
        ]
    )
    SESSION_MEMORY[current_session] = memory[-12:]
    return reply, current_session, reservation_saved


def _reservation_intent(message: str) -> bool:
    lower = message.lower()
    keywords = [
        "book",
        "reservation",
        "reserve",
        "table",
        "booking",
        "réserver",
        "reservation",
        "حجز",
        "طاولة",
    ]
    return any(keyword in lower for keyword in keywords)


def _merge_reservation_details(session_id: str, message: str) -> bool:
    if not _reservation_intent(message) and session_id not in RESERVATION_MEMORY:
        return False

    details = RESERVATION_MEMORY.setdefault(session_id, {})
    details.update(parse_reservation_details(message))

    if missing_reservation_fields(details):
        return False

    create_reservation(
        {
            "name": details["name"],
            "phone": details["phone"],
            "reservation_date": details["reservation_date"],
            "reservation_time": details["reservation_time"],
            "people": int(details["people"]),
            "notes": "Created from chatbot conversation.",
            "source": "chat",
        }
    )
    RESERVATION_MEMORY.pop(session_id, None)
    return True
