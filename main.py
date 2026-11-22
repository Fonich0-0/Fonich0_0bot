import logging
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot.config import BOT_TOKEN, DATABASE_URL, PORT, WEBHOOK_PATH, WEBHOOK_URL
from bot.handlers.game_guess_number import router_nums
from bot.handlers.game_guess_word import router_word
from bot.handlers.game_tic_tac_toe import router_ttt
from bot.handlers.user_menu import UserHandlers, router_menu
from bot.database.db import Database


async def on_startup(bot: Bot, db: Database):
  await db.connect()
  await db.init_db()
  await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")


async def on_shutdown(bot: Bot, db: Database):
  await db.close()


def main():
  logging.basicConfig(level=logging.INFO)

  bot = Bot(token=BOT_TOKEN)
  dp = Dispatcher()

  # 1. Создаем единый объект базы данных
  db = Database(dsn=DATABASE_URL)
  dp["db"] = db

  # 2. Инициализируем классы хендлеров и передаем им общий db
  UserHandlers(router_menu, db)
  UserHandlers(router_menu, db)
  UserHandlers(router_menu, db)
  UserHandlers(router_menu, db)
  # Если игровые хендлеры тоже сделаны классами с БД, подключайте их так же:
  # GuessNumberHandlers(router_nums, db)

  dp.startup.register(on_startup)
  dp.shutdown.register(on_shutdown)

  dp.include_router(router_menu)
  dp.include_router(router_nums)
  dp.include_router(router_word)
  dp.include_router(router_ttt)

  app = web.Application()
  SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
  setup_application(app, dp, bot=bot)

  web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
  main()