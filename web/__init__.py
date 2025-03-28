# web/__init__.py
from flask import Flask
from dotenv import load_dotenv

load_dotenv()  # Carga variables de entorno

app = Flask(__name__)
app.config.from_object('web.config')

# Importa las rutas después de crear el objeto app
from web import routes
