# app/core/auth.py (обновлённый)
from fastapi import Depends, Request
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy, BearerTransport, AuthenticationBackend
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.manager import BaseUserManager, UUIDIDMixin
from decouple import config
from typing import AsyncGenerator, Optional

from app.models.user import User
from app.database.database import AsyncSessionLocal
from app.schemas.user import UserOut, UserCreate, UserUpdate

SECRET = config("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# Асинхронная сессия
async def get_async_session() -> AsyncGenerator[AsyncSessionLocal, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Получение пользователя из БД
async def get_user_db(session: AsyncSessionLocal = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

# User Manager
class UserManager(UUIDIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"Пользователь {user.id} зарегистрирован.")

    async def on_after_update(
        self,
        user: User,
        update_dict: dict,
        request: Optional[Request] = None,
    ):
        print(f"Пользователь {user.id} обновлён.")

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[dict] = None,
    ):
        print(f"Пользователь {user.id} вошёл в систему.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Пользователь {user.id} забыл пароль. Токен: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# Стратегия аутентификации — JWT
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

# Аутентификационный бэкенд
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,  # Теперь не None!
    get_strategy=get_jwt_strategy,
)

# Основной экземпляр fastapi-users
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Зависимости для получения текущего пользователя
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)