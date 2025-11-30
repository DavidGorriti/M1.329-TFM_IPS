from fastapi import APIRouter
from services.date_service import DateService
from datetime import datetime
from zoneinfo import ZoneInfo
from config.config import Config

config = Config()
date_router = APIRouter()
current_timezone = ZoneInfo(config.timezone)
date_service = DateService()

@date_router.get("/current-date")
async def get_current_date():
    # Devuelve la fecha/hora actual en la zona horaria configurada
    return date_service.get_current_date_utc().astimezone(current_timezone)