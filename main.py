from http import HTTPStatus

from app.schemas.authenticate_schemas import Login

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
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import Settings
from infrastructure.db_context import get_session
from app.models.user import User

# Imports atualizados
from app.security import get_current_user
from app.services.authenticate import (
    authenticate_user_service,
    create_access_token_service,
)

app = FastAPI()
settings = Settings()


@app.post("/users/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(
    user: UserCreate, session: AsyncSession = Depends(get_session)
):
    return await create_user_repo(user, session)


@app.get("/users/", status_code=HTTPStatus.OK, response_model=UserPublic)
async def get_user_by_email(
    user: GetByEmail = Depends(), session: AsyncSession = Depends(get_session)
):
    return await get_user_by_email_repo(user, session)


@app.patch("/users/", status_code=HTTPStatus.OK, response_model=UserPublic)
async def patch_user(
    patch: UserPatch,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await patch_user_repo(
        session=session,
        user_input=patch,
        current_user=current_user,
    )


@app.post("/login", response_model=UserPublic)
async def login_for_access_token(
    user_login: Login,
    response: Response,
    session: AsyncSession = Depends(get_session),
):

    user = await authenticate_user_service(
        session, user_login.email.root, user_login.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Usa o serviço renomeado para criar o token
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token_service(
        data={"sub": user.email.root, "id": user.id, "name": user.name},
        expires_delta=access_token_expires,
    )

    # 3. Define o cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        secure=settings.AUTH_COOKIE_SECURE,
    )

    return user


@app.get("/users/me", response_model=UserPublic)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.delete("/users/", status_code=status.HTTP_200_OK)
async def delete_user(
    delete_confirmation: DeleteUser,
    response: Response,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
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


@app.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    """
    Realiza o logout removendo o cookie de autenticação do navegador.
    """
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        secure=settings.AUTH_COOKIE_SECURE,
    )

    return {"message": "Logout successful"}
