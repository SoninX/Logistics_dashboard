from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from api.schemas.route import RouteCreate, RouteResponse
from api.crud.route import create_route, create_routes_batch, delete_all_routes, get_routes
from api.database import get_db

router = APIRouter(prefix="/routes", tags=["routes"])

@router.post("/", response_model=dict)
async def create_route_endpoint(route: RouteCreate, db: Session = Depends(get_db)):
    db_route = create_route(db, route)
    return {"id": db_route.id}

@router.post("/batch", response_model=List[dict])
async def create_routes_batch_endpoint(routes: List[RouteCreate], db: Session = Depends(get_db)):
    db_routes = create_routes_batch(db, routes)
    return [{"id": r.id} for r in db_routes]

@router.delete("/all", response_model=dict)
async def delete_routes_endpoint(db: Session = Depends(get_db)):
    delete_all_routes(db)
    return {"status": "deleted"}

@router.get("/", response_model=List[RouteResponse])
async def get_routes_endpoint(db: Session = Depends(get_db)):
    routes = get_routes(db)
    return routes