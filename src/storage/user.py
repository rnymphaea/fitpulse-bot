from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage.models import User

async def create_user(session: AsyncSession, telegram_id: int, username: str):
#    result = await session.execute(
#        select(User).where(User.telegram_id == telegram_id)
#    )
#    exists = result.scalar_one_or_none()
    user = await get_user(session, telegram_id)
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username
        )
        session.add(user)
        await session.commit()


async def get_user(session: AsyncSession, telegram_id: int):
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    return user

