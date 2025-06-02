# ./app.py
# Entry point de la aplicación Dash: layout principal y registro de callbacks

import os
import logging
from dash import Dash, html, dcc, Input, Output, callback_context
import dash_bootstrap_components as dbc

# Componentes originales
from components.upload_component import upload_component
from components.ocr_selector import ocr_selector
from components.llm_selector import llm_selector
from components.progress_bar import progress_bar
from components.graph_view import graph_view
# from components.embedding_view import embedding_view # Comentado si no se usa directamente en layout

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
server.config['SESSION_COOKIE_EXPIRES'] = None
server.config['SESSION_COOKIE_HTTPONLY'] = True
server.config['SESSION_COOKIE_SECURE'] = True if os.environ.get('RAILWAY_ENVIRONMENT_NAME') else False
server.config['PERMANENT_SESSION_LIFETIME'] = 600

# ⭐ CONFIGURAR RUTAS DE AUTENTICACIÓN ⭐
setup_auth_routes(app)


# ---- Contenido de la página principal (Grafo) - ANTES get_main_layout ----
def get_main_layout_content():
    """Layout del contenido de la página principal (procesamiento y grafo)."""
    print("DEBUG: Llamando a get_main_layout_content()")
    # El header con info de usuario y logout ahora está en la navbar
    return dbc.Container([
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
                })
            ], width=3, style={"backgroundColor": "#f8fafc", "padding": "16px", "borderRadius": "12px", "minHeight": "calc(100vh - 76px)"}), # Ajustar si es necesario
            dbc.Col([
                graph_view(),
                html.Div(id="embedding-panel", style={"marginTop": "32px"})
            ], width=9, style={"padding": "24px"})
        ])
    ], fluid=True, style={"background": "#f1f5f9", "minHeight": "calc(100vh - 56px)"}) # Ajustar altura si hay navbar


# ---- NUEVA FUNCIÓN: Layout base con Navegación ----
def get_base_layout_with_navbar():
    """Layout base que incluye la barra de navegación y el contenedor de página."""
    print("DEBUG: Llamando a get_base_layout_with_navbar()")
    current_user = get_current_user()

    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Procesamiento y Grafo", href="/")),
            dbc.NavItem(dbc.NavLink("Chat RAG Educativo", href="/chat")),
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
                color="light"
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
        html.Div(id='page-content', children=[html.P("Cargando contenido inicial de la página...")]) # Contenido inicial
    ])


# ---- MODIFICADA: Función para servir el layout principal o el de login ----
def serve_layout():
    """Función que decide qué layout servir según autenticación."""
    print("DEBUG: Llamando a serve_layout()")
    if not is_authenticated():
        print("DEBUG: serve_layout -> No autenticado, sirviendo get_login_layout()")
        return get_login_layout()
    else:
        # Si está autenticado, sirve el layout base con navegación
        print("DEBUG: serve_layout -> Autenticado, sirviendo get_base_layout_with_navbar()")
        return get_base_layout_with_navbar()

# ⭐ ASIGNAR LAYOUT DINÁMICO ⭐
print("DEBUG: Asignando app.layout = serve_layout")
app.layout = serve_layout


# ---- NUEVO CALLBACK: Para renderizar el contenido de la página ----
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    """Actualiza el contenido de la página basado en la URL."""
    print(f"DEBUG: display_page -> pathname: {pathname}")
    if pathname == '/chat':
        print("DEBUG: display_page -> Sirviendo chat_page_layout()")
        return chat_page_layout()
    elif pathname == '/':
        print("DEBUG: display_page -> Sirviendo get_main_layout_content() para /")
        return get_main_layout_content()
    # else:
    #     return "404 - Página no encontrada" # O redirigir
    print(f"DEBUG: display_page -> Pathname '{pathname}' no coincide, sirviendo get_main_layout_content() por defecto")
    return get_main_layout_content()


# ---- Registro de Callbacks ----
register_ocr_callbacks(app)
register_llm_callbacks(app)
register_graph_callbacks(app)
register_embedding_callbacks(app)
register_chat_callbacks(app) # ⭐ REGISTRAR NUEVOS CALLBACKS DEL CHAT ⭐

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run_server(debug=True if not os.environ.get("RAILWAY_ENVIRONMENT_NAME") else False, host="0.0.0.0", port=port)