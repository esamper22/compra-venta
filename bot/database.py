# bot/database.py
import json
import os
from datetime import datetime, timedelta

from bot.utils import generate_password

DB_FILE = 'database.json'

def load_database():
    """Carga la base de datos, si no existe la crea con una estructura inicial."""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as db:
            json.dump({"usuarios": []}, db, indent=4)
    with open(DB_FILE, 'r') as db:
        return json.load(db)

def save_database(data):
    """Guarda la base de datos en formato JSON."""
    with open(DB_FILE, 'w') as db:
        json.dump(data, db, indent=4)

def create_first_user(user_id, username):
    """Guarda solo el ID y nombre de usuario en la base de datos."""
    data = load_database()
    user = next((u for u in data["usuarios"] if u["user_id"] == user_id), None)
    
    if not user:
        user = {
            "user_id": user_id,
            "username": username,
            "plan": "basico",
            "publicaciones": [],
            "mensajes_programados": [],
            "rol": "usuario",
            "solicitud": "no enviada",
            'notificado': False
        }
        data["usuarios"].append(user)
        save_database(data)
        return True # Usuario creado con éxito
    return False # Usuario ya existente

def upgrade_user_to_premium(user_chat_id):
    """Actualiza un usuario al plan premium o lo inicializa si no existe."""
    data = load_database()
    user = next((u for u in data["usuarios"] if u["user_id"] == user_chat_id), None)
    
    fecha_inicio = datetime.now()
    fecha_fin = fecha_inicio + timedelta(days=30)
    
    
    user["plan"] = "premium"
    user["dias_plan"] = 30
    user["password"] = generate_password()
    user["fecha_inicio"] = fecha_inicio.strftime("%Y-%m-%d")
    user["solicitud"] = "aceptada"
    user["fecha_fin"] = fecha_fin.strftime("%Y-%m-%d")

    save_database(data)
    return user

def account_premium(user_chat_id):
    """Verifica si un usuario es premium."""
    data = load_database()
    user = next((u for u in data["usuarios"] if u["user_id"] == user_chat_id), None)
    
    if user:
        return user["plan"] == "premium"
    return False

def get_user_id(user_chat_id):
    """Obtiene el ID de un usuario."""
    data = load_database()
    user = next((u for u in data["usuarios"] if u["user_id"] == user_chat_id), None)
    
    if user: return user
    return None

def update_user(user_id, update_data):
    """
    Actualiza los datos de un usuario en la base de datos.
    
    Parámetros:
      - user_id: ID del usuario a actualizar.
      - update_data: Diccionario con los campos a actualizar, por ejemplo {"rol": "admin"}.
    """
    data = load_database()
    for user in data["usuarios"]:
        if user["user_id"] == user_id:
            user.update(update_data)
            break
    save_database(data)

def get_day_expiration(user_chat_id):
    """Obtiene los días restantes de un usuario premium."""
    data = load_database()
    user = next((u for u in data["usuarios"] if u["user_id"] == user_chat_id), None)
    
    if user["plan"] == "premium":
        fecha_fin = datetime.strptime(user["fecha_fin"], "%Y-%m-%d")
        dias_restantes = (fecha_fin - datetime.now()).days
        return dias_restantes
    else:
        return 0