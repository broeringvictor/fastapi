import pytest
from unittest.mock import MagicMock
from fastapi import Request, HTTPException, status
from freezegun import freeze_time
from datetime import timedelta

from app.security import get_current_user
from app.services.authenticate import create_access_token_service


@pytest.mark.asyncio
async def test_get_current_user_success_cookie(session, user_on_db):
    token = create_access_token_service({"sub": user_on_db.email.root})

    request = MagicMock(spec=Request)
    request.cookies.get.return_value = token
    request.headers.get.return_value = None

    user = await get_current_user(request, session)
    assert user.id == user_on_db.id
    assert user.email.root == user_on_db.email.root


@pytest.mark.asyncio
async def test_get_current_user_success_header(session, user_on_db):
    token = create_access_token_service({"sub": user_on_db.email.root})

    request = MagicMock(spec=Request)
    request.cookies.get.return_value = None
    request.headers.get.return_value = f"Bearer {token}"

    user = await get_current_user(request, session)
    assert user.id == user_on_db.id


@pytest.mark.asyncio
async def test_get_current_user_no_token(session):
    request = MagicMock(spec=Request)
    request.cookies.get.return_value = None
    request.headers.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(request, session)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Not authenticated"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(session):
    request = MagicMock(spec=Request)
    request.cookies.get.return_value = "invalid_token"
    request.headers.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(request, session)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(session):
    # Token válido, mas email não existe no banco
    token = create_access_token_service({"sub": "nonexistent@example.com"})

    request = MagicMock(spec=Request)
    request.cookies.get.return_value = token
    request.headers.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(request, session)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_missing_sub(session):
    # Token válido, mas sem claim 'sub'
    token = create_access_token_service({"foo": "bar"})

    request = MagicMock(spec=Request)
    request.cookies.get.return_value = token
    request.headers.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(request, session)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_expired_token(session, user_on_db):
    initial_time = "2024-01-01 12:00:00"

    with freeze_time(initial_time):
        # Token expira em 10 minutos (12:10:00)
        expires = timedelta(minutes=10)
        token = create_access_token_service(
            {"sub": user_on_db.email.root},
            expires_delta=expires,
        )

    # Simula tempo avançado para 12:11:00 (token expirado)
    with freeze_time("2024-01-01 12:11:00"):
        request = MagicMock(spec=Request)
        request.cookies.get.return_value = token
        request.headers.get.return_value = None

        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(request, session)

        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_user_invalid_type(session, user_on_db):
    # Token válido, mas com tipo errado (ex: refresh token)
    # Precisamos gerar manualmente para sobrescrever o 'type'
    from datetime import datetime, timezone
    import jwt
    from app.settings import Settings

    settings = Settings()
    now = datetime.now(timezone.utc)
    data = {
        "sub": user_on_db.email.root,
        "exp": now + timedelta(minutes=10),
        "iat": now,
        "type": "refresh",  # Tipo inválido para autenticação
    }
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    request = MagicMock(spec=Request)
    request.cookies.get.return_value = token
    request.headers.get.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(request, session)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
