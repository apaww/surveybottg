import asyncio
import logging
import os
from data import db
import dotenv
from aiogram import Bot, Dispatcher

from handlers import start, menu, info, surveys, survey, profile, csurvey, esurvey


async def main() -> None:
    db.create_db()
    logging.basicConfig(level=logging.DEBUG)

    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)
    TOKEN = os.getenv("TOKEN")

    bot = Bot(token=TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_routers(
        start.router,
        menu.router,
        info.router,
        surveys.router,
        survey.router,
        profile.router,
        esurvey.router,
        csurvey.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)
    TOKEN = os.getenv("TOKEN")
    DB_NAME = os.getenv("DB_NAME")
    if TOKEN == '':
        token = input('Введите токен бота: ')
        os.environ["TOKEN"] = token
        dotenv.set_key(dotenv_file, "TOKEN", os.environ["TOKEN"])
    try:
        asyncio.run(main())
    except Exception as e:
        print(f'Что-то пошло не так...\n{e}')
