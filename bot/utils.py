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