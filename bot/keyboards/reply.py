from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


skip=ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Пропустить"),
            KeyboardButton(text="Завершить не сохраняя")
        ],
    ],
    resize_keyboard=True,
)