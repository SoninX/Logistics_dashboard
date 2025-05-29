from sqlalchemy import Column, Integer, String, Float, DateTime
from api.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String)
    fuel_efficiency = Column(Float)
    last_maintenance_date = Column(DateTime)
    mileage = Column(Integer)
    idle_hours = Column(Float)
    status = Column(String)
    avg_fuel_consumption = Column(Float)
    engine_hours = Column(Integer)
    tire_condition = Column(String)
    battery_health = Column(Integer)