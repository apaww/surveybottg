import re
from contextlib import suppress
from aiogram import Router, types, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command, CommandObject
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from keyboards import reply, inline_esurvey
from aiogram.types import FSInputFile
from data import db
from datetime import date
import csv

router = Router()


class EditSurvey(StatesGroup):
    new_name = State()
    new_questions = State()
    delete_survey = State()


@router.message(StateFilter(None), Command(commands=["edit", "изменить"], ignore_case=True))
async def command_surveys_handler(message: types.Message, bot: Bot, state: FSMContext) -> None:
    if len(message.text.split()) == 1:
        await message.answer("⚠️ Вы неправильно ввели команду!\nЧтобы получить информацию об опросе введите <code>/изменить {id}</code>", reply_markup=reply.menu_kb)
        return
    try:
        ssid = int(message.text.split()[1])
    except Exception:
        await message.answer("⚠️ Вы неправильно ввели команду!\nЧтобы получить информацию об опросе введите <code>/изменить {id}</code>", reply_markup=reply.menu_kb)
        return
    parsed = db.get_survey(ssid)
    if not len(parsed):
        await message.answer("Такого опроса не существует 😢\nЧтобы получить информацию об опросе введите <code>/изменить {id}</code>", reply_markup=reply.menu_kb)
    elif parsed[2] != message.from_user.id:
        await message.answer("Это не ваш опрос! 😢\nЧтобы получить информацию об опросе введите <code>/изменить {id}</code>", reply_markup=reply.menu_kb)
    else:
        await state.update_data(sid=ssid)
        st = '\n'.join(
            [f'{i + 1}. {parsed[4].split("|")[i]}' for i in range(len(parsed[4].split("|")))])
        await message.answer(f"❓ Вопросы:\n{st}")
        await message.answer(f"Информация об опросе 📃\nНазвание: {parsed[1]}\nДата создания: {parsed[3]}\nКоличество вопрсов: {len(parsed[4].split('|'))}\nКоличество полученных ответов: {len(db.get_answers_by_sid(ssid))}\nId: {parsed[0]}", reply_markup=inline_esurvey.paginator(sid=ssid))


@router.callback_query(inline_esurvey.Pagination.filter(F.action.in_(['edit'])))
async def pagination_handler(call: CallbackQuery, bot: Bot, callback_data: inline_esurvey.Pagination) -> None:
    await bot.answer_callback_query(call.id)
    await bot.send_message(call.from_user.id, f"📜 Редактирование опроса:\n💫 Введите новое имя опроса следующим сообщением\nДля отмены редактирования опроса, нажмите <code>стоп ⛔</code> в меню ниже.",
                           reply_markup=reply.survey_kb)
    await state.set_state(EditSurvey.new_name)


@router.message(EditSurvey.new_name)
async def get_name(message: types.Message, state: FSMContext) -> None:
    if message.text == 'стоп ⛔':
        await state.clear()
        await message.answer(f"Процесс редактирования опроса прекращен!", reply_markup=reply.menu_kb)
        return
    await state.update_data(name=message.text.strip())
    await message.answer(
        "📜 Редактирование опроса:\nОтправьте все вопросы одним сообщением в формате <code>{номер вопроса}. {вопрос}</code>.\nНапример:\n1. Ваш пол\n2. Сколько вам лет?\nДля отмены редактирования опроса, нажмите <code>стоп ⛔</code> в меню ниже.",
        reply_markup=reply.survey_kb)
    await state.set_state(EditSurvey.new_questions)


@router.message(EditSurvey.new_questions)
async def get_questions(message: types.Message, state: FSMContext) -> None:
    if message.text == 'стоп ⛔':
        await state.clear()
        await message.answer(f"Процесс редактирования опроса прекращен!", reply_markup=reply.menu_kb)
        return
    questions = re.split(r'[0-9]+\.+', message.text.replace('\n', ''))
    questions = [question.strip() for question in questions[1:]]
    if (len(questions) == 0):
        await message.answer(f"⚠️ Вы ввели вопросы в неправильном формате! Попробуйте изменить опрос снова!",
                             reply_markup=reply.menu_kb)
        await state.clear()
        return

    data = await state.get_data()
    name = data['name']
    sid = data['sid']
    today = date.today()
    db.change_survey(sid, name, questions)
    await message.answer(f"Вы успешно изменили опрос! 🥳\nid измененного опроса: {sid}", reply_markup=reply.menu_kb)
    await state.clear()


@router.callback_query(inline_esurvey.Pagination.filter(F.action.in_(['export'])))
async def pagination_handler(call: CallbackQuery, bot: Bot, callback_data: inline_esurvey.Pagination) -> None:
    await bot.answer_callback_query(call.id)
    sid = int(callback_data.sid)
    fileName = f'./data/answers/{sid}.csv'
    answers = db.get_answers_by_sid(sid)
    survey = db.get_survey(sid)
    questions = survey[4].replace(';', '')
    data = []

    data.append({
        'user': survey[1].replace(';', ''),
        'answers': questions
    })

    for answer in answers:
        uanswers = answer[1].replace(';', '')
        data.append({
            'user': str(answer[0]).replace(';', ''),
            'answers': uanswers
        })

    with open(fileName, 'w', newline='', encoding="utf8") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(data[0].keys()),
            delimiter=';')
        writer.writeheader()
        for d in data:
            writer.writerow(d)

    file = FSInputFile(fileName)

    await bot.send_message(call.from_user.id, f"📃 Ответы на ваш опрос были экспортированы в csv файл!\n💫 В первой строке идет название столбцов, во второй - название опроса и вопросы, далее идут ответы пользователей и их телеграмм id",
                           reply_markup=reply.menu_kb)
    await bot.send_document(call.from_user.id, file)
    await state.clear()


@router.callback_query(inline_esurvey.Pagination.filter(F.action.in_(['delete'])))
async def pagination_handler(call: CallbackQuery, bot: Bot, callback_data: inline_esurvey.Pagination) -> None:
    await bot.answer_callback_query(call.id)
    await bot.send_message(call.from_user.id, f"🗑️ Удаление опроса\nЧтобы подтвердить удаление опроса, введите <code>подтверждаю</code> следующим сообщением!", reply_markup=reply.menu_kb)
    await state.set_state(EditSurvey.delete_survey)


@router.message(EditSurvey.delete_survey)
async def get_sure(message: types.Message, state: FSMContext) -> None:
    sid = int(callback_data.sid)
    if message.text == 'подтверждаю':
        await state.clear()
        db.delete_survey(sid)
        await message.answer(f"🗑️ Опрос был удален!", reply_markup=reply.menu_kb)
        return
    await message.answer(
        "Процесс удаления опросы был отменен!",
        reply_markup=reply.menu_kb)
    await state.clear()
