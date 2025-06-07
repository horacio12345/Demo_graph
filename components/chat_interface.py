# ./components/chat_interface.py
# Interfaz de chat para el agente RAG conversacional - VERIFICADO con IDs correctos

from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

def chat_interface():
    """
    Componente de interfaz de chat para hacer preguntas al agente RAG.
    Todos los IDs están verificados para coincidir con los callbacks.
    """
    return dbc.Container([
        # Header del chat
        dbc.Row([
            dbc.Col([
                html.H3([
                    "🤖 Agente RAG Conversacional",
                    html.Br(),
                    html.Small("Pregunta sobre los documentos procesados", 
                              className="ms-2", style={'color': '#1d5ff9', 'fontSize': '1.3rem'})   
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
                                id="chat-input",  # ⭐ ID VERIFICADO ⭐
                                type="text",
                                placeholder="Ejemplo: ¿Qué información hay sobre Albert Einstein?",
                                style={"fontSize": "14px", "backgroundColor": "#1a2035", "color": "#ffffff", "border": "1px solid #334155"}
                            ),
                            dbc.Button(
                                "Enviar",
                                id="chat-send-btn",  # ⭐ ID VERIFICADO ⭐
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
                                    id="chat-llm-selector",  # ⭐ ID VERIFICADO ⭐
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
                                    id="chat-status",  # ⭐ ID VERIFICADO ⭐
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
                    id="chat-conversation",  # ⭐ ID VERIFICADO ⭐
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

def parse_markdown_to_html(text: str):
    """
    Convierte Markdown básico a elementos HTML de Dash manteniendo estilos consistentes
    """
    if not text:
        return []
    
    lines = text.split('\n')
    elements = []
    current_paragraph = []
    in_list = False
    list_items = []
    
    for line in lines:
        line_stripped = line.strip()
        
        # Headers (## Título)
        if line_stripped.startswith('##'):
            # Finalizar lista si existe
            if in_list and list_items:
                elements.append(create_list(list_items))
                list_items = []
                in_list = False
            
            # Añadir párrafo previo si existe
            if current_paragraph:
                paragraph_text = '\n'.join(current_paragraph)
                elements.append(create_paragraph_with_formatting(paragraph_text))
                current_paragraph = []
            
            # Crear header
            header_text = line_stripped.replace('##', '').strip()
            elements.append(html.H4(
                header_text,
                style={
                    'color': '#1a365d !important',
                    'fontSize': '1.1rem',
                    'fontWeight': '600',
                    'marginTop': '1rem',
                    'marginBottom': '0.5rem'
                }
            ))
        
        # Listas con *
        elif line_stripped.startswith('* '):
            # Finalizar párrafo previo si existe
            if current_paragraph:
                paragraph_text = '\n'.join(current_paragraph)
                elements.append(create_paragraph_with_formatting(paragraph_text))
                current_paragraph = []
            
            # Añadir a lista
            list_text = line_stripped[2:].strip()  # Quitar "* "
            list_items.append(list_text)
            in_list = True
        
        # Línea vacía
        elif line_stripped == '':
            # Finalizar lista si existe
            if in_list and list_items:
                elements.append(create_list(list_items))
                list_items = []
                in_list = False
            
            if current_paragraph:
                paragraph_text = '\n'.join(current_paragraph)
                elements.append(create_paragraph_with_formatting(paragraph_text))
                current_paragraph = []
        
        # Línea normal
        else:
            # Finalizar lista si existe
            if in_list and list_items:
                elements.append(create_list(list_items))
                list_items = []
                in_list = False
            
            current_paragraph.append(line)
    
    # Finalizar elementos pendientes
    if in_list and list_items:
        elements.append(create_list(list_items))
    elif current_paragraph:
        paragraph_text = '\n'.join(current_paragraph)
        elements.append(create_paragraph_with_formatting(paragraph_text))
    
    return elements

def create_paragraph_with_formatting(text: str):
    """
    Crea un párrafo procesando formato inline (**bold**)
    """
    if not text.strip():
        return html.Br()
    
    # Procesar texto con **bold**
    parts = []
    remaining_text = text
    
    while '**' in remaining_text:
        # Encontrar primer **
        start_idx = remaining_text.find('**')
        if start_idx == -1:
            break
            
        # Añadir texto antes del **
        if start_idx > 0:
            parts.append(remaining_text[:start_idx])
        
        # Encontrar el ** de cierre
        remaining_after_start = remaining_text[start_idx + 2:]
        end_idx = remaining_after_start.find('**')
        
        if end_idx == -1:
            # No hay cierre, añadir todo el resto
            parts.append(remaining_text[start_idx:])
            break
        
        # Extraer texto en bold
        bold_text = remaining_after_start[:end_idx]
        parts.append(html.Strong(
            bold_text,
            style={'color': '#0a3622', 'fontWeight': '600'}
        ))
        
        # Continuar con el resto
        remaining_text = remaining_after_start[end_idx + 2:]
    
    # Añadir texto restante
    if remaining_text:
        parts.append(remaining_text)
    
    return html.P(
        parts,
        style={
            'color': '#0f5132',
            'fontSize': '0.95rem',
            'lineHeight': '1.6',
            'marginBottom': '0.5rem',
            'whiteSpace': 'pre-wrap'
        }
    )

def create_list(items):
    """
    Crea una lista HTML con items
    """
    list_elements = []
    for item in items:
        # Procesar formato inline en cada item
        processed_item = create_paragraph_with_formatting(item)
        # Convertir el párrafo a contenido de li
        list_elements.append(html.Li(
            processed_item.children,  # Usar el contenido del párrafo
            style={'color': '#0f5132', 'marginBottom': '0.25rem'}
        ))
    
    return html.Ul(
        list_elements,
        style={
            'margin': '0.5rem 0',
            'paddingLeft': '1.5rem',
            'color': '#0f5132'
        }
    )

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
    Crea un mensaje del bot en el chat con formato Markdown procesado manualmente.
    """
    # Verificar que la respuesta no esté vacía
    if not answer or not answer.strip():
        answer = "Lo siento, no pude generar una respuesta basada en la información disponible."
    
    # Procesar el markdown manualmente
    formatted_content = parse_markdown_to_html(answer)
    
    card_content = [
        html.Div([
            html.Strong("🤖 Respuesta del Agente:", 
                       className="text-success",
                       style={'color': '#0a3622 !important'}),
            html.Div(
                formatted_content,
                style={'marginTop': '0.5rem'}
            )
        ])
    ]
    
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