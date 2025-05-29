from sqlalchemy.orm import Session
from api.models.weather import Weather
from api.schemas.weather import WeatherCreate

def create_weather(db: Session, weather: WeatherCreate):
    db_weather = Weather(**weather.dict())
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    return db_weather

def create_weather_batch(db: Session, weathers: list[WeatherCreate]):
    db_weathers = [Weather(**w.dict()) for w in weathers]
    db.add_all(db_weathers)
    db.commit()
    return db_weathers

def delete_all_weather(db: Session):
    db.query(Weather).delete()
    db.commit()

def get_weather(db: Session):
    return db.query(Weather).all()