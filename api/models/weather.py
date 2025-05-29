from sqlalchemy import Column, Integer, String, Float, DateTime
from api.database import Base

class Weather(Base):
    __tablename__ = "weather"
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String)
    timestamp = Column(DateTime)
    temperature = Column(Float)
    condition = Column(String)
    wind_speed = Column(Float)
    humidity = Column(Integer)
    severity = Column(String)