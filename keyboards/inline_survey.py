from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class Pagination(CallbackData, prefix='pag'):
    action: str


def paginator():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='📜 Пройти опрос', callback_data=Pagination(action='start').pack()),
        width=1
    )
    return builder.as_markup()