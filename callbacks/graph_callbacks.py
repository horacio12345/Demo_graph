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

def register_graph_callbacks(app):
    
    @app.callback(
        [Output("knowledge-graph", "elements"),
         Output("embedding-panel", "children")],
        [Input("progress-info", "children")],
        prevent_initial_call=True
    )
    def update_graph_and_panel(progress_message):
        """
        Actualiza el grafo cuando se completa el procesamiento.
        """
        global GRAPH_DATA
        
        print(f"🔄 Callback activado con mensaje: {progress_message}")
        
        # Verificar si hay mensaje de éxito con entidades/relaciones
        if not progress_message or "entidades" not in str(progress_message):
            print("⚠️ No hay datos de entidades en el mensaje")
            return [], create_empty_panel()
        
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
                return [], create_no_data_panel()
            
            # Construir elementos para Cytoscape
            elements = build_cytoscape_elements(entities, relations)
            print(f"✅ Elementos creados: {len(elements)}")
            
            # Crear panel de información
            info_panel = create_graph_info_panel(entities, relations)
            
            return elements, info_panel
            
        except Exception as e:
            print(f"❌ Error en callback del grafo: {e}")
            import traceback
            traceback.print_exc()
            return [], create_error_panel(str(e))
    
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

def build_cytoscape_elements(entities, relations):
    """
    Construye elementos de Cytoscape desde entidades y relaciones.
    """
    elements = []
    
    print(f"🔧 Construyendo elementos...")
    print(f"📝 Entidades de ejemplo: {entities[:2] if entities else 'Ninguna'}")
    print(f"🔗 Relaciones de ejemplo: {relations[:2] if relations else 'Ninguna'}")
    
    # Agregar nodos (entidades)
    for entity in entities:
        try:
            node_element = {
                'data': {
                    'id': str(entity.get('id', '')),
                    'label': str(entity.get('text', entity.get('id', 'Sin nombre'))),
                    'type': str(entity.get('type', 'Unknown'))
                },
                'classes': f"node-{entity.get('type', 'unknown').lower()}"
            }
            elements.append(node_element)
            print(f"✅ Nodo agregado: {node_element['data']['label']} ({node_element['data']['type']})")
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
                print(f"✅ Arista agregada: {source_id} → {target_id} ({edge_element['data']['label']})")
            else:
                print(f"⚠️ Relación ignorada - nodos no encontrados: {source_id} → {target_id}")
        except Exception as e:
            print(f"❌ Error agregando relación {relation}: {e}")
            continue
    
    print(f"🎯 Total elementos creados: {len(elements)}")
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

def create_node_detail_panel(node_data):
    """
    Panel detallado para nodo seleccionado.
    """
    from dash import html
    import dash_bootstrap_components as dbc
    
    # Colores por tipo
    type_colors = {
        'Person': 'danger',
        'Organization': 'info', 
        'Location': 'primary',
        'Industry': 'success',
        'Concept': 'success',
        'Email': 'warning',
        'Position': 'warning',
        'Role': 'warning',
        'Unknown': 'secondary'
    }
    
    node_type = node_data.get('type', 'Unknown')
    color = type_colors.get(node_type, 'secondary')
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5([
                dbc.Badge(node_type, color=color, className="me-2"),
                node_data.get('label', 'Sin nombre')
            ], className="mb-0")
        ]),
        dbc.CardBody([
            html.P([
                html.Strong("ID: "),
                html.Code(node_data.get('id', 'N/A'))
            ]),
            html.P([
                html.Strong("Tipo: "),
                node_data.get('type', 'Desconocido')
            ]),
            html.P([
                html.Strong("Etiqueta: "),
                node_data.get('label', 'Sin etiqueta')
            ]),
            
            # Buscar relaciones de este nodo
            html.Hr(),
            html.H6("🔗 Conexiones:"),
            html.Div(id="node-connections", children=get_node_connections(node_data.get('id')))
        ])
    ], className="mt-3")

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