from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from decouple import config

def str_to_bool(value: str) -> bool:
    return value.lower() in ("true", "1", "on", "yes")

# Определяем режим тестирования
TESTING = str_to_bool(config("TESTING", default="false"))

print(TESTING)
if TESTING:
    DATABASE_URL = config("DATABASE_TEST_URL")
else:
    DATABASE_URL = config("DATABASE_URL")

print(DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=False)


AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

