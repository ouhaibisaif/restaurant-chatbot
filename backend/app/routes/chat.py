from fastapi import APIRouter, Request

from app.models.schemas import ChatRequest, ChatResponse
from app.services.ollama_service import generate_chat_reply
from app.services.security import RateLimiter, client_key


router = APIRouter()
limiter = RateLimiter(max_requests=30, window_seconds=60)


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    limiter.check(client_key(request))
    reply, session_id, reservation_saved = await generate_chat_reply(
        payload.message,
        payload.session_id,
        payload.language,
        payload.history,
    )
    return ChatResponse(
        reply=reply,
        session_id=session_id,
        reservation_saved=reservation_saved,
    )
