from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_evaluations():
    return {
        "message": "Список оценок загрушка"
    }