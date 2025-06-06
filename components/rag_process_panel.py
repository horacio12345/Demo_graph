# ./components/rag_process_panel.py
# Panel educativo que muestra el proceso RAG paso a paso - VERSIÓN CORREGIDA

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Dict, Any, List

def rag_process_panel():
    """
    Panel principal que muestra el proceso RAG educativo.
    """
    return dbc.Card([
        dbc.CardHeader([
            html.H3([
                html.I(className="fas fa-cogs me-2"),
                "Proceso RAG en Tiempo Real"
            ], className="mb-0", style={
                'color': '#ffffff',  # Azul claro
                'fontSize': '1.8rem',  # Más grande
                'fontWeight': 'normal'    # Más grueso
                })
        ]),
        dbc.CardBody([
            html.Div(
                id="rag-process-content",
                children=[create_initial_state()],
                style={"minHeight": "600px"}
            )
        ], style={'backgroundColor': '#0a0e1a', 'border': 'none'})
    ], className="shadow-sm h-100", style={'border': 'none', 'boxShadow': 'none'})

def create_initial_state():
    """
    Estado inicial del panel antes de hacer preguntas.
    """
    return html.Div([
        html.Div([
            html.I(className="fas fa-play-circle fa-3x text-light mb-3"),
            html.H5("Sistema RAG Detallado", className="text-light"),
            html.P([
                "Muestra del proceso de Retrieval-Augmented Generation paso a paso."
            ], className="text-center", style={'opacity': '1.0', 'color': '#9fc3ee'})
        ], className="text-center py-3"),
        
        # Explicación de los pasos
        html.Div([
            html.H6("🔍 Pasos del Proceso RAG:", className="text-light mb-3"),
            create_step_card("1", "Vectorización", "Tu pregunta se convierte en números", "info", inactive=False),
            create_step_card("2", "Búsqueda", "Se buscan fragmentos similares", "info", inactive=False),  
            create_step_card("3", "Contexto", "Se construye el contexto relevante", "info", inactive=False),
            create_step_card("4", "Generación", "El LLM crea la respuesta final", "info", inactive=False)
        ], className="mt-4")
    ], className="text-light")

def create_step_card(number: str, title: str, description: str, color: str = "info", inactive: bool = False):
    """
    Crea una tarjeta para un paso del proceso RAG.
    """
    opacity_style = {'opacity': '0.5'} if inactive else {}
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                dbc.Badge(number, color="light", className="me-2", pill=True, style={
                    'fontSize': '1.5em',
                    'color': '#2f6bf5',
                    'backgroundColor': 'white',
                    'border': '3px solid #2f6bf5',
                    'fontWeight': 'bold'
                }),
                html.Strong(title, className="me-2", style={'color': '#7da2f7'}),
                html.Small(description, className="text-light", style={'opacity': '1.0'})
            ])
        ], className="py-2")
    ], className="mb-2", outline=True, color=color, 
       style={**{'backgroundColor': 'transparent', 'borderColor': '#334155'}, **opacity_style})

def create_complete_process_view(rag_data: Dict[str, Any]):
    """
    Vista completa del proceso RAG con todos los pasos ejecutados.
    """
    print(f"DEBUG: create_complete_process_view recibió: {rag_data}")
    
    if not rag_data or not rag_data.get("success", False):
        error_msg = rag_data.get("error", "Error desconocido") if rag_data else "No hay datos disponibles"
        return create_error_view(error_msg)
    
    steps = rag_data.get("steps", {})
    print(f"DEBUG: steps extraídos: {steps}")
    
    return html.Div([
        # Resumen ejecutivo
        create_executive_summary(rag_data),
        
        html.Hr(style={'borderColor': '#334155'}),
        
        # Los 4 pasos principales
        create_vectorization_step(steps.get("search", {}).get("vectorization", {})),
        create_search_step(steps.get("search", {}).get("search", {})),
        create_context_step(steps.get("context", {})),
        create_response_step(steps.get("response", {}))
    ])

