"""
Seed script: creates admin user and default configuration
"""
import asyncio
from passlib.context import CryptContext
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.config import AppConfig, DEFAULT_CONFIG

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_admin_user():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == 'admin@sampleapp.com'))
        if result.scalar_one_or_none():
            print('Admin user already exists')
            return
        user = User(
            email='admin@sampleapp.com',
            password_hash=pwd_context.hash('admin123'),
            first_name='Admin',
            last_name='User',
            is_admin=True,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        print('Admin user created: admin@sampleapp.com / admin123')


async def seed_default_config():
    async with AsyncSessionLocal() as db:
        added = 0
        for config_data in DEFAULT_CONFIG:
            result = await db.execute(
                select(AppConfig).where(AppConfig.key == config_data["key"])
            )
            if result.scalar_one_or_none():
                continue
            config = AppConfig(**config_data)
            db.add(config)
            added += 1
        await db.commit()
        if added > 0:
            print(f'Added {added} default configuration items')
        else:
            print('Default configuration already exists')


async def main():
    await seed_admin_user()
    await seed_default_config()


if __name__ == '__main__':
    asyncio.run(main())
