from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from api.schemas.delivery import DeliveryCreate, DeliveryResponse
from api.crud.delivery import create_delivery, create_delivery_batch, delete_all_deliveries, get_deliveries
from api.database import get_db

router = APIRouter(prefix="/deliveries", tags=["deliveries"])

@router.post("/", response_model=dict)
async def create_delivery_endpoint(delivery: DeliveryCreate, db: Session = Depends(get_db)):
    db_delivery = create_delivery(db, delivery)
    return {"id": db_delivery.id}

@router.post("/batch", response_model=List[dict])
async def create_delivery_batch_endpoint(deliveries: List[DeliveryCreate], db: Session = Depends(get_db)):
    db_deliveries = create_delivery_batch(db, deliveries)
    return [{"id": d.id} for d in db_deliveries]

@router.delete("/all", response_model=dict)
async def delete_deliveries_endpoint(db: Session = Depends(get_db)):
    delete_all_deliveries(db)
    return {"status": "deleted"}

@router.get("/", response_model=List[DeliveryResponse])
async def get_deliveries_endpoint(db: Session = Depends(get_db)):
    deliveries = get_deliveries(db)
    return deliveries