from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

def select_option_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить блюдо", callback_data="add_plate")],
        [InlineKeyboardButton(text="Приёмы пищи", callback_data="meals")],
    ])
    return keyboard


def meals_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завтрак", callback_data="breakfast"), InlineKeyboardButton(text="Перекус", callback_data="snack")],
        [InlineKeyboardButton(text="Обед", callback_data="lunch"), InlineKeyboardButton(text="Ужин", callback_data="dinner")],
        [InlineKeyboardButton(text="Статистика за день", callback_data="stat")],
        ])
    return keyboard


def plot_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="График", callback_data="plot")]
    ])
    return keyboard
