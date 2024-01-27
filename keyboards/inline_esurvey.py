from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class Pagination(CallbackData, prefix='pag'):
    action: str
    sid: int


def paginator(sid: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='📜 Изменнить опрос',
                             callback_data=Pagination(action='edit', sid=sid).pack()),
        InlineKeyboardButton(text='📃 Выгрузить ответы',
                             callback_data=Pagination(action='export', sid=sid).pack()),
        InlineKeyboardButton(text='🗑️ Удалить опрос',
                             callback_data=Pagination(action='delete', sid=sid).pack()),
        width=2
    )
    return builder.as_markup()
