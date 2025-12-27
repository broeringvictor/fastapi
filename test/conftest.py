import os

# Ensure auth cookie works with TestClient (http://testserver)
# Must run before importing the app/settings.
os.environ.setdefault("AUTH_COOKIE_SECURE", "false")

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from typing import AsyncGenerator

from app.models import table_registry
from app.models.user import User
from main import app
from infrastructure.db_context import get_session

# 1. Configuração da Engine
# StaticPool é vital para :memory:
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# 2. Fixture de Ciclo de Vida do Banco (Responsável ÚNICA pelas tabelas)
@pytest_asyncio.fixture(scope="function")
async def setup_db():
    """
    Cria as tabelas antes do teste e as remove depois.
    Scope='function' garante isolamento total entre testes.
    """
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    yield  # O teste roda aqui

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


# 3. Fixture da Sessão (Depende de setup_db)
@pytest_asyncio.fixture(scope="function")
async def session(setup_db) -> AsyncGenerator[AsyncSession, None]:
    """
    Entrega uma sessão pronta para uso nos testes de unidade (modelos/services).
    """
    async with TestingSessionLocal() as session:
        yield session
        # O rollback não é estritamente necessário se dropamos as tabelas,
        # mas é boa prática garantir que a sessão feche limpa.
        await session.rollback()


# 4. Fixture do Client (Depende de setup_db)
@pytest.fixture(scope="function")
def client(setup_db):
    """
    Cliente para testes de integração (rotas).
    Removemos o asyncio.run e a criação de tabelas daqui.
    """

    async def get_session_override():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# 5. Fixture de Usuário para evitar acoplamento de teste
@pytest_asyncio.fixture
async def user_on_db(session):
    user = User(
        name="Test User",
        email="teste_broering@gmail.com",
        password="S@@ecupassword12",
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@pytest_asyncio.fixture
async def token(client, user_on_db):
    response = client.post(
        "/login",
        json={
            "email": user_on_db.email.root,
            "password": "S@@ecupassword12",
        },
    )
    assert response.status_code == 200
    return response.cookies.get("access_token")
