from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from models import User
import schemas
from datetime import datetime, timedelta
import jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


ALGORITHM = ["HS256"]
ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_SECRET = "30da6931cbb41a02566302e347f9ac2bd423b74c48bd117467c524fbf65ea359"


async def authenticate_user(user_handle: str, password: str):
    user = await User.get(user_handle=user_handle)
    if(not user):
        return False
    if(not user.verify_password(password)):
        return False
    return user

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