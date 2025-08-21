from fastapi import APIRouter

from app.core.auth import fastapi_users, auth_backend
from app.schemas.user import UserUpdate, UserRead, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

# Роутер для JWT: /auth/jwt/login, /auth/jwt/logout
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
    tags=["auth"],
)

# Роутер регистрации: /auth/register
router.include_router(
    fastapi_users.get_register_router(
        user_schema=UserRead,
        user_create_schema=UserCreate,
        ),
    tags=["auth"],
)

# Роутер управления пользователем: /auth/users/me, /auth/users/{id}
router.include_router(
    fastapi_users.get_users_router(
        user_schema=UserRead,
        user_update_schema=UserUpdate
    ),
    prefix="/users",
    tags=["users"],
)
