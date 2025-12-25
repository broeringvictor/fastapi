from http import HTTPStatus
from fastapi import HTTPException

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schemas import UserCreate
from settings import Settings


def create_user(user_input: UserCreate):
    """Cria um novo usuário."""

    engine = create_engine(Settings().DATABASE_URL)
    try:
        with Session(engine) as session:
            verify_user = session.scalar(
                select(User).where(
                    User.email == user_input.email
                )

            )
            if verify_user:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail='Email already registered.'
                )

            new_user = User.create(
                name=user_input.name,
                email=user_input.email,
                password=user_input.password)

            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            return new_user

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f'Error creating user: {e}'
        )

