# ./callbacks/graph_callbacks.py
# Callbacks corregidos - datos persistentes entre callbacks

from dash import Input, Output, State, no_update, callback_context
from core import graph_builder
import networkx as nx
import dash
import json
import os

# Variable global para almacenar datos del grafo entre callbacks
GRAPH_DATA = {
    'entities': [],
    'relations': [],
    'last_update': None
}

# REEMPLAZAR en graph_callbacks.py - callback update_graph_and_panel

def register_graph_callbacks(app):
    
    @app.callback(
        [Output("knowledge-graph", "elements"),
         Output("embedding-panel", "children"),
         Output("dynamic-legend", "children")],  # ← NUEVO OUTPUT
        [Input("progress-info", "children")],
        prevent_initial_call=True
    )
    def update_graph_and_panel(progress_message):
        """
        Actualiza el grafo Y la leyenda dinámica cuando se completa el procesamiento.
        """
        global GRAPH_DATA
        
        print(f"🔄 Callback activado con mensaje: {progress_message}")
        
        # Verificar si hay mensaje de éxito con entidades/relaciones
        if not progress_message or "entidades" not in str(progress_message):
            print("⚠️ No hay datos de entidades en el mensaje")
            return [], create_empty_panel(), create_empty_legend()  # ← LEYENDA VACÍA
        
        try:
            # Intentar obtener datos de Flask g primero
            from flask import g
            entities = getattr(g, "entities", [])
            relations = getattr(g, "relations", [])
            
            print(f"📊 Datos de Flask g: {len(entities)} entidades, {len(relations)} relaciones")
            
            # Si no hay datos en g, usar datos globales
            if not entities and not relations:
                entities = GRAPH_DATA['entities']
                relations = GRAPH_DATA['relations']
                print(f"📊 Usando datos globales: {len(entities)} entidades, {len(relations)} relaciones")
            else:
                # Actualizar datos globales
                GRAPH_DATA['entities'] = entities
                GRAPH_DATA['relations'] = relations
                print("✅ Datos globales actualizados")
            
            if not entities and not relations:
                print("❌ No hay datos para el grafo")
                return [], create_no_data_panel(), create_empty_legend()  # ← LEYENDA VACÍA
            
            # Construir elementos para Cytoscape
            elements = build_cytoscape_elements(entities, relations)
            print(f"✅ Elementos creados: {len(elements)}")
            
            # Crear panel de información
            info_panel = create_graph_info_panel(entities, relations)
            
            # ⭐ CREAR LEYENDA DINÁMICA ⭐
            # Contar tipos de entidades (ya se hace en create_graph_info_panel, reutilizar)
            entity_counts = {}
            for entity in entities:
                entity_type = entity.get('type', 'Unknown')
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            
            # Generar leyenda dinámica
            dynamic_legend = create_dynamic_legend(entity_counts)
            print(f"🏷️ Leyenda creada con {len(entity_counts)} tipos diferentes")
            
            return elements, info_panel, dynamic_legend  # ← RETORNAR LEYENDA
            
        except Exception as e:
            print(f"❌ Error en callback del grafo: {e}")
            import traceback
            traceback.print_exc()
            return [], create_error_panel(str(e)), create_empty_legend()  # ← LEYENDA VACÍA EN ERROR
    
    # El resto de callbacks sin cambios...
    @app.callback(
        Output("embedding-panel", "children", allow_duplicate=True),
        [Input("knowledge-graph", "tapNodeData")],
        prevent_initial_call=True
    )
    def show_node_details(node_data):
        """
        Muestra información del nodo seleccionado.
        """
        if not node_data:
            return no_update
        
        print(f"🔍 Nodo seleccionado: {node_data}")
        
        try:
            return create_node_detail_panel(node_data)
        except Exception as e:
            print(f"❌ Error mostrando detalles: {e}")
            return create_error_panel(str(e))


# REEMPLAZAR en graph_callbacks.py - función build_cytoscape_elements

