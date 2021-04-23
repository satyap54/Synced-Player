from fastapi import APIRouter
import schemas
from models import Room, User
from typing import List
from fastapi import Depends, HTTPException, status
from dependencies import get_current_user_util
from fastapi.encoders import jsonable_encoder


router = APIRouter(tags=["rooms"])


@router.post('/room/create', response_model=schemas.RoomPydantic)
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

@router.get('/room/myrooms', response_model=List[schemas.RoomPydantic])
async def get_user_rooms(user: schemas.UserPydantic=Depends(get_current_user_util)):
    user = await User.get_user(user.id)
    rooms_list = await Room.filter(host=user)
    ret_list = [schemas.RoomPydantic(id=obj.id, room_name=obj.room_name, room_code=obj.room_code, created_on=obj.created_on,
                host=user.user_handle) for obj in rooms_list]
    return ret_list

@router.get('/room/{room_code}', response_model=schemas.RoomPydantic)
async def get_room(room_code: str):
    room = await Room.get(room_code=room_code).prefetch_related("host").first()
    obj = schemas.RoomPydantic(id=room.id, room_name=room.room_name, room_code = room.room_code, created_on=room.created_on,
                                host=room.host.user_handle)
    return obj

@router.delete('/room/{room_code}')
async def delete_room(room_code: str, user: schemas.UserPydantic=Depends(get_current_user_util)):
    room = await Room.get(room_code=room_code).prefetch_related("host").first()
    user = await User.get_user(id=user.id)
    if(not (room.host == user)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only host can delete the room",
        )
    await room.delete()
    return{
        "message" : f'Room with code {room_code} deleted'
    }