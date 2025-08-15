from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import get_db
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.core.security import manager_required, get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def created_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(manager_required)
):
    """
    Толкько manager может создавать задачи в своей команде.
    Можно назначить испольнителя.
    """
    # Проверка: команда сущуствует и пользователь в ней
    if not current_user.team_id:
        raise HTTPException(
            status_code=400,
            detail="Вы не состоите в команде"
        )
        
    # Если назначаем - проверяем, что исполнитель в той же команде
    if task_data.assignee_id:
        result = await db.execute(
            select(User)
            .where(User.id == task_data.assignee_id, User.team_id == current_user.team_id)
        )
        assignee =  result.scalars().first()
        if not assignee:
            raise HTTPException(
                status_code=400,
                detail="Исполнитель не найден или не в вашей команде"
            )
        
        task = Task(
            **task_data.dict(exclude_unset=True),
            creator_id=current_user.id,
            team_id=current_user.team_id,
            status=TaskStatus.open
        )
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
@router.get('/', response_model=list[TaskOut])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить задачи своей команды.
    """
    result = await db.execute(
        select(Task)
        .where(Task.team_id == current_user.team_id)
        .offset(skip)
        .limit(limit)
    )
    tasks = result.scalars().all()
    return tasks

@router.get("/{task_id}", response_model=TaskOut)
async def get_tasks(
    task_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id, Task.team_id == current_user.team_id)
    )
    
    task = result.scalars().first()
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )
    return task

@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int, 
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id, Task.team_id == current_user.team_id)
    )
    task = result.scalars().first()
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )
        
    # Проверка: автор или менеджер
    if current_user.id != task.creator_id and not current_user.role in ["manager", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Нет прав на редактивроение"
        )
        
    for key, value in task_data.dict(exclude_unset=True).items():
        setattr(task, key, value)
        
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id, Task.team_id == current_user.team_id)
    )
    task = result.scalars().first()
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )
        
    if current_user.id != task.creator_id and current_user.role != "manager":
        raise HTTPException(
            status_code=403,
            detail="Нет прав на удаление"
        )
        
    await db.delete(task)
    await db.commit()
    return


    