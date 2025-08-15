from fastapi import APIRouter

router = APIRouter()

@router.get("/register")
def register():
    return {
        "message": "Регистрация загрушка"
    }
    
@router.get("/login")
def login():
    return {
        "message": "Логин загрушка"
    }


