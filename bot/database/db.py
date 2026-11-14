import aiosqlite


class DataBase:
    def __init__(self, db_name: str = 'game_base.db'):
        self.db_name = db_name
        self.conn = None

    async def connect(self):
        """Открывает соединение с БД"""
        self.conn = await aiosqlite.connect(self.db_name)

    async def close(self):
        """Сохраняет изменения и закрывает БД"""
        if self.conn:
            await self.conn.commit()
            await self.conn.close()
            self.conn = None

    async def init_db(self):
        """Создает таблицу и закрывает БД"""
        await self.connect()
        try:
            await self.conn.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    user_id INTEGER PRIMARY KEY,
                    user_name TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    coins INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        finally:
            await self.close()

    async def register_user(self, user_id: int, user_name: str):
        """Регистрирует игрока и сразу закрывает БД"""
        await self.connect()
        try:
            await self.conn.execute(
                'INSERT OR IGNORE INTO players (user_id, user_name) VALUES (?, ?)',
                (user_id, user_name)
            )
        finally:
            await self.close()
