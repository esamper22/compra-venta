import threading
import time
from bot import main as bot_main
from web import app
from dotenv import load_dotenv
import os

# Cargar variables de entorno al inicio
load_dotenv()

def run_bot():
    print("Bot iniciado...")
    bot_main.start_bot()  # Función que inicia el bot

def run_web():
    # Obtener las variables de entorno
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))  # Asegurar que sea un entero
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    print(f"Iniciando web en {HOST}:{PORT} (debug={DEBUG})")
    app.run(host=HOST, port=PORT, debug=DEBUG)  # Configurable desde .env

def monitor_threads(threads):
    while True:
        threads_to_restart = []

        for name, thread, target in threads:
            if not thread.is_alive():
                print(f"[ERROR] El hilo '{name}' se detuvo. Reiniciando...")
                new_thread = threading.Thread(target=target, name=name)
                threads_to_restart.append((name, new_thread, target))

        # Reiniciar hilos fuera del bucle para evitar modificar `threads` mientras se itera
        for item in threads_to_restart:
            threads.remove(next(t for t in threads if t[0] == item[0]))  # Remover el hilo caído
            threads.append(item)
            item[1].start()  # Iniciar el nuevo hilo

        time.sleep(1)  # Evitar uso excesivo de CPU

if __name__ == '__main__':
    while True:  # Bucle infinito para reiniciar la aplicación en caso de fallo
        try:
            threads = [
                ("BotThread", threading.Thread(target=run_bot, name="BotThread"), run_bot),
                ("WebThread", threading.Thread(target=run_web, name="WebThread"), run_web)
            ]

            # Iniciar hilos
            for _, thread, _ in threads:
                thread.start()

            monitor_threads(threads)  # Monitoreo y reinicio de hilos

        except Exception as e:
            print(f"[CRITICAL ERROR] La aplicación falló con el error: {e}")
            print("Reiniciando la aplicación en 5 segundos...")
            time.sleep(5)  # Esperar antes de reiniciar
