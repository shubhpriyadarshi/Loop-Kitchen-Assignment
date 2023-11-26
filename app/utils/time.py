import pytz
from app.models.business_hours.models import BusinessHours

def utc_to_local(timestamp, timezone):
    utc = pytz.utc.localize(timestamp)
    local = utc.astimezone(pytz.timezone(timezone))
    return local

