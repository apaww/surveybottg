from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class Pagination(CallbackData, prefix='pag'):
    action: str


def paginator():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='📜 Пройденные опросы',
                             callback_data=Pagination(action='done').pack()),
        InlineKeyboardButton(text='📃 Созданные опросы',
                             callback_data=Pagination(action='created').pack()),
        width=2
    )
    return builder.as_markup()
