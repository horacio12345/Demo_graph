# ./components/rag_process_panel.py
# Panel educativo que muestra el proceso RAG paso a paso en tiempo real

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from typing import Dict, Any, List

def rag_process_panel():
    """
    Panel principal que muestra el proceso RAG educativo.
    """
    return dbc.Card([
        # Reemplazamos dbc.CardHeader con un div personalizado
        html.Div([
            html.Div([
                html.I(className="fas fa-cogs me-2"),
                html.Span("Proceso RAG en Tiempo Real", style={
                    'color': '#a3b0f1',
                    'fontSize': '1.5rem',
                    'fontWeight': '500',
                    'verticalAlign': 'middle'
                })
            ], style={'padding': '20px'})
        ], style={
            'backgroundColor': '#0a0e1a',
            'borderRadius': '16px 16px 0 0',
            'width': '100%',
            'boxSizing': 'border-box',
            'border': 'none',  
            'borderBottom': 'none'  
        }),
        dbc.CardBody([
            html.Div(
                id="rag-process-content",
                children=[create_initial_state()],
                style={"minHeight": "600px"}
            )
        ], style={
            'backgroundColor': '#0a0e1a',
            'borderRadius': '0 0 16px 16px',
            'border': 'none'  
        })
    ], className="shadow-sm h-100", style={
        'border': 'none',  
        'boxShadow': 'none',  
        'overflow': 'hidden'
    })

def create_initial_state():
    """
    Estado inicial del panel antes de hacer preguntas.
    """
    return html.Div([
        html.Div([
            html.I(className="fas fa-play-circle fa-3x text-light mb-3"),
            html.H5("Sistema RAG Preparado", className="text-light"),
            html.P([
                "Descripción del proceso de Retrieval-Augmented Generation paso a paso."
            ], className="text-light-50 text-center")
        ], className="text-center py-3"),
        
        # Explicación de los pasos
        html.Div([
            html.H6("🔍 Pasos del Proceso RAG:", className="text-light mb-3"),
            create_step_explanation("1", "Vectorización", "Tu pregunta se convierte en números", "info"),
            create_step_explanation("2", "Búsqueda", "Se buscan fragmentos similares", "info"),  
            create_step_explanation("3", "Contexto", "Se construye el contexto relevante", "info"),
            create_step_explanation("4", "Generación", "El LLM crea la respuesta final", "info")
        ], className="mt-2")
    ], className="text-light")

def create_step_explanation(number: str, title: str, description: str, color: str = "info"):
    """
    Crea una explicación visual de un paso del proceso.
    """
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                dbc.Badge(number, color=color, className="me-2", pill=True, style={'fontSize': '0.9em'}),
                html.Strong(title, className="me-2 text-light"),
                html.Small(description, className="text-light-50")
            ])
        ], className="py-2")
    ], className="mb-2", outline=True, color=color, style={'backgroundColor': 'transparent', 'borderColor': '#334155'})

def create_processing_state():
    """
    Estado mientras se procesa una pregunta.
    """
    return html.Div([
        html.Div([
            dbc.Spinner(size="lg", color="primary"),
            html.H5("Procesando pregunta...", className="mt-3 text-primary"),
            html.P("Ejecutando pipeline RAG", className="text-muted")
        ], className="text-center py-5")
    ])

def create_complete_process_view(rag_data: Dict[str, Any]):
    """
    Vista completa del proceso RAG con todos los pasos.
    
    Args:
        rag_data: Datos del proceso RAG desde el orquestador
    """
    if not rag_data or not rag_data.get("success", False):
        return create_error_view(rag_data.get("error", "Error desconocido"))
    
    steps = rag_data.get("steps", {})
    
    return html.Div([
        # Resumen ejecutivo
        create_executive_summary(rag_data),
        
        html.Hr(),
        
        # Paso 1: Vectorización  
        create_vectorization_step(steps.get("search", {}).get("vectorization", {})),
        
        # Paso 2: Búsqueda semántica
        create_search_step(steps.get("search", {}).get("search", {})),
        
        # Paso 3: Construcción de contexto
        create_context_step(steps.get("context", {})),
        
        # Paso 4: Generación de respuesta
        create_response_step(steps.get("response", {})),
        
        # Paso 5: Información de fuentes
        create_sources_step(steps.get("sources", {}))
    ])

