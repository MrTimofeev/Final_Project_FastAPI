import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New user",
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "hashed_password" not in data
    
@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, registered_user):
    response = await client.post(
        "/auth/jwt/login",
        data={
            "username": "newuser@example.com",
            "password": "password123"
        }
    )
    print(f"ОТВЕТ СЕРВЕРА: {response.text}")
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    