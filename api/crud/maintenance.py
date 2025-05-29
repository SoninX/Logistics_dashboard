from sqlalchemy.orm import Session
from api.models.maintenance import Maintenance
from api.schemas.maintenance import MaintenanceCreate

def create_maintenance(db: Session, maintenance: MaintenanceCreate):
    db_maintenance = Maintenance(**maintenance.dict())
    db.add(db_maintenance)
    db.commit()
    db.refresh(db_maintenance)
    return db_maintenance

def create_maintenance_batch(db: Session, maintenances: list[MaintenanceCreate]):
    db_maintenances = [Maintenance(**m.dict()) for m in maintenances]
    db.add_all(db_maintenances)
    db.commit()
    return db_maintenances

def delete_all_maintenance(db: Session):
    db.query(Maintenance).delete()
    db.commit()

def get_maintenance(db: Session):
    return db.query(Maintenance).all()