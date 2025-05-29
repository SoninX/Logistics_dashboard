from sqlalchemy.orm import Session
from api.models.route import Route
from api.schemas.route import RouteCreate

def create_route(db: Session, route: RouteCreate):
    db_route = Route(**route.dict())
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route

def create_routes_batch(db: Session, routes: list[RouteCreate]):
    db_routes = [Route(**r.dict()) for r in routes]
    db.add_all(db_routes)
    db.commit()
    return db_routes

def delete_all_routes(db: Session):
    db.query(Route).delete()
    db.commit()

def get_routes(db: Session):
    return db.query(Route).all()