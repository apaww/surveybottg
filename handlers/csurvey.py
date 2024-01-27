import re
from aiogram import Router, types, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from keyboards import reply
from data import db
from datetime import date

router = Router()


class CreateSurvey(StatesGroup):
    get_name = State()
    get_questions = State()
    created_survey = State()


@router.message(StateFilter(None), Command(commands=["create", "создать"], ignore_case=True))
async def command_surveys_handler(message: types.Message, bot: Bot, state: FSMContext) -> None:
    await message.answer(
        f"📜 Создание опроса:\n💫 Введите имя опроса следующим сообщением\nДля отмены создания опроса, нажмите <code>стоп ⛔</code> в меню ниже.",
        reply_markup=reply.survey_kb)
    await state.set_state(CreateSurvey.get_name)


@router.message(CreateSurvey.get_name)
async def get_name(message: types.Message, state: FSMContext) -> None:
    if message.text == 'стоп ⛔':
        await state.clear()
        await message.answer(f"Процесс создания опроса прекращен!", reply_markup=reply.menu_kb)
        return
    await state.update_data(name=message.text.strip())
    await message.answer(
        "📜 Создание опроса:\nОтправьте все вопросы одним сообщением в формате <code>{номер вопроса}. {вопрос}</code>.\nНапример:\n1. Ваш пол\n2. Сколько вам лет?\nДля отмены создания опроса, нажмите <code>стоп ⛔</code> в меню ниже.",
        reply_markup=reply.survey_kb)
    await state.set_state(CreateSurvey.get_questions)


@router.message(CreateSurvey.get_questions)
async def get_questions(message: types.Message, state: FSMContext) -> None:
    if message.text == 'стоп ⛔':
        await state.clear()
        await message.answer(f"Процесс создания опроса прекращен!", reply_markup=reply.menu_kb)
        return
    questions = re.split(r'[0-9]+\.+', message.text.replace('\n', ''))
    questions = [question.strip() for question in questions[1:]]
    if (len(questions) == 0):
        await message.answer(f"Вы ввели вопросы в неправильном формате! Попробуйте создать опрос снова!",
                             reply_markup=reply.menu_kb)
        await state.clear()
        return

    data = await state.get_data()
    name = data['name']
    today = date.today()
    sid = db.create_survey(name, message.from_user.id,
                           str(today.strftime("%m/%d/%y")), questions)
    await message.answer(f"Вы успешно создали опрос! 🥳\nid созданного опроса: {sid}", reply_markup=reply.menu_kb)
    await state.clear()
