from pydantic import BaseModel, ConfigDict


class TeamCreate(BaseModel):
    name: str


class TeamOut(BaseModel):
    id: int
    name: str
    team_code: str
    creator_id: int

    model_config = ConfigDict(from_attributes=True)
