from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):

    full_name: str = Field(min_length=2, max_length=100)

    email: EmailStr

    password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Full name cannot be empty")

        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return str(value).lower()


class UserResponse(BaseModel):

    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)