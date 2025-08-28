import argparse
import asyncio
import getpass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database.database import get_db
from app.models.user import User
from app.utils.security import get_password_hash


async def create_superuser(email: str, password: str, full_name: Optional[str] = None):
    async for db in get_db():
        session: AsyncSession = db

        # Проверяем, существует ли пользователь
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if user:
            if user.is_superuser:
                print(f"❌ Пользователь с email '{email}' уже является суперпользователем.")
            else:
                print(f"❌ Пользователь с email '{email}' существует, но не является суперпользователем.")
            return

        # Создаём суперпользователя
        superuser = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name or "ADMIN",
            is_active=True,
            is_superuser=True,
            role="admin"
        )

        session.add(superuser)
        await session.commit()
        await session.refresh(superuser)
        print(f"✅ Суперпользователь '{email}' успешно создан.")
        await session.close()
        break


def main():
    parser = argparse.ArgumentParser(description="Утилиты командной строки для приложения")
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Команда: createsuperuser
    create_parser = subparsers.add_parser("createsuperuser", help="Создать суперпользователя")
    create_parser.add_argument("--email", type=str, help="Email пользователя")
    create_parser.add_argument("--full-name", type=str, help="Полное имя (опционально)")

    args = parser.parse_args()

    if args.command == "createsuperuser":
        email = args.email or input("Email: ")

        # Запрашиваем пароль скрыто
        password = getpass.getpass("Пароль: ")
        password_confirm = getpass.getpass("Подтвердите пароль: ")

        if password != password_confirm:
            print("❌ Пароли не совпадают.")
            return

        if len(password) < 6:
            print("❌ Пароль слишком короткий (минимум 6 символов).")
            return

        asyncio.run(create_superuser(email, password, args.full_name))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()