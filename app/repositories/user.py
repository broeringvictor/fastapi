from http import HTTPStatus
from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user_schemas import UserCreate, UserPublic, UserPatch


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
        await session.flush()
        await session.refresh(new_user)

        return new_user


async def get_user_by_email_repo(
    GetByEmail, session: AsyncSession
) -> UserPublic:
    """Recupera um usuário pelo email."""
    try:
        result = await session.scalar(
            select(User).where(User.email == GetByEmail.email)
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
        user_input: UserPatch, session: AsyncSession
) -> User:
    """Edita um usuário existente."""

    async with session.begin():
        # 1. Recupera o usuário atual (Await é obrigatório aqui)
        # Assume-se que user_input.email contém o e-mail atual do usuário (identificador)
        user = await get_user_by_email_repo(user_input.email, session)

        # 2. Se houver troca de e-mail, verifica se o novo e-mail já existe
        if user_input.new_email and user_input.new_email != user_input.email:
            email_exists = await session.scalar(
                select(User).where(User.email == user_input.new_email)
            )
            if email_exists:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="New email is already in use.",
                )

        # 3. Aplica as alterações na instância carregada
        user.patch_user(
            name=user_input.name,
            new_email=user_input.new_email,
            password=user_input.password,
        )

        # 4. Adiciona à sessão (O SQLAlchemy detecta mudanças automaticamente, mas add garante)
        session.add(user)

    # 5. Refresh para atualizar updated_at e retornar o estado final
    await session.refresh(user)
    return user