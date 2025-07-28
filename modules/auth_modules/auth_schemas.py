from typing import Optional

from pydantic import Field , BaseModel, EmailStr


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: str
    last_name: str
    password: str = Field(..., min_length=8)
    role: str
    phone_number: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_role: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    phone_number: str | None = None

    class Config:
        from_attributes = True


class UserUpdateAdminRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None # Admin có thể thay đổi vai trò
    is_active: Optional[bool] = None
    phone_number: Optional[str] = None

