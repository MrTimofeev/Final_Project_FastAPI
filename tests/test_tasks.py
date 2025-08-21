import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
async def test_create_task_by_manager(client: AsyncClient, manager_user, db_session):
    # Добавим менеджера в команду
    from app.models.team import Team
    team = Team(
        name="Dev Team",
        team_code="dev123",
        creator_id=manager_user.id
    )
    db_session.add(team)
    await db_session.commit()
    await db_session.refresh(team)

    manager_user.team_id = team.id
    db_session.add(manager_user)
    await db_session.commit()

    # Логин
    login = await client.post(
        "/auth/jwt/login",
        data={
            "username": "manager@example.com",
            "password": "password123"
        }
    )

    token = login.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    response = await client.post(
        "/tasks/",
        json={
            "title": "Новая задача",
            "description": "Сделать MVP",
            "deadline": "2025-04-10T10:00:00"
        }
    )
    
    print("Status:", response.status_code)
    print("Response:", response.text)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Новая задача"
    assert data["status"] == "open"
