from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models.user import User, table_registry
from test.factories.models import UserFactory



engine = create_engine("sqlite:///:memory:")
table_registry.metadata.create_all(engine)
user_data = UserFactory.build()

user = User(
    name=user_data.name,
    email=user_data.email,
    password=user_data.password,
)

def test_user_model_creation():

    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)

    assert user.id is not None
    assert user.name == user_data.name

    assert str(user.email) == str(user_data.email)

    # O TypeDecorator converte string -> Password, então deve virar VO
    assert user.password is not user_data.password

def test_user_model_email():

    with Session(engine) as session:
        session.scalar(
            select(User).where(User.email == user_data.email)
        )

    assert str(user.email) == str(user_data.email)
