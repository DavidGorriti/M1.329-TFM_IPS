from pydantic import BaseModel

class WifiMeasurement(BaseModel):
    mac_bssid: str
    rssi: float