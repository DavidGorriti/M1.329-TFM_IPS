from pydantic import BaseModel
from typing import List
from models.wifi_measurement import WifiMeasurement

class EstimatePositionRequest(BaseModel):
    device_name: str
    wifi_measurements: List[WifiMeasurement]