from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from datetime import datetime
from typing import List

from app.database.database import get_db
from app.models.user import User
from app.models.team import Team
from app.models.meeting import Meeting
from app.models.meeting_participant import MeetingParticipant
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingOut
from app.core.security import get_current_user, manager_required

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("/", response_model=MeetingOut, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_data: MeetingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(manager_required)    
):
    """
    Создание встречи с проверкой пересечения времени для всех участников.
    Только manager может создать. 
    """
    # Проверка: пользователь в команде
    if not current_user.team_id:
        raise HTTPException(status_code=400, detail="Вы не состоите в команде")
    
    # Проверка: все участники - из одной команды
    participants = await db.execute(
        select(User).where(User.id.in_(meeting_data.participant_ids))
    )
    participants = participants.scalars().all()
    
    if len(participants) != len(meeting_data.participant_ids):
        raise HTTPException(status_code=400, detail="Один или несколько учатников не найдены")
    
    for p in participants:
        if p.team_id != current_user.team_id:
            raise HTTPException(status_code=400, detail="Все участники должны быть в одной команде")
    
    
    # Проверка пересечения времени
    for participant in participants:
        # Ищем все встречи участника в тот же день
        result = await db.execute(
            select(Meeting).join(Meeting.participants)
            .where(
                MeetingParticipant.user_id == participant.id,
                Meeting.id != None, # Все встречи
                or_(
                    and_(
                        Meeting.start_time < meeting_data.end_time,
                        Meeting.end_time > meeting_data.start_time
                    ),
                )
            )
        )
        overlapping = result.scalars().all()
        
        if overlapping:
            raise HTTPException(
                status_code=400,
                detail=f"У участника {participant.email} есть пересекающаяся встреча"
            )

        # Создаем встречу
        meeting = Meeting(
            title=meeting_data.title,
            description=meeting_data.description,
            start_time=meeting_data.start_time,
            end_time=meeting_data.end_time,
            team_id=current_user.team_id
        )
        
        db.add(meeting)
        await db.flush() # Чтобы получить ID
        
        # Добавляем участников
        
        for p in participants:
            participant_link  = MeetingParticipant(meeting_id=meeting.id, user_id=p.id)
            db.add(participant_link)
            
        await db.commit()
        await db.refresh(meeting)
        return meeting
    
    
@router.get("/", response_model=List[MeetingOut])
async def get_meetings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить все встречи, в которых учавствует пользователь.
    """
    result = await db.execute(
        select(Meeting).join(Meeting.participants)
        .where(MeetingParticipant.user_id == current_user.id)
    )
    meetings = result.scalars().all()
    return meetings


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meting(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить встречу. Только создатель или admin может удалить.
    """
    
    result = await db.execute(
        select(Meeting)
        .where(Meeting.id == meeting_id)
    )
    
    meeting = result.scalars().first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Встреча не найдена")
    
    # Проверка прав
    if meeting.team.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Нет парв на удаление")
    
    await db.delete(meeting)
    await db.commit()
    return 

