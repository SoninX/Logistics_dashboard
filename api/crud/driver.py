from sqlalchemy.orm import Session
from api.models.driver import Driver
from api.schemas.driver import DriverCreate

def create_driver(db: Session, driver: DriverCreate):
    db_driver = Driver(**driver.dict())
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

def create_driver_batch(db: Session, drivers: list[DriverCreate]):
    db_drivers = [Driver(**d.dict()) for d in drivers]
    db.add_all(db_drivers)
    db.commit()
    return db_drivers

def delete_all_drivers(db: Session):
    db.query(Driver).delete()
    db.commit()

def get_drivers(db: Session):
    return db.query(Driver).all()