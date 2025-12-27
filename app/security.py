from typing import Annotated

import jwt
from fastapi import HTTPException, Request, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError, DecodeError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.authenticate import get_user_by_email_repo
from app.settings import Settings
from infrastructure.db_context import get_session

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


async def get_current_user(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    token = request.cookies.get("access_token")

    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        token_type: str = payload.get("type")

        if email is None or token_type != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = await get_user_by_email_repo(session, email)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user
