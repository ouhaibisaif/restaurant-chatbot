from fastapi import APIRouter, Request

from app.database.db import create_reservation, list_reservations
from app.models.schemas import ReservationRequest, ReservationResponse
from app.services.security import RateLimiter, client_key


router = APIRouter()
limiter = RateLimiter(max_requests=20, window_seconds=60)


@router.post("/reservation", response_model=ReservationResponse)
def reserve(payload: ReservationRequest, request: Request) -> ReservationResponse:
    limiter.check(client_key(request))
    reservation = create_reservation(
        {
            "name": payload.name,
            "phone": payload.phone,
            "reservation_date": payload.reservation_date.isoformat(),
            "reservation_time": payload.reservation_time.strftime("%H:%M"),
            "people": payload.people,
            "notes": payload.notes or "",
            "source": payload.source,
        }
    )
    return ReservationResponse(**reservation)


@router.get("/admin/reservations", response_model=list[ReservationResponse])
def admin_reservations() -> list[ReservationResponse]:
    return [ReservationResponse(**item) for item in list_reservations()]
