from pydantic import BaseModel, ValidationError, EmailStr, PositiveInt, validator
from typing import Optional
import datetime
import phonenumbers as ph


class UserCreatePydantic(BaseModel):
    email: EmailStr
    user_handle: str
    password: str
    phone_number: Optional[str]
    exp: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True
    
    @validator("phone_number")
    def validate_phone_number(cls, v):
        phone_number = ph.parse(v)
        return ph.is_possible_number(phone_number)


class UserLoginPydantic(BaseModel):
    user_handle: str
    password: str

    class Config:
        orm_mode = True


class UserPydantic(BaseModel):
    id: int
    user_handle: str

    class Config:
        orm_mode = True
    

class RoomCreatePydantic(BaseModel):
    room_name: str

    class Config:
        orm_mode = True


class RoomPydantic(BaseModel):
    id: int
    room_name: str
    room_code: str
    created_on: datetime.datetime

    class Config:
        orm_mode = True