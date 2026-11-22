import os
import random
import sys
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.db import Database

router_nums = Router()

MIN_NUM = 1
MAX_NUM = 100
MAX_ATTEMPTS = 5  # Меньше log2(100) ≈ 6.64 -> гарантированного бинарного поиска нет
REWARD_COINS = 25


class GuessNumberStates(StatesGroup):
    playing = State()


class GuessNumberHandlers:
    def __init__(self, router: Router, db: Database): 
        self.router = router
        self.db = db  
        self.register()


    async def cmd_guess_number(self, message: Message, state: FSMContext) -> None:
        player = await self.db.get_player(message.from_user.id)
        if player is None:
            await message.answer("Пользователь не найден, используйте /start.")
            return

        secret = random.randint(MIN_NUM, MAX_NUM)
        await state.set_state(GuessNumberStates.playing)
        await state.update_data(secret=secret, attempts_left=MAX_ATTEMPTS)

        await message.answer(
            f"🔢 Я загадал число от <b>{MIN_NUM}</b> до <b>{MAX_NUM}</b>.\n"
            f"У тебя всего <b>{MAX_ATTEMPTS}</b> попыток — угадать по логарифму вслепую не выйдет!\n"
            f"Награда за победу: <b>{REWARD_COINS}</b> монет. Введи число:",
            parse_mode="HTML",
        )

    async def process_guess(self, message: Message, state: FSMContext) -> None:
        if not message.text or not message.text.strip().lstrip("-").isdigit():
            await message.answer("Пожалуйста, отправь целое число.")
            return

        guess = int(message.text.strip())
        if not (MIN_NUM <= guess <= MAX_NUM):
            await message.answer(f"Число должно быть в диапазоне от {MIN_NUM} до {MAX_NUM}.")
            return

        data = await state.get_data()
        secret = data["secret"]
        attempts_left = data["attempts_left"] - 1

        if guess == secret:
            await state.clear()
            # Подключи свой метод начисления монет в БД, например:
            # await self.db.add_coins(message.from_user.id, REWARD_COINS)
            await message.answer(
                f"🎉 Точно! Это число <b>{secret}</b>. Ты получаешь <b>{REWARD_COINS}</b> монет!",
                parse_mode="HTML",
            )
            return

        if attempts_left <= 0:
            await state.clear()
            await message.answer(
                f"💥 Попытки закончились! Я загадал число <b>{secret}</b>. Попробуй ещё раз: /guess_number",
                parse_mode="HTML",
            )
            return

        hint = "больше" if guess < secret else "меньше"
        await state.update_data(attempts_left=attempts_left)
        await message.answer(
            f"Моё число <b>{hint}</b>, чем {guess}.\n"
            f"Осталось попыток: <b>{attempts_left}</b>.",
            parse_mode="HTML",
        )

    def register(self) -> None:
        self.router.message.register(self.cmd_guess_number, Command("guess_number"))
        self.router.message.register(self.process_guess, GuessNumberStates.playing)

