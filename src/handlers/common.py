from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from src.storage.user import create_user
from src.keyboards.common import start_keyboard

router = Router()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession):
    await create_user(session, message.from_user.id, message.from_user.username)
    kb = start_keyboard()
    await message.answer("птичка киви", reply_markup=kb)

