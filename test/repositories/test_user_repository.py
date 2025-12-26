import pytest
from pydantic import ValidationError
from sqlalchemy import select
from app.repositories.user import create_user_repo
from app.models.user import User
from app.schemas.user_schemas import UserCreate
from test.factories.models import UserFactory


@pytest.mark.asyncio
async def test_get_user_by_email(session, user_on_db):

    result = await session.scalar(
        select(User).where(User.email == "teste_broering@gmail.com")
    )

    assert result is not None
    assert result.email.root == "teste_broering@gmail.com"


@pytest.mark.asyncio
async def test_create_user_with_invalid_password(session):
    _user = UserFactory.build()

    async def assert_validation_error(password_input, expected_msg):
        user_input = UserCreate(
            name=_user.name,
            email=_user.email,
            password=password_input,
        )

        with pytest.raises(ValidationError) as excinfo:
            await create_user_repo(user_input, session)

        # Verifica se a mensagem esperada está contida na lista de erros
        errors = excinfo.value.errors()
        assert any(expected_msg in err["msg"] for err in errors)

    await assert_validation_error(
        "Short1!", "A senha deve ter entre 8 e 16 caracteres."
    )


@pytest.mark.asyncio
async def test_create_user_repo(session):
    _user = UserFactory.build()
    user_input = UserCreate(
        name=_user.name,
        email=_user.email,
        password=_user.password,
    )

    user_created = await create_user_repo(user_input, session)
    assert user_created.id is not None
    assert user_created.name == _user.name
    assert str(user_created.email) == str(_user.email)
