# ./core/graph_builder.py
# Lógica para construir un grafo de entidades y relaciones a partir de la salida del LLM

import networkx as nx

def build_knowledge_graph(entities, relations):
    """
    Crea y retorna un objeto NetworkX dirigido (DiGraph) a partir de entidades y relaciones.
    """
    G = nx.DiGraph()
    # Añade nodos con su metadata
    for ent in entities:
        G.add_node(ent["id"], label=ent.get("text", ""), type=ent.get("type", "Entity"))
    # Añade aristas con metadata
    for rel in relations:
        G.add_edge(rel["source_id"], rel["target_id"], label=rel.get("type", ""), text=rel.get("text", ""))
    return G

def to_cytoscape_elements(G):
    """
    Convierte el grafo NetworkX a elementos para Dash Cytoscape.
    """
    elements = []
    for node_id, data in G.nodes(data=True):
        elements.append({
            "data": {"id": node_id, "label": data.get("label", node_id), "type": data.get("type", "Entity")}
        })
    for source, target, data in G.edges(data=True):
        elements.append({
            "data": {
                "source": source,
                "target": target,
                "label": data.get("label", ""),
                "text": data.get("text", "")
            }
        })
    return elements