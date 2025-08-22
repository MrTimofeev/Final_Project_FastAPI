import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_team_by_admin(client: AsyncClient, admin_user):
    # логинимся как админ
    login = await client.post(
        "/auth/jwt/login",
        data={"username": "admin@example.com", "password": "password123"},
    )

    token = login.json()["access_token"]

    client.headers["Authorization"] = f"Bearer {token}"

    response = await client.post("/team/", json={"name": "Test Team"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Team"


@pytest.mark.asyncio
async def test_join_team_by_code(client: AsyncClient, regular_user, db_session):
    # Сначала создаем команду
    from app.models.team import Team

    team = Team(name="Test Team", team_code="abcd1234", creator_id=regular_user.id)
    db_session.add(team)
    await db_session.commit()

    # Логинимся как другой пользователь
    login = await client.post(
        "/auth/jwt/login",
        data={"username": "user@example.com", "password": "password123"},
    )

    token = login.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    response = await client.post("/team/join?team_code=abcd1234")

    assert response.status_code == 200
    assert response.json()["team_code"] == "abcd1234"
