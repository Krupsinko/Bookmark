from pytest import MonkeyPatch
from sqlalchemy import select
from freezegun import freeze_time
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta


from .utils import *
from app.db.models import User
from app.routers.users import authenticate_user, get_current_user
import app.routers.users as users





@pytest.mark.asyncio
async def test_authenticate_user(seed_data,
                                 db_session):
    username = "test"
    password = "x"
    
    stmt = select(User).where(User.username == username)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    assert user is not None
    
    test_user = await authenticate_user(username, password, db_session)
    assert test_user is not None
    assert test_user == user 
    
    
    

@freeze_time("2025-01-01 12:00:00", tz_offset=0)
def test_create_jwt(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(users, "ALGORITHM", "HS256")
    monkeypatch.setattr(users, "SECRET_KEY", "testkey")
    username = "testuser"
    user_id = 1
    role = "user"
    token = users.create_jwt(username, user_id, role, timedelta(minutes=30))
    assert isinstance(token, str) and token
    
    payload = jwt.decode(token, key="testkey", algorithms="HS256")
    assert payload["sub"] == username
    assert payload["id"] == user_id
    assert payload["role"] == role
    assert payload["exp"] == int(datetime(2025, 1, 1, 12, 30, tzinfo=timezone.utc).timestamp())




def test_get_current_user(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(users, "ALGORITHM", "HS256")
    monkeypatch.setattr(users, "SECRET_KEY", "testkey")
    
    username = "testuser"
    user_id = 1
    role = "user"
    
    token = users.create_jwt(username, user_id, role, timedelta(minutes=30))
    user = get_current_user(token)
    
    assert user is not None
    assert user["sub"] == username
    assert user["id"] == user_id
    assert user["role"] == role
    
    
    
    
def test_get_current_user_invalid_signature(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(users, "ALGORITHM", "HS256")
    monkeypatch.setattr(users, "SECRET_KEY", "testkey")
    
    encode = {"sub": "testuser",
              "id": 1,
              "role": "user"}
    
    token = jwt.encode(encode, key="wrong_key", algorithm="HS256")
    
    with pytest.raises(HTTPException) as excinfo:
        users.get_current_user(token)
        
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    


@freeze_time("2025-01-01 12:00:00", tz_offset=0)
def test_get_current_user_expired_token(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(users, "ALGORITHM", "HS256")
    monkeypatch.setattr(users, "SECRET_KEY", "testkey")
    
    token = users.create_jwt("testuser", 1, "user", timedelta(minutes=30))
    
    with freeze_time("2025-01-01 12:31:00"):
        with pytest.raises(HTTPException) as excinfo:
            get_current_user(token)
    
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        
        


def test_get_current_user_missing_claims(monkeypatch: MonkeyPatch):
    monkeypatch.setattr(users, "ALGORITHM", "HS256")
    monkeypatch.setattr(users, "SECRET_KEY", "testkey")
    
    # Missing "id": 1, key-value pair
    encode = {"sub": "testuser",
              "role": "user"}
    
    token = jwt.encode(encode, key="testkey", algorithm="HS256")
    
    with pytest.raises(HTTPException) as excinfo:
        users.get_current_user(token)
        
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    
    
    
@pytest.mark.asyncio
async def test_login(seed_data,
                     db_session,
                     monkeypatch: MonkeyPatch,
                     async_client: AsyncClient):
    
    monkeypatch.setattr(users, "ALGORITHM", "HS256")
    monkeypatch.setattr(users, "SECRET_KEY", "testkey")
    
    request_data = {"username": "test",
                    "password": "x"}
    
    response = await async_client.post("/user/token",
                                       data=request_data)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"
    
    access_token = response_data["access_token"]
    payload = jwt.decode(token=access_token, key="testkey", algorithms="HS256")
    
    assert payload["sub"] == "test"
    assert payload["id"] == 1
    assert payload["role"] == "user"




@pytest.mark.asyncio
async def test_create_user(db_session,
                           async_client: AsyncClient):
    request_data = {
        "email": "test@email.com",
        "username": "testuser",
        "password": "x",
        "role": "user"
    }
    
    response = await async_client.post("/user/", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    result = await db_session.execute(select(User).where(User.email == request_data["email"]))
    user = result.scalar_one_or_none()
    
    assert user.email == request_data["email"]
    assert user.username == request_data["username"]
    assert bcrypt_context.verify(request_data["password"], user.hashed_password)
    assert user.role == request_data["role"]
    