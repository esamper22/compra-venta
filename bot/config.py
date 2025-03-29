# bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno definidas en .env

BOT_TOKEN = os.getenv('BOT_TOKEN')
# URL de tu API en PythonAnywhere
BASE_URL = os.getenv('BASE_URL')

SUPER_ADMIN = super_admin = {
    "user_id": int(os.getenv("SUPER_ADMIN_USER_ID")),
    "username": os.getenv("SUPER_ADMIN_USERNAME"),
    "plan": os.getenv("SUPER_ADMIN_PLAN"),
    "publicaciones": eval(os.getenv("SUPER_ADMIN_PUBLICACIONES")),  # Ten cuidado con eval
    "mensajes_programados": eval(os.getenv("SUPER_ADMIN_MENSAJES_PROGRAMADOS")),  # Ten cuidado con eval
    "rol": os.getenv("SUPER_ADMIN_ROL"),
}


if not BOT_TOKEN:
    raise ValueError("No se encontró el BOT_TOKEN en las variables de entorno.")
