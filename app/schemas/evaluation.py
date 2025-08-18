from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EvalustionCreate(BaseModel):
    task_id: int
    score: int # от 1 до 5 
    
class EvaluationOut(BaseModel):
    id: int
    task_id: int
    user_id: int # Кто оценил (менеджер)
    score: int
    evaluated_at: datetime
    
    class Config:
        from_attributes = True
        
        
    