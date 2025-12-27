import factory
from pydantic import SecretStr
from app.models.user import User
from app.value_objects.password import Password
from app.value_objects.email_vo import Email


class UserFactory(factory.Factory):
    class Meta:
        model = User

    name = factory.Sequence(lambda n: f"User{n}")
    email = factory.LazyAttribute(
        lambda obj: Email(root=f"{obj.name}@example.com")
    )
    password = factory.LazyAttribute(
        lambda o: Password(root=SecretStr("DefaultP@ssw0rd!"))
    )
