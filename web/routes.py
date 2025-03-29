# web/routes.py
from flask import render_template, request, redirect, url_for, flash

from controller.queries import load_database
from . import app
from flask import session

@app.route('/')
def index():
    """Página de inicio de la mini app."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta para el inicio de sesión."""
    
    if 'username' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        data = load_database()
        data_admin = data["superadmin"]
        
        usuario = next((u for u in data["usuarios"] if u.get("username") == username and u.get("password") == password), None)
        is_super_admin = username == data_admin.get("username") and password == data_admin.get("password")
        
    
        if usuario or is_super_admin:
            flash("Inicio de sesión exitoso", "success")
            # Iniciar la sesión del usuario utilizando Flask session.
            session['username'] = usuario.get("username") if usuario else data_admin.get("username")
            return redirect(url_for('dashboard'))
        else:
            flash("Credenciales incorrectas", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Ruta para cerrar sesión."""
    session.clear()  # Limpiar la sesión del usuario.
    flash("Has cerrado sesión exitosamente.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Ruta para el dashboard del usuario autenticado."""
    # Verificar si el usuario está autenticado.
    if 'username' not in session:
        flash("Debes iniciar sesión para acceder al dashboard.", "danger")
        return redirect(url_for('login'))
    return render_template('dashboard.html')
