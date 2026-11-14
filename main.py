import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import db
from handlers import router

async def main():
    # Включаем вывод логов в консоль, чтобы видеть, что бот работает
    logging.basicConfig(level=logging.INFO)

    # Создаем таблицу (БД сама откроется и закроется)
    await db.init_db()

    # Создаем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем роутеры из файлов
    # dp.include_router(start.router)

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