def create_executive_summary(rag_data: Dict[str, Any]):
    """
    Resumen ejecutivo del proceso RAG.
    """
    steps = rag_data.get("steps", {})
    search_info = steps.get("search", {}).get("search", {})
    context_info = steps.get("context", {})
    
    return dbc.Card([
        dbc.CardHeader([
            html.H6([
                html.I(className="fas fa-chart-pie me-2"),
                "Resumen del Proceso"
            ], className="mb-0 text-light")
        ], style={'backgroundColor': '#1a1f2e', 'border': '1px solid #334155'}),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6(search_info.get("total_found", 0), className="text-info mb-0"),
                    html.Small("Chunks encontrados", className="text-light", style={'opacity': '0.7'})
                ], width=6),
                dbc.Col([
                    html.H6(context_info.get("chunks_used", 0), className="text-success mb-0"),
                    html.Small("Chunks usados", className="text-light", style={'opacity': '0.7'})
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    html.H6(context_info.get("unique_sources", 0), className="text-primary mb-0"),
                    html.Small("Fuentes únicas", className="text-light", style={'opacity': '0.7'})
                ], width=6),
                dbc.Col([
                    html.H6(rag_data.get("llm_method", "N/A").upper(), className="text-warning mb-0"),
                    html.Small("LLM utilizado", className="text-light", style={'opacity': '0.7'})
                ], width=6)
            ], className="mt-2")
        ], style={'backgroundColor': '#1a1f2e'})
    ], color="light", outline=True, className="mb-3", 
       style={'backgroundColor': '#1a1f2e', 'borderColor': '#334155'})

def create_vectorization_step(vectorization_data: Dict[str, Any]):
    """
    Paso 1: Visualización de la vectorización.
    """
    if not vectorization_data.get("success", False):
        return create_step_error("1", "Vectorización", vectorization_data.get("error", "Error desconocido"))
    
    first_values = vectorization_data.get("first_values", [])
    dimensions = vectorization_data.get("dimensions", 0)
    
    return create_process_step(
        number="1",
        title="Vectorización de la Pregunta", 
        status="success",
        content=[
            html.P([
                f"La pregunta se convirtió en un vector de {dimensions} dimensiones usando el modelo ",
                html.Code(vectorization_data.get("model_used", "text-embedding-3-small"), 
                         style={'backgroundColor': '#2d3748', 'color': '#e2e8f0', 'padding': '2px 4px'})
            ], className="text-light"),
            
            # Visualización de primeros valores
            html.H6("Primeros 10 valores del embedding:", className="mt-3 text-light"),
            create_embedding_visualization(first_values),
            
            # Estadísticas
            html.Small([
                f"Dimensiones totales: {dimensions} | ",
                f"Longitud de pregunta: {vectorization_data.get('question_length', 'N/A')} caracteres"
            ], className="text-light", style={'opacity': '0.7'})
        ]
    )

def create_search_step(search_data: Dict[str, Any]):
    """
    Paso 2: Visualización de la búsqueda semántica.
    """
    if not search_data.get("success", False):
        return create_step_error("2", "Búsqueda", search_data.get("error", "Error desconocido"))
    
    return create_process_step(
        number="2",
        title="Búsqueda Semántica",
        status="success", 
        content=[
            html.P([
                f"Se encontraron {search_data.get('total_found', 0)} fragmentos similares ",
                f"usando similitud coseno en la base de datos vectorial."
            ], className="text-light"),
            
            # Scores de similitud
            html.H6("Scores de Relevancia:", className="mt-3 text-light"),
            create_similarity_scores(search_data.get("top_scores", [])),
            
            # Estadísticas
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Strong(f"{search_data.get('total_found', 0)}", className="text-info"),
                        html.Br(),
                        html.Small("Fragmentos encontrados", className="text-light", style={'opacity': '0.7'})
                    ], width=4),
                    dbc.Col([
                        html.Strong(f"{search_data.get('avg_score', 0):.3f}", className="text-success"),
                        html.Br(),
                        html.Small("Score promedio", className="text-light", style={'opacity': '0.7'})
                    ], width=4),
                    dbc.Col([
                        html.Strong(f"{search_data.get('unique_sources', 0)}", className="text-warning"),
                        html.Br(),
                        html.Small("Fuentes únicas", className="text-light", style={'opacity': '0.7'})
                    ], width=4)
                ])
            ], className="mt-3")
        ]
    )

