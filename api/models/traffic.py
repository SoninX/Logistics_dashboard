from sqlalchemy import Column, Integer, String, Float, DateTime
from api.database import Base

class Traffic(Base):
    __tablename__ = "traffic"
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String)
    timestamp = Column(DateTime)
    traffic_index = Column(Float)
    delay_minutes = Column(Float)
    severity = Column(String)