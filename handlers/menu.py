from aiogram import Router, types, Bot
from aiogram.filters.command import Command
from keyboards import reply

router = Router()


@router.message(Command(commands=["menu", "меню"], ignore_case=True))
async def command_menu_handler(message: types.Message, bot: Bot) -> None:
    await message.answer("Мои команды:\n"
                         "<code>/меню</code> - выводит данное сообщение\n"
                         "<code>/опросы</code> - выводит список всех доступных опросов\n"
                         "<code>/опрос {id}</code> - открывает страницу опроса с заданным id\n"
                         "<code>/инфо</code> - информация о боте\n"
                         "<code>/профиль</code> - информация о пользователе\n"
                         "<code>/создать</code> - создать опрос\n"
                         "<code>/изменить {id}</code> - изменить опрос""", reply_markup=reply.menu_kb)
