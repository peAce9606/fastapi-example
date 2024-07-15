from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt

from sqlalchemy.orm import Session

from server import auth, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind = engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

#Dependency
def get_db():
    db = SessionLocal()
    try : 
        yield db
    finally:
        db.close()

@app.post("/auth/register",response_model = schemas.User)
def register_user(user:schemas.UserCreate, db:Session=Depends(get_db)):
    db_user = auth.get_user(db, username = user.username)
    if db_user:
        raise HTTPException(status_code = 400, detail = "Username already registered")
    return auth.register_user(db = db, user = user)

@app.post("/auth/login", response_model = schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username or password",
            headers = {"WWW-Authenticate": "Bearer"},
        )
    
    return auth.create_tokens(user.username)

@app.post("/auth/refresh", response_model = schemas.Token)
async def refresh_token(refresh_token: object = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(refresh_token, auth.SECRET_KEY, algorithms = [auth.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        if username is None or token_type != "refresh":
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid refresh token",
                headers = {"WWW-Authenticate": "Bearer"},
            )
        return auth.create_tokens(username)
    except JWTError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid refresh token",
            headers = {"WWW-Authenticate": "Bearer"},
        )

@app.get("/auth/me", response_model = schemas.User)
def read_users_me(token: object = Depends(oauth2_scheme), db:Session = Depends(get_db)):
    current_user = auth.get_current_user(db, token)
    return current_user
