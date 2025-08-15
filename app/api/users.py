from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.utils.security import get_password_hash

router = APIRouter()


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def created_user(
    user: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Создание пользователя
    """

    # Проверка: email уже существует
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегестрирован"
        )

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
        is_active=True
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.get("/", response_model=List[UserOut])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка пользователей с пагинацией
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalar().all()
    return users


@router.get('/{user_id}', response_model=UserOut)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить пользователя по id
    """

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить профиль пользователя.
    Только владеле или admin может обновить.
    """

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.password is not None:
        user.hased_password = get_password_hash(user_update.password)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить пользователя.
    Только сам пользователь или admin может удалить.
    """
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    await db.delete(user)
    await db.commit
    return


