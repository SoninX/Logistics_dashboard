from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from api.schemas.vehicle import VehicleCreate, VehicleResponse
from api.crud.vehicle import create_vehicle, create_vehicle_batch, delete_all_vehicles, get_vehicles
from api.database import get_db

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.post("/", response_model=dict)
async def create_vehicle_endpoint(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = create_vehicle(db, vehicle)
    return {"id": db_vehicle.id}

@router.post("/batch", response_model=List[dict])
async def create_vehicle_batch_endpoint(vehicles: List[VehicleCreate], db: Session = Depends(get_db)):
    db_vehicles = create_vehicle_batch(db, vehicles)
    return [{"id": v.id} for v in db_vehicles]

@router.delete("/all", response_model=dict)
async def delete_vehicles_endpoint(db: Session = Depends(get_db)):
    delete_all_vehicles(db)
    return {"status": "deleted"}

@router.get("/", response_model=List[VehicleResponse])
async def get_vehicles_endpoint(db: Session = Depends(get_db)):
    vehicles = get_vehicles(db)
    return vehicles