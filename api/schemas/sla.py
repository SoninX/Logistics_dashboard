from pydantic import BaseModel

class SLACreate(BaseModel):
    name: str
    max_hours: float
    penalty: float

class SLAResponse(BaseModel):
    id: int
    name: str
    max_hours: float
    penalty: float

    class Config:
        from_attributes = True