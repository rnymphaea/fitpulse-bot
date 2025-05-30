from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from sqlalchemy.ext.asyncio import AsyncSession

from src.keyboards.admin import admin_keyboard
from src.keyboards.common import start_keyboard
from main import ADMIN

admin_router = Router()

@admin_router.message(Command("admin"))
async def process_admin(message: Message):
    if str(message.from_user.id) != ADMIN:
        kb = start_keyboard()
        await message.answer("Вы не админ!", reply_markup=kb)
    else:
        kb = admin_keyboard()
        await message.answer("Выберите действие: ", reply_markup=kb)


@admin_router.callback_query(F.data == "delete_all_food_data")
async def delete_all_food_data(callback: CallbackQuery, session: AsyncSession):
    success = await delete_all_user_food_data(session, callback.from_user.id)
    if success:
        await callback.message.answer("Удаление всех данных о продуктах и приёмах пищи прошло успешно.")
    else:
        await callback.message.answer("Что-то пошло не так при удалении данных о продуктах и приёмах пищи.")
    await callback.answer()
