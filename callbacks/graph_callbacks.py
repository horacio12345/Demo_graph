# ./callbacks/graph_callbacks.py
# Callbacks simplificados - SIN CACHE

from dash import Input, Output, State, no_update, callback_context
from core import graph_builder
import networkx as nx
import dash
import json
import os

def register_graph_callbacks(app):
    
    @app.callback(
        [Output("knowledge-graph", "elements"),
         Output("embedding-panel", "children"),
         Output("dynamic-legend", "children")],
        [Input("progress-info", "children")],
        prevent_initial_call=True
    )
    def update_graph_simple(progress_message):
        """
        Actualiza el grafo de manera simple - sin cache.
        """
        if not progress_message or "entidades" not in str(progress_message):
            return no_update, no_update, no_update
        
        try:
            # Obtener datos del módulo OCR directamente
            from callbacks.ocr_callbacks import GRAPH_DATA as OCR_GRAPH_DATA
            entities = OCR_GRAPH_DATA.get('entities', [])
            relations = OCR_GRAPH_DATA.get('relations', [])

            if not entities and not relations:
                return [], create_no_data_panel(), create_empty_legend()

            # Construir elementos para Cytoscape
            elements = build_cytoscape_elements(entities, relations)
            
            # Crear panel de información
            info_panel = create_graph_info_panel(entities, relations)
            
            # Crear leyenda dinámica
            entity_counts = {}
            for entity in entities:
                entity_type = entity.get('type', 'Unknown')
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            
            dynamic_legend = create_dynamic_legend(entity_counts)
            
            return elements, info_panel, dynamic_legend
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return [], create_error_panel(str(e)), create_empty_legend()
    
    @app.callback(
        [Output("knowledge-graph", "elements", allow_duplicate=True),
         Output("embedding-panel", "children", allow_duplicate=True),
         Output("dynamic-legend", "children", allow_duplicate=True)],
        [Input("generate-graph-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def generate_graph_from_pinecone(n_clicks):
        """
        Genera el grafo desde documentos almacenados en Pinecone.
        """
        if not n_clicks:
            return no_update, no_update, no_update
        
        try:
            
            # 1. Verificar que hay datos en Pinecone
            from core import embeddings
            stats = embeddings.get_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            
            if total_vectors == 0:
                return [], create_error_panel("No hay documentos procesados en Pinecone"), create_empty_legend()
            
            # 2. Obtener chunks representativos usando queries diversas
            from openai import OpenAI
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            sample_queries = [
                "person organization company",
                "location place city",
                "work relationship role",
                "important information concepts"
            ]
            
            all_chunks = []
            seen_ids = set()
            
            for query in sample_queries:
                try:
                    # Generar embedding para la query
                    response = client.embeddings.create(
                        input=query,
                        model="text-embedding-3-small"
                    )
                    query_vector = response.data[0].embedding
                    
                    # Buscar chunks similares
                    results = embeddings.query_embedding(
                        query_vector=query_vector,
                        top_k=3,
                        include_metadata=True
                    )
                    
                    # Procesar resultados
                    for match in results.get('matches', []):
                        chunk_id = match['id']
                        if chunk_id not in seen_ids:
                            chunk_text = match['metadata'].get('chunk_text', '')
                            if chunk_text and len(chunk_text.strip()) > 50:
                                all_chunks.append(chunk_text)
                                seen_ids.add(chunk_id)
                                
                except Exception as e:
                    print(f"⚠️ Error con query '{query}': {e}")
                    continue
            
            if not all_chunks:
                return [], create_error_panel("No se pudieron recuperar chunks de Pinecone"), create_empty_legend()
            
            # 3. Extraer entidades y relaciones de los chunks
            from core import llm
            all_entities, all_relations = [], []
            
            for i, chunk in enumerate(all_chunks[:8]):  # Limitar para no saturar
                try:
                    llm_result = llm.extract_entities_relations(chunk, llm_method="openai")
                    
                    if isinstance(llm_result, dict):
                        chunk_entities = llm_result.get("entities", [])
                        chunk_relations = llm_result.get("relations", [])
                        
                        # Asegurar IDs únicos
                        for entity in chunk_entities:
                            if "id" in entity:
                                entity["id"] = f"pin_{i}_{entity['id']}"
                        
                        for relation in chunk_relations:
                            if "source_id" in relation:
                                relation["source_id"] = f"pin_{i}_{relation['source_id']}"
                            if "target_id" in relation:
                                relation["target_id"] = f"pin_{i}_{relation['target_id']}"
                        
                        all_entities.extend(chunk_entities)
                        all_relations.extend(chunk_relations)
                        
                except Exception as e:
                    print(f"❌ Error procesando chunk {i}: {e}")
                    continue
            
            if not all_entities and not all_relations:
                return [], create_error_panel("No se pudieron extraer entidades de los documentos"), create_empty_legend()
            
            # 4. Actualizar datos en OCR_CALLBACKS para mantener consistencia
            from callbacks.ocr_callbacks import GRAPH_DATA as OCR_GRAPH_DATA
            OCR_GRAPH_DATA['entities'] = all_entities
            OCR_GRAPH_DATA['relations'] = all_relations
            OCR_GRAPH_DATA['last_update'] = "Generado desde Pinecone"
            
            # 5. Construir elementos del grafo
            elements = build_cytoscape_elements(all_entities, all_relations)
            
            # 6. Crear panel de información
            info_panel = create_pinecone_info_panel(all_entities, all_relations, total_vectors, len(all_chunks))
            
            # 7. Crear leyenda dinámica
            entity_counts = {}
            for entity in all_entities:
                entity_type = entity.get('type', 'Unknown')
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            
            dynamic_legend = create_dynamic_legend(entity_counts)
                        
            return elements, info_panel, dynamic_legend
            
        except Exception as e:
            print(f"❌ Error generando grafo desde Pinecone: {e}")
            import traceback
            traceback.print_exc()
            return [], create_error_panel(f"Error: {str(e)}"), create_empty_legend()
    
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
        
        try:
            return create_node_detail_panel(node_data)
        except Exception as e:
            print(f"❌ Error mostrando detalles: {e}")
            return create_error_panel(str(e))

def create_pinecone_info_panel(entities, relations, total_vectors, chunks_processed):
    """
    Crea panel de información específico para grafo generado desde Pinecone.
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
            html.H3("🔄 Grafo Generado desde Pinecone", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4(len(entities), className="mb-0 text-light"),
                    html.P("Entidades", className="mb-0")
                ], width=3),
                dbc.Col([
                    html.H4(len(relations), className="text-success"),
                    html.P("Relaciones", className="mb-0")
                ], width=3),
                dbc.Col([
                    html.H4(total_vectors, className="text-info"),
                    html.P("Vectores en BBDD", className="mb-0")
                ], width=3),
                dbc.Col([
                    html.H4(chunks_processed, className="text-warning"),
                    html.P("Chunks procesados", className="mb-0")
                ], width=3)
            ], className="text-center mb-3"),
            
            html.Hr(),
            
            dbc.Alert([
                html.P([
                    "✅ Grafo generado exitosamente desde la base de datos vectorial. ",
                    f"Se analizaron {chunks_processed} fragmentos de texto representativos."
                ], className="mb-0")
            ], color="success"),
            
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

def build_cytoscape_elements(entities, relations):
    """
    Construye elementos de Cytoscape desde entidades y relaciones.
    """
    elements = []
    
    # Agregar nodos (entidades)
    for entity in entities:
        try:
            entity_type = entity.get('type', 'Unknown')
            entity_id = str(entity.get('id', ''))
            entity_label = str(entity.get('text', entity.get('id', 'Sin nombre')))
            
            node_element = {
                'data': {
                    'id': entity_id,
                    'label': entity_label,
                    'type': entity_type
                },
                'classes': f"node-{entity_type.lower()}"
            }
            
            elements.append(node_element)
            
        except Exception as e:
            print(f"❌ Error agregando entidad {entity}: {e}")
            continue
    
    # Agregar aristas (relaciones)
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

        except Exception as e:
            print(f"❌ Error agregando relación {relation}: {e}")
            continue
    
    return elements
    
    # DEBUG: Mostrar tipos de entidades encontrados
    types_found = set()
    for element in elements:
        if 'data' in element and 'type' in element['data']:
            types_found.add(element['data']['type'])
    
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
            html.H3("📊 Estadísticas del Grafo", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4(len(entities), className="mb-0 text-light"),
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
    
    # Buscar embedding relacionado
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
            
            # Embeddings
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
            model="text-embedding-3-small"
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
                        f"{value:.20f}",
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
    
    if not node_id:
        return "No se pudo determinar las conexiones."
    
    try:
        # Obtener datos actuales del OCR
        from callbacks.ocr_callbacks import GRAPH_DATA as OCR_GRAPH_DATA
        relations = OCR_GRAPH_DATA.get('relations', [])
        entities = OCR_GRAPH_DATA.get('entities', [])
        
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
        
    except Exception as e:
        print(f"❌ Error obteniendo conexiones: {e}")
        return [html.P("Error obteniendo conexiones.")]

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