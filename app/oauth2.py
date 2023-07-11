from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from .config import settings

from . import schemas, database,models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):

    # copying the input
    to_encode = data.copy()
    # set the expire time
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # adding the expire property to the "copy" of the dictionary
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, crendtials_exception):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id: str = payload.get("user_id","user_type")
        if id is None:
            raise crendtials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise crendtials_exception
    return token_data 


def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(database.get_db)):
    crendtials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, crendtials_exception)
    user = db.query(models.User).filter(models.User.user_id == token.id).first()
    return user
