from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_teams():
    return {
        "message": "Список команд загрушка"
    }