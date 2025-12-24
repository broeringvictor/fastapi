from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schemas import UserCreate
from settings import Settings


def create_user(user: UserCreate)
    """Cria um novo usuário."""

    engine = create_engine(Settings().DATABASE_URL)

    with Session(engine) as session:
        verify_user = session.scalar(
            select(User).where(
                User.email == user.email
            )

        )
        if verify_user:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST
                detail='Email already registered.'
            )



        session.add(new_user)
        session.commit()
        session.refresh(new_user)