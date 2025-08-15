from pydantic import BaseModel
from typing import Optional

class TeamCreate(BaseModel):
    name: str
    
class TeamOut(BaseModel):
    id: int
    name: str
    team_code: str
    creator_id: int
    
    class Config:
        from_attributes = True