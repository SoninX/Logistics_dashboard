from sqlalchemy import Column, Integer, String, Float
from api.database import Base

class SLA(Base):
    __tablename__ = "slas"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    max_hours = Column(Float)
    penalty = Column(Float)