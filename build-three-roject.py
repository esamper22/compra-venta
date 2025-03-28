import os

def create_file(path, content=""):
    """Crea un archivo con contenido opcional."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_project_structure():
    # Estructura del proyecto
    structure = {
            "bot": {
                "__init__.py": "",
                "config.py": "# Configuraciones específicas para el bot",
                "handlers.py": "# Funciones y comandos del bot",
                "utils.py": "# Funciones auxiliares",
                "database.py": "# Funciones para manejar la base de datos JSON",
                "main.py": "# Punto de entrada del bot",
            },
            "web": {
                "__init__.py": "# Inicializa la aplicación Flask",
                "config.py": "# Configuraciones de Flask",
                "routes.py": "# Definición de rutas y vistas",
                "models.py": "# Modelos de datos",
                "static": {
                    "css": {
                        "style.css": "/* Estilos CSS */"
                    },
                    "js": {
                        "main.js": "// Código JavaScript"
                    },
                    "images": {}
                },
                "templates": {
                    "base.html": "<!-- Template base -->",
                    "index.html": "<!-- Página principal -->"
                }
        },
        ".env": "# Variables de entorno",
        ".gitignore": "__pycache__/\n.env",
        "requirements.txt": "# Flask\n# pyTelegramBotAPI\n# python-dotenv",
        "run.py": "# Script principal para iniciar el bot y la web",
        "README.md": "# Documentación del proyecto"
    }

    def create_structure(base_path, structure):
        for name, content in structure.items():
            path = os.path.join(base_path, name)
            if isinstance(content, dict):
                os.makedirs(path, exist_ok=True)
                create_structure(path, content)
            else:
                create_file(path, content)

    # Crear la estructura
    create_structure(".", structure)

if __name__ == "__main__":
    create_project_structure()