from contextlib import suppress
from aiogram import Router, types, Bot, F
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from keyboards import reply, inline
from data import db

router = Router()


@router.message(Command(commands=["surveys", "опросы"], ignore_case=True))
async def command_surveys_handler(message: types.Message, bot: Bot) -> None:
    parsed = db.get_surveys((1, 5))

    if not len(parsed):
        await message.answer(f"Доступные опросы:\n(Название | id)\nДоступных опросов нет 😢\nСтраница 1", reply_markup=reply.menu_kb)
    else:
        st = '\n'.join([f'📄 {survey[1]} | {survey[0]}' for survey in parsed])
        await message.answer(f"Доступные опросы:\n(Название | id)\n{st}\nСтраница 1", reply_markup=inline.paginator(1))


@router.callback_query(inline.Pagination.filter(F.action.in_(['prev', 'next'])))
async def pagination_handler(call: CallbackQuery, bot: Bot, callback_data: inline.Pagination) -> None:
    page_num = int(callback_data.page)
    page = page_num - 1 if page_num > 1 else 1

    if callback_data.action == 'next':
        page = page_num + \
            1 if len(db.get_surveys(
                (page_num * 5 + 1, (page_num + 1) * 5))) else page_num

    if page == 1:
        with suppress(TelegramBadRequest):
            parsed = db.get_surveys((1, 5))
            st = '\n'.join(
                [f'📄 {survey[1]} | {survey[0]}' for survey in parsed])
            await call.message.edit_text(f"Доступные опросы:\n(Название | id)\n{st}\nСтраница {page}", reply_markup=inline.paginator(page))
        await call.answer()
    else:
        with suppress(TelegramBadRequest):
            parsed = db.get_surveys(((page - 1) * 5 + 1, page * 5))
            st = '\n'.join(
                [f'📄 {survey[1]} | {survey[0]}' for survey in parsed])
            await call.message.edit_text(f"Доступные опросы:\n(Название | id)\n{st}\nСтраница {page}", reply_markup=inline.paginator(page))
        await call.answer()
