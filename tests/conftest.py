import pytest_asyncio
from httpx import AsyncClient, ASGITransport 
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app as fastapi_app
from fastapi import FastAPI
from app.database.database import Base, get_db, engine
from app.models.user import User
from app.models.comment import Comment
from app.models.team import Team
from app.models.task import Task
from app.models.evaluation import Evaluation
from app.models.meeting_participant import MeetingParticipant
from app.models.meeting import Meeting

from app.utils.security import get_password_hash

# тестовая база в памяти 
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

TestingSessionLocal = sessionmaker(
    class_=AsyncSession, expire_on_commit=False, bind=engine
)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Используем общий TestingSessionLocal, привязанный к engine
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        await session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
        
@pytest_asyncio.fixture(scope="function", autouse=True)
def override_dependency(db_session):
    print("🔧 Оверрайд зависимостей: get_db -> db_session")
    
    # Мы будем подменять get_db на генератор, который возвращает db_session
    def override_get_db():
        yield db_session  # Это важно — yield!

    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield
    fastapi_app.dependency_overrides.clear()
    
        
@pytest_asyncio.fixture
async def client():
    print("🔧 Создаём ASGI-клиент с transport...")
    fastapi_app.state.TESTING = True
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        
@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Admin",
        role="admin",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user

@pytest_asyncio.fixture
async def manager_user(db_session: AsyncSession):
    user = User(
        email="manager@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Manager",
        role="manager",
        is_active=True,
        team_id=None
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user

@pytest_asyncio.fixture
async def regular_user(db_session: AsyncSession):
    user = User(
        email="user@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="User",
        role="user",
        is_active=True,
        team_id = None
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient):
    """Регистрирует пользователя и возвращает его данные"""
    response = await client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New user",
        }
    )
    assert response.status_code == 201
    return response.json()

