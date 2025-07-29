import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from modules.auth_modules.auth_crud import get_user_by_username, create_user
from modules.auth_modules.auth_schemas import CreateUserRequest
from database import AsyncSessionLocal
from config import settings


async def seed_initial_admin_user():
    async with AsyncSessionLocal() as session:
        admin_username = settings.DEFAULT_ADMIN_USERNAME
        admin_user_exists = await get_user_by_username(session, admin_username)

        if not admin_user_exists:
            print(f"INFO: Initial admin user '{admin_username}' not found. Creating default admin user.")

            admin_email = settings.DEFAULT_ADMIN_EMAIL
            admin_first_name = settings.DEFAULT_ADMIN_FIRST_NAME
            admin_last_name = settings.DEFAULT_ADMIN_LAST_NAME
            admin_password = settings.DEFAULT_ADMIN_PASSWORD

            admin_create_request = CreateUserRequest(
                email=admin_email,
                username=admin_username,
                first_name=admin_first_name,
                last_name=admin_last_name,
                password=admin_password,
                role="admin",
                phone_number=settings.DEFAULT_ADMIN_PHONE_NUMBER
            )
            # Tạo người dùng admin
            await create_user(session, admin_create_request)
            print(f"INFO: Initial admin user '{admin_username}' created.")
        else:
            print(f"INFO: Admin user '{admin_username}' already exists. Skipping creation.")

