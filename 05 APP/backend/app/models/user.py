from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    userId: str
    deviceName: str
    lastUpdateTimestamp: datetime
    latitude: float
    longitude: float
    floorId: int
    lastUpdateInSeconds: int