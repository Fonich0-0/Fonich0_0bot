import sys
import os
from functools import partial
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
        '''Команда /start для авторизации пользователя
        по его id в Telegram; вывод информации об успехе.'''
        await self.db.init_db()

        user_id = message.from_user.id
        user_name = message.from_user.first_name

        await self.db.register_user(user_id, user_name)
        await message.answer(f"Привет, {user_name}! Ты зарегистрирован.")


    async def cmd_help(self, message: Message):
        text = (
            "📖 <b>Справка по игре</b>\n\n"
            "Добро пожаловать! Здесь ты можешь прокачивать своего персонажа и копить монеты.\n\n"
            "<b>Доступные команды:</b>\n"
            "🔹 /start — регистрация в игре и создание профиля\n"
            "🔹 /profile — карточка игрока (имя, уровень и монеты)\n"
            "🔹 /balance — быстро проверить свой кошелёк\n"
            "🔹 /help — показать это меню\n\n"
            "💡 <i>Совет: если бот пишет, что профиль не найден, просто нажми /start.</i>"
        )
        await message.answer(text, parse_mode="HTML")


    async def cmd_profile(self, flag: bool, message: Message) -> tuple | None:
        '''- Берёт данные из базы данных и выводит профиль пользователя;
        - Если пользователь не найден вежливо выводит использовать команду /start; 
        - Аргумент flag нужен чтобы можно было не присылать карточку
        игрока с user_name, coins, level (для дополнительных отдельных команд)'''

        player = await self.db.get_player(message.from_user.id)

        if player is None:
            await message.answer(
                'Пользователь не найден, используйте /start.'
                    )
            return

        user_name, coins, level = player

        if flag:
            await message.answer(
                f"Карточка игрока:\n\nИмя: {user_name}\nМонеты: {coins}\nУровень: {level}"
            )
        return (user_name, coins, level)


    async def cmd_balance(self, message: Message) -> int | None:
        '''Выводит информацию о балансе пользователя с помощью
        self.cmd_profile(False, message) - False, чтобы не было
        полной карточки игрока'''

        player = await self.cmd_profile(False, message)
        if player is None:
            return
        
        balance = player[1]

        await message.answer(
                    f"Ваш баланс:\nМонеты: {balance}"
                )
        return balance


    # Метод регистрации всех хендлеров
    def register(self):
        self.router.message.register(self.cmd_start, Command("start"))
        self.router.message.register(self.cmd_help, Command("help"))
        self.router.message.register(partial(self.cmd_profile, True), Command("profile"))
        self.router.message.register(self.cmd_balance, Command("balance"))


# Инициализируем класс, чтобы хендлеры зарегистрировались в router
UserHandlers(router)
