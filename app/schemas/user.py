from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Схема для создание пользователя (регистарции)
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name = Optional[str] = None # type: ignore
    role: Optional[str] = "user"
    

# Схема дотя ответа (без пароля!)
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    team_id: Optional[str]
    
    class Config:
        from_attributes = True
        
        
# Схема обновление профиля
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None # если передан - обновляем хеш
    


    