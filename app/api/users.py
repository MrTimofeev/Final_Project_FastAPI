# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserRead
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserRead])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список пользователей своей команды.
    Пагинация: skip, limit
    """
    if not current_user.team_id:
        raise HTTPException(status_code=400, detail="Вы не состоите в команде")

    result = await db.execute(
        select(User).where(User.team_id == current_user.team_id)
        .offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Просмотр профиля другого пользователя.
    Только если он в той же команде.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.team_id != current_user.team_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Нет доступа к профилю")

    return user