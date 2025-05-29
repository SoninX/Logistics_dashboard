from sqlalchemy.orm import Session
from api.models.vehicle import Vehicle
from api.schemas.vehicle import VehicleCreate

def create_vehicle(db: Session, vehicle: VehicleCreate):
    db_vehicle = Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def create_vehicle_batch(db: Session, vehicles: list[VehicleCreate]):
    db_vehicles = [Vehicle(**v.dict()) for v in vehicles]
    db.add_all(db_vehicles)
    db.commit()
    return db_vehicles

def delete_all_vehicles(db: Session):
    db.query(Vehicle).delete()
    db.commit()

def get_vehicles(db: Session):
    return db.query(Vehicle).all()