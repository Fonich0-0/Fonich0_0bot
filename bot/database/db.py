import asyncpg


class Database:

  def __init__(self, dsn: str):
    self.dsn = dsn
    self.pool: asyncpg.Pool | None = None

  async def connect(self):
    """Создает пул соединений при старте бота"""
    self.pool = await asyncpg.create_pool(
        dsn=self.dsn, min_size=1, max_size=5, max_inactive_connection_lifetime=30
    )

  async def close(self):
    """Закрывает пул при остановке"""
    if self.pool:
      await self.pool.close()

  async def init_db(self):
    """Создает таблицу игроков (вызывается 1 раз при запуске)"""
    async with self.pool.acquire() as conn:
      await conn.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    user_id BIGINT PRIMARY KEY,
                    user_name TEXT NOT NULL,
                    user_age INT,
                    user_region TEXT,
                    level INTEGER DEFAULT 1,
                    coins INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

  async def register_user(self, user_id: int, user_name: str):
    """Регистрирует игрока"""
    async with self.pool.acquire() as conn:
      await conn.execute(
          """
                INSERT INTO players (user_id, user_name) 
                VALUES ($1, $2) 
                ON CONFLICT (user_id) DO NOTHING
            """,
          user_id,
          user_name,
      )

  async def get_player(self, user_id: int) -> tuple | None:
    """Возвращает кортеж (user_name, coins, level) или None"""
    async with self.pool.acquire() as conn:
      row = await conn.fetchrow(
          """
                SELECT user_name, coins, level 
                FROM players 
                WHERE user_id = $1
            """,
          user_id,
      )
      if row is None:
        return None
      return (row["user_name"], row["coins"], row["level"])
