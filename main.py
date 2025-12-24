from fastapi import FastAPI, HTTPException
from http import HTTPStatus

from app.models.user import User
from app.schemas.schemas import Message
from app.schemas.user_schemas import UserCreate, UserCreateResponse, UserPublic
from app.value_objects.password import Password


app = FastAPI()




@app.get("/", status_code=200, response_model=Message)
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

