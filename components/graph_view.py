# ./components/graph_view.py
# Componente para la visualización del grafo de conocimiento usando Dash Cytoscape

import dash_cytoscape as cyto
from dash import html

def graph_view(elements=[], layout_name="cose", style=None, stylesheet=None):
    default_style = {
        "width": "100%",
        "height": "700px",
        "backgroundColor": "#1e293b",
        "borderRadius": "16px",
        "boxShadow": "0 4px 32px rgba(0,0,0,0.3)",
        "margin": "auto"
    }
    if style:
        default_style.update(style)

    # Estilos visuales y coloridos para nodos/aristas
    default_stylesheet = [
        {
            "selector": "node",
            "style": {
                "label": "data(label)",
                "background-color": "#0ea5e9",
                "color": "#fff",
                "font-size": "18px",
                "text-outline-width": 2,
                "text-outline-color": "#2563eb",
                "border-width": 3,
                "border-color": "#2563eb",
                "width": "48px",
                "height": "48px",
                "shape": "ellipse",
                "text-valign": "center"
            },
        },
        {
            "selector": "node[type = 'Person']",
            "style": {
                "background-color": "#facc15",
                "text-outline-color": "#eab308",
            }
        },
        {
            "selector": "node[type = 'Organization']",
            "style": {
                "background-color": "#34d399",
                "text-outline-color": "#059669",
            }
        },
        {
            "selector": "node[type = 'Location']",
            "style": {
                "background-color": "#818cf8",
                "text-outline-color": "#6366f1",
            }
        },
        {
            "selector": "edge",
            "style": {
                "label": "data(label)",
                "curve-style": "bezier",
                "width": 3,
                "line-color": "#e11d48",
                "target-arrow-color": "#e11d48",
                "target-arrow-shape": "triangle-backcurve",
                "arrow-scale": 2,
                "font-size": "14px",
                "text-background-color": "#f3f4f6",
                "text-background-opacity": 0.8,
                "color": "#111827",
            }
        }
    ]
    # Permite personalización de estilos externos
    used_stylesheet = stylesheet or default_stylesheet

    return html.Div([
        cyto.Cytoscape(
            id="knowledge-graph",
            elements=elements,
            layout={'name': layout_name},
            style=default_style,
            stylesheet=used_stylesheet,
            minZoom=0.15,
            maxZoom=2.5
        )
    ])