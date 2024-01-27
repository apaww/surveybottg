from aiogram import Router, types, Bot
from aiogram.filters.command import Command
from importlib.metadata import version
from keyboards import reply

router = Router()


@router.message(Command(commands=["info", "инфо"], ignore_case=True))
async def command_info_handler(message: types.Message, bot: Bot) -> None:
    await message.answer(f"Информация о боте:\n"
                         f"• Бот написан на aiogram {version('aiogram')} 🤖\n"
                         f"• Для датабазы использовалась sqlite3 📃\n"
                         "• Если вы обнаружили баг или у вас возникли вопросы, "
                         "вы можете написать <a href='tg://user?id=1188864359'>разработчику бота</a> 👈", reply_markup=reply.menu_kb, disable_web_page_preview=True)