def build_cytoscape_elements(entities, relations):
    """
    Construye elementos de Cytoscape desde entidades y relaciones.
    VERSIÓN CORREGIDA que asegura que los colores funcionen.
    """
    elements = []
    
    print(f"🔧 Construyendo elementos...")
    print(f"📝 Entidades de ejemplo: {entities[:2] if entities else 'Ninguna'}")
    print(f"🔗 Relaciones de ejemplo: {relations[:2] if relations else 'Ninguna'}")
    
    # Agregar nodos (entidades) - CORREGIDO
    for entity in entities:
        try:
            entity_type = entity.get('type', 'Unknown')
            entity_id = str(entity.get('id', ''))
            entity_label = str(entity.get('text', entity.get('id', 'Sin nombre')))
            
            # ⭐ ELEMENTO CORREGIDO ⭐
            node_element = {
                'data': {
                    'id': entity_id,
                    'label': entity_label,
                    'type': entity_type  # ← IMPORTANTE: esto debe estar para selectores [type="..."]
                },
                'classes': f"node-{entity_type.lower()}"  # ← BACKUP: clase CSS para selectores .node-xxx
            }
            
            elements.append(node_element)
            
            # DEBUG: Verificar que los datos sean correctos
            print(f"✅ Nodo: ID={entity_id}, Type={entity_type}, Label={entity_label[:20]}...")
            
        except Exception as e:
            print(f"❌ Error agregando entidad {entity}: {e}")
            continue
    
    # Agregar aristas (relaciones) - sin cambios
    entity_ids = {e.get('id') for e in entities}
    
    for relation in relations:
        try:
            source_id = str(relation.get('source_id', ''))
            target_id = str(relation.get('target_id', ''))
            
            # Verificar que ambos nodos existen
            if source_id in entity_ids and target_id in entity_ids:
                edge_element = {
                    'data': {
                        'id': f"{source_id}-{target_id}",
                        'source': source_id,
                        'target': target_id,
                        'label': str(relation.get('type', 'relacionado')),
                        'type': str(relation.get('type', 'unknown'))
                    },
                    'classes': f"edge-{relation.get('type', 'unknown').lower()}"
                }
                elements.append(edge_element)
                print(f"✅ Arista agregada: {source_id} → {target_id} ({edge_element['data']['label']})")
            else:
                print(f"⚠️ Relación ignorada - nodos no encontrados: {source_id} → {target_id}")
        except Exception as e:
            print(f"❌ Error agregando relación {relation}: {e}")
            continue
    
    print(f"🎯 Total elementos creados: {len(elements)}")
    
    # ⭐ DEBUG FINAL: Mostrar tipos de entidades encontrados ⭐
    types_found = set()
    for element in elements:
        if 'data' in element and 'type' in element['data']:
            types_found.add(element['data']['type'])
    
    print(f"🏷️ Tipos de entidades encontrados: {list(types_found)}")
    
    return elements

def create_graph_info_panel(entities, relations):
    """
    Crea panel con estadísticas del grafo.
    """
    from dash import html
    import dash_bootstrap_components as dbc
    
    # Contar tipos de entidades
    entity_counts = {}
    for entity in entities:
        entity_type = entity.get('type', 'Unknown')
        entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
    
    # Contar tipos de relaciones
    relation_counts = {}
    for relation in relations:
        rel_type = relation.get('type', 'Unknown')
        relation_counts[rel_type] = relation_counts.get(rel_type, 0) + 1
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5("📊 Estadísticas del Grafo", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4(len(entities), className="text-primary"),
                    html.P("Entidades", className="mb-0")
                ], width=4),
                dbc.Col([
                    html.H4(len(relations), className="text-success"),
                    html.P("Relaciones", className="mb-0")
                ], width=4),
                dbc.Col([
                    html.H4(len(entity_counts), className="text-info"),
                    html.P("Tipos", className="mb-0")
                ], width=4)
            ], className="text-center mb-3"),
            
            html.Hr(),
            
            # Desglose por tipos
            html.H6("🏷️ Tipos de Entidades:"),
            html.Ul([
                html.Li(f"{type_name}: {count}") 
                for type_name, count in entity_counts.items()
            ], className="mb-3"),
            
            html.H6("🔗 Tipos de Relaciones:"),
            html.Ul([
                html.Li(f"{type_name}: {count}") 
                for type_name, count in relation_counts.items()
            ])
        ])
    ], className="mt-3")

