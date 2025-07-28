from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models import Users, PasswordResetToken
from modules.auth_modules.auth_schemas import CreateUserRequest
from modules.auth_modules.auth_utils import get_password_hash
from datetime import datetime, timedelta
from uuid import uuid4

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(Users).filter(Users.username == username))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(Users).filter(Users.email == email))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(Users).filter(Users.id == user_id))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_data: CreateUserRequest):
    hashed_password = get_password_hash(user_data.password)
    db_user = Users(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role,
        hashed_password=hashed_password,
        is_active=True,
        phone_number=user_data.phone_number
    )
    db.add(db_user)
    await db.commit() # Thêm await
    await db.refresh(db_user) # Thêm await
    return db_user

async def save_password_reset_token(db: AsyncSession, user_id: int) -> str:
    await db.execute(delete(PasswordResetToken).filter(PasswordResetToken.user_id == user_id))
    await db.commit() # Thêm await

    token = str(uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=1) # Token hết hạn sau 1 giờ

    new_token_entry = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(new_token_entry)
    await db.commit()
    return token

async def get_password_reset_token_entry(db: AsyncSession, token: str):
    result = await db.execute(select(PasswordResetToken).filter(PasswordResetToken.token == token))
    return result.scalars().first()

async def delete_password_reset_token_entry(db: AsyncSession, token_entry: PasswordResetToken):
    await db.delete(token_entry)
    await db.commit()

async def update_user_password(db: AsyncSession, user: Users, new_password: str):
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Users).offset(skip).limit(limit))
    return result.scalars().all()

async def get_user_detail_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(Users).filter(Users.id == user_id))
    return result.scalars().first()

async def update_user_by_admin(db: AsyncSession, user_model: Users, user_data):
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user_model, field, value)
    db.add(user_model)
    await db.commit()
    await db.refresh(user_model)
    return user_model

async def delete_user_by_admin(db: AsyncSession, user_model: Users):
    await db.delete(user_model)
    await db.commit()

