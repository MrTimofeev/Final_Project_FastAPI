import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_meeting_no_overlap(
    client: AsyncClient, manager_user, regular_user, db_session
):

    from app.models.team import Team

    team = Team(name="Team", team_code="meet123", creator_id=manager_user.id)
    db_session.add(team)
    await db_session.commit()

    manager_user.team_id = team.id
    db_session.add(manager_user)

    regular_user.team_id = team.id
    db_session.add(regular_user)

    await db_session.commit()

    login = await client.post(
        "/auth/jwt/login",
        data={"username": "manager@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    # Первая стреча
    response = await client.post(
        "/meetings/",
        json={
            "title": "Встреча 1",
            "start_time": "2025-04-05T10:00:00",
            "end_time": "2025-04-05T11:00:00",
            "participant_ids": [manager_user.id, regular_user.id],
        },
    )
    assert response.status_code == 201

    # Вторая - в то же время -> должна быть ошибка
    response = await client.post(
        "/meetings/",
        json={
            "title": "Встреча 2",
            "start_time": "2025-04-05T10:30:00",
            "end_time": "2025-04-05T11:30:00",
            "participant_ids": [regular_user.id],
        },
    )
    assert response.status_code == 400
