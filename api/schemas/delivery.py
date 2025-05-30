from pydantic import BaseModel
from datetime import datetime

class DeliveryCreate(BaseModel):
    vehicle_id: int
    driver_id: int
    scheduled_time: str
    actual_time: str
    status: str
    sla_type: str
    distance_km: float
    fuel_consumed: float
    idle_time_min: float
    vehicle_condition: str
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    estimated_time_min: float
    actual_time_min: float
    fuel_efficiency: float
    estimated_fuel_cost: float
    route_efficiency: float
    traffic_index: float
    sla_compliance: int
    delay_minutes: float
    penalty_amount: float
    weather_condition: str
    weather_severity: str
    temperature: float
    humidity: int
    wind_speed: float
    date: str
    time_of_day: str
    day_of_week: str
    is_weekend: bool

class DeliveryResponse(BaseModel):
    id: int
    vehicle_id: int
    driver_id: int
    scheduled_time: datetime
    actual_time: datetime
    status: str
    sla_type: str
    distance_km: float
    fuel_consumed: float
    idle_time_min: float
    vehicle_condition: str
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    estimated_time_min: float
    actual_time_min: float
    fuel_efficiency: float
    estimated_fuel_cost: float
    route_efficiency: float
    traffic_index: float
    sla_compliance: int
    delay_minutes: float
    penalty_amount: float
    weather_condition: str
    weather_severity: str
    temperature: float
    humidity: int
    wind_speed: float
    date: datetime
    time_of_day: str
    day_of_week: str
    is_weekend: bool

    class Config:
        from_attributes = True