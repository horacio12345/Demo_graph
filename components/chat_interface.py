# ./components/chat_interface.py
# Interfaz de chat para el agente RAG conversacional - VERSIÓN COMPLETA

from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

def chat_interface():
    """
    Componente de interfaz de chat para hacer preguntas al agente RAG.
    """
    return dbc.Container([
        # Header del chat
        dbc.Row([
            dbc.Col([
                html.H3([
                    "🤖 Agente RAG Conversacional",
                    html.Br(),
                    html.Small("Pregunta sobre los documentos procesados", 
                              className="ms-2", style={'color': '#0927ac', 'fontSize': '1.3rem'})   
                ], className="mb-3 chat-rag-title", style={'fontSize': '2rem'}),
            ])
        ]),
        
        # Input para la pregunta
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody(style={'backgroundColor': '#0a0e1a', 'padding': '20px', 'borderRadius': '16px'}, children=[
                        html.H5("💬 Haz tu pregunta", className="card-title mb-3 text-light"),
                        dbc.InputGroup([
                            dbc.Input(
                                id="chat-input",
                                type="text",
                                placeholder="Ejemplo: ¿Qué información hay sobre Albert Einstein?",
                                style={"fontSize": "14px", "backgroundColor": "#1a2035", "color": "#ffffff", "border": "1px solid #334155"}
                            ),
                            dbc.Button(
                                "Enviar",
                                id="chat-send-btn",
                                n_clicks=0,
                                color="primary",
                                className="ms-2"
                            )
                        ], className="mb-3"),
                        
                        # Selector de LLM y estado
                        dbc.Row([
                            dbc.Col([
                                html.Label("Modelo LLM:", className="form-label text-light"),
                                dcc.Dropdown(
                                    id="chat-llm-selector",
                                    options=[
                                        {"label": "OpenAI GPT-4o", "value": "openai"},
                                        {"label": "Claude Sonnet 4", "value": "claude"}
                                    ],
                                    value="openai",
                                    clearable=False,
                                    className="bg-dark text-light"
                                )
                            ], width=6),
                            dbc.Col([
                                html.Label("Estado:", className="form-label text-light"),
                                html.Div(
                                    id="chat-status",
                                    children="💤 Esperando pregunta...",
                                    className="form-control-plaintext text-light"
                                )
                            ], width=6)
                        ])
                    ])
                ], className="shadow-sm")
            ])
        ], className="mb-4"),
        
        # Área de conversación
        dbc.Row([
            dbc.Col([
                html.Div(
                    id="chat-conversation",
                    children=[
                        html.Div([
                            html.P("Aquí verás la respuesta a tu pregunta...",
                                  className="text-muted",
                                  style={
                                      'fontStyle': 'italic',
                                      'opacity': '0.7',
                                      'fontSize': '1rem',
                                      'position': 'absolute',
                                      'top': '50%',
                                      'left': '50%',
                                      'transform': 'translate(-50%, -50%)',
                                      'width': '100%',
                                      'padding': '0 20px',
                                      'textAlign': 'left',
                                      'color': '#6c757d'
                                  })
                        ], className="w-100 h-100 position-relative")
                    ],
                    style={
                        "minHeight": "260px",
                        "maxHeight": "calc(100vh - 210px)",  
                        "overflowY": "auto",
                        "padding": "20px",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "10px",
                        "border": "1px solid #dee2e6",
                        "position": "relative",  
                        "marginBottom": "20px"  
                    }
                )
            ])
        ])
    ], fluid=True)

def create_user_message(question: str) -> dbc.Card:
    """
    Crea un mensaje del usuario en el chat.
    """
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Strong("👤 Tu pregunta:", 
                           className="text-primary", 
                           style={'color': '#0d6efd !important'}),
                html.P(question, 
                      className="mb-0 mt-2",
                      style={'color': '#212529 !important', 'fontSize': '0.95rem'})
            ])
        ], style={'color': '#212529 !important'})
    ], className="mb-3 ms-5", color="light", style={'backgroundColor': '#f8f9fa !important'})

def create_bot_message(answer: str, show_process: bool = False) -> dbc.Card:
    """
    Crea un mensaje del bot en el chat.
    """
    # Verificar que la respuesta no esté vacía
    if not answer or not answer.strip():
        answer = "Lo siento, no pude generar una respuesta basada en la información disponible."
    
    card_content = [
        html.Div([
            html.Strong("🤖 Respuesta del Agente:", 
                       className="text-success",
                       style={'color': '#0a3622 !important'}),
            html.P(answer, 
                  className="mb-0 mt-2", 
                  style={
                      "whiteSpace": "pre-wrap",
                      'color': '#0f5132 !important',
                      'fontSize': '0.95rem'
                  })
        ])
    ]
    
    if show_process:
        card_content.append(
            html.Div([
                dbc.Button(
                    [html.I(className="fas fa-cogs me-2"), "Ver Proceso RAG Detallado"],
                    id="show-process-btn",
                    color="outline-info",
                    size="sm",
                    className="mt-2",
                    style={
                        'backgroundColor': '#0dcaf0 !important',
                        'color': '#000 !important',
                        'borderColor': '#0dcaf0 !important'
                    }
                )
            ])
        )
    
    return dbc.Card([
        dbc.CardBody(card_content, style={'color': '#0f5132 !important'})
    ], className="mb-3 me-5", color="success", outline=True, 
       style={'backgroundColor': '#d1e7dd !important', 'borderColor': '#198754 !important'})

def create_loading_message() -> dbc.Card:
    """
    Crea un mensaje de carga mientras se procesa la pregunta.
    """
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                dbc.Spinner(size="sm", spinnerClassName="me-2"),
                html.Strong("🤖 Procesando tu pregunta...", 
                           className="text-info",
                           style={'color': '#032830 !important'}),
                html.P([
                    "Estoy buscando información relevante en los documentos y ",
                    "construyendo una respuesta basada en el contenido disponible."
                ], className="mb-0 mt-2 text-muted",
                   style={'color': '#055160 !important'})
            ])
        ], style={'color': '#055160 !important'})
    ], className="mb-3 me-5", color="info", outline=True,
       style={'backgroundColor': '#cff4fc !important', 'borderColor': '#0dcaf0 !important'})

def create_error_message(error: str) -> dbc.Card:
    """
    Crea un mensaje de error en el chat.
    """
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Strong("❌ Error:", 
                           className="text-danger",
                           style={'color': '#58151c !important'}),
                html.P(error, 
                      className="mb-0 mt-2",
                      style={'color': '#721c24 !important', 'fontSize': '0.95rem'})
            ])
        ], style={'color': '#721c24 !important'})
    ], className="mb-3 me-5", color="danger", outline=True,
       style={'backgroundColor': '#f8d7da !important', 'borderColor': '#dc3545 !important'})