def create_context_step(context_data: Dict[str, Any]):
    """
    Paso 3: Visualización de la construcción del contexto.
    """
    if not context_data.get("success", False):
        return create_step_error("3", "Contexto", context_data.get("error", "Error desconocido"))
    
    return create_process_step(
        number="3",
        title="Construcción del Contexto",
        status="success",
        content=[
            html.P([
                f"Se utilizaron {context_data.get('chunks_used', 0)} de {context_data.get('chunks_provided', 0)} ",
                f"fragmentos disponibles para construir el contexto."
            ], className="text-light"),
            
            # Preview del contexto
            html.H6("Vista previa del contexto:", className="mt-3 text-light"),
            html.Pre(
                context_data.get("context_preview", "Sin preview disponible"),
                style={
                    "backgroundColor": "#2d3748",
                    "color": "#e2e8f0",
                    "padding": "10px",
                    "borderRadius": "5px",
                    "fontSize": "12px",
                    "maxHeight": "150px",
                    "overflowY": "auto",
                    "border": "1px solid #4a5568"
                }
            ),
            
            # Estadísticas del contexto
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Strong(f"{context_data.get('total_length', 0)}", className="text-info"),
                        html.Br(),
                        html.Small("Caracteres totales", className="text-light", style={'opacity': '0.7'})
                    ], width=4),
                    dbc.Col([
                        html.Strong(f"{context_data.get('avg_relevance_score', 0):.3f}", className="text-success"),
                        html.Br(),
                        html.Small("Relevancia promedio", className="text-light", style={'opacity': '0.7'})
                    ], width=4),
                    dbc.Col([
                        html.Strong(f"{context_data.get('unique_sources', 0)}", className="text-warning"),
                        html.Br(),
                        html.Small("Documentos únicos", className="text-light", style={'opacity': '0.7'})
                    ], width=4)
                ])
            ], className="mt-3")
        ]
    )

def create_response_step(response_data: Dict[str, Any]):
    """
    Paso 4: Visualización de la generación de respuesta.
    """
    if not response_data.get("success", False):
        return create_step_error("4", "Generación", response_data.get("error", "Error desconocido"))
    
    return create_process_step(
        number="4",
        title="Generación de Respuesta",
        status="success",
        content=[
            html.P([
                f"El modelo {response_data.get('llm_used', 'LLM')} generó una respuesta ",
                f"de {response_data.get('response_length', 0)} caracteres basándose en el contexto."
            ], className="text-light"),
            
            # Configuración del LLM
            html.H6("Configuración del LLM:", className="mt-3 text-light"),
            html.Ul([
                html.Li(f"Modelo: {response_data.get('model', 'N/A')}", className="text-light"),
                html.Li(f"Temperatura: {response_data.get('temperature', 'N/A')}", className="text-light"),
                html.Li(f"Tokens máximos: {response_data.get('max_tokens', 'N/A')}", className="text-light"),
                html.Li(f"Tokens utilizados: {response_data.get('tokens_used', 'N/A')}", className="text-light")
            ]),
            
            # Estadísticas
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Strong(f"{response_data.get('prompt_length', 0)}", className="text-info"),
                        html.Br(),
                        html.Small("Caracteres del prompt", className="text-light", style={'opacity': '0.7'})
                    ], width=6),
                    dbc.Col([
                        html.Strong(f"{response_data.get('response_length', 0)}", className="text-success"),
                        html.Br(),
                        html.Small("Caracteres de respuesta", className="text-light", style={'opacity': '0.7'})
                    ], width=6)
                ])
            ], className="mt-3")
        ]
    )

