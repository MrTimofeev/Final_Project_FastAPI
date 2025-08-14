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
    hased_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.user)
    
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team  = relationship("Team", back_populates="members")
    owned_team = relationship("Team", back_populates="creator")
    
    # Связи
    
    task = relationship("Task", back_populates="assignee", foreign_keys="[Task.assignee_id]")
    created_task = relationship("Task", back_populates="creator", foreign_keys="[Task.creator_id]")
    evaluations =  relationship("Evaluations", back_populates="user")
    meeting_participants = relationship("MeetingParticipants", back_populates="user")
