import re
from contextlib import suppress
from aiogram import Router, types, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command, CommandObject
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from keyboards import reply, inline_survey
from data import db

router = Router()


class AnswerSurvey(StatesGroup):
    answering_the_survey = State()


@router.message(StateFilter(None), Command(commands=["survey", "опрос"], ignore_case=True))
async def command_surveys_handler(message: types.Message, bot: Bot, state: FSMContext) -> None:
    if len(message.text.split()) == 1:
        await message.answer("⚠️ Вы неправильно ввели команду!\nЧтобы получить информацию об опросе введите <code>/опрос {id}</code>", reply_markup=reply.menu_kb)
        return
    try:
        ssid = int(message.text.split()[1])
    except Exception:
        await message.answer("⚠️ Вы неправильно ввели команду!\nЧтобы получить информацию об опросе введите <code>/опрос {id}</code>", reply_markup=reply.menu_kb)
        return
    parsed = db.get_survey(ssid)
    if not len(parsed):
        await message.answer("Такого опроса не существует 😢\nЧтобы получить информацию об опросе введите <code>/опрос {id}</code>", reply_markup=reply.menu_kb)
    else:
        await state.update_data(sid=ssid)
        await message.answer(f"Информация об опросе 📃\nНазвание: {parsed[1]}\nДата создания: {parsed[3]}\nКоличество вопрсов: {len(parsed[4].split('|'))}\nId: {parsed[0]}", reply_markup=inline_survey.paginator())


@router.callback_query(inline_survey.Pagination.filter(F.action.in_(['start'])))
async def pagination_handler(call: CallbackQuery, bot: Bot, callback_data: inline_survey.Pagination, state: FSMContext) -> None:
    await bot.answer_callback_query(call.id)
    data = await state.get_data()
    ssid = data['sid']

    if ssid in db.get_answer_by_uid(call.from_user.id):
        await bot.send_message(call.from_user.id, "⚠️ Вы уже проходили данный опрос!", reply_markup=reply.menu_kb)
        await state.clear()
        return
    parsed = db.get_survey(ssid)[4].split('|')
    st = '\n'.join([f'{i + 1}. {parsed[i]}' for i in range(len(parsed))])
    await bot.send_message(call.from_user.id, "📜 Инструкция:\nОтветьте на все вопросы одним сообщением в формате <code>{номер вопроса}. {ответ}</code>.\nНапример:\n1. Да\n2. 25 лет\nДля отмены прохождения опроса, нажмите <code>стоп ⛔</code> в меню ниже.")
    await bot.send_message(call.from_user.id, f"❓ Вопросы:\n{st}", reply_markup=reply.survey_kb)
    await state.set_state(AnswerSurvey.answering_the_survey)


@router.message(AnswerSurvey.answering_the_survey)
async def get_answer(message: types.Message, state: FSMContext) -> None:
    if message.text == 'стоп ⛔':
        await state.clear()
        await message.answer(f"Прохождение опроса прекращено!", reply_markup=reply.menu_kb)
        return
    data = await state.get_data()
    sid = data['sid']
    answers = re.split(r'[0-9]+\.+', message.text.replace('\n', ''))
    answers = [answer.strip() for answer in answers[1:]]
    if (len(answers) == 0) or (len(answers) != len(db.get_survey(sid)[4].split('|'))):
        await message.answer(f"Вы ответили на вопросы в неправильном формате. Попробуйте пройти опрос снова!", reply_markup=inline_survey.paginator(message, sid))
        await state.clear()
        return

    db.create_answer(sid, message.from_user.id, answers)
    await message.answer(f"Вы успешно прошли опрос! 🥳", reply_markup=reply.menu_kb)
    await state.clear()
