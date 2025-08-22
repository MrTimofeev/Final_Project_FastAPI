import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_evaluation_by_manager(
    client: AsyncClient, manager_user, db_session
):
    # Настраиваем команду и задачу
    from app.models.team import Team
    from app.models.task import Task

    team = Team(name="Team", team_code="eval123", creator_id=manager_user.id)
    db_session.add(team)
    await db_session.commit()

    # Привязываем менеджера к команде
    manager_user.team_id = team.id
    db_session.add(manager_user)
    await db_session.commit()
    await db_session.refresh(manager_user)

    # Создаем задачу
    task = Task(
        title="Done Task",
        status="done",
        creator_id=manager_user.id,
        team_id=team.id,
        assignee_id=manager_user.id,
    )

    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    # Логин
    login = await client.post(
        "/auth/jwt/login",
        data={"username": "manager@example.com", "password": "password123"},
    )

    token = login.json()["access_token"]

    response = await client.post(
        "/evaluations/",
        json={"task_id": task.id, "score": 5},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 201
    assert response.json()["score"] == 5
