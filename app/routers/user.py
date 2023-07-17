from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter(
    prefix="/user",
    tags=['Users']
)

###### Create User ######


@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_user.user_type == "admin":

        month_year = datetime.now().strftime("%m%Y")
        user_username = user.first_name + user.last_name + month_year
        user_query = db.query(models.User).filter(
            models.User.username == user_username)
        check_user = user_query.first()
        if check_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"{check_user.username} is already a user.")
        user.password = utils.hash(user.password)
        user_dict = user.dict()
        print(user_dict)
        user_dict.update({"username": user_username})
        user_dict.update({"full_name": user.first_name + " " + user.last_name})
        new_user = models.User(**user_dict)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f'{current_user.username} is not allowed to create users.')


@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.user_id == id)
    user = user_query.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id = {id} not found")
    return user
