from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

def select_option_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить блюдо", callback_data="add_plate")],
        [InlineKeyboardButton(text="Приёмы пищи", callback_data="meals")],
    ])
    return keyboard


def meals_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завтрак", callback_data="breakfast")],
        [InlineKeyboardButton(text="Обед", callback_data="lunch")],
        [InlineKeyboardButton(text="Ужин", callback_data="dinner")],
    ])
    return keyboard