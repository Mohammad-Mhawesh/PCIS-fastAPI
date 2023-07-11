from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings
### For Regular SQL ###
""" import psycopg2 
from psycopg2.extras import RealDictCursor
import time """

db_url = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(db_url)

# create Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# establish a connection then closes for every execution


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


""" while True:
    try:
        conn = psycopg2.connect(host="localhost", database="FAST_API_DATABASE",
                                user="postgres", password="Nousername", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection sucessful")
        break

    except Exception as error:
        print("Database connection failed")
        print("Error: ", error)
        time.sleep(2)
 """
