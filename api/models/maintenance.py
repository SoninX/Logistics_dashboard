from sqlalchemy import Column, Integer, String, Float, DateTime
from api.database import Base

class Maintenance(Base):
    __tablename__ = "maintenance"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer)
    date = Column(DateTime)
    type = Column(String)
    cost = Column(Float)
    description = Column(String)
    status = Column(String)