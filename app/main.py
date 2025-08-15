from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.database.database import Base, engine
from app.api import auth, users, teams, tasks, meetings, evaluations
from app.models.user import User


# Жизненный цикл приложения
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # при старте создаем таблицы (если их нет)
    async with engine.begin() as conn:
        pass
    yield
    await engine.dispose()


app = FastAPI(
    title="Итоговый проект, система управление командами",
    description="Упрощенная система упаравления командами, задачами, оценками и встречами",
    version="0.0.1",
    lifespan=lifespan
)

# Разрешаем CORS (на всякий случай, если будет фронтенд)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажи конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключааем статически шаблоны
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# Роут для проверки@
@app.get("/")
def read_root():
    return {
        "message": "Добро пожаловать в систему",
        "docs": "/docs",
        "admin": "/admin",
        "login": "/login"
    }

# Подключаем роуты (авторизация, пользователи и т.д.)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(teams.router, prefix="/teams", tags=["teams"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
app.include_router(evaluations.router, prefix="/evaluations", tags=["evaluations"])
