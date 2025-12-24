import re
import string

import bcrypt
from pydantic import RootModel, SecretStr, field_validator, ConfigDict

# Compilando regex fora da classe
_REGEX_HAS_LETTER = re.compile(r"[A-Za-z]")
_REGEX_HAS_NUMBER = re.compile(r"\d")

class Password(RootModel):
    """
    Value Object rico.
    Comporta-se como um container transparente para o SecretStr,
    mas permite métodos de domínio.
    """
    root: SecretStr

    # 1. Imutabilidade (Característica essencial de Value Objects)
    model_config = ConfigDict(frozen=True)

    # 2. Validação na construção (Garante integridade)
    @field_validator("root")
    @classmethod
    def _validar_regras(cls, value: SecretStr) -> SecretStr:
        senha = value.get_secret_value()


        if not (8 <= len(senha) <= 16):
            raise ValueError("A senha deve ter entre 8 e 16 caracteres.")

        if not _REGEX_HAS_LETTER.search(senha) or not _REGEX_HAS_NUMBER.search(senha):
            raise ValueError("A senha deve conter letras e números.")

        if not any(char in string.punctuation for char in senha):
            raise ValueError("A senha deve conter pelo menos um caractere especial.")

        return value


    def check_password(self, plain_password: str) -> bool:
        """Verifica se a senha plana corresponde ao hash/valor guardado."""
        return self.root.get_secret_value() == bcrypt.checkpw(plain_password)


