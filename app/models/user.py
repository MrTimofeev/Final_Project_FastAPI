from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database.database import Base
import enum


class RoleEnum(enum.Enum):
    user = "user"
    manager = "manager"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.user)

    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team = relationship("Team", back_populates="members", foreign_keys=[team_id])
    owned_teams = relationship(
        "Team", back_populates="creator", foreign_keys="Team.creator_id"
    )

    # Связи
    tasks = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assignee_id"
    )
    created_tasks = relationship(
        "Task", back_populates="creator", foreign_keys="Task.creator_id"
    )
    evaluations = relationship("Evaluation", back_populates="user")
    meeting_participants = relationship("MeetingParticipant", back_populates="user")
