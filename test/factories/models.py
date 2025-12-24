from polyfactory import Use
from polyfactory.factories.dataclass_factory import DataclassFactory

from app.models.user import User


class UserFactory(DataclassFactory[User]):
    __model__ = User

    # O model User tem o campo `password` (não `plain_password`).
    # Como o mapeamento aceita string e converte para Password, geramos uma string válida.
    password: str = Use(lambda: "Teste@123@")

    @classmethod
    def name(cls) -> str:
        return cls.__faker__.name()

    @classmethod
    def email(cls) -> str:
        return cls.__faker__.email()