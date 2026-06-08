from fastapi import APIRouter

from app.database.sample_data import MENU, RESTAURANT


router = APIRouter()


@router.get("/menu")
def get_menu() -> dict:
    return {"restaurant": RESTAURANT, "menu": MENU}
