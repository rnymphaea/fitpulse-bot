from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy.orm import selectinload

from src.storage.models import Product, User, MealType, Meal, MealItem
from src.storage.user import get_user

async def get_product(session: AsyncSession, telegram_id: int, name_product: str):
    user = await get_user(session, telegram_id)
    if not user:
        return False

    
    result = await session.execute(
        select(Product).where(
            (Product.user_id == user.id) & (Product.name == name_product)
        )
    )
    exists = result.scalar_one_or_none()

    return exists

async def create_product(session: AsyncSession, telegram_id: int, info: dict):
    user = await get_user(session, telegram_id)
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
    

async def get_products(session: AsyncSession, telegram_id: int):
    user = await get_user(session, telegram_id)
    if user:
        query = select(Product).where(Product.user_id == user.id)
        result = await session.execute(query)
        return result.scalars().all()


async def get_meal_type(session: AsyncSession, meal_name: str):
    result = await session.execute(
        select(MealType).where(MealType.name == meal_name)
    )
    meal_type = result.scalar_one_or_none()
    return meal_type


async def create_meal(session: AsyncSession, telegram_id: int, info: dict):
    meal_name = info['meal_type']
    meal_type = await get_meal_type(session, meal_name)
    user = await get_user(session, telegram_id)
    try:
        if meal_type and user:
            meal = Meal(
                user_id = user.id,
                type_id = meal_type.id
            )
            session.add(meal)
            await session.flush()

        for product_info in info['meal_products']:
            product = await get_product(session, telegram_id, product_info[0])
            if not product:
                raise ValueError("product not found")

            meal_item = MealItem(
                meal_id=meal.id,
                product_id=product.id,
                quantity=product_info[-1]
            )

            session.add(meal_item)
            
            await session.commit()
    except ValueError as e:
        print(e)
        await session.rollback()
        raise


async def get_today_meals(session: AsyncSession, telegram_id: int):
    user = await get_user(session, telegram_id)
    if not user:
        return []

    today = datetime.today().date()
    result = await session.execute(
        select(Meal).options(
            selectinload(Meal.type),
            selectinload(Meal.products).selectinload(MealItem.product)
        ).where(
            Meal.user_id == user.id,
            func.date(Meal.created_at) == today
        ).order_by(Meal.created_at)
    )

    today_meals = []

    for meal in result.scalars().all():
        meal_info = {
            "type": meal.type.name,
            "time": meal.created_at.strftime("%H:%M"),
            "products": []
        }
        
        for meal_item in meal.products:
            product = meal_item.product
            meal_info["products"].append({
                "name": product.name,
                "calories": product.calories,
                "protein": product.protein,
                "fats": product.fats,
                "carbs": product.carbs,
                "fiber": product.fiber,
                "quantity": meal_item.quantity
            })
        
        today_meals.append(meal_info) 
    return today_meals
