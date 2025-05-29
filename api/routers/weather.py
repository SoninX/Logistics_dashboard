from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from api.schemas.weather import WeatherCreate, WeatherResponse
from api.crud.weather import create_weather, create_weather_batch, delete_all_weather, get_weather
from api.database import get_db

router = APIRouter(prefix="/weather", tags=["weather"])

@router.post("/", response_model=dict)
async def create_weather_endpoint(weather: WeatherCreate, db: Session = Depends(get_db)):
    db_weather = create_weather(db, weather)
    return {"id": db_weather.id}

@router.post("/batch", response_model=List[dict])
async def create_weather_batch_endpoint(weathers: List[WeatherCreate], db: Session = Depends(get_db)):
    db_weathers = create_weather_batch(db, weathers)
    return [{"id": w.id} for w in db_weathers]

@router.delete("/all", response_model=dict)
async def delete_weather_endpoint(db: Session = Depends(get_db)):
    delete_all_weather(db)
    return {"status": "deleted"}

@router.get("/", response_model=List[WeatherResponse])
async def get_weather_endpoint(db: Session = Depends(get_db)):
    weather = get_weather(db)
    return weather