# REEMPLAZAR en graph_callbacks.py - función create_node_detail_panel

def create_node_detail_panel(node_data):
    """
    Panel detallado para nodo seleccionado CON EMBEDDINGS.
    """
    from dash import html
    import dash_bootstrap_components as dbc
    
    # Colores por tipo
    type_colors = {
        'Person': 'danger', 'Persona': 'danger',
        'Organization': 'info', 'Organización': 'info',
        'Location': 'primary', 'Ubicación': 'primary',
        'Industry': 'success', 'Industria': 'success',
        'Concept': 'success', 'Concepto': 'success',
        'Email': 'warning',
        'Position': 'warning', 'Posición': 'warning',
        'Role': 'warning', 'Rol': 'warning',
        'Unknown': 'secondary', 'Desconocido': 'secondary'
    }
    
    node_type = node_data.get('type', 'Unknown')
    color = type_colors.get(node_type, 'secondary')
    node_label = node_data.get('label', 'Sin nombre')
    node_id = node_data.get('id', 'N/A')
    
    # ⭐ BUSCAR EMBEDDING RELACIONADO ⭐
    embedding_section = get_node_embedding_info(node_label, node_id)
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5([
                dbc.Badge(node_type, color=color, className="me-2"),
                node_label
            ], className="mb-0")
        ]),
        dbc.CardBody([
            # Información básica del nodo
            html.P([
                html.Strong("ID: "),
                html.Code(node_id)
            ]),
            html.P([
                html.Strong("Tipo: "),
                node_type
            ]),
            html.P([
                html.Strong("Etiqueta: "),
                node_label
            ]),
            
            # Conexiones
            html.Hr(),
            html.H6("🔗 Conexiones:"),
            html.Div(id="node-connections", children=get_node_connections(node_id)),
            
            # ⭐ NUEVA SECCIÓN: EMBEDDINGS ⭐
            html.Hr(),
            html.H6("🧠 Embedding (Vector):"),
            embedding_section
            
        ])
    ], className="mt-3")


def get_node_embedding_info(node_label, node_id, num_values=15):
    """
    Busca y muestra información del embedding relacionado con el nodo.
    """
    from dash import html
    import dash_bootstrap_components as dbc
    
    try:
        # Importar función de embeddings
        from core import embeddings
        from openai import OpenAI
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        
        if not OPENAI_API_KEY:
            return html.P("❌ No se puede acceder a embeddings: API key no configurada", 
                         style={'color': '#ef4444', 'fontSize': '12px'})
        
        # Generar embedding para el texto del nodo
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            input=node_label,
            model="text-embedding-ada-002"
        )
        embedding_vector = response.data[0].embedding
        
        # Tomar los primeros N valores
        first_values = embedding_vector[:num_values]
        
        # Crear visualización de los valores
        embedding_items = []
        
        # Mostrar valores en filas de 5
        for i in range(0, len(first_values), 5):
            row_values = first_values[i:i+5]
            row_elements = []
            
            for j, value in enumerate(row_values):
                # Colorear según valor (positivo=verde, negativo=rojo)
                color = '#22c55e' if value >= 0 else '#ef4444'
                
                row_elements.append(
                    html.Span(
                        f"{value}",
                        style={
                            'backgroundColor': color,
                            'color': 'white',
                            'padding': '2px 6px',
                            'margin': '2px',
                            'borderRadius': '4px',
                            'fontSize': '10px',
                            'fontFamily': 'monospace',
                            'display': 'inline-block',
                            'minWidth': '55px',
                            'textAlign': 'center'
                        }
                    )
                )
            
            embedding_items.append(
                html.Div(row_elements, style={'marginBottom': '4px'})
            )
        
        # Estadísticas del embedding
        avg_value = sum(embedding_vector) / len(embedding_vector)
        max_value = max(embedding_vector)
        min_value = min(embedding_vector)
        
        return html.Div([
            html.P([
                html.Small(f"Mostrando primeros {num_values} de {len(embedding_vector)} dimensiones:", 
                          style={'color': '#64748b'})
            ]),
            
            # Valores del embedding
            html.Div(embedding_items, style={
                'backgroundColor': '#1e293b',
                'padding': '8px',
                'borderRadius': '6px',
                'marginBottom': '8px',
                'border': '1px solid #334155'
            }),
            
            # Estadísticas
            html.Div([
                html.Small([
                    html.Strong("📊 Stats: "),
                    f"Promedio: {avg_value:.4f} | ",
                    f"Máx: {max_value:.4f} | ",
                    f"Mín: {min_value:.4f}"
                ], style={'color': '#94a3b8', 'fontSize': '10px'})
            ]),
            
            # Explicación educativa
            html.Details([
                html.Summary("💡 ¿Qué es esto?", style={'color': '#60a5fa', 'cursor': 'pointer', 'fontSize': '12px'}),
                html.P([
                    "Cada palabra/concepto se convierte en un vector de 1,536 números. ",
                    "Estos números capturan el 'significado' matemático del texto. ",
                    "Palabras similares tienen vectores similares. ",
                    html.Strong("Verde = valores positivos, Rojo = valores negativos.")
                ], style={'fontSize': '11px', 'color': '#cbd5e1', 'marginTop': '4px'})
            ], style={'marginTop': '8px'})
        ])
        
    except Exception as e:
        print(f"❌ Error obteniendo embedding: {e}")
        return html.P([
            "⚠️ No se pudo obtener el embedding. ",
            html.Small(f"Error: {str(e)[:50]}...", style={'color': '#94a3b8'})
        ], style={'color': '#f59e0b', 'fontSize': '12px'})

