from aiogram import Router, types, Bot
from aiogram.filters.command import Command
from keyboards import reply

router = Router()


@router.message(Command(commands=["start", "старт"], ignore_case=True))
async def command_start_handler(message: types.Message, bot: Bot) -> None:
    await message.answer(f"Привет! Я {(await bot.get_me()).username}, твой личный помощник для прохождения различных опросов!"
                        "😊 Давай начнем! Просто напиши <code>/опросы</code>, чтобы приступить к интересным вопросам."
                        "Также ты можешь воспользоваться командами <code>/меню</code>, <code>/инфо</code> или <code>/профиль</code> "
                        "для получения дополнительной информации. Удачи, и пусть опросы будут веселыми и познавательными! 🎉", reply_markup=reply.menu_kb)