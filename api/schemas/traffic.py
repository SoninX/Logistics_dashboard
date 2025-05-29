from pydantic import BaseModel
from datetime import datetime

class TrafficCreate(BaseModel):
    location: str
    timestamp: str
    traffic_index: float
    delay_minutes: float
    severity: str

class TrafficResponse(BaseModel):
    id: int
    location: str
    timestamp: datetime
    traffic_index: float
    delay_minutes: float
    severity: str

    class Config:
        from_attributes = True