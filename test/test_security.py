import pytest
from unittest.mock import MagicMock
from fastapi import Request, HTTPException, status

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
