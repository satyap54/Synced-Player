import schemas
from models import User, Room

from typing import Optional, List
from datetime import datetime, timedelta

import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, oauth2
from fastapi.encoders import jsonable_encoder
from passlib.hash import bcrypt
from tortoise.contrib.fastapi import register_tortoise

'''
TODO:
    1) Test using postman, swagger UI doesn't take in acces_token in header. For now, use Mod-Headers
    2) Modify RoomPydantic to include some data about host
'''

app = FastAPI()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
ALGORITHM = ["HS256"]
ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_SECRET = "30da6931cbb41a02566302e347f9ac2bd423b74c48bd117467c524fbf65ea359"


register_tortoise(
    app,
    db_url="sqlite://store.db",
    modules={
        'models': ['models'],
    },
    generate_schemas=True,
    add_exception_handlers=True,
)


async def authenticate_user(user_handle: str, password: str):
    user = await User.get(user_handle=user_handle)
    if(not user):
        return False
    if(not user.verify_password(password)):
        return False
    return user


'''
    End-points for user's data
'''
@app.post('/auth/token')
async def generate_token(user_data: schemas.UserLoginPydantic):
    user = await authenticate_user(user_data.user_handle, user_data.password)
    if(not user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid handle or password",
        )
    user_obj = schemas.UserPydantic.from_orm(user)
    to_encode = user_obj.dict()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #user_obj.exp = expire
    to_encode.update({"exp" : expire})
    token = jwt.encode(to_encode, JWT_SECRET)
    return{
        "access_token": token,
        "token_type": "bearer",
    }

@app.post("/auth/register", response_model=schemas.UserPydantic)
async def create_user(user_data: schemas.UserCreatePydantic):
    user_obj = await User.create(
        user_handle = user_data.user_handle,
        email = user_data.email,
        phone_number = user_data.phone_number,
        password_hash = bcrypt.hash(user_data.password),
    )
    await user_obj.save()
    obj = schemas.UserPydantic.from_orm(user_obj)
    return obj

async def get_current_user_util(token: str=Depends(oauth2_scheme)):
    user = None
    try: 
        payload = jwt.decode(token, JWT_SECRET, algorithms=ALGORITHM)
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or user doesn't exist",
        )
    obj = schemas.UserPydantic.from_orm(user)
    return obj

@app.get('/users/me', response_model=schemas.UserPydantic)
async def get_current_user(user: schemas.UserPydantic=Depends(get_current_user_util)):
    return user


'''
    End-points for rooms
'''
@app.post('/room/create', response_model=schemas.RoomPydantic)
async def create_room(room: schemas.RoomCreatePydantic, user: schemas.UserPydantic=Depends(get_current_user_util)):
    room_code = await Room.generate_room_code()
    created_room = await Room.create(
        host = await User.get_user(user.id),
        room_name = room.room_name,
        room_code = room_code,
    )
    await created_room.save()
    obj = schemas.RoomPydantic(id=created_room.id, room_name=created_room.room_name, room_code = created_room.room_code,
                        created_on=created_room.created_on, host=jsonable_encoder(created_room.host.user_handle))
    return obj

@app.get('/room/myrooms', response_model=List[schemas.RoomPydantic])
async def get_user_rooms(user: schemas.UserPydantic=Depends(get_current_user_util)):
    user = await User.get_user(user.id)
    rooms_list = await Room.filter(host=user)
    ret_list = [schemas.RoomPydantic(id=obj.id, room_name=obj.room_name, room_code=obj.room_code, created_on=obj.created_on,
                host=user.user_handle) for obj in rooms_list]
    return ret_list

@app.get('/room/{room_code}', response_model=schemas.RoomPydantic)
async def get_room(room_code: str):
    room = await Room.get(room_code=room_code).prefetch_related("host").first()
    obj = schemas.RoomPydantic(id=room.id, room_name=room.room_name, room_code = room.room_code, created_on=room.created_on,
                                host=room.host.user_handle)
    return obj