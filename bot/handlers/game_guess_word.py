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

router_word = Router()

FALLBACK_WORDS = [
    ("АЛГОРИТМ", "Пошаговая инструкция для решения задачи"),
    ("КЛАВИАТУРА", "Устройство ввода с клавишами"),
    ("ПЕРЕМЕННАЯ", "Именованная область памяти для хранения значения"),
    ("СЕРВЕР", "Компьютер, обрабатывающий запросы клиентов"),
]
MAX_MISTAKES = 6
REWARD_COINS = 30


class GuessWordStates(StatesGroup):
    playing = State()


class GuessWordHandlers:
    
    def __init__(self, router: Router, db: Database): 
        self.router = router
        self.db = db  
        self.register()


    @staticmethod
    def _render_word(word: str, opened: set[str]) -> str:
        return " ".join(ch if ch in opened else "_" for ch in word)

    async def cmd_guess_word(self, message: Message, state: FSMContext) -> None:
        player = await self.db.get_player(message.from_user.id)
        if player is None:
            await message.answer("Пользователь не найден, используйте /start.")
            return

        # При желании можно брать слово из БД: word, hint = await self.db.get_random_word()
        word, hint = random.choice(FALLBACK_WORDS)
        opened: set[str] = set()

        await state.set_state(GuessWordStates.playing)
        await state.update_data(
            word=word,
            hint=hint,
            opened=list(opened),
            mistakes_left=MAX_MISTAKES,
        )

        await message.answer(
            f"🔤 Угадай слово!\n"
            f"Подсказка: <i>{hint}</i>\n\n"
            f"<code>{self._render_word(word, opened)}</code>\n\n"
            f"Ошибок до поражения: <b>{MAX_MISTAKES}</b>.\n"
            f"Отправь одну букву или слово целиком:",
            parse_mode="HTML",
        )

    async def process_word_input(self, message: Message, state: FSMContext) -> None:
        if not message.text:
            await message.answer("Введите букву или слово текстом.")
            return

        guess = message.text.strip().upper().replace("Ё", "Е")
        data = await state.get_data()
        word: str = data["word"]
        hint: str = data["hint"]
        opened: set[str] = set(data["opened"])
        mistakes_left: int = data["mistakes_left"]

        # Попытка назвать слово целиком
        if len(guess) > 1:
            if guess == word:
                await state.clear()
                # await self.db.add_coins(message.from_user.id, REWARD_COINS)
                await message.answer(
                    f"🏆 Верно! Загаданное слово — <b>{word}</b>. Награда: <b>{REWARD_COINS}</b> монет!",
                    parse_mode="HTML",
                )
                return
            mistakes_left -= 1
            if mistakes_left <= 0:
                await state.clear()
                await message.answer(
                    f"😔 Ошибки закончились. Слово было: <b>{word}</b>. Сыграем ещё: /guess_word",
                    parse_mode="HTML",
                )
                return
            await state.update_data(mistakes_left=mistakes_left)
            await message.answer(
                f"❌ Не то слово. Осталось ошибок: <b>{mistakes_left}</b>.\n"
                f"<code>{self._render_word(word, opened)}</code>",
                parse_mode="HTML",
            )
            return

        # Ввод одной буквы
        if not guess.isalpha():
            await message.answer("Пожалуйста, введите букву.")
            return

        if guess in opened:
            await message.answer("Эту букву уже открывали, попробуй другую.")
            return

        if guess in word:
            opened.add(guess)
            if set(word).issubset(opened):
                await state.clear()
                # await self.db.add_coins(message.from_user.id, REWARD_COINS)
                await message.answer(
                    f"🎉 Ты открыл всё слово: <b>{word}</b>! Награда: <b>{REWARD_COINS}</b> монет!",
                    parse_mode="HTML",
                )
                return
            await state.update_data(opened=list(opened))
            await message.answer(
                f"✅ Есть такая буква!\n<code>{self._render_word(word, opened)}</code>",
                parse_mode="HTML",
            )
        else:
            mistakes_left -= 1
            if mistakes_left <= 0:
                await state.clear()
                await message.answer(
                    f"😔 Ошибки закончились. Слово было: <b>{word}</b>. Новый раунд: /guess_word",
                    parse_mode="HTML",
                )
                return
            await state.update_data(mistakes_left=mistakes_left)
            await message.answer(
                f"❌ Буквы <b>{guess}</b> нет. Осталось ошибок: <b>{mistakes_left}</b>.\n"
                f"<code>{self._render_word(word, opened)}</code>",
                parse_mode="HTML",
            )

    def register(self) -> None:
        self.router.message.register(self.cmd_guess_word, Command("guess_word"))
        self.router.message.register(self.process_word_input, GuessWordStates.playing)

