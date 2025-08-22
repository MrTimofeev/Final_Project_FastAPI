from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    team_code = Column(String, unique=True, index=True)  # для приглошения

    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship(
        "User", back_populates="owned_teams", foreign_keys=[creator_id]
    )

    members = relationship("User", back_populates="team", foreign_keys="User.team_id")
    tasks = relationship("Task", back_populates="team")
    meetings = relationship("Meeting", back_populates="team")
