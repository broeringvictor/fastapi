from pydantic import BaseModel, ConfigDict
from app.value_objects.email_vo import Email


class Token(BaseModel):
    access_token: str
    token_type: str
    model_config = ConfigDict(from_attributes=True)


class Login(BaseModel):
    email: Email
    password: str
    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    username: str | None = None
    model_config = ConfigDict(from_attributes=True)
