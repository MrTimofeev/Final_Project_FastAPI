from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database.database import Base

class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_id = Column(Integer, ForeignKey("users.id")) # кто оценил (менеджер)
    score = Column(Integer, nullable=False) # от 1 до 5
    evaluated_at = Column(DateTime, server_default=func.now())
    
    task = relationship("Task", back_populates="evaluations")
    user = relationship("User", back_populates="evaluations")
    