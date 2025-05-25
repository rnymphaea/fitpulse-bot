from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from storage.models import User

async def create_user(session: AsyncSession, telegram_id: int, username: str):
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    exists = result.scalar_one_or_none()

    if not exists:
        user = User(
            telegram_id=telegram_id,
            username=username
        )
        session.add(user)
        await session.commit()

