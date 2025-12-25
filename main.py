from http import HTTPStatus

from fastapi import FastAPI

from app.schemas.schemas import Message
from app.schemas.user_schemas import UserPublic, UserCreate
from app.repositories.user import create_user as create_user_repo

app = FastAPI()




@app.get("/", status_code=200, response_model=Message)
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/users/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserCreate):
    return create_user_repo(user)

