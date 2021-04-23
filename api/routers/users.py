import schemas
from models import User
from typing import List
from datetime import datetime, timedelta
import jwt
from fastapi import Depends, HTTPException, status, APIRouter
from passlib.hash import bcrypt
from dependencies import (authenticate_user, 
                                get_current_user_util, 
                                oauth2_scheme, 
                                ACCESS_TOKEN_EXPIRE_MINUTES,
                                JWT_SECRET,
                                ALGORITHM,)


router = APIRouter(tags=["users"])


@router.post('/auth/token')
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

@router.post("/auth/register", response_model=schemas.UserPydantic)
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

@router.get('/users/me', response_model=schemas.UserPydantic)
async def get_current_user(user: schemas.UserPydantic=Depends(get_current_user_util)):
    return user

@router.delete('/users/me/delete')
async def delete_current_user(user: schemas.UserPydantic=Depends(get_current_user_util)):
    obj = await User.get_user(user.id)
    await obj.delete()
    return{
        "message" : "User deleted",
    }