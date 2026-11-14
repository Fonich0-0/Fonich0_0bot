from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.db import DataBase

router = Router()

class UserHandlers:
    def __init__(self, router: Router):
        self.router = router
        self.db = DataBase()
        self.db.init_db()
        # Сразу вызываем регистрацию при создании класса
        self.register()

    async def cmd_start(self, message: Message):
        user_id = message.from_user.id
        user_name = message.from_user.first_name

        await self.db.register_user(user_id, user_name)
        await message.answer(f"Привет, {user_name}! Ты зарегистрирован.")

    async def cmd_help(self, message: Message):
        await message.answer("Это раздел помощи по игре.")

    # Метод регистрации всех хендлеров
    def register(self):
        self.router.message.register(self.cmd_start, Command("start"))
        self.router.message.register(self.cmd_help, Command("help"))


# Инициализируем класс, чтобы хендлеры зарегистрировались в router
UserHandlers(router)
