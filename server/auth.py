import os

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from . import models,schemas

import bcrypt
from dotenv import load_dotenv

load_dotenv()

# Token expiration seconds Info from .env
ACCESS_TOKEN_EXPIRE = os.getenv("ACCESS_TOKEN_EXPIRE")
REFRESH_TOKEN_EXPIRE = os.getenv("REFRESH_TOKEN_EXPIRE")

# Secret key and algorithm for JWT from .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def register_user(db: Session, user:schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username = user.username, password = hashed_password)
    db.add(db_user)
    db.commit() 
    db.refresh(db_user)
    return db_user

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_password_hash(password):
    salt = bcrypt.gensalt(12, b"2b")
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def verify_password(plain_password, hashed_password):
    if bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8')):
        return True
    return False

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    print(expire)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

def create_tokens(username: str):
    access_token_expires = timedelta(seconds = int(ACCESS_TOKEN_EXPIRE))
    refresh_token_expires = timedelta(seconds = int(REFRESH_TOKEN_EXPIRE))
    
    access_token = create_token(
        data={"sub": username, "type": "access"},
        expires_delta = access_token_expires
    )
    refresh_token = create_token(
        data={"sub": username, "type": "refresh"},
        expires_delta = refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def get_current_user(db, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "access":
            raise credentials_exception
        token_data = schemas.TokenData(username = username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username = token_data.username)
    if user is None:
        raise credentials_exception
    return user
