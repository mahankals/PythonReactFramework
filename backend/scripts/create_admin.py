#!/usr/bin/env python3
"""
Create admin user (simplified for User+RBAC deployment)
"""
import asyncio
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin_user(email: str, password: str, first_name: str, last_name: str, phone: str | None = None):
    engine = create_async_engine(
        settings.database_url.replace('postgresql://', 'postgresql+asyncpg://'),
        echo=False
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            if existing.is_admin:
                print(f"Admin user {email} already exists")
                return
            existing.is_admin = True
            await db.commit()
            print(f"User {email} promoted to admin")
            return

        user = User(
            email=email,
            password_hash=pwd_context.hash(password),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            is_active=True,
            is_admin=True,
        )
        db.add(user)
        await db.commit()
        print(f"Admin user created: {email}")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', default='')
    parser.add_argument('--password', default='')
    parser.add_argument('--first-name', default='')
    parser.add_argument('--last-name', default='')
    args = parser.parse_args()
    await create_admin_user(args.email, args.password, args.first_name, args.last_name)

if __name__ == '__main__':
    asyncio.run(main())
