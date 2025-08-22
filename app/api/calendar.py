from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, date, timedelta


from app.database.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.meeting import Meeting
from app.models.meeting_participant import MeetingParticipant
from app.core.security import get_current_user


router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/day")
async def get_calendar_day(
    target_date: date = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Календарь на день: задачи и встречи.
    """

    if not target_date:
        target_date = date.today()

    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date, datetime.max.time())

    # Задачи (с дедалйном на этот день)
    task_result = await db.execute(
        select(Task).where(
            Task.assignee_id == current_user.id,
            Task.deadline >= start,
            Task.deadline <= end,
        )
    )
    tasks = task_result.scalars().all()

    # Встречи
    meetings_result = await db.execute(
        select(Meeting)
        .join(Meeting.participants)
        .where(
            MeetingParticipant.user_id == current_user.id,
            Meeting.start_time >= start,
            Meeting.end_time <= end,
        )
    )

    meetings = meetings_result.scalars().all()

    return {
        "date": target_date,
        "tasks": [{"id": t.id, "title": t.title, "status": t.status} for t in tasks],
        "meetings": [
            {
                "id": m.id,
                "title": m.title,
                "time": f"{m.start_time.time()} - {m.end_time.time()}",
            }
            for m in meetings
        ],
    }


@router.get("/month")
async def get_calendar_month(
    target_month: int = None,
    target_years: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Календаль на месяц: группировка по дням.
    """

    now = datetime.now()
    month = target_month or now.month
    year = target_years or now.year

    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)

    # Задачи
    tasks_result = await db.execute(
        select(Task).where(
            Task.assignee_id == current_user.id,
            Task.deadline >= start,
            Task.deadline < end,
        )
    )

    tasks = tasks_result.scalars().all()

    # Встречи
    meetings_result = await db.execute(
        select(Meeting)
        .join(Meeting.participants)
        .where(
            MeetingParticipant.user_id == current_user.id,
            Meeting.start_time >= start,
            Meeting.end_time < end,
        )
    )
    meetings = meetings_result.scalars().all()

    calendar = {}
    current = start
    while current < end:
        day = current.date()
        calendar[day] = {"tasks": [], "meetings": []}
        current += timedelta(days=1)

    for t in tasks:
        day = t.deadline.date()
        if day in calendar:
            calendar[day]["tasks"].append({"id": t.id, "title": t.title})

    for m in meetings:
        day = m.start_time.date()
        if day in calendar:
            calendar[day]["meetings"].append({"id": m.id, "title": m.title})

    return {"year": year, "month": month, "calendar": calendar}
