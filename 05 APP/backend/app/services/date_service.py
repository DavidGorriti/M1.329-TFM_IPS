from datetime import datetime
from zoneinfo import ZoneInfo

class DateService:

    def get_current_date_utc(self):
        # Devuelve la fecha/hora actual en UTC
        return datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
        