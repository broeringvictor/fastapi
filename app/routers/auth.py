from datetime import timedelta
from typing import Literal, cast

from fastapi import APIRouter, HTTPException, Response, status

from app.deps import T_Session
from app.schemas.authenticate_schemas import Login
from app.schemas.user_schemas import UserPublic
from app.services.authenticate import (
    authenticate_user_service,
    create_access_token_service,
)
from app.settings import Settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

settings: Settings = Settings()


@router.post("/", response_model=UserPublic)
async def login(session: T_Session, user_login: Login, response: Response):
    user = await authenticate_user_service(
        session, user_login.email.root, user_login.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token_service(
        data={"sub": user.email.root, "id": user.id, "name": user.name},
        expires_delta=access_token_expires,
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        samesite=cast(
            Literal["lax", "strict", "none"], settings.AUTH_COOKIE_SAMESITE
        ),
        secure=settings.AUTH_COOKIE_SECURE,
    )

    return user


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    """
    Realiza o logout removendo o cookie de autenticação do navegador.
    """
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite=cast(
            Literal["lax", "strict", "none"], settings.AUTH_COOKIE_SAMESITE
        ),
        secure=settings.AUTH_COOKIE_SECURE,
    )

    return {"message": "Logout successful"}
