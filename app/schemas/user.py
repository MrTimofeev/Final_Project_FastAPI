# app/schemas/user.py
from pydantic import EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from fastapi_users import schemas
from enum import Enum


class RoleEnum(str, Enum):
    user = "user"
    manager = "manager"
    admin = "admin"


class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: RoleEnum = RoleEnum.user
    is_active: bool = True
    is_superuser: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    
    model_config = ConfigDict(
        from_attributes=True, 
        json_schema_extra= {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "password123",
                    "full_name": "John Doe"
                }
            ]
        }
    )


class UserUpdate(schemas.BaseUserUpdate):
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None
