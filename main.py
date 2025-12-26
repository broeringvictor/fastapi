from http import HTTPStatus

from app.schemas.authenticate_schemas import Login
from app.schemas.schemas import Message
from app.schemas.user_schemas import (
    UserCreate,
    GetByEmail,
    UserPatch,
    UserPublic,
)
from app.repositories.user import (
    create_user_repo,
    get_user_by_email_repo,
    patch_user_repo,
)
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import Settings
from infrastructure.db_context import get_session
from app.models.user import User

# Imports atualizados
from app.security import get_current_user
from app.services.authenticate import authenticate_user_service, create_access_token_service

app = FastAPI()
settings = Settings()


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
    return await create_user_repo(user, session)


@app.get("/users/", status_code=HTTPStatus.OK, response_model=UserPublic)
async def get_user_by_email(
    user: GetByEmail = Depends(), session: AsyncSession = Depends(get_session)
):
    return await get_user_by_email_repo(user, session)


@app.patch("/users/", status_code=HTTPStatus.OK, response_model=UserPublic)
async def patch_user(
    user: UserPatch, session: AsyncSession = Depends(get_session)
):
    return await patch_user_repo(user, session)

@app.post("/login", response_model=UserPublic)
async def login_for_access_token(
        user_login: Login,
        response: Response,
        session: AsyncSession = Depends(get_session)
):

    user = await authenticate_user_service(
        session,
        user_login.email,
        user_login.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Usa o serviço renomeado para criar o token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token_service(
        data={"sub": user.email.root},
        expires_delta=access_token_expires
    )

    # 3. Define o cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=True,
    )

    return user

@app.get("/users/me", response_model=UserPublic)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    """
    Realiza o logout removendo o cookie de autenticação do navegador.
    """
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=True
    )

    return {"message": "Logout successful"}

