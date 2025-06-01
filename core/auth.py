# ./core/auth.py
# Sistema de autenticación para Dash usando Flask sessions y JWT

import json
import os
import hashlib
import logging
from pathlib import Path
from dotenv import load_dotenv
from flask import session, request, redirect
from functools import wraps

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logger = logging.getLogger(__name__)

# Obtener credenciales de administrador desde .env
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

def hash_password(password):
    """Generar hash seguro de contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, password):
    """Verificar si una contraseña coincide con el hash almacenado."""
    return stored_hash == hash_password(password)



class AuthManager:
    def __init__(self):
        """Inicializar gestor de autenticación."""
        self.data_dir = Path(__file__).resolve().parent.parent / 'data'
        self.users_file = self.data_dir / 'users.json'
        self.users = self._load_users()
        
    def _load_users(self):
        """Cargar usuarios del archivo JSON o crear uno nuevo si no existe."""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                    
                # Verificar si las contraseñas están en texto plano y convertirlas a hash
                updated = False
                for username, password in list(users_data.items()):
                    # Si la contraseña no parece un hash SHA-256 (64 caracteres hex)
                    if not (len(password) == 64 and all(c in '0123456789abcdef' for c in password)):
                        # Convertir a hash
                        users_data[username] = hash_password(password)
                        updated = True
                        logger.warning(f"Contraseña en texto plano detectada para {username}. Convertida a hash.")
                
                if updated:
                    self._save_users(users_data)
                    
                return users_data
            else:
                # Crear admin por defecto usando credenciales del .env
                default_users = {
                    ADMIN_USERNAME: hash_password(ADMIN_PASSWORD)
                }
                self._save_users(default_users)
                return default_users
                
        except Exception as e:
            logger.error(f"Error cargando usuarios: {e}")
            # En caso de error, crear un archivo nuevo
            default_users = {
                ADMIN_USERNAME: hash_password(ADMIN_PASSWORD)
            }
            self._save_users(default_users)
            return default_users
            
    def _save_users(self, users_data):
        """Guardar usuarios en el archivo JSON."""
        try:
            # Asegurar que existe el directorio
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            # Guardar usuarios
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error guardando usuarios: {e}")
            return False
            
    def authenticate(self, username, password):
        """Verificar credenciales de usuario."""
        if username in self.users:
            stored_hash = self.users[username]
            return verify_password(stored_hash, password)
        return False
        
    def add_user(self, username, password):
        """Añadir un nuevo usuario."""
        if username in self.users:
            return False, "El usuario ya existe"
            
        if not username or not password:
            return False, "Usuario y contraseña son obligatorios"
            
        self.users[username] = hash_password(password)
        success = self._save_users(self.users)
        
        if success:
            return True, f"Usuario {username} creado correctamente"
        else:
            return False, "Error guardando el usuario"
            
    def delete_user(self, username):
        """Eliminar un usuario."""
        if username not in self.users:
            return False, "El usuario no existe"
            
        # No permitir eliminar al administrador
        if username == ADMIN_USERNAME:
            return False, "No se puede eliminar el usuario administrador"
            
        del self.users[username]
        success = self._save_users(self.users)
        
        if success:
            return True, f"Usuario {username} eliminado correctamente"
        else:
            return False, "Error eliminando el usuario"
            
    def get_users(self):
        """Obtener la lista de usuarios."""
        return list(self.users.keys())
        
    def is_admin(self, username):
        """Verificar si un usuario es administrador."""
        return username == ADMIN_USERNAME

# Instancia global del AuthManager
auth_manager = AuthManager()

def is_authenticated():
    """Verificar si el usuario actual está autenticado."""
    return 'authenticated' in session and session['authenticated']

def get_current_user():
    """Obtener el usuario actual autenticado."""
    if is_authenticated():
        return session.get('username')
    return None

def login_user(username, password):
    """Intentar hacer login con credenciales."""
    if auth_manager.authenticate(username, password):
        # Crear sesión TEMPORAL (no permanente)
        session.permanent = False  # ⭐ CLAVE: sesión temporal
        session['authenticated'] = True
        session['username'] = username
        
        logger.info(f"Usuario {username} autenticado correctamente")
        return True, "Login exitoso"
    else:
        logger.warning(f"Intento de login fallido para usuario: {username}")
        return False, "Usuario o contraseña incorrectos"

def logout_user():
    """Cerrar sesión del usuario actual."""
    username = session.get('username', 'unknown')
    session.clear()
    logger.info(f"Usuario {username} cerró sesión")
    return True

def setup_auth_routes(app):
    """Configurar rutas de autenticación en la app Flask."""
    
    @app.server.route('/login', methods=['GET', 'POST'])
    def login():
        """Ruta de login."""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            success, message = login_user(username, password)
            if success:
                return redirect('/')
            else:
                return f"""
                <html><body>
                <h2>Error: {message}</h2>
                <a href="/login">Volver a intentar</a>
                </body></html>
                """
        
        # Mostrar formulario de login
        return """
        <html>
        <head>
            <title>Login - RAG Demo</title>
            <style>
                body { font-family: Arial; max-width: 400px; margin: 100px auto; padding: 20px; }
                input { width: 100%; padding: 10px; margin: 10px 0; }
                button { width: 100%; padding: 12px; background: #007cba; color: white; border: none; cursor: pointer; }
                button:hover { background: #005a8b; }
                .form-group { margin: 15px 0; }
                h2 { text-align: center; color: #333; }
            </style>
        </head>
        <body>
            <h2>🔐 Acceso al Sistema RAG</h2>
            <form method="post">
                <div class="form-group">
                    <input type="text" name="username" placeholder="Usuario" required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" placeholder="Contraseña" required>
                </div>
                <button type="submit">Iniciar Sesión</button>
            </form>
        </body>
        </html>
        """
    
    @app.server.route('/logout')
    def logout():
        """Ruta de logout."""
        logout_user()
        return redirect('/login')
    
    # Middleware para proteger todas las rutas excepto login
    @app.server.before_request
    def require_login():
        """Middleware que requiere autenticación para todas las rutas excepto login."""
        if request.endpoint and request.endpoint in ['login', 'logout']:
            return  # Permitir acceso a rutas de auth
        
        if not is_authenticated():
            return redirect('/login')

def get_login_layout():
    """Layout alternativo para mostrar cuando no está autenticado."""
    from dash import html, dcc
    
    return html.Div([
        html.Div([
            html.H2("🔐 Acceso Requerido", style={'textAlign': 'center', 'color': '#333'}),
            html.P("Debes iniciar sesión para acceder a esta aplicación.", 
                   style={'textAlign': 'center', 'color': '#666'}),
            html.Div([
                html.A("Ir al Login", 
                       href="/login",
                       style={
                           'display': 'inline-block',
                           'padding': '12px 24px',
                           'backgroundColor': '#007cba',
                           'color': 'white',
                           'textDecoration': 'none',
                           'borderRadius': '4px',
                           'fontWeight': 'bold'
                       })
            ], style={'textAlign': 'center', 'marginTop': '20px'})
        ], style={
            'maxWidth': '400px',
            'margin': '100px auto',
            'padding': '40px',
            'border': '1px solid #ddd',
            'borderRadius': '8px',
            'boxShadow': '0 2px 10px rgba(0,0,0,0.1)'
        })
    ], style={'backgroundColor': '#f5f5f5', 'minHeight': '100vh'})