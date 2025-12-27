import pytest
import jwt
from datetime import timedelta
from app.services.authenticate import (
    create_access_token_service,
    authenticate_user_service,
)
from app.settings import Settings

settings = Settings()


@pytest.mark.asyncio
async def test_create_access_token_service():
    data = {"sub": "test@example.com"}
    token = create_access_token_service(data)

    assert isinstance(token, str)

    # Decode token to verify contents
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert payload["sub"] == "test@example.com"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_create_access_token_service_with_expiry():
    data = {"sub": "test@example.com"}
    expires = timedelta(minutes=10)
    token = create_access_token_service(data, expires_delta=expires)

    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert payload["sub"] == "test@example.com"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_authenticate_user_service_success(session, user_on_db):
    # user_on_db has password "S@@ecupassword12" defined in conftest.py
    user = await authenticate_user_service(
        session, user_on_db.email.root, "S@@ecupassword12"
    )
    assert user is not None
    assert user.id == user_on_db.id


@pytest.mark.asyncio
async def test_authenticate_user_service_user_not_found(session):
    user = await authenticate_user_service(
        session, "nonexistent@example.com", "password"
    )
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_service_wrong_password(session, user_on_db):
    user = await authenticate_user_service(
        session, user_on_db.email.root, "WrongPassword123!"
    )
    assert user is None
