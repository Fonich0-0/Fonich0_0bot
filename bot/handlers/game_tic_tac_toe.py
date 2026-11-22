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

router_ttt = Router()

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # строки
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # столбцы
    (0, 4, 8), (2, 4, 6),             # диагонали
]
REWARD_COINS = 20


class TTTStates(StatesGroup):
    playing = State()


class TicTacToeHandlers:
    def __init__(self, router: Router, db: Database):
        self.router = router
        self.db = Database()
        self.register()

    @staticmethod
    def _render_board(board: list[str]) -> str:
        cells = []
        for idx, val in enumerate(board, start=1):
            if val == "X":
                cells.append("❌")
            elif val == "O":
                cells.append("⭕")
            else:
                cells.append(f"{idx}️⃣")
        rows = [
            f"{cells[0]} {cells[1]} {cells[2]}",
            f"{cells[3]} {cells[4]} {cells[5]}",
            f"{cells[6]} {cells[7]} {cells[8]}",
        ]
        return "\n".join(rows)

    @staticmethod
    def _check_winner(board: list[str]) -> str | None:
        for a, b, c in WIN_LINES:
            if board[a] != "" and board[a] == board[b] == board[c]:
                return board[a]
        if "" not in board:
            return "DRAW"
        return None

    @staticmethod
    def _bot_move(board: list[str]) -> int:
        free = [i for i, v in enumerate(board) if v == ""]
        # Сначала пробуем выиграть или заблокировать X
        for mark in ("O", "X"):
            for pos in free:
                copy = board[:]
                copy[pos] = mark
                if TicTacToeHandlers._check_winner(copy) == mark:
                    return pos
        if 4 in free:
            return 4
        return random.choice(free)

    async def _start_game(self, message: Message, state: FSMContext, mode: str) -> None:
        player = await self.db.get_player(message.from_user.id)
        if player is None:
            await message.answer("Пользователь не найден, используйте /start.")
            return

        board = [""] * 9
        await state.set_state(TTTStates.playing)
        await state.update_data(board=board, mode=mode, turn="X")

        mode_label = "против бота" if mode == "bot" else "с другом (передача хода)"
        await message.answer(
            f"🎮 Крестики-нолики (<b>{mode_label}</b>)\n\n"
            f"{self._render_board(board)}\n\n"
            f"Ход <b>❌ (X)</b>. Введи номер клетки (1–9):",
            parse_mode="HTML",
        )

    async def cmd_ttt_bot(self, message: Message, state: FSMContext) -> None:
        await self._start_game(message, state, mode="bot")

    async def cmd_ttt_friend(self, message: Message, state: FSMContext) -> None:
        await self._start_game(message, state, mode="friend")

    async def process_move(self, message: Message, state: FSMContext) -> None:
        if not message.text or not message.text.strip().isdigit():
            await message.answer("Введите номер свободной клетки от 1 до 9.")
            return

        cell = int(message.text.strip()) - 1
        if not (0 <= cell <= 8):
            await message.answer("Номер клетки должен быть от 1 до 9.")
            return

        data = await state.get_data()
        board: list[str] = data["board"]
        mode: str = data["mode"]
        turn: str = data["turn"]

        if board[cell] != "":
            await message.answer("Эта клетка уже занята, выбери другую.")
            return

        board[cell] = turn
        result = self._check_winner(board)

        if result:
            await state.clear()
            outcome_text = (
                "🤝 Ничья!"
                if result == "DRAW"
                else f"🏆 Победил <b>{'❌ (X)' if result == 'X' else '⭕ (O)'}</b>!"
            )
            if mode == "bot" and result == "X":
                # await self.db.add_coins(message.from_user.id, REWARD_COINS)
                outcome_text += f"\nНаграда: <b>{REWARD_COINS}</b> монет."

            await message.answer(
                f"{self._render_board(board)}\n\n{outcome_text}",
                parse_mode="HTML",
            )
            return

        if mode == "bot":
            bot_pos = self._bot_move(board)
            board[bot_pos] = "O"
            bot_result = self._check_winner(board)

            if bot_result:
                await state.clear()
                if bot_result == "DRAW":
                    msg = "🤝 Ничья!"
                elif bot_result == "X":
                    # await self.db.add_coins(message.from_user.id, REWARD_COINS)
                    msg = f"🎉 Ты победил бота и получил <b>{REWARD_COINS}</b> монет!"
                else:
                    msg = "🤖 Бот победил! Попробуй ещё: /ttt_bot"

                await message.answer(
                    f"{self._render_board(board)}\n\n{msg}",
                    parse_mode="HTML",
                )
                return

            await state.update_data(board=board, turn="X")
            await message.answer(
                f"Бот сходил на клетку {bot_pos + 1}.\n\n"
                f"{self._render_board(board)}\n\n"
                f"Твой ход <b>❌ (X)</b> (1–9):",
                parse_mode="HTML",
            )
        else:
            next_turn = "O" if turn == "X" else "X"
            await state.update_data(board=board, turn=next_turn)
            await message.answer(
                f"{self._render_board(board)}\n\n"
                f"Ход передан! Теперь ходит <b>{'⭕ (O)' if next_turn == 'O' else '❌ (X)'}</b> (1–9):",
                parse_mode="HTML",
            )

    def register(self) -> None:
        self.router.message.register(self.cmd_ttt_bot, Command("ttt_bot"))
        self.router.message.register(self.cmd_ttt_friend, Command("ttt_friend"))
        self.router.message.register(self.process_move, TTTStates.playing)

