from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from routers import rooms, users


'''
TODO:
    1) Test using postman, swagger UI doesn't take in acces_token in header. For now, use Mod-Headers
    2) Modify RoomPydantic to include some data about host
    3) Place constants in a .env file, currently in dependencies
'''

app = FastAPI()
app.include_router(users.router)
app.include_router(rooms.router)

register_tortoise(
    app,
    db_url="sqlite://store.db",
    modules={
        'models': ['models'],
    },
    generate_schemas=True,
    add_exception_handlers=True,
)