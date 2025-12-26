from __future__ import annotations

import datetime
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models import table_registry
from app.value_objects.data_time_sp import tz_sp_now
# Importa do novo arquivo (email_vo), mas a classe geralmente se mantém como Email
from app.value_objects.email_vo import Email, EmailType
from app.value_objects.password import Password, PasswordType


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Uso do TypeDecorator e do VO Email
    email: Mapped[Email] = mapped_column(
        EmailType(), nullable=False, unique=True, index=True
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

    @classmethod
    def create(
            cls,
            name: str,
            email: str,
            password: str,
    ) -> User:
        return cls(
            name=name,
            email=Email(email),
            password=Password(password),
        )

    def validar_senha(self, input_password: str) -> bool:
        # Atualizado para usar o método verify_password do pwdlib
        return self.password.verify_password(input_password)

    def patch_user(
            self,
            name: str | None = None,
            new_email: str | None = None,
            password: str | None = None,
    ) -> None:
        """Atualiza os atributos da instância se os valores forem fornecidos."""
        if name is not None:
            self.name = name

        if new_email is not None:
            self.update_email(new_email)

        if password is not None:
            self.password = Password(password)

        self.touch()

    def update_email(self, email: str) -> None:
        self.email = Email(email)
        self.touch()

    def touch(self) -> None:
        self.updated_at = tz_sp_now()

    def to_public_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email.root,
            "created_at": self.created_at.isoformat(),
        }