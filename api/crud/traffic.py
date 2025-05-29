from sqlalchemy.orm import Session
from api.models.traffic import Traffic
from api.schemas.traffic import TrafficCreate

def create_traffic(db: Session, traffic: TrafficCreate):
    db_traffic = Traffic(**traffic.dict())
    db.add(db_traffic)
    db.commit()
    db.refresh(db_traffic)
    return db_traffic

def create_traffic_batch(db: Session, traffics: list[TrafficCreate]):
    db_traffics = [Traffic(**t.dict()) for t in traffics]
    db.add_all(db_traffics)
    db.commit()
    return db_traffics

def delete_all_traffic(db: Session):
    db.query(Traffic).delete()
    db.commit()

def get_traffic(db: Session):
    return db.query(Traffic).all()