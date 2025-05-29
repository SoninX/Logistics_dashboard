from pydantic import BaseModel

class RouteCreate(BaseModel):
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    distance_km: float
    typical_traffic: float
    route_name: str

class RouteResponse(BaseModel):
    id: int
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    distance_km: float
    typical_traffic: float
    route_name: str

    class Config:
        from_attributes = True