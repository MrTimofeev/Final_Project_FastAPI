from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_meetings():
    return {
        "message": "Список встреч загрушка"
    }