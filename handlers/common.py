from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from keyboards import common as kb_common

router = Router()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    kb = kb_common.start_keyboard()
    await message.answer("птичка киви", reply_markup=kb)