def get_node_connections(node_id):
    """
    Obtiene las conexiones de un nodo específico.
    """
    from dash import html
    global GRAPH_DATA
    
    if not node_id:
        return "No se pudo determinar las conexiones."
    
    relations = GRAPH_DATA.get('relations', [])
    entities = GRAPH_DATA.get('entities', [])
    
    # Crear mapa de IDs a nombres
    entity_map = {e.get('id'): e.get('text', e.get('id')) for e in entities}
    
    # Buscar relaciones
    outgoing = []
    incoming = []
    
    for rel in relations:
        if rel.get('source_id') == node_id:
            target_name = entity_map.get(rel.get('target_id'), rel.get('target_id'))
            outgoing.append(f"{rel.get('type', 'relacionado')} → {target_name}")
        elif rel.get('target_id') == node_id:
            source_name = entity_map.get(rel.get('source_id'), rel.get('source_id'))
            incoming.append(f"{source_name} → {rel.get('type', 'relacionado')}")
    
    result = []
    
    if outgoing:
        # Crear elementos sin listas anidadas
        outgoing_items = [html.Strong("Salientes:"), html.Br()]
        for conn in outgoing[:5]:
            outgoing_items.extend([html.Small(conn), html.Br()])
        result.append(html.P(outgoing_items))
    
    if incoming:
        # Crear elementos sin listas anidadas
        incoming_items = [html.Strong("Entrantes:"), html.Br()]
        for conn in incoming[:5]:
            incoming_items.extend([html.Small(conn), html.Br()])
        result.append(html.P(incoming_items))
    
    if not result:
        result = [html.P("No hay conexiones registradas.")]
    
    return result

def create_empty_panel():
    """Panel cuando no hay datos."""
    from dash import html
    import dash_bootstrap_components as dbc
    
    return dbc.Alert([
        html.H6("📄 Sube un documento", className="alert-heading"),
        html.P("El grafo aparecerá automáticamente después de procesar un documento.")
    ], color="info")

def create_no_data_panel():
    """Panel cuando no se extraen datos."""
    from dash import html
    import dash_bootstrap_components as dbc
    
    return dbc.Alert([
        html.H6("⚠️ Sin datos para mostrar", className="alert-heading"),
        html.P("No se pudieron extraer entidades o relaciones del documento.")
    ], color="warning")

def create_error_panel(error_msg):
    """Panel de error."""
    from dash import html
    import dash_bootstrap_components as dbc
    
    return dbc.Alert([
        html.H6("❌ Error", className="alert-heading"),
        html.P(f"Error: {error_msg}")
    ], color="danger")

