import json
import os


DB_FILE = 'database.json'

def load_database():
    """Carga la base de datos JSON, creándola si no existe."""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as db:
            json.dump({"usuarios": []}, db, indent=4)
    with open(DB_FILE, 'r') as db:
        return json.load(db)

def generate_key_value():
    import secrets
    # Generar una clave secreta de 24 bytes en formato hexadecimal
    return secrets.token_hex(24)

if __name__ == '__main__':
    print(generate_key_value())