# bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno definidas en .env

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
if not BOT_TOKEN:
    raise ValueError("No se encontró el BOT_TOKEN en las variables de entorno.")
