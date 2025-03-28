# bot/main.py
import telebot
from .config import BOT_TOKEN
from .handlers.handlers_user import register_handlers_user
from .handlers.handlers_admin import register_handlers_admin

bot = telebot.TeleBot(BOT_TOKEN)

# Registra los handlers con el bot
register_handlers_admin(bot)
register_handlers_user(bot)

def start_bot():
    """Inicia el bot en modo polling."""
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error en el bot: {e}")
        # Aquí podrías implementar un reinicio o manejo de errores más robusto

if __name__ == '__main__':
    start_bot()