# Agregar esta función a graph_callbacks.py - DESPUÉS de las importaciones

def create_dynamic_legend(entity_counts):
    """
    Crea leyenda dinámica basada en los tipos de entidades presentes.
    """
    from dash import html
    
    if not entity_counts:
        return html.Div()  # Sin datos = sin leyenda
    
    # MAPEO DE TIPOS A COLORES Y FORMAS (consistente con stylesheet)
    type_config = {
        'Person': {
            'color': '#ef4444',
            'shape': 'circle',
            'icon_style': {'borderRadius': '50%'},
            'label': 'Personas'
        },
        'Organization': {
            'color': '#10b981', 
            'shape': 'rectangle',
            'icon_style': {'borderRadius': '2px'},
            'label': 'Organizaciones'
        },
        'Location': {
            'color': '#3b82f6',
            'shape': 'diamond', 
            'icon_style': {'transform': 'rotate(45deg)'},
            'label': 'Ubicaciones'
        },
        'Industry': {
            'color': '#22c55e',
            'shape': 'hexagon',
            'icon_style': {'clipPath': 'polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)'},
            'label': 'Industrias'
        },
        'Concept': {
            'color': '#22c55e',
            'shape': 'hexagon', 
            'icon_style': {'clipPath': 'polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%)'},
            'label': 'Conceptos'
        },
        'Email': {
            'color': '#f59e0b',
            'shape': 'triangle',
            'icon_style': {'clipPath': 'polygon(50% 0%, 0% 100%, 100% 100%)'},
            'label': 'Emails'
        },
        'Position': {
            'color': '#f59e0b',
            'shape': 'triangle',
            'icon_style': {'clipPath': 'polygon(50% 0%, 0% 100%, 100% 100%)'},
            'label': 'Posiciones'
        },
        'Role': {
            'color': '#f59e0b', 
            'shape': 'triangle',
            'icon_style': {'clipPath': 'polygon(50% 0%, 0% 100%, 100% 100%)'},
            'label': 'Roles'
        }
    }
    
    # COLORES AUTOMÁTICOS para tipos desconocidos
    fallback_colors = ['#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1']
    
    legend_items = []
    
    # Ordenar tipos por cantidad (más frecuentes primero)
    sorted_types = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
    
    for i, (entity_type, count) in enumerate(sorted_types):
        # Obtener configuración del tipo
        if entity_type in type_config:
            config = type_config[entity_type]
        else:
            # Tipo desconocido - asignar color automático
            color_idx = i % len(fallback_colors)
            config = {
                'color': fallback_colors[color_idx],
                'shape': 'circle',
                'icon_style': {'borderRadius': '50%'},
                'label': entity_type.replace('_', ' ').title()
            }
        
        # Crear icono
        icon_style = {
            'width': '12px',
            'height': '12px', 
            'backgroundColor': config['color'],
            'display': 'inline-block',
            'marginRight': '6px',
            **config['icon_style']
        }
        
        # Crear item de leyenda
        legend_item = html.Div([
            html.Div(style=icon_style),
            html.Span(
                f"{config['label']} ({count})", 
                style={'color': '#e2e8f0', 'fontSize': '11px'}
            )
        ], style={
            'marginBottom': '3px', 
            'display': 'flex', 
            'alignItems': 'center'
        })
        
        legend_items.append(legend_item)
    
    # Construir leyenda completa
    return html.Div([
        html.H6(
            "🏷️ Leyenda", 
            style={
                'color': '#e2e8f0', 
                'marginBottom': '10px', 
                'fontSize': '14px',
                'margin': '0 0 8px 0'
            }
        ),
        html.Div(legend_items)
    ], style={
        'background': 'rgba(15, 23, 42, 0.9)',
        'padding': '12px',
        'borderRadius': '8px', 
        'border': '1px solid rgba(255, 255, 255, 0.1)',
        'minWidth': '140px',
        'backdropFilter': 'blur(10px)',
        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.3)'
    })


def create_empty_legend():
    """
    Leyenda vacía cuando no hay datos.
    """
    from dash import html
    return html.Div()  # Simplemente vacío

