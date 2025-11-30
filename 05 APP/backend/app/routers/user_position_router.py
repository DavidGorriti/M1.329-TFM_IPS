from fastapi import APIRouter
from services.user_position_service import UserPositionService
from services.date_service import DateService
from datetime import datetime
from zoneinfo import ZoneInfo
from config.config import Config

config = Config()
user_positions_router = APIRouter()
user_service = UserPositionService()
current_timezone = ZoneInfo(config.timezone)
date_service = DateService()

@user_positions_router.get("/user-positions")
async def get_user_positions():
    # Devuelve las últimas posiciones conocidas de las personas
    current_system_timestamp = date_service.get_current_date_utc().astimezone(current_timezone)
    users = user_service.get_users_positions()
    for user in users:
        user.lastUpdateInSeconds = (current_system_timestamp - user.lastUpdateTimestamp).total_seconds()
    
    return {
        "systemTimestamp": current_system_timestamp,
        "users": users
    }

@user_positions_router.get("/clear-user-positions")
async def clear_user_positions():
    # Borra los datos la base de datos de ubicaciones online
    users = user_service.clear_users_positions()