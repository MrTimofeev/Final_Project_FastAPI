from pydantic import BaseModel
from typing import Optional, List
from .user import UserOut

class TeamCreate(BaseModel):
    name: str
    
class TeamOut(BaseModel):
    id: int
    name: str
    team_code: str
    creator_id: int
    members: List[UserOut]
    
    class Config:
        from_attributes = True