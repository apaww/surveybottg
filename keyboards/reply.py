from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='/меню'),
            KeyboardButton(text='/опросы')
        ],
        [
            KeyboardButton(text='/инфо'),
            KeyboardButton(text='/профиль')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите действие из меню',
    selective=True
)

survey_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='стоп ⛔'),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите действие из меню',
    selective=True
)
