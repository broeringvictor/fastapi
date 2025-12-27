from http import HTTPStatus
from fastapi import HTTPException
from pydantic import ValidationError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user_schemas import (
    UserCreate,
    UserPublic,
    UserPatch,
    GetByEmail,
)


async def create_user_repo(
    user_input: UserCreate, session: AsyncSession
) -> UserPublic:
    """Cria um novo usuário."""

    async with session.begin():
        verify_existence = await session.scalar(
            select(User).where(User.email == user_input.email)
        )
        if verify_existence:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Email already registered.",
            )

        new_user = User.create(
            name=user_input.name,
            email=user_input.email,
            password=user_input.password,
        )

        session.add(new_user)

    await session.refresh(new_user)

    return new_user


async def get_user_by_email_repo(
    user_input: GetByEmail, session: AsyncSession
) -> UserPublic:
    """Recupera um usuário pelo email."""
    try:
        result = await session.scalar(
            select(User).where(User.email == user_input.email)
        )

        if not result:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="User not found."
            )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {e}",
        )


async def patch_user_repo(
    user_input: UserPatch,
    current_user: User,
    session: AsyncSession,
) -> User:
    """Edita um usuário existente."""

    # 1. Verifica duplicidade de e-mail se houve alteração
    if (
        user_input.new_email
        and user_input.new_email != current_user.email.root
    ):
        email_exists = await session.scalar(
            select(User).where(User.email == user_input.new_email)
        )
        if email_exists:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="New email is already in use.",
            )

    try:
        # 2. Aplica as alterações (Isso dispara a validação do Password/Email)
        current_user.patch_user(
            name=user_input.name,
            new_email=user_input.new_email,
            password=user_input.password,
        )

        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

        return current_user

    except ValidationError as e:
        error_details = e.errors(include_url=False, include_context=False)

        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=error_details
        )
