import os
from dotenv import load_dotenv

# Загружаем данные из файла .env 
load_dotenv()

# Достаем токен в обычную переменную
BOT_TOKEN = os.getenv("BOT_TOKEN")

