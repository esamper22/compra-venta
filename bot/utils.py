# Funciones auxiliares
# bot/utils.py
import random
import string

def formatear_fecha(fecha_iso):
    """Convierte una fecha ISO a un formato más legible."""
    from datetime import datetime
    fecha = datetime.fromisoformat(fecha_iso)
    return fecha.strftime("%d/%m/%Y %H:%M:%S")

def generate_password(length=8):
        """Genera una contraseña aleatoria."""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

# ================================
# Funciones auxiliares de parsing
# ================================
def parse_id_list(input_text):
    """
    Convierte una cadena de IDs separados por comas en una lista de enteros.
    Ejemplo: "12345,67890,  34567" -> [12345, 67890, 34567]
    """
    try:
        # Separa por comas y limpia espacios
        ids = [int(x.strip()) for x in input_text.split(",") if x.strip().isdigit()]
        return ids
    except Exception as e:
        print("Error en parse_id_list:", e)
        return []

def parse_solicitude_list(input_text):
    """
    Convierte una cadena de solicitudes separadas por comas en una lista de diccionarios.
    Cada elemento debe tener el formato "user_id decision", por ejemplo:
      "12345 A,67890 D" se convierte en:
      [{"user_id": 12345, "decision": "A"}, {"user_id": 67890, "decision": "D"}]
    """
    solicitudes = []
    try:
        # Se separa por comas
        entries = input_text.split(",")
        for entry in entries:
            parts = entry.strip().split()
            if len(parts) != 2 or parts[1] not in ["A", "D"]:
                continue  # Ignora entradas mal formateadas
            solicitudes.append({"user_id": int(parts[0]), "decision": parts[1]})
    except Exception as e:
        print("Error en parse_solicitude_list:", e)
    return solicitudes
