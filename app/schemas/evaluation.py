from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class EvaluationCreate(BaseModel):
    task_id: int
    score: int = Field(ge=1, le=5)


class EvaluationOut(BaseModel):
    id: int
    task_id: int
    user_id: int  # Кто оценил (менеджер)
    score: int
    evaluated_at: datetime

    model_config = ConfigDict(from_attributes=True)
