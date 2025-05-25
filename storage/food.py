from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from storage.models import Product, User

async def product_exists(session: AsyncSession, telegram_id: int, name_product: str):
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return False

    
    result = await session.execute(
        select(Product).where(
            (Product.user_id == user.id) & (Product.name == name_product)
        )
    )
    exists = result.scalar_one_or_none()

    return exists is not None

async def create_product(session: AsyncSession, telegram_id: int, info: dict):
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if user:
        name = info['name'].lower()
        calories = info['calories']
        protein, fats, carbs = info['pfc']
        fiber = info['fiber']
        product = Product(
            user_id=user.id,
            name=name,
            calories=calories,
            protein=protein,
            fats=fats,
            carbs=carbs,
            fiber=fiber,
            category_id=1
        )
        session.add(product)
        await session.commit()
    
