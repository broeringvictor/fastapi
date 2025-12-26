from http import HTTPStatus

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.schemas import Message
from app.schemas.user_schemas import UserPublic, UserCreate, GetByEmail
from app.repositories.user import create_user_repo, get_user_by_email_repo
from infrastructure.db_context import get_session

app = FastAPI()


@app.get("/", status_code=200, response_model=Message)
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/users/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(
    user: UserCreate, session: AsyncSession = Depends(get_session)
):
    return await create_user_repo(user)


@app.get("/users/", status_code=HTTPStatus.FOUND, response_model=UserPublic)
async def get_user_by_email(
    user: GetByEmail, session: AsyncSession = Depends(get_session)
):
    return await get_user_by_email_repo(user)
