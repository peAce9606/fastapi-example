from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True,index = True)
    username = Column(String(255), unique = True)
    password = Column(String(255))
    created_at = Column(DateTime, default = datetime.now)
    last_login = Column(DateTime, default = datetime.now)
