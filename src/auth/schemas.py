from pydantic import BaseModel, Field


class AuthUser(BaseModel):
    username: str
    password: str = Field(min_length=6, max_length=128)


class RegisterUser(AuthUser):
    email: str
    first_name: str
    last_name: str


class UserResponse(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str


class AccessTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
