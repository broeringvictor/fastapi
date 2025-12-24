from __future__ import annotations

import datetime
from pydantic import EmailStr
from sqlalchemy import DateTime, Integer, String, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column

from app.models import table_registry
from app.value_objects.data_time_sp import tz_sp_now
from app.value_objects.password import Password


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


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[EmailStr] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )

    password: Mapped[Password] = mapped_column(PasswordType(), nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        init=False,
        default_factory=tz_sp_now,
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        init=False,
        default_factory=tz_sp_now,
        nullable=False,
    )

    def validar_senha(self, input_password: str) -> bool:
        return self.password.check_password(input_password)

    def update_email(self, new_email: str) -> None:
        self.email = EmailStr(new_email)
        self.touch()

    def touch(self) -> None:
        """Atualiza o updated_at (útil para outros métodos de update no futuro)."""
        self.updated_at = tz_sp_now()

    def to_public_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }
