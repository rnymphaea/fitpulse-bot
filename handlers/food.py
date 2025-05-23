from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from keyboards import food as kb_food

router = Router()

@router.callback_query(F.data == "food")
async def food(callback: CallbackQuery):
    kb = kb_food.select_option_keyboard()
    await callback.message.edit_text("Выберите опцию", reply_markup=kb)

@router.callback_query(F.data == "add_plate")
async def food(callback: CallbackQuery):
    kb = kb_food.select_option_keyboard()
    await callback.message.edit_text("Выберите опцию", reply_markup=kb)

@router.callback_query(F.data == "meals")
async def food(callback: CallbackQuery):
    kb = kb_food.meals_keyboard()
    await callback.message.edit_text("Какой приём пищи вы хотите добавить?", reply_markup=kb)