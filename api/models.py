from enum import unique
from tortoise import fields, models
from passlib.hash import bcrypt
import uuid


'''
TODO:
    1) Define Regex validators for:
        a) user_handle should not contain special characters except underscore
        b) email
        c) phone_number
'''
class User(models.Model):
    # uses auto-generated id as pk
    email = fields.CharField(max_length=50, unique=True, null=False)
    user_handle = fields.CharField(max_length=20, unique=True, null=False)
    joined = fields.DatetimeField(auto_now_add=True, auto_now=False)
    password_hash = fields.CharField(max_length=100)
    phone_number = fields.CharField(max_length=15, unique=True, null=True)

    @classmethod
    async def get_user(cls, id):
        return await cls.get(id = id)
    
    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)


class Room(models.Model):
    # weak-entity
    # uses auto-generated id as pk
    room_code = fields.CharField(max_length=8, unique=True, null=False)
    room_name = fields.CharField(max_length=15, unique=False, null=True)
    created_on = fields.DatetimeField(auto_now_add=True)
    host = fields.ForeignKeyField('models.User', related_name=None, on_delete='CASCADE')
    
    @classmethod
    async def generate_room_code(cls):
        code = None
        while(True):
            code = str(uuid.uuid4().hex)
            code = code.upper()
            code = "-".join((code[0:3], code[3:6]))
            room = await cls.filter(room_code = code)
            if len(room) == 0:
                break
        return code
    
    def __str__(self) -> str:
        return f"code = {self.room_code},  host={self.host}"