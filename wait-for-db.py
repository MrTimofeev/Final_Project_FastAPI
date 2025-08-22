import time
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/business_management"


async def wait_for_db():
    engine = create_async_engine(DATABASE_URL, echo=False)
    while True:
        try:
            async with engine.connect() as conn:
                print("База данных готова!")
                return
        except Exception as e:
            print("Ожидание базы данных... (ошибка подключения)")
            time.sleep(2)


if __name__ == "__main__":
    asyncio.run(wait_for_db())
