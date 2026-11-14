import sys
import os
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db import DataBase

router = Router()

class UserHandlers:
    def __init__(self, router: Router):
        self.router = router
        self.db = DataBase()
        # Сразу вызываем регистрацию при создании класса
        self.register()

    async def cmd_start(self, message: Message):
        await self.db.init_db()

        user_id = message.from_user.id
        user_name = message.from_user.first_name

        await self.db.register_user(user_id, user_name)
        await message.answer(f"Привет, {user_name}! Ты зарегистрирован.")

    async def cmd_help(self, message: Message):
        await message.answer("Это раздел помощи по игре.")

    async def cmd_profile(self, message: Message) -> None:
        player = await self.db.get_player(message.from_user.id)

        if player is None:
            await message.answer(
                """
                Пользователь не найден, ипсользуйте /start.
                """
                    )
            return

        user_name, coins, level = player

        await message.answer(
            f"Карточка игрока:\n\nИмя: {user_name}\nМонеты: {coins}\nУровень: {level}"
        )


    # Метод регистрации всех хендлеров
    def register(self):
        self.router.message.register(self.cmd_start, Command("start"))
        self.router.message.register(self.cmd_help, Command("help"))
        self.router.message.register(self.cmd_profile, Command("profile"))


# Инициализируем класс, чтобы хендлеры зарегистрировались в router
UserHandlers(router)
