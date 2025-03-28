import threading
import time
from bot import main as bot_main
from web import app
from waitress import serve
from dotenv import load_dotenv
import os


def run_bot():
    print("Bot iniciado...")
    bot_main.start_bot()  # Función que inicia el bot

def run_web():
    load_dotenv()
    # Obtener las variables de entorno
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")
    # Ejecutar la aplicación Flask usando Waitress
    print("Web iniciada...")
    serve(app, HOST, PORT)

def monitor_threads(threads):
    while True:
        for name, thread, target in threads:
            if not thread.is_alive():
                print(f"[ERROR] El hilo '{name}' se detuvo. Reiniciando...")
                new_thread = threading.Thread(target=target, name=name)
                threads.remove((name, thread, target))
                threads.append((name, new_thread, target))
                new_thread.start()
        time.sleep(1)  # Evitar un uso excesivo de CPU

if __name__ == '__main__':
    while True:  # Bucle infinito para reiniciar la aplicación en caso de fallo
        try:
            threads = []
            bot_thread = threading.Thread(target=run_bot, name="BotThread")
            web_thread = threading.Thread(target=run_web, name="WebThread")

            threads.append(("BotThread", bot_thread, run_bot))
            threads.append(("WebThread", web_thread, run_web))

            bot_thread.start()
            web_thread.start()
            monitor_threads(threads)

        except Exception as e:
            print(f"[CRITICAL ERROR] La aplicación falló con el error: {e}")
            print("Reiniciando la aplicación en 5 segundos...")
            time.sleep(5)  # Esperar antes de reiniciar