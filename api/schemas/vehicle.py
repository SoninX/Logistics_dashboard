from pydantic import BaseModel
from datetime import datetime

class VehicleCreate(BaseModel):
    model: str
    fuel_efficiency: float
    last_maintenance_date: str
    mileage: int
    idle_hours: float
    status: str
    avg_fuel_consumption: float
    engine_hours: int
    tire_condition: str
    battery_health: int

class VehicleResponse(BaseModel):
    id: int
    model: str
    fuel_efficiency: float
    last_maintenance_date: datetime
    mileage: int
    idle_hours: float
    status: str
    avg_fuel_consumption: float
    engine_hours: int
    tire_condition: str
    battery_health: int

    class Config:
        from_attributes = True