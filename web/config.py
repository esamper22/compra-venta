# web/config.py
import os

SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'my_precious')
DEBUG = False  # En producción, DEBUG debe ser False
