import re
import string
from pydantic import RootModel, SecretStr, field_validator, ConfigDict
from sqlalchemy import TypeDecorator, String

# Compilando regex fora da classe
_REGEX_HAS_LETTER = re.compile(r"[A-Za-z]")
_REGEX_HAS_NUMBER = re.compile(r"\d")


class Password(RootModel):
    """
    Value Object rico.
    Comporta-se como um container transparente para o SecretStr.
    Valida regras de negócio (tamanho, complexidade) na instanciação.
    """

    root: SecretStr

    model_config = ConfigDict(frozen=True)

    @field_validator("root")
    @classmethod
    def _validar_regras(cls, value: SecretStr) -> SecretStr:
        senha = value.get_secret_value()

        # AQUI: Use ValueError, não ValidationError
        if not (8 <= len(senha) <= 16):
            raise ValueError("A senha deve ter entre 8 e 16 caracteres.")

        if not _REGEX_HAS_LETTER.search(senha) or not _REGEX_HAS_NUMBER.search(
            senha
        ):
            raise ValueError("A senha deve conter letras e números.")

        if not any(char in string.punctuation for char in senha):
            raise ValueError(
                "A senha deve conter pelo menos um caractere especial."
            )

        return value

    def check_password(self, plain_password: str) -> bool:
        import secrets

        return secrets.compare_digest(
            self.root.get_secret_value(), plain_password
        )


class PasswordType(TypeDecorator):
    """Persiste o Value Object `Password` como string no banco (VARCHAR).

    Isso evita tentar mapear o tipo Password diretamente.

    Nota: por enquanto isso grava a senha em texto (regra do projeto atual).
    Quando você implementar hash, troque para `password_hash`.
    """

    impl = String(255)
    cache_ok = True

    def process_bind_param(self, value: Password | str | None, dialect):  # type: ignore[override]
        if value is None:
            return None
        if isinstance(value, Password):
            return value.root.get_secret_value()
        if isinstance(value, str):
            return Password.model_validate(value).root.get_secret_value()
        raise TypeError(f"Invalid type for password: {type(value)!r}")

    def process_result_value(self, value: str | None, dialect):  # type: ignore[override]
        if value is None:
            return None
        return Password.model_validate(value)
