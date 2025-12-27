from pydantic import BaseModel, EmailStr, ConfigDict

from app.value_objects.email_vo import Email


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    model_config = ConfigDict(from_attributes=True)


class GetByEmail(BaseModel):
    email: EmailStr


class UserPublic(BaseModel):
    id: int
    name: str
    email: Email
    model_config = ConfigDict(from_attributes=True)


class UserCreateResponse(BaseModel):
    user: UserPublic
    detail: str
    model_config = ConfigDict(from_attributes=True)


class UserPatch(BaseModel):
    name: str | None = None
    new_email: EmailStr | None = None
    password: str | None = None
    model_config = ConfigDict(from_attributes=True)


class DeleteUser(BaseModel):
    confirmation: bool


class UserLogin(BaseModel):
    email: EmailStr
    password: str
