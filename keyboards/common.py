from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

def start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Питание", callback_data="food")],
        [InlineKeyboardButton(text="Тренировки", callback_data="trainings")],
    ])
    return keyboard


def confirmation_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да", callback_data="confirmation_yes")],
        [InlineKeyboardButton(text="❌ Нет", callback_data="confirmation_no")],
    ])
    return keyboard
