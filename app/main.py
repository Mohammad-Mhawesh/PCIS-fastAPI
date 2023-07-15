from fastapi import FastAPI

#from app import post, vote
from .database import engine
from . import models
from .routers import user, auth, call, client
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(call.router)
app.include_router(client.router)

@app.get("/")
def root():
    return {"message": "Pew Pew Pew Ahmad Mohsen"}
