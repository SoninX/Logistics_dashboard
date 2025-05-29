from sqlalchemy import Column, Integer, String, Float, DateTime
from api.database import Base

class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    license_number = Column(String)
    total_deliveries = Column(Integer)
    punctuality_score = Column(Float)
    incident_count = Column(Integer)
    status = Column(String)
    training_completed = Column(String)
    joined_date = Column(DateTime)
    contact_number = Column(String)