import pytest
from pydantic import ValidationError

from app.models.user import User
from app.schemas.user_schemas import UserPublic
from app.value_objects.email_vo import Email

from test.factories.models import UserFactory


@pytest.mark.asyncio
async def test_user_model_creation(session):
    user_data = UserFactory.build()

    # Use User.create para garantir que a lógica de VOs (Email/Password) seja exercitada
    user = User.create(
        name=user_data.name,
        email=user_data.email.root,
        password=user_data.password.root.get_secret_value(),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    assert user.id is not None
    assert user.name == user_data.name

    user_schema = UserPublic.model_validate(user)
    assert isinstance(user_schema.email, Email)
    assert user.email.root == user_schema.email.root


def test_user_with_invalid_email_in_model():
    user_data = UserFactory.build()

    invalid_emails = [
        "plainaddress",
        "@missingusername.com",
        "username@.com",
        "username@com",
        "username@domain..com",
    ]

    for invalid_email in invalid_emails:
        with pytest.raises(ValidationError) as excinfo:
            User.create(
                name=user_data.name,
                email=invalid_email,
                password=user_data.password.root.get_secret_value(),
            )

        errors = excinfo.value.errors()

        # CORREÇÃO: Verifica a mensagem definida no seu Value Object Email
        # O Pydantic V2 encapsula o ValueError, então a msg conterá "Email inválido"
        assert any("Email inválido" in err["msg"] for err in errors)


def test_user_with_invalid_password_in_model():
    user_data = UserFactory.build()

    def assert_validation_error(password_input, expected_msg):
        with pytest.raises(ValidationError) as excinfo:
            User.create(
                name=user_data.name,
                email=user_data.email.root,
                password=password_input,
            )

        errors = excinfo.value.errors()
        assert any(expected_msg in err["msg"] for err in errors)

    # Nota: Certifique-se que seu VO Password levanta exatamente estas mensagens

    assert_validation_error(
        "Short1!", "A senha deve ter entre 8 e 16 caracteres."
    )

    assert_validation_error(
        "LongPassword123456789!", "A senha deve ter entre 8 e 16 caracteres."
    )

    assert_validation_error(
        "SenhaSemNumero!", "A senha deve conter letras e números."
    )

    assert_validation_error(
        "12345678!", "A senha deve conter letras e números."
    )

    assert_validation_error(
        "SenhaComNumero1",
        "A senha deve conter pelo menos um caractere especial.",
    )
