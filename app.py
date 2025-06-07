# ./app.py
# Entry point de la aplicación Dash: layout principal y registro de callbacks

import os
import logging
from dash import Dash, html, dcc, Input, Output, callback_context
import dash_bootstrap_components as dbc
import warnings

# Componentes originales
from components.upload_component import upload_component
from components.ocr_selector import ocr_selector
from components.llm_selector import llm_selector
from components.progress_bar import progress_bar
from components.graph_view import graph_view
from components.embedding_view import embedding_view # Comentado si no se usa directamente en layout

# Callbacks originales
from callbacks.ocr_callbacks import register_ocr_callbacks
from callbacks.llm_callbacks import register_llm_callbacks
from callbacks.graph_callbacks import register_graph_callbacks
from callbacks.embedding_callbacks import register_embedding_callbacks

# ⭐ IMPORTAR SISTEMA DE AUTENTICACIÓN ⭐
from core.auth import setup_auth_routes, is_authenticated, get_current_user, get_login_layout

# ⭐ IMPORTAR LAYOUT DE LA PÁGINA DE CHAT Y SUS CALLBACKS ⭐
from agent.chat_page import layout as chat_page_layout # ASUME QUE ESTÁ EN ./agent/chat_page.py
from callbacks.chat_callbacks import register_chat_callbacks

# ⭐ CONFIGURACIÓN DE LOGS PARA PRODUCCIÓN ⭐
warnings.filterwarnings("ignore", category=RuntimeWarning)
logging.basicConfig(level=logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR], suppress_callback_exceptions=True)

server = app.server

# ⭐ CONFIGURAR CLAVE SECRETA PARA FLASK SESSIONS ⭐
server.secret_key = os.environ.get('FLASK_SECRET_KEY', 'cambiar_en_produccion_clave_secreta_flask')

# ⭐ CONFIGURAR SESIONES TEMPORALES ⭐
server.config['SESSION_COOKIE_EXPIRES'] = None
server.config['SESSION_COOKIE_HTTPONLY'] = True
server.config['SESSION_COOKIE_SECURE'] = True if os.environ.get('RAILWAY_ENVIRONMENT_NAME') else False
server.config['PERMANENT_SESSION_LIFETIME'] = 1800

# ⭐ CONFIGURAR RUTAS DE AUTENTICACIÓN ⭐
setup_auth_routes(app)

# ⭐ LAYOUT DE VALIDACIÓN PARA CALLBACKS DINÁMICOS ⭐
validation_layout = html.Div([
    # Componentes principales
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    
    # Stores globales
    dcc.Store(id='graph-cache', storage_type='session', data={}),
    dcc.Store(id='rag-process-data', storage_type='memory', data={}),
    
    # Componentes de la página principal (grafo)
    html.Div(id='upload-data'),
    html.Div(id='input-url'),
    html.Button(id='process-url-btn', n_clicks=0),
    html.Div(id='ocr-method'),
    html.Div(id='llm-method'),
    html.Div(id='loading-progress'),
    html.Div(id='progress-info'),
    html.Button(id='generate-graph-btn', n_clicks=0),
    html.Button(id='btn-reset-pinecone', n_clicks=0),
    html.Div(id='dynamic-legend'),
    html.Div(id='knowledge-graph'),
    html.Div(id='embedding-panel'),
    
    # Componentes de la página de chat
    html.Div(id='chat-conversation'),
    html.Div(id='chat-status'),
    html.Div(id='rag-process-content'),
    dcc.Input(id='chat-input'),
    html.Button(id='chat-send-btn', n_clicks=0),
    html.Div(id='chat-llm-selector'),
    html.Button(id='show-process-btn', n_clicks=0),
])

# Asignar layout de validación
app.validation_layout = validation_layout


def get_main_layout_content():
    """Layout del contenido de la página principal (procesamiento y grafo)."""
    return dbc.Container([
        dcc.Store(id='graph-cache', storage_type='session', data={}),
        dcc.Store(id='rag-process-data', storage_type='memory', data={}),
        
        dbc.Row([
            dbc.Col([
                html.Hr(),
                upload_component(),
                ocr_selector(),
                llm_selector(),
                progress_bar(),
                html.Button("Reset Pinecone", id="btn-reset-pinecone", n_clicks=0, style={
                    "margin": "8px 0", "background": "#e11d48", "color": "white", "borderRadius": "8px"
                })
            ], width=3, style={"backgroundColor": "#f8fafc", "padding": "16px", "borderRadius": "12px", "minHeight": "calc(100vh - 76px)"}),
            dbc.Col([
                graph_view(),
                html.Div(id="embedding-panel", style={"marginTop": "32px"})
            ], width=9, style={"padding": "24px"}),
            html.Div(id="rag-process-content", style={"display": "none"})  
        ])
    ], fluid=True, style={"background": "#f1f5f9", "minHeight": "calc(100vh - 56px)"})

def get_base_layout_with_navbar():
    """Layout base que incluye la barra de navegación y el contenedor de página."""
    current_user = get_current_user()

    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Procesamiento y Grafo", href="/", className="nav-link-custom")),
            dbc.NavItem(dbc.NavLink("Chat RAG", href="/chat", className="nav-link-custom")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem(f"👤 Usuario: {current_user}", header=True),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Cerrar Sesión", href="/logout", external_link=True),
                ],
                nav=True,
                in_navbar=True,
                label="Cuenta",
                align_end=True,
                toggle_style={
                    "color": "#f5f6fc",
                    "fontWeight": "500",
                    "backgroundColor": "transparent",
                    "border": "none"
                },
                toggleClassName="nav-link-custom",
                menu_variant="dark"
            ),
        ],
        brand="RAG Demo App",
        brand_href="/",
        color="dark",
        dark=True,
        sticky="top",
        className="mb-3"
    )
    return html.Div([
        dcc.Location(id='url', refresh=False),
        navbar,
        html.Div(id='page-content', children=[html.P("Cargando contenido inicial de la página...")])
    ])


def serve_layout():
    """Función que decide qué layout servir según autenticación."""
    if not is_authenticated():
        return get_login_layout()
    else:
        return get_base_layout_with_navbar()

app.layout = serve_layout


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    """Actualiza el contenido de la página basado en la URL."""
    if pathname == '/chat':
        return chat_page_layout()
    elif pathname == '/':
        return get_main_layout_content()
    
    return get_main_layout_content()


# ---- Registro de Callbacks ----
register_ocr_callbacks(app)
register_llm_callbacks(app)
register_graph_callbacks(app)
register_embedding_callbacks(app)
register_chat_callbacks(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run_server(debug=False if not os.environ.get("RAILWAY_ENVIRONMENT_NAME") else False, host="0.0.0.0", port=port)