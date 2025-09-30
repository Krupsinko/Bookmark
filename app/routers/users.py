from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import os

from ..db.database import get_db
from ..db.models import User
from ..schemas.schemas import CreateUserRequest, CreateUserResponse, Token


ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/token")
bcrypt_context = CryptContext(schemes=["bcrypt"])

router = APIRouter(
    prefix="/user",
    tags=["User"])


db_dependency = Annotated[AsyncSession, Depends(get_db)]
    
    
async def authenticate_user(username: str, password: str, db: db_dependency):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
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
                             key=SECRET_KEY,
                             algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        role = payload.get("role")
        if username is None or user_id is None or role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Unauthorized",
                                headers={"WWW-Authenticate": "Bearer"})
        return {"sub": username, "id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    
    
    
@router.post("/token",status_code=status.HTTP_200_OK ,response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Invalid credentials")
    token = create_jwt(user.username, user.id, user.role, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}



    
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CreateUserResponse)
async def create_user(db: db_dependency, 
                      user_request: CreateUserRequest):
    stmt = select(User).where(User.email == user_request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    new_user = User(
        email=user_request.email,
        username=user_request.username,
        hashed_password=bcrypt_context.hash(user_request.password),
        role=user_request.role)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
