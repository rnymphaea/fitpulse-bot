from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


def admin_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Удалить все данные", callback_data="delete_all_food_data")]
    ])
    return keyboard


