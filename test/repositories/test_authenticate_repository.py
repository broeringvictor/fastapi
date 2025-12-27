import pytest
from app.repositories.authenticate import get_user_by_email_repo


@pytest.mark.asyncio
async def test_get_user_by_email_repo_found(session, user_on_db):
    user = await get_user_by_email_repo(session, user_on_db.email.root)
    assert user is not None
    assert user.id == user_on_db.id
    assert user.email.root == user_on_db.email.root


@pytest.mark.asyncio
async def test_get_user_by_email_repo_not_found(session):
    user = await get_user_by_email_repo(session, "nonexistent@example.com")
    assert user is None
