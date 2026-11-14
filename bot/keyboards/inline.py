from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

# def get_confirm_kb():
#     builder = InlineKeyboardBuilder()
#     builder.add(InlineKeyboardButton(text='Подтвердить', callback_data='confirm'))
#     builder.add(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
#     return builder.as_markup()

def action_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Сложение', callback_data='plus'))
    builder.add(InlineKeyboardButton(text='Вычитание', callback_data='minus'))
    builder.add(InlineKeyboardButton(text='Умножение', callback_data='multiplication'))
    builder.add(InlineKeyboardButton(text='Деление', callback_data='division'))
    builder.add(InlineKeyboardButton(text='Степень', callback_data='exponentiation'))
    return builder.as_markup()