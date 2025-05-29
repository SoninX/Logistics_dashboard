from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from api.schemas.sla import SLACreate, SLAResponse
from api.crud.sla import create_sla, create_slas_batch, delete_all_slas, get_slas
from api.database import get_db

router = APIRouter(prefix="/slas", tags=["slas"])

@router.post("/", response_model=dict)
async def create_sla_endpoint(sla: SLACreate, db: Session = Depends(get_db)):
    db_sla = create_sla(db, sla)
    return {"id": db_sla.id}

@router.post("/batch", response_model=List[dict])
async def create_slas_batch_endpoint(slas: List[SLACreate], db: Session = Depends(get_db)):
    db_slas = create_slas_batch(db, slas)
    return [{"id": s.id} for s in db_slas]

@router.delete("/all", response_model=dict)
async def delete_slas_endpoint(db: Session = Depends(get_db)):
    delete_all_slas(db)
    return {"status": "deleted"}

@router.get("/", response_model=List[SLAResponse])
async def get_slas_endpoint(db: Session = Depends(get_db)):
    slas = get_slas(db)
    return slas