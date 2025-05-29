from pydantic import BaseModel
from datetime import datetime

class DriverCreate(BaseModel):
    name: str
    license_number: str
    total_deliveries: int
    punctuality_score: float
    incident_count: int
    status: str
    training_completed: str
    joined_date: str
    contact_number: str

class DriverResponse(BaseModel):
    id: int
    name: str
    license_number: str
    total_deliveries: int
    punctuality_score: float
    incident_count: int
    status: str
    training_completed: bool
    joined_date: datetime
    contact_number: str

    class Config:
        from_attributes = True