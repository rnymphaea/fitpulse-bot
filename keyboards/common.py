from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

def start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Питание", callback_data="food")],
        [InlineKeyboardButton(text="Тренировки", callback_data="trainings")],
    ])
    return keyboard