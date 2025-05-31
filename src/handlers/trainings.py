from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter
from aiogram.enums.parse_mode import ParseMode

trainings_router = Router()

@trainings_router.callback_query(F.data == "trainings")
async def trainings(callback: CallbackQuery):
    await callback.message.answer("trainings")

