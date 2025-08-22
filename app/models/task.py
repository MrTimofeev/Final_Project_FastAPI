from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    func,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from app.database.database import Base
import enum


class TaskStatus(enum.Enum):
    open = "open"
    in_progress = "in_progress"
    done = "done"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.open)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship(
        "User", back_populates="created_tasks", foreign_keys=[creator_id]
    )

    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assignee = relationship("User", back_populates="tasks", foreign_keys=[assignee_id])

    team_id = Column(Integer, ForeignKey("teams.id"))
    team = relationship("Team", back_populates="tasks")

    comments = relationship(
        "Comment", back_populates="task", cascade="all, delete-orphan"
    )
    evaluations = relationship("Evaluation", back_populates="task")
