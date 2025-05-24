from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from storage.models import User

async def create_user(session: AsyncSession, telegram_id: int, username: str):
    user = User(
        telegram_id=telegram_id,
        username=username
    )
    session.add(user)
    await session.commit()
