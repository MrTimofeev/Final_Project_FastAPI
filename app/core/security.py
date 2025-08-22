from fastapi import Depends, HTTPException, status
from typing import Callable

from app.core.auth import current_active_user
from app.models.user import User, RoleEnum
from app.database.database import AsyncSession


# Базовая зависимость - авторизованный пользователь
async def get_current_user(user: User = Depends(current_active_user)):
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Пользователь не активен")
    return user


# Проверка роли
def role_required(required_role: RoleEnum) -> Callable:
    def check_role(user: User = Depends(get_current_user)):
        if user.role != required_role and not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется роль {required_role.value}",
            )
        return user

    return check_role


# Проверка: admin или superuser
def admin_required(user: User = Depends(get_current_user)):
    if user.role != RoleEnum.admin and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен: терубется роль manager или admin",
        )
    return user


# Проверка: manager или выше
def manager_required(user: User = Depends(get_current_user)):
    if user.role not in [RoleEnum.manager, RoleEnum.admin] and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен, требуется роль manager или admin",
        )
    return user


# Проверка: пользователь в той же команде
async def user_in_same_team(user: User, obj_team_id: int, db: AsyncSession):
    if user.team_id != obj_team_id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к объекту из другой команды",
        )


# Проверка: только автор или manager команды может редактировать/удалять
async def is_object_owner_or_manager(
    user: User, obj_user_id: int, team_id: int, db: AsyncSession
):
    # Владелец объекта
    if user.id == obj_user_id:
        return True

    # Менеджер команды
    if user.role == RoleEnum.manager and user.team_id == team_id:
        return True

    # Админ
    if user.role == RoleEnum.admin:
        return True
    if user.is_superuser:
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав для выполнения действия",
    )
