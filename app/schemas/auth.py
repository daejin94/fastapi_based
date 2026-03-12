from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.common import APIResponse


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_in: int
    refresh_token_expires_in: int

    model_config = ConfigDict(from_attributes=True)


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    access_token_expires_in: int


class CurrentUserResponse(BaseModel):
    id: int
    email: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TokenPairAPIResponse(APIResponse[TokenPairResponse]):
    pass


class AccessTokenAPIResponse(APIResponse[AccessTokenResponse]):
    pass


class CurrentUserAPIResponse(APIResponse[CurrentUserResponse]):
    pass
