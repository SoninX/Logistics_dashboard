from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from api.schemas.traffic import TrafficCreate, TrafficResponse
from api.crud.traffic import create_traffic, create_traffic_batch, delete_all_traffic, get_traffic
from api.database import get_db

router = APIRouter(prefix="/traffic", tags=["traffic"])

@router.post("/", response_model=dict)
async def create_traffic_endpoint(traffic: TrafficCreate, db: Session = Depends(get_db)):
    db_traffic = create_traffic(db, traffic)
    return {"id": db_traffic.id}

@router.post("/batch", response_model=List[dict])
async def create_traffic_batch_endpoint(traffics: List[TrafficCreate], db: Session = Depends(get_db)):
    db_traffics = create_traffic_batch(db, traffics)
    return [{"id": t.id} for t in db_traffics]

@router.delete("/all", response_model=dict)
async def delete_traffic_endpoint(db: Session = Depends(get_db)):
    delete_all_traffic(db)
    return {"status": "deleted"}

@router.get("/", response_model=List[TrafficResponse])
async def get_traffic_endpoint(db: Session = Depends(get_db)):
    traffic = get_traffic(db)
    return traffic