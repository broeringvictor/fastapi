import pytest
from pydantic import ValidationError, SecretStr
from app.value_objects.password import Password


def test_password_valid_creation():
    raw_password = "S@@ecupassword12"
    pwd = Password(raw_password)

    assert isinstance(pwd.root, SecretStr)
    assert pwd.root.get_secret_value() == raw_password


def test_password_validation_rules():
    # Helper para verificar mensagem de erro
    def assert_error(password_input, expected_msg_part):
        with pytest.raises(ValidationError) as excinfo:
            Password(password_input)
        errors = excinfo.value.errors()
        assert any(expected_msg_part in err["msg"] for err in errors)

    # Tamanho
    assert_error("Short1!", "entre 8 e 16 caracteres")
    assert_error("LongPassword123456789!", "entre 8 e 16 caracteres")

    # Complexidade
    assert_error("NoNumber!", "letras e números")
    assert_error("12345678!", "letras e números")
    assert_error("NoSpecialChar1", "caractere especial")


def test_password_verify_and_hash():
    raw_password = "S@@ecupassword12"

    # Para testar verify_password, precisamos de uma instância que contenha o hash,
    # pois verify_password usa pwd_context.verify(plain, hash).
    hashed = Password.hash_password(raw_password)
    pwd = Password(hashed)

    # Verifica método de instância verify_password
    assert pwd.verify_password(raw_password) is True
    assert pwd.verify_password("WrongPass1!") is False

    # Verifica método estático hash_password
    assert hashed.startswith("$argon2")
    assert hashed != raw_password


def test_password_skip_validation_for_hash():
    # Se passar um hash existente, deve pular validação de regras
    existing_hash = "$argon2id$v=19$m=65536,t=3,p=4$..."
    pwd = Password(existing_hash)
    assert pwd.root.get_secret_value() == existing_hash
