from http import HTTPStatus
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user_schemas import (
    UserCreate,
    GetByEmail,
    UserPatch,
    UserPublic,
    DeleteUser,
)
from app.repositories.user import (
    create_user_repo,
    get_user_by_email_repo,
    patch_user_repo,
)
from fastapi import Depends, status, Response, APIRouter

from app.security import get_current_user
from app.settings import Settings

from infrastructure.db_context import get_session

T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[AsyncSession, Depends(get_session)]
router = APIRouter(
    prefix="/users",
    tags=["users"],
)
settings = Settings()


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserCreate, session: T_Session):
    return await create_user_repo(user, session)


@router.get("/", status_code=HTTPStatus.OK, response_model=UserPublic)
async def get_user_by_email(session: T_Session, user: GetByEmail = Depends()):
    return await get_user_by_email_repo(user, session)


@router.patch("/", status_code=HTTPStatus.OK, response_model=UserPublic)
async def patch_user(
    session: T_Session,
    patch: UserPatch,
    current_user: T_CurrentUser,
):
    return await patch_user_repo(
        session=session,
        user_input=patch,
        current_user=current_user,
    )


@router.get("/me", response_model=UserPublic)
async def read_me(current_user: T_CurrentUser):
    return current_user


@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_user(
    session: T_Session,
    delete_confirmation: DeleteUser,
    response: Response,
    current_user: T_CurrentUser,
):
    if delete_confirmation.confirmation:
        await session.delete(current_user)
        await session.commit()
        response.delete_cookie(
            key="access_token",
            httponly=True,
            samesite=settings.AUTH_COOKIE_SAMESITE,
            secure=settings.AUTH_COOKIE_SECURE,
        )
        return {"message": "User deleted successfully"}

    return {"message": "Deletion cancelled"}
