from sqlalchemy.orm import Session
from api.models.sla import SLA
from api.schemas.sla import SLACreate

def create_sla(db: Session, sla: SLACreate):
    db_sla = SLA(**sla.dict())
    db.add(db_sla)
    db.commit()
    db.refresh(db_sla)
    return db_sla

def create_slas_batch(db: Session, slas: list[SLACreate]):
    db_slas = [SLA(**s.dict()) for s in slas]
    db.add_all(db_slas)
    db.commit()
    return db_slas

def delete_all_slas(db: Session):
    db.query(SLA).delete()
    db.commit()

def get_slas(db: Session):
    return db.query(SLA).all()