from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from settings import Settings

engine = create_async_engine(
    Settings().DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency Injection Generator.
    Gerencia o ciclo de vida da sessão: abre, entrega e fecha automaticamente.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            # O 'async with' já garante o fechamento (close), mas o bloco finally
            # é útil para logs ou limpezas adicionais se necessário.
            await session.close()
