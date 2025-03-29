import json
import os
from datetime import datetime, timedelta
from bot.utils import generate_password
from bot.config import SUPER_ADMIN
from dotenv import load_dotenv

load_dotenv()
# Ruta del archivo JSON que actuará como "base de datos"
DB_FILE = os.getenv("DATABASE_NAME", 'db.json')


def load_database():
    """
    Carga la base de datos desde el archivo JSON.
    
    Si el archivo no existe, lo crea con una estructura inicial.
    
    Retorna:
        dict: Contenido del archivo JSON.
    """
    if not os.path.exists(DB_FILE):
        # Si no existe, se crea un archivo con la estructura inicial
        with open(DB_FILE, 'w') as db:
            json.dump({"usuarios": []}, db, indent=4)
    # Se abre el archivo en modo lectura y se devuelve el contenido en formato dict
    with open(DB_FILE, 'r') as db:
        return json.load(db)


def save_database(data):
    """
    Guarda los datos en el archivo JSON.
    
    Parámetros:
        data (dict): Datos a guardar.
    """
    with open(DB_FILE, 'w') as db:
        json.dump(data, db, indent=4)


def create_first_database():
    if not os.path.exists(DB_FILE):
        # Si no existe, se crea un archivo con la estructura inicial
        with open(DB_FILE, 'w') as db:
            json.dump({"superadmin":SUPER_ADMIN, "usuarios": []}, db, indent=4)


def create_first_user(user_id, username):
    """
    Crea un usuario en la base de datos si no existe ya.
    
    Parámetros:
        user_id (int): Identificador único del usuario (por ejemplo, su ID de Telegram).
        username (str): Nombre de usuario.
        
    Retorna:
        bool: True si se creó el usuario, False si ya existía.
    """
    data = load_database()
    # Busca si el usuario ya existe en la base de datos
    user = next((u for u in data["usuarios"] if u["user_id"] == user_id), None)
    
    if not user:
        # Estructura inicial del usuario
        user = {
            "user_id": user_id,
            "username": username,
            "plan": "basico",                # Plan por defecto
            "publicaciones": [],             # Lista para publicaciones
            "mensajes_programados": [],      # Lista para mensajes programados
            "rol": "usuario",                # Rol predeterminado: usuario
            "solicitud": "no enviada",       # Estado de solicitud para plan premium
            "notificado": False  ,            # Indicador para evitar notificaciones múltiples
        }
        data["usuarios"].append(user)
        save_database(data)
        return True  # Usuario creado con éxito
    return False  # Usuario ya existente


def upgrade_user_to_premium(user_chat_id):
    """
    Actualiza un usuario al plan premium, asignándole 30 días de servicio.
    
    Parámetros:
        user_chat_id (int): ID del usuario (por ejemplo, su ID de Telegram).
    
    Retorna:
        dict: Datos del usuario actualizado.
    """
    data = load_database()
    user = next((u for u in data["usuarios"] if u["user_id"] == user_chat_id), None)
    
    if user:
        fecha_inicio = datetime.now()
        fecha_fin = fecha_inicio + timedelta(days=30)
        
        # Actualizar la información del usuario
        user["plan"] = "premium"
        user["dias_plan"] = 30
        user["password"] = generate_password()  # Genera una contraseña aleatoria
        user["fecha_inicio"] = fecha_inicio.strftime("%Y-%m-%d")
        user["fecha_fin"] = fecha_fin.strftime("%Y-%m-%d")
        user["solicitud"] = "aceptada"  # Marca la solicitud como aceptada
        
        save_database(data)
        return user
    else:
        # Si el usuario no existe, se podría decidir crearlo o retornar None
        return None


def account_premium(user_chat_id):
    """
    Verifica si un usuario tiene el plan premium.
    
    Parámetros:
        user_chat_id (int): ID del usuario.
    
    Retorna:
        bool: True si el usuario es premium, False de lo contrario.
    """
    data = load_database()
    user = next((u for u in data["usuarios"] if u["user_id"] == user_chat_id), None)
    if user:
        return user["plan"] == "premium"
    return False


def get_user_id(user_chat_id):
    """
    Obtiene el diccionario completo del usuario a partir de su ID.
    
    Parámetros:
        user_chat_id (int): ID del usuario.
    
    Retorna:
        dict o None: Datos del usuario si existe, de lo contrario None.
    """
    data = load_database()
    user = next((u for u in data["usuarios"] if u["user_id"] == user_chat_id), None)
    return user  # Retorna el usuario o None si no se encontró


def update_user(user_id, update_data):
    """
    Actualiza los datos de un usuario en la base de datos.
    
    Parámetros:
        user_id (int): ID del usuario a actualizar.
        update_data (dict): Diccionario con los campos a actualizar. Ejemplo: {"rol": "admin"}.
    """
    data = load_database()
    for user in data["usuarios"]:
        if user["user_id"] == user_id:
            user.update(update_data)
            break
    save_database(data)


def get_admins():
    data = load_database()
    return [u.get("user_id") for u in data["usuarios"] if u.get("rol") == "admin"]


def check_is_admin():
    id_superadmin = load_database()["superadmin"].get("user_id")
    data = load_database()
    ids_admin = [u.get("user_id") for u in data["usuarios"] if u.get("rol") == "admin"]
    return [id_superadmin] + ids_admin

    
def get_day_expiration(user_chat_id):
    """
    Calcula los días restantes antes de que expire el plan premium del usuario.
    
    Parámetros:
        user_chat_id (int): ID del usuario.
    
    Retorna:
        int: Número de días restantes; 0 si el usuario no es premium o si ya expiró.
    """
    data = load_database()
    user = next((u for u in data["usuarios"] if u["user_id"] == user_chat_id), None)
    if user and user["plan"] == "premium":
        # Convertir la fecha de fin en objeto datetime
        fecha_fin = datetime.strptime(user["fecha_fin"], "%Y-%m-%d")
        dias_restantes = (fecha_fin - datetime.now()).days
        return dias_restantes if dias_restantes > 0 else 0
    return 0
