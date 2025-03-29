# bot/main.py
import telebot
from bot.config import BOT_TOKEN
from bot.handlers.handlers_user import register_handlers_user
from bot.handlers.handlers_admin import register_handlers_admin
from controller.queries import create_first_database

bot = telebot.TeleBot(BOT_TOKEN)

# Registra los handlers con el bot
register_handlers_admin(bot)
register_handlers_user(bot)
create_first_database()

def start_bot():
    """Inicia el bot en modo polling."""
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error en el bot: {e}")

if __name__ == '__main__':
    start_bot()