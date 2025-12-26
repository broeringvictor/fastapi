from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

async def get_user_by_email_repo(session: AsyncSession, email: str) -> User | None:
    """
    Busca usuário pelo email retornando None se não existir.
    Utilizado para processos internos como autenticação.
    """
    return await session.scalar(select(User).where(User.email == email))
