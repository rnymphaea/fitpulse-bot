from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from storage.user import create_user

from sqlalchemy.ext.asyncio import AsyncSession

from keyboards import common as kb_common

router = Router()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession):
    await create_user(session, message.from_user.id, message.from_user.username)
    kb = kb_common.start_keyboard()
    await message.answer("птичка киви", reply_markup=kb)

