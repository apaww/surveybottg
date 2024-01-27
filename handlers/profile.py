from contextlib import suppress
from aiogram import Router, types, Bot, F
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from keyboards import reply, inline_profile, inline
from data import db

router = Router()


@router.message(Command(commands=["profile", "профиль"], ignore_case=True))
async def command_start_handler(message: types.Message, bot: Bot) -> None:
    parsed = db.get_answer_by_uid(message.from_user.id)
    await message.answer(f"🙂 Пользователь {message.from_user.username} прошел {len(parsed)} опросов!",
                         reply_markup=inline_profile.paginator())


@router.callback_query(inline_profile.Pagination.filter(F.action.in_(['done'])))
async def pagination_handler(call: CallbackQuery, bot: Bot, callback_data: inline_profile.Pagination) -> None:
    await bot.answer_callback_query(call.id)
    surveys = db.get_surveys_by_answers_by_uid(call.from_user.id)

    if not len(surveys):
        await bot.send_message(call.from_user.id, "⚠️ Вы еще не прошли ни одного опроса", reply_markup=reply.menu_kb)
        return

    print(surveys)
    st = '\n'.join(
        [f'📄 {survey[0][1]} | {survey[0][0]}' for survey in surveys])
    await bot.send_message(call.from_user.id, f"Пройденные опросы:\n(Название | id)\n{st}", reply_markup=reply.menu_kb)


@router.callback_query(inline_profile.Pagination.filter(F.action.in_(['done'])))
async def pagination_handler(call: CallbackQuery, bot: Bot, callback_data: inline_profile.Pagination) -> None:
    await bot.answer_callback_query(call.id)
    surveys = db.get_surveys_by_answers_by_uid(call.from_user.id)

    if not len(surveys):
        await bot.send_message(call.from_user.id, "⚠️ Вы еще не прошли ни одного опроса", reply_markup=reply.menu_kb)
        return

    print(surveys)
    st = '\n'.join(
        [f'📄 {survey[0][1]} | {survey[0][0]}' for survey in surveys])
    await bot.send_message(call.from_user.id, f"Пройденные опросы:\n(Название | id)\n{st}", reply_markup=reply.menu_kb)


@router.callback_query(inline_profile.Pagination.filter(F.action.in_(['created'])))
async def pagination_handler(call: CallbackQuery, bot: Bot, callback_data: inline_profile.Pagination) -> None:
    await bot.answer_callback_query(call.id)
    surveys = db.get_surveys_by_uid(call.from_user.id)

    if not len(surveys):
        await bot.send_message(call.from_user.id, "⚠️ Вы еще не создали ни одного опроса", reply_markup=reply.menu_kb)
        return

    print(surveys)
    st = '\n'.join(
        [f'📄 {survey[1]} | {survey[0]}' for survey in surveys])
    await bot.send_message(call.from_user.id, f"Созданные опросы:\n(Название | id)\n{st}", reply_markup=reply.menu_kb)
