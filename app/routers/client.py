from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter(
    prefix="/client",
    tags=['Clients']
)

### Create Client ###
@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.ClientResponse)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.user_type == "admin" :
        ### Search if client already exists ###
        client_query = db.query(models.Client).filter(models.Client.client_name == client.client_name)
        client_search = client_query.first()
        if client_search :
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail= f"{client.client_name} is already a client!")
        else:
            new_client = models.Client(**client.dict())
            db.add(new_client)
            db.commit()
            db.refresh(new_client)
            return new_client
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f'{current_user.username} is not allowed to create clients')
    
### Get Clients ###
@router.get("/",status_code=status.HTTP_200_OK,response_model=List[schemas.ClientResponse])
def get_clients(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    clients = db.query(models.Client).all()
    return clients
