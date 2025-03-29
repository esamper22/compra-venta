import os

def generate_key_value():
    import secrets
    # Generar una clave secreta de 24 bytes en formato hexadecimal
    return secrets.token_hex(24)

if __name__ == '__main__':
    print(generate_key_value())