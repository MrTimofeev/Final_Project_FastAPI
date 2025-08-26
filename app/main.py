from app.admin import setup_admin
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from decouple import config

from app.database.database import engine
from app.api import (
    auth,
    frontend_routes,
    users,
    teams,
    tasks,
    meetings,
    evaluations,
    calendar,
)

SECRET = config("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
DEBUG = config("DEBUG")


# Жизненный цикл приложения
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        pass
    yield
    await engine.dispose()


app = FastAPI(
    title="Итоговый проект, система управление командами",
    description="Упрощенная система упаравления командами, задачами, оценками и встречами",
    version="0.0.1",
    lifespan=lifespan,
    debug=DEBUG,
)

# Разрешаем CORS (на всякий случай, если будет фронтенд)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажи конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET,
    max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
)


# Подключааем статически шаблоны
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# # Роут для проверки@
# @app.get("/")
# def read_root():
#     return {
#         "message": "Добро пожаловать в систему",
#         "docs": "/docs",
#         "admin": "/admin",
#         "login": "/auth/jwt/login"
#     }


# Подключаем роуты (авторизация, пользователи и т.д.)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(tasks.router)
app.include_router(meetings.router)
app.include_router(evaluations.router)
app.include_router(calendar.router)
app.include_router(frontend_routes.router)


setup_admin(app)
