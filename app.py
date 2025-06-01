# ./app.py
# Entry point de la aplicación Dash: layout principal y registro de callbacks
import os
import logging
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from components.upload_component import upload_component
from components.ocr_selector import ocr_selector
from components.llm_selector import llm_selector
from components.progress_bar import progress_bar
from components.graph_view import graph_view
from components.embedding_view import embedding_view

from callbacks.ocr_callbacks import register_ocr_callbacks
from callbacks.llm_callbacks import register_llm_callbacks
from callbacks.graph_callbacks import register_graph_callbacks
from callbacks.embedding_callbacks import register_embedding_callbacks

# ⭐ IMPORTAR SISTEMA DE AUTENTICACIÓN ⭐
from core.auth import setup_auth_routes, is_authenticated, get_current_user, get_login_layout

# ⭐ CONFIGURACIÓN DE LOGS PARA PRODUCCIÓN ⭐
if os.environ.get("RAILWAY_ENVIRONMENT_NAME"):  # Detecta Railway
    logging.basicConfig(
        level=logging.WARNING,  # Solo warnings y errores
        format='%(levelname)s: %(message)s'
    )
else:
    logging.basicConfig(
        level=logging.DEBUG,    # Todo en local
        format='%(levelname)s: %(message)s'
    )

app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR], suppress_callback_exceptions=True)

# ⭐ LÍNEA CRÍTICA PARA DEPLOYMENT ⭐
server = app.server

# ⭐ CONFIGURAR CLAVE SECRETA PARA FLASK SESSIONS ⭐
server.secret_key = os.environ.get('FLASK_SECRET_KEY', 'cambiar_en_produccion_clave_secreta_flask')
# ⭐ CONFIGURAR SESIONES TEMPORALES ⭐
server.config['SESSION_COOKIE_HTTPONLY'] = True
server.config['SESSION_COOKIE_SECURE'] = True if os.environ.get('RAILWAY_ENVIRONMENT_NAME') else False
server.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
server.config['PERMANENT_SESSION_LIFETIME'] = 0

# ⭐ CONFIGURAR RUTAS DE AUTENTICACIÓN ⭐
setup_auth_routes(app)

# ---- Layout condicional con autenticación ----
def get_authenticated_layout():
    """Layout principal de la aplicación (requiere autenticación)."""
    current_user = get_current_user()
    
    return dbc.Container([
        # Header con info de usuario y logout
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span(f"👤 Usuario: {current_user}", style={'color': '#666', 'marginRight': '20px'}),
                    html.A("Cerrar Sesión", href="/logout", 
                          style={'color': '#dc3545', 'textDecoration': 'none', 'fontWeight': 'bold'})
                ], style={'textAlign': 'right', 'padding': '10px 0', 'borderBottom': '1px solid #eee'})
            ], width=12)
        ]),
        
        # Layout principal
        dbc.Row([
            dbc.Col([
                html.H2("RAG Demo - Knowledge Graph Extraction", style={'color': 'black'}),
                html.Hr(),
                upload_component(),
                ocr_selector(),
                llm_selector(),
                progress_bar(),
                html.Button("Reset Pinecone", id="btn-reset-pinecone", n_clicks=0, style={
                    "margin": "8px 0", "background": "#e11d48", "color": "white", "borderRadius": "8px"
                }),
            ], width=3, style={"backgroundColor": "#f8fafc", "padding": "16px", "borderRadius": "12px", "minHeight": "96vh"}),
            dbc.Col([
                graph_view(),
                html.Div(id="embedding-panel", style={"marginTop": "32px"})
            ], width=9, style={"padding": "24px"})
        ])
    ], fluid=True, style={"background": "#f1f5f9", "minHeight": "100vh"})

def serve_layout():
    """Función que decide qué layout servir según autenticación."""
    if is_authenticated():
        return get_authenticated_layout()
    else:
        return get_login_layout()

# ⭐ ASIGNAR LAYOUT DINÁMICO ⭐
app.layout = serve_layout

# ---- Registro de callbacks ----
register_ocr_callbacks(app)
register_llm_callbacks(app)
register_graph_callbacks(app)
register_embedding_callbacks(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run_server(debug=False, host="0.0.0.0", port=port)