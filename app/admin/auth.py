# app/admin/auth.py
from sqladmin.authentication import AuthenticationBackend
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from app.models.user import User
from app.database.database import AsyncSessionLocal
from sqlalchemy import select


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        return RedirectResponse(url="/login", status_code=302)

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return RedirectResponse(url="/login", status_code=302)

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("user_id")
        print(user_id)
        if not user_id:
            return False

        try:
            user_id_int = int(user_id)
        except ValueError:
            raise HTTPException(400, "Invalid user ID")

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_id_int))
            user = result.scalar_one_or_none()

        if not user:
            return RedirectResponse(url="/login", status_code=307)

        if not user.is_active:
            return RedirectResponse(url="/login", status_code=307)
        if not user.is_superuser:
            return RedirectResponse(url="/login", status_code=307)

        return True
