from sqlalchemy.orm import Session
from api.models.delivery import Delivery
from api.schemas.delivery import DeliveryCreate

def create_delivery(db: Session, delivery: DeliveryCreate):
    db_delivery = Delivery(**delivery.dict())
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery

def create_delivery_batch(db: Session, deliveries: list[DeliveryCreate]):
    db_deliveries = [Delivery(**d.dict()) for d in deliveries]
    db.add_all(db_deliveries)
    db.commit()
    return db_deliveries

def delete_all_deliveries(db: Session):
    db.query(Delivery).delete()
    db.commit()

def get_deliveries(db: Session):
    return db.query(Delivery).all()