from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from api.schemas.maintenance import MaintenanceCreate, MaintenanceResponse
from api.crud.maintenance import create_maintenance, create_maintenance_batch, delete_all_maintenance, get_maintenance
from api.database import get_db

router = APIRouter(prefix="/maintenance", tags=["maintenance"])

@router.post("/", response_model=dict)
async def create_maintenance_endpoint(maintenance: MaintenanceCreate, db: Session = Depends(get_db)):
    db_maintenance = create_maintenance(db, maintenance)
    return {"id": db_maintenance.id}

@router.post("/batch", response_model=List[dict])
async def create_maintenance_batch_endpoint(maintenances: List[MaintenanceCreate], db: Session = Depends(get_db)):
    db_maintenances = create_maintenance_batch(db, maintenances)
    return [{"id": m.id} for m in db_maintenances]

@router.delete("/all", response_model=dict)
async def delete_maintenance_endpoint(db: Session = Depends(get_db)):
    delete_all_maintenance(db)
    return {"status": "deleted"}

@router.get("/", response_model=List[MaintenanceResponse])
async def get_maintenance_endpoint(db: Session = Depends(get_db)):
    maintenance = get_maintenance(db)
    return maintenance