from datetime import timedelta
from typing import Annotated

from fastapi import (
    APIRouter,
    HTTPException,
    Response,
    status,
    Depends,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from jwt.exceptions import PyJWTError, DecodeError

from app.models.user import User
from app.repositories.authenticate import get_user_by_email_repo
from app.schemas.authenticate_schemas import Login
from app.schemas.user_schemas import UserPublic
from app.security import get_current_user
from app.services.authenticate import (
    authenticate_user_service,
    create_access_token_service,
    create_refresh_token_service,
)
from app.settings import Settings
from infrastructure.db_context import get_session

T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[AsyncSession, Depends(get_session)]
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

    refresh_token = create_refresh_token_service(data={"sub": user.email.root})

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        # O cookie espera o tempo em segundos, mas nossa config está em minutos
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        # O cookie espera o tempo em segundos, mas nossa config está em dias
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )

    return user


@router.post("/refresh")
async def refresh_access_token(session: T_Session, request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        token_type: str = payload.get("type")

        if email is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user = await get_user_by_email_repo(session, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

    except (PyJWTError, DecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Gera novo access token
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    new_access_token = create_access_token_service(
        data={"sub": user.email.root, "id": user.id, "name": user.name},
        expires_delta=access_token_expires,
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_access_token}",
        httponly=True,
        # O cookie espera o tempo em segundos, mas nossa config está em minutos
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )

    return {"message": "Access token refreshed"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
