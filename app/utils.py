from typing import List
from .import models
from sqlalchemy.orm import Session
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_client_by_id_or_name(db: Session, client_id: int, client_name: str) -> models.Client:
    if client_id != -1:
        return db.query(models.Client).filter(models.Client.client_id == client_id).first()
    elif client_name != "":
        return db.query(models.Client).filter(models.Client.client_name == client_name).first()
    return None


def get_user_by_id(db: Session, user_id: int) -> models.User:
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_machine_by_id_and_client_id(db: Session, machine_id: int, client_id: int) -> models.Machine:
    return db.query(models.Machine).filter(models.Machine.machine_id == machine_id, models.Machine.client_id == client_id).first()


def get_call_by_id(db: Session, call_id: int) -> models.Call:
    return db.query(models.Call).filter(models.Call.call_id == call_id).first()


def get_all_calls(db: Session, limit: int, skip: int) -> List[models.Call]:
    return db.query(models.Call).limit(limit).offset(skip).all()


""" def get_all_calls_by_search(db:Session,search:str,limit:int,skip:int):
    return db.query(models.Call).filter(models.Call.) """


def get_engineer_call_by_id(db: Session, call_id: int, assigned_to_id: int,) -> models.Call:
    return db.query(models.Call).filter(models.Call.call_id == call_id, models.Call.assigned_to_id == assigned_to_id).first()


def get_engineer_calls(db: Session, assigned_to_id: int, limit: int, skip: int) -> List[models.Call]:
    return db.query(models.Call).filter(models.Call.assigned_to_id == assigned_to_id).limit(limit).offset(skip).all()


def get_engineer_closed_calls(db: Session, assigned_to_id: int, limit: int, skip: int) -> List[models.Call]:
    return db.query(models.Call).filter(models.Call.assigned_to_id == assigned_to_id, models.Call.closed == True ).limit(limit).offset(skip).all()
    
def get_engineer_open_calls(db: Session, assigned_to_id: int, limit: int, skip: int) -> List[models.Call]:
    return db.query(models.Call).filter(models.Call.assigned_to_id == assigned_to_id, models.Call.closed == False).limit(limit).offset(skip).all()
