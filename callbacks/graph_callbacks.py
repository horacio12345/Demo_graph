# ./callbacks/graph_callbacks.py
# Callbacks para la visualización/interacción del grafo (y panel de detalles)

from dash import Input, Output, State, no_update
from core import graph_builder
import dash

def register_graph_callbacks(app):

    @app.callback(
        Output("knowledge-graph", "elements"),
        Input("progress-info", "children"),
        State("progress-info", "children"),
        prevent_initial_call=True
    )
    def update_graph(progress, prev_progress):
        # Se asume que las entidades y relaciones están en una variable global (ajustar a tu pipeline)
        from flask import g
        entities, relations = getattr(g, "entities", []), getattr(g, "relations", [])
        G = graph_builder.build_knowledge_graph(entities, relations)
        elements = graph_builder.to_cytoscape_elements(G)
        return elements

    @app.callback(
        Output("embedding-panel", "children"),
        Input("knowledge-graph", "tapNodeData"),
        prevent_initial_call=True
    )
    def show_node_embedding(node_data):
        if not node_data:
            return "Selecciona un nodo para ver el embedding y chunk."
        # Aquí puedes recuperar el chunk y embedding real desde Pinecone/db usando el node_id
        # Demo: mostramos dummy
        return f"Detalles de nodo: {node_data}"