from datetime import datetime, timedelta, timezone
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import Settings
from app.models.user import User
from app.repositories.authenticate import get_user_by_email_repo

settings = Settings()


def create_access_token_service(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """Gera o token JWT assinado."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def authenticate_user_service(
    session: AsyncSession, email: str, password: str
) -> User | None:
    """
    Orquestra a autenticação: Repo -> Validação de Senha.
    """
    user = await get_user_by_email_repo(session, email)

    if not user:
        return None

    if not user.password.verify_password(password):
        return None

    return user
