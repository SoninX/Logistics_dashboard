from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from api.schemas.driver import DriverCreate, DriverResponse
from api.crud.driver import create_driver, create_driver_batch, delete_all_drivers, get_drivers
from api.database import get_db

router = APIRouter(prefix="/drivers", tags=["drivers"])

@router.post("/", response_model=dict)
async def create_driver_endpoint(driver: DriverCreate, db: Session = Depends(get_db)):
    db_driver = create_driver(db, driver)
    return {"id": db_driver.id}

@router.post("/batch", response_model=List[dict])
async def create_driver_batch_endpoint(drivers: List[DriverCreate], db: Session = Depends(get_db)):
    db_drivers = create_driver_batch(db, drivers)
    return [{"id": d.id} for d in db_drivers]

@router.delete("/all", response_model=dict)
async def delete_drivers_endpoint(db: Session = Depends(get_db)):
    delete_all_drivers(db)
    return {"status": "deleted"}

@router.get("/", response_model=List[DriverResponse])
async def get_drivers_endpoint(db: Session = Depends(get_db)):
    drivers = get_drivers(db)
    return drivers