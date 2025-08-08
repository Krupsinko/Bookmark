from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from sqlalchemy.orm import Session
from ..db.database import SessionLocal
from ..db.models import Users

from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import os

ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/token")
bcrypt_context = CryptContext(schemes=["bcrypt"])

router = APIRouter(
    prefix="/user",
    tags=["User"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
    
class CreateUserRequest(BaseModel):
    email: str
    username: str
    password: str
    role: str
    
    
class CreateUserResponse(BaseModel):
    id: int
    name: str
    email: str
    
    class Config():
        from_attributes = True
        
        
class Token(BaseModel):
    access_token: str
    token_type: str
    
    
def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username==username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user



    
def create_jwt(username: str, user_id: int, role:str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)




def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token,
                             SECRET_KEY,
                             ALGORITHM)
        username = payload.get("sub")
        user_id = payload.get("id")
        role = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Unauthorized",
                                headers={"WWW-Authenticate": "Bearer"})
        return {"sub": username, "id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    
    
    
@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Invalid credentials")
    token = create_jwt(user.username, user.id, user.role, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}



    
@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def create_user(db: db_dependency, 
                      user_request: CreateUserRequest):
    user = db.query(Users).filter(Users.email==user_request.email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    new_user = Users(
        email=user_request.email,
        username=user_request.username,
        hashed_password=bcrypt_context.hash(user_request.password),
        role=user_request.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