def create_process_step(number: str, title: str, status: str, content: List):
    """
    Crea un paso del proceso con formato consistente.
    """
    color_map = {
        "success": "success",
        "info": "info", 
        "warning": "warning",
        "error": "danger"
    }
    
    icon_map = {
        "success": "fas fa-check-circle",
        "info": "fas fa-info-circle",
        "warning": "fas fa-exclamation-triangle", 
        "error": "fas fa-times-circle"
    }
    
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className=f"{icon_map.get(status, 'fas fa-circle')} me-2", style={'color': '#60a5fa'}),
                dbc.Badge(number, color=color_map.get(status, "secondary"), className="me-2", pill=True),
                title
            ])
        ], style={'backgroundColor': '#1a1f2e', 'border': '1px solid #334155', 'color': '#e2e8f0'}),
        dbc.CardBody(content, style={'backgroundColor': '#1a1f2e', 'border': '1px solid #334155'})
    ], color=color_map.get(status, "light"), outline=True, className="mb-3",
       style={'backgroundColor': '#1a1f2e', 'borderColor': '#334155'})

def create_step_error(number: str, step_name: str, error_message: str):
    """
    Crea la visualización de un error en un paso.
    """
    return create_process_step(
        number=number,
        title=f"Error en {step_name}",
        status="error",
        content=[
            html.P(f"Se produjo un error durante {step_name.lower()}:", className="text-light"),
            html.Code(error_message, style={"color": "#f56565", 'backgroundColor': '#2d3748', 'padding': '4px 8px'})
        ]
    )

def create_error_view(error_message: str):
    """
    Vista de error general.
    """
    return html.Div([
        dbc.Alert([
            html.H5([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "Error en el Proceso RAG"
            ], className="alert-heading"),
            html.P(f"Se produjo un error: {error_message}"),
            html.Hr(),
            html.P("Intenta hacer otra pregunta o verifica que hay documentos procesados.", className="mb-0")
        ], color="danger")
    ])

def create_embedding_visualization(values: List[float]):
    """
    Visualiza los primeros valores del embedding.
    """
    if not values:
        return html.P("No hay valores para mostrar", className="text-light", style={'opacity': '0.7'})
    
    # Crear visualización con colores
    value_items = []
    for i, value in enumerate(values[:10]):  # Solo primeros 10
        color = "#22c55e" if value >= 0 else "#ef4444"
        value_items.append(
            html.Span(
                f"{value:.15f}",
                style={
                    "backgroundColor": color,
                    "color": "white",
                    "padding": "2px 6px",
                    "margin": "2px",
                    "borderRadius": "4px",
                    "fontSize": "11px",
                    "minWidth": "120px",
                    "display": "inline-block",
                    "textAlign": "center",
                    "fontFamily": "monospace"
                }
            )
        )
    
    return html.Div(value_items, style={"lineHeight": "2"})

def create_similarity_scores(scores: List[float]):
    """
    Visualiza los scores de similitud.
    """
    if not scores:
        return html.P("No hay scores para mostrar", className="text-light", style={'opacity': '0.7'})
    
    score_items = []
    for i, score in enumerate(scores[:5]):  # Solo primeros 5
        score_items.append(
            dbc.Progress(
                value=score * 100,
                label=f"{score:.15f}",
                color="success" if score > 0.8 else "warning" if score > 0.6 else "info",
                className="mb-2",
                style={"height": "25px", 'minWidth': '300px'}
            )
        )
    
    return html.Div(score_items, style={'minWidth': '300px'})