from __future__ import annotations

import re

from pydantic import RootModel, ConfigDict, field_validator

# Regex básica e pragmática para e-mail.
# (Você pode substituir por uma validação mais completa depois.)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Email(RootModel[str]):
    """Value Object de Email.

    Motivo:
    - Deixa a validação no domínio (camada baixa), sem depender de DTO.
    - Evita colocar `EmailStr` (Pydantic) diretamente como tipo do atributo do ORM.

    Nota: Aqui usamos `RootModel[str]` para o VO se comportar como string.
    """

    root: str
    model_config = ConfigDict(frozen=True)

    @field_validator("root")
    @classmethod
    def _validate(cls, v: str) -> str:
        value = v.strip()
        if not value:
            raise ValueError("Email não pode ser vazio.")
        if not _EMAIL_RE.match(value):
            raise ValueError("Email inválido.")
        # normalização simples
        return value.lower()

    def __str__(self) -> str:
        return self.root

