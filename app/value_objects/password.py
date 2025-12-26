import re
import string
from pydantic import RootModel, SecretStr, field_validator, ConfigDict
from sqlalchemy import TypeDecorator, String
from pwdlib import PasswordHash

# Configuração do algoritmo de hash (Argon2 é o padrão recomendado do pwdlib)
pwd_context = PasswordHash.recommended()

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

        # Verifica se é um hash (Argon2 geralmente começa com $argon2)
        # Se for hash, pulamos a validação de complexidade, pois é leitura do banco
        if senha.startswith("$argon2"):
            return value

        # Validação da senha em texto plano (User Input)
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

    def verify_password(self, plain_password: str) -> bool:
        """Verifica se a senha em texto bate com o hash armazenado."""
        return pwd_context.verify(plain_password, self.root.get_secret_value())

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Gera o hash da senha."""
        return pwd_context.hash(plain_password)


class PasswordType(TypeDecorator):
    """Persiste o Value Object `Password` como string no banco (VARCHAR)."""

    impl = String(255)
    cache_ok = True

    def process_bind_param(self, value: Password | str | None, dialect):  # type: ignore[override]
        if value is None:
            return None

        # Lógica de Hash ao salvar:
        # Se recebemos um Password VO, extraímos o valor.
        # Se esse valor ainda não for um hash (não começa com $argon2), hasheamos agora.
        secret_val = ""
        if isinstance(value, Password):
            secret_val = value.root.get_secret_value()
        elif isinstance(value, str):
            secret_val = value
        else:
            raise TypeError(f"Invalid type for password: {type(value)!r}")

        # Se já estiver hasheado (leitura/update sem troca de senha), mantém.
        if secret_val.startswith("$argon2"):
            return secret_val

        # Se for texto plano, hasheia antes de salvar no banco
        return pwd_context.hash(secret_val)

    def process_result_value(self, value: str | None, dialect):  # type: ignore[override]
        if value is None:
            return None
        # Ao ler do banco, instanciamos o Password com o hash
        return Password(value)
