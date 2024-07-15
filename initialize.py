import os

from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# MySQL Connection Info from .env
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DB_NAME = os.getenv("DB_NAME")

# Create a connection to the MySQL server (not to a specific database)
def create_new_database():
    engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}")
    
    try:
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
        return {"message": f"Database '{DB_NAME}' created successfully"}
    except Exception as e:
        return {"error": str(e)}

def check_database():
    # Check if the database exists
    engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}")
    if database_exists(engine.url):
        return {"message": f"Database '{DB_NAME}' exists"}
    else:
        return {"message": f"Database '{DB_NAME}' does not exist"}

if __name__ == "__main__":
    database_check_result = check_database()
    if database_check_result["message"] == f"Database '{DB_NAME}' does not exist":
        result = create_new_database()
        print(result["message"])
    else:
        print(database_check_result["message"])