def create_executive_summary(rag_data: Dict[str, Any]):
    """
    Resumen ejecutivo del proceso RAG.
    """
    summary = {
        "llm_used": rag_data.get("llm_method", "unknown"),
        "chunks_found": rag_data.get("steps", {}).get("search", {}).get("search", {}).get("total_found", 0),
        "chunks_used": rag_data.get("steps", {}).get("context", {}).get("chunks_used", 0),
        "response_length": len(rag_data.get("final_answer", "")),
        "unique_sources": rag_data.get("steps", {}).get("sources", {}).get("unique_documents", 0)
    }
    
    return dbc.Card([
        dbc.CardHeader([
            html.H6([
                html.I(className="fas fa-chart-pie me-2"),
                "Resumen del Proceso"
            ], className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6(summary["chunks_found"], className="text-info mb-0"),
                    html.Small("Chunks encontrados", className="text-muted")
                ], width=6),
                dbc.Col([
                    html.H6(summary["chunks_used"], className="text-success mb-0"),
                    html.Small("Chunks usados", className="text-muted")
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    html.H6(summary["unique_sources"], className="text-primary mb-0"),
                    html.Small("Fuentes únicas", className="text-muted")
                ], width=6),
                dbc.Col([
                    html.H6(summary["llm_used"].upper(), className="text-warning mb-0"),
                    html.Small("LLM utilizado", className="text-muted")
                ], width=6)
            ], className="mt-2")
        ])
    ], color="light", className="mb-3")

def create_vectorization_step(vectorization_data: Dict[str, Any]):
    """
    Paso 1: Visualización de la vectorización.
    """
    if not vectorization_data.get("success", False):
        return create_step_error("Vectorización", vectorization_data.get("error", "Error desconocido"))
    
    first_values = vectorization_data.get("first_values", [])
    dimensions = vectorization_data.get("dimensions", 0)
    
    return create_process_step(
        number="1",
        title="Vectorización de la Pregunta", 
        status="success",
        content=[
            html.P([
                f"Tu pregunta se convirtió en un vector de {dimensions} dimensiones usando el modelo ",
                html.Code(vectorization_data.get("model_used", "text-embedding-ada-002"))
            ]),
            
            # Visualización de primeros valores
            html.H6("Primeros 10 valores del embedding:", className="mt-3"),
            create_embedding_visualization(first_values),
            
            # Estadísticas
            html.Small([
                f"Dimensiones totales: {dimensions} | ",
                f"Longitud de pregunta: {vectorization_data.get('question_length', 'N/A')} caracteres"
            ], className="text-muted")
        ]
    )

def create_search_step(search_data: Dict[str, Any]):
    """
    Paso 2: Visualización de la búsqueda semántica.
    """
    if not search_data.get("success", False):
        return create_step_error("Búsqueda", search_data.get("error", "Error desconocido"))
    
    return create_process_step(
        number="2",
        title="Búsqueda Semántica",
        status="success", 
        content=[
            html.P([
                f"Se encontraron {search_data.get('total_found', 0)} fragmentos similares ",
                f"usando similitud coseno en la base de datos vectorial."
            ]),
            
            # Scores de similitud
            html.H6("Scores de Relevancia:", className="mt-3"),
            create_similarity_scores(search_data.get("top_scores", [])),
            
            # Estadísticas
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Strong(f"{search_data.get('total_found', 0)}", className="text-info"),
                        html.Br(),
                        html.Small("Fragmentos encontrados", className="text-muted")
                    ], width=4),
                    dbc.Col([
                        html.Strong(f"{search_data.get('avg_score', 0):.3f}", className="text-success"),
                        html.Br(),
                        html.Small("Score promedio", className="text-muted")
                    ], width=4),
                    dbc.Col([
                        html.Strong(f"{search_data.get('unique_sources', 0)}", className="text-warning"),
                        html.Br(),
                        html.Small("Fuentes únicas", className="text-muted")
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
        return create_step_error("Contexto", context_data.get("error", "Error desconocido"))
    
    return create_process_step(
        number="3",
        title="Construcción del Contexto",
        status="success",
        content=[
            html.P([
                f"Se utilizaron {context_data.get('chunks_used', 0)} de {context_data.get('chunks_provided', 0)} ",
                f"fragmentos disponibles para construir el contexto."
            ]),
            
            # Preview del contexto
            html.H6("Vista previa del contexto:", className="mt-3"),
            html.Pre(
                context_data.get("context_preview", "Sin preview disponible"),
                style={
                    "backgroundColor": "#f8f9fa",
                    "padding": "10px",
                    "borderRadius": "5px",
                    "fontSize": "12px",
                    "maxHeight": "150px",
                    "overflowY": "auto"
                }
            ),
            
            # Estadísticas del contexto
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Strong(f"{context_data.get('total_length', 0)}", className="text-info"),
                        html.Br(),
                        html.Small("Caracteres totales", className="text-muted")
                    ], width=4),
                    dbc.Col([
                        html.Strong(f"{context_data.get('avg_relevance_score', 0):.3f}", className="text-success"),
                        html.Br(),
                        html.Small("Relevancia promedio", className="text-muted")
                    ], width=4),
                    dbc.Col([
                        html.Strong(f"{context_data.get('unique_sources', 0)}", className="text-warning"),
                        html.Br(),
                        html.Small("Documentos únicos", className="text-muted")
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
        return create_step_error("Generación", response_data.get("error", "Error desconocido"))
    
    return create_process_step(
        number="4",
        title="Generación de Respuesta",
        status="success",
        content=[
            html.P([
                f"El modelo {response_data.get('llm_used', 'LLM')} generó una respuesta ",
                f"de {response_data.get('response_length', 0)} caracteres basándose en el contexto."
            ]),
            
            # Configuración del LLM
            html.H6("Configuración del LLM:", className="mt-3"),
            html.Ul([
                html.Li(f"Modelo: {response_data.get('model', 'N/A')}"),
                html.Li(f"Temperatura: {response_data.get('temperature', 'N/A')}"),
                html.Li(f"Tokens máximos: {response_data.get('max_tokens', 'N/A')}"),
                html.Li(f"Tokens utilizados: {response_data.get('tokens_used', 'N/A')}")
            ]),
            
            # Estadísticas
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Strong(f"{response_data.get('prompt_length', 0)}", className="text-info"),
                        html.Br(),
                        html.Small("Caracteres del prompt", className="text-muted")
                    ], width=6),
                    dbc.Col([
                        html.Strong(f"{response_data.get('response_length', 0)}", className="text-success"),
                        html.Br(),
                        html.Small("Caracteres de respuesta", className="text-muted")
                    ], width=6)
                ])
            ], className="mt-3")
        ]
    )

