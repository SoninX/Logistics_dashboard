from pydantic import BaseModel
from datetime import datetime

class MaintenanceCreate(BaseModel):
    vehicle_id: int
    date: str
    type: str
    cost: float
    description: str
    status: str

class MaintenanceResponse(BaseModel):
    id: int
    vehicle_id: int
    date: datetime
    type: str
    cost: float
    description: str
    status: str

    class Config:
        from_attributes = True