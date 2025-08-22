from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import uuid4

from app.database.database import get_db
from app.models.team import Team
from app.models.user import User
from app.schemas.team import TeamCreate, TeamOut
from app.core.security import admin_required, get_current_user

router = APIRouter(prefix="/team", tags=["teams"])


@router.post("/", response_model=TeamOut, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(admin_required),
):
    """
    Только admin может создать конмаду.
    Генерируется уникальный team_code.
    """

    # Поверка: имя команды уникально
    result = await db.execute(select(Team).where(Team.name == team_data.name))
    if result.scalars().first():
        raise HTTPException(
            status_code=400, detail="Команда с таким имененм уже существует"
        )

    team_code = str(uuid4()).split("-")[0]  # уникальный код
    team = Team(name=team_data.name, team_code=team_code, creator_id=user.id)
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team


@router.post("/join", response_model=TeamOut)
async def join_team_by_code(
    team_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Присоединение пользователя к команде по коду.
    Нельзя менять команду, если уже в составе.
    """

    if current_user.team_id is not None:
        raise HTTPException(status_code=400, detail="Вы уже состоите в команде")

    result = await db.execute(select(Team).where(Team.team_code == team_code))
    team = result.scalars().first()

    if not team:
        raise HTTPException(status_code=404, detail="Команда с таким кодом не найдена")
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one()

    user.team_id = team.id
    db.add(user)

    await db.commit()
    await db.refresh(user)

    return team