def create_sources_step(sources_data: Dict[str, Any]):
    """
    Paso 5: Información de las fuentes utilizadas.
    """
    if not sources_data.get("success", False):
        return create_step_error("Fuentes", sources_data.get("error", "Error desconocido"))
    
    sources_detail = sources_data.get("sources_detail", [])
    
    return create_process_step(
        number="5",
        title="Fuentes Utilizadas",
        status="info",
        content=[
            html.P([
                f"Se utilizaron {sources_data.get('total_chunks_used', 0)} fragmentos de ",
                f"{sources_data.get('unique_documents', 0)} documentos únicos."
            ]),
            
            # Lista de fuentes
            html.H6("Fragmentos utilizados:", className="mt-3"),
            html.Div([
                create_source_item(source) for source in sources_detail[:5]  # Mostrar solo los primeros 5
            ]),
            
            # Relevancia promedio
            html.Div([
                html.Strong(f"Relevancia promedio: {sources_data.get('avg_relevance', 0):.3f}", 
                           className="text-success")
            ], className="mt-3")
        ]
    )

def create_source_item(source: Dict[str, Any]):
    """
    Crea un item para mostrar información de una fuente.
    """
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Small([
                    html.Strong(f"Chunk #{source.get('chunk_number', 'N/A')}", className="text-primary"),
                    f" | Score: {source.get('relevance_score', 0):.3f}",
                    f" | Fuente: {source.get('source_file', 'N/A')}"
                ], className="text-muted"),
                html.P(source.get('text_preview', 'Sin preview'), 
                      className="mb-0 mt-1", style={"fontSize": "0.9rem"})
            ])
        ], className="py-2")
    ], className="mb-2", color="light")

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
        # Reemplazamos dbc.CardHeader con un div personalizado
        html.Div([
            html.Div([
                html.I(className=f"{icon_map.get(status, 'fas fa-circle')} me-2"),
                dbc.Badge(number, color=color_map.get(status, "secondary"), className="me-2", pill=True),
                title
            ], style={'padding': '20px'})
        ], style={
            'backgroundColor': '#000000',
            'borderRadius': '16px 16px 0 0',
            'borderBottom': '1px solid #000000',
            'width': '100%',
            'boxSizing': 'border-box'
        }),
        dbc.CardBody(content)
    ], color=color_map.get(status, "light"), outline=True, className="mb-3")

def create_step_error(step_name: str, error_message: str):
    """
    Crea la visualización de un error en un paso.
    """
    return create_process_step(
        number="❌",
        title=f"Error en {step_name}",
        status="error",
        content=[
            html.P(f"Se produjo un error durante {step_name.lower()}:"),
            html.Code(error_message, style={"color": "#dc3545"})
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
        return html.P("No hay valores para mostrar", className="text-muted")
    
    # Crear visualización con colores
    value_items = []
    for i, value in enumerate(values[:10]):  # Solo primeros 10
        color = "#22c55e" if value >= 0 else "#ef4444"
        value_items.append(
            html.Span(
                f"{value:.3f}",
                style={
                    "backgroundColor": color,
                    "color": "white",
                    "padding": "2px 6px",
                    "margin": "2px",
                    "borderRadius": "4px",
                    "fontSize": "11px",
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
        return html.P("No hay scores para mostrar", className="text-muted")
    
    score_items = []
    for i, score in enumerate(scores[:5]):  # Solo primeros 5
        score_items.append(
            dbc.Progress(
                value=score * 100,
                label=f"{score:.3f}",
                color="success" if score > 0.8 else "warning" if score > 0.6 else "info",
                className="mb-2",
                style={"height": "25px"}
            )
        )
    
    return html.Div(score_items)