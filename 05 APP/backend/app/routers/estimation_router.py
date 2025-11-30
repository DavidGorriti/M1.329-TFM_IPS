from fastapi import APIRouter
from datetime import datetime
from zoneinfo import ZoneInfo
from services.knn_service import KNNService
from services.user_position_service import UserPositionService
from services.date_service import DateService
from models.estimate_position_request import EstimatePositionRequest
from config.config import Config
from repositories.database_repo import Database

config = Config()
estimation_router = APIRouter()
knn_service = KNNService()
user_position_service = UserPositionService()
current_timezone = ZoneInfo(config.timezone)
date_service = DateService()

@estimation_router.post("/estimate-position")
async def estimate_position(request: EstimatePositionRequest):
    # Realiza la estimación de la posición y lo devuelve en la respuesta
    current_system_timestamp = date_service.get_current_date_utc()

    position = knn_service.estimate_2d_floor(request)
    position["device_name"] = request.device_name
    position["currentTimestamp"] = current_system_timestamp
    
    user_position_service.update_user_info(position,request.wifi_measurements)
    
    position["currentTimestamp"] = current_system_timestamp.astimezone(current_timezone).isoformat()
    
    return position