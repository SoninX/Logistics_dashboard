from sqlalchemy import Column, Integer, String, Float
from api.database import Base

class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    origin_lat = Column(Float)
    origin_lng = Column(Float)
    dest_lat = Column(Float)
    dest_lng = Column(Float)
    distance_km = Column(Float)
    typical_traffic = Column(Float)
    route_name = Column(String)