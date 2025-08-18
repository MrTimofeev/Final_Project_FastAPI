from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.database.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.evaluation import Evaluation
from app.schemas.evaluation import EvalustionCreate, EvaluationOut
from app.core.security import manager_required, get_current_user

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("/", response_model=EvaluationOut, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    evaluation_data: EvalustionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(manager_required)
):
    """
    Только manager можеь оценить задачу.
    Задача должна быть в статусе 'done'.
    Оценка от 1 до 5.
    """
    # Провека: оценка 1 до 5
    if not (1 <= evaluation_data.score <= 5):
        raise HTTPException(
            status_code=400, detail="Оценка должны быть от 1 до 5")

    # Проверка: задача существует и в команде пользователя
    result = await db.execute(
        select(Task).where(
            Task.id == evaluation_data.task_id,
            Task.team_id == current_user.team_id
        )
    )
    task = result.scalar().first()
    if not task:
        raise HTTPException(
            status_code=404, detail="Задача не найдена или вы не в команде")

    if task.status != "done":
        raise HTTPException(
            status_code=400, detail="Оценивать можно только выполненые задачи")

    # Проверка: уже оценена?
    result = await db.execute(
        select(Evaluation).where(Evaluation.task_id == evaluation_data.task_id)
    )

    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Задача уже оценена")

    evaluation = Evaluation(
        task_id=evaluation_data.task_id,
        user_id=current_user.id,
        score=evaluation_data.score
    )

    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)
    return evaluation


@router.get("/my", response_model=list[EvaluationOut])
async def get_my_evaluations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Пользователь видит все свои оцененные задачи.
    """

    result = await db.execute(
        select(Evaluation)
        .join(Task)
        .where(Task.assignee_id == current_user.id)
    )
    evaluations = result.scalar().all()
    return evaluations


@router.get("/average")
async def get_average_score(
    period: str = "week", # week, month
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Средняя оценка за период.
    """
    
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:
        raise HTTPException(status_code=400, detail="period должен быть 'week' или 'monrh'")
    
    result = await db.execute(
        select(func.avg(Evaluation.score))
        .join(Task)
        .where(
            Task.assignee_id == current_user.id,
            Evaluation.evaluated_at >= start_date
        )
    )
    avg = result.scalar()
    return {
        "average_score": round(avg, 2) if avg else 0.0
    }
    
    
