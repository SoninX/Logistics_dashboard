from pydantic import BaseModel
from datetime import datetime

class WeatherCreate(BaseModel):
    location: str
    timestamp: str
    temperature: float
    condition: str
    wind_speed: float
    humidity: int
    severity: str

class WeatherResponse(BaseModel):
    id: int
    location: str
    timestamp: datetime
    temperature: float
    condition: str
    wind_speed: float
    humidity: int
    severity: str

    class Config:
        from_attributes = True