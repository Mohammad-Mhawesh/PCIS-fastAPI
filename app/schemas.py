from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    password: str
    user_type: str
    phone_number: str


class UserLogin(UserCreate):
    pass


class UserResponse(BaseModel):
    full_name: str
    username: str
    phone_number: int
    user_id: int

    class Config:
        orm_mode = True

# ------------------------------------------------------------
# Machine


class MachineResponse(BaseModel):
    machine_id: int
    client_id: int

    class Config:
        orm_mode = True
# ------------------------------------------------------------
# Client


class ClientCreate(BaseModel):
    client_name: str


class ClientResponse(BaseModel):

    client_name: str
    client_id: int

    class Config:
        orm_mode = True
# ------------------------------------------------------------
# Calls


class CallUpdate(BaseModel):
    client_id: Optional[int] = None
    client_name:  Optional[str] = None
    assigned_to_id: Optional[int] = None
    machine_id: Optional[int] = None
    cause: Optional[str] = ""


class CallCreate(BaseModel):
    client_id: Optional[int] = None
    client_name:  Optional[str] = None
    assigned_to_id: int
    machine_id: int
    cause: str = "Cause not recorded"
    engineer_response: str = "Waiting for engineer's response"


class CallResponse(BaseModel):
    call_id: int
    cause: str
    engineer_response : str = None
    closed: bool
#    machine_id = int
    client: ClientResponse
    machine: MachineResponse
    assigned_to_user: UserResponse
    created_by_user: UserResponse

    class Config:
        orm_mode = True

# ------------------------------------------------------------


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    owner: UserResponse
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class PostVoteResponse(BaseModel):
    Post: PostResponse
    votes: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)
