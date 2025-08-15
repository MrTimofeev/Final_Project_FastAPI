from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.task import TaskStatus

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    assignee_id: Optional[int] = None
    
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    deadline: Optional[datetime] = None
    assignee_id: Optional[int] = None
    
class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    deadline: Optional[datetime] = None
    created_at: datetime
    creator_id: int
    assignee_id: Optional[int] = None
    team_id: int
    
    class Config:
        from_attributes = True 