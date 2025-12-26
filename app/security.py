from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import Settings
from app.models.user import User
from infrastructure.db_context import get_session
from app.repositories.authenticate import get_user_by_email_repo  # Importação atualizada

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(
        request: Request,
        session: AsyncSession = Depends(get_session)
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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # Uso da função renomeada do repositório
    user = await get_user_by_email_repo(session, email)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user