# ./components/graph_view.py
# Componente simplificado que garantiza la visualización

import dash_cytoscape as cyto
from dash import html

def graph_view(elements=[], layout_name="cose", style=None, stylesheet=None):
    """
    Componente simplificado del grafo que garantiza la visualización correcta.
    """
    
    # Estilo del contenedor - FONDO NEGRO GARANTIZADO
    default_style = {
        "width": "100%",
        "height": "700px",
        "backgroundColor": "#0a0e1a",  # Negro profundo
        "borderRadius": "16px",
        "border": "2px solid #334155",
        "boxShadow": "0 10px 40px rgba(0,0,0,0.8)",
        "margin": "auto"
    }
    
    if style:
        default_style.update(style)

    # STYLESHEET PROFESIONAL SIMPLIFICADO
    working_stylesheet = [
        # Nodos base
        {
            "selector": "node",
            "style": {
                "label": "data(label)",
                "width": "60px",
                "height": "60px",
                "background-color": "#3b82f6",  # Azul por defecto
                "color": "#ffffff",
                "font-size": "12px",
                "font-weight": "bold",
                "text-valign": "center",
                "text-halign": "center",
                "text-outline-width": 2,
                "text-outline-color": "#000000",
                "border-width": 3,
                "border-color": "#1e40af",
                "shape": "ellipse"
            }
        },
        
        # Personas - ROJO VIBRANTE
        {
            "selector": "node[type = 'Person']",
            "style": {
                "background-color": "#ef4444",
                "border-color": "#dc2626",
                "shape": "ellipse"
            }
        },
        
        # Organizaciones - VERDE AZULADO
        {
            "selector": "node[type = 'Organization']",
            "style": {
                "background-color": "#10b981",
                "border-color": "#059669",
                "shape": "rectangle"
            }
        },
        
        # Ubicaciones - AZUL
        {
            "selector": "node[type = 'Location']",
            "style": {
                "background-color": "#3b82f6",
                "border-color": "#2563eb",
                "shape": "diamond"
            }
        },
        
        # Industrias - VERDE
        {
            "selector": "node[type = 'Industry'], node[type = 'Concept']",
            "style": {
                "background-color": "#22c55e",
                "border-color": "#16a34a",
                "shape": "hexagon"
            }
        },
        
        # Email/Posición - NARANJA
        {
            "selector": "node[type = 'Email'], node[type = 'Position'], node[type = 'Role']",
            "style": {
                "background-color": "#f59e0b",
                "border-color": "#d97706",
                "shape": "triangle"
            }
        },
        
        # Otros - PÚRPURA
        {
            "selector": "node[type = 'Unknown'], node:untyped",
            "style": {
                "background-color": "#8b5cf6",
                "border-color": "#7c3aed",
                "shape": "octagon"
            }
        },
        
        # Aristas
        {
            "selector": "edge",
            "style": {
                "label": "data(label)",
                "curve-style": "bezier",
                "width": "4px",
                "line-color": "#64748b",
                "target-arrow-color": "#64748b",
                "target-arrow-shape": "triangle",
                "arrow-scale": 1.5,
                "font-size": "10px",
                "color": "#e2e8f0",
                "text-background-color": "rgba(15, 23, 42, 0.8)",
                "text-background-opacity": 1,
                "text-border-width": 1,
                "text-border-color": "#334155"
            }
        },
        
        # Relaciones importantes - ROJO
        {
            "selector": "edge[type = 'works_at'], edge[type = 'located_in']",
            "style": {
                "line-color": "#ef4444",
                "target-arrow-color": "#ef4444",
                "width": "6px"
            }
        },
        
        # Hover effects
        {
            "selector": "node:hover",
            "style": {
                "border-width": "6px",
                "opacity": 0.8
            }
        },
        
        {
            "selector": "node:selected",
            "style": {
                "border-width": "8px",
                "border-color": "#fbbf24"
            }
        }
    ]

    # Layout optimizado
    optimized_layout = {
        'name': layout_name,
        'idealEdgeLength': 100,
        'nodeOverlap': 20,
        'refresh': 20,
        'fit': True,
        'padding': 30,
        'randomize': False,
        'componentSpacing': 100,
        'nodeRepulsion': 400000,
        'edgeElasticity': 100,
        'nestingFactor': 5,
        'gravity': 80,
        'numIter': 1000,
        'initialTemp': 200,
        'coolingFactor': 0.95,
        'minTemp': 1.0
    }

    return html.Div([
        # Leyenda flotante (simplificada)
        html.Div([
            html.H6("🏷️ Leyenda", style={"color": "#e2e8f0", "marginBottom": "10px", "fontSize": "14px"}),
            html.Div([
                html.Div([
                    html.Div(style={
                        "width": "12px", "height": "12px", "borderRadius": "50%",
                        "backgroundColor": "#ef4444", "display": "inline-block", "marginRight": "6px"
                    }),
                    html.Span("Personas", style={"color": "#e2e8f0", "fontSize": "11px"})
                ], style={"marginBottom": "3px", "display": "flex", "alignItems": "center"}),
                
                html.Div([
                    html.Div(style={
                        "width": "12px", "height": "12px", "borderRadius": "2px",
                        "backgroundColor": "#10b981", "display": "inline-block", "marginRight": "6px"
                    }),
                    html.Span("Organizaciones", style={"color": "#e2e8f0", "fontSize": "11px"})
                ], style={"marginBottom": "3px", "display": "flex", "alignItems": "center"}),
                
                html.Div([
                    html.Div(style={
                        "width": "12px", "height": "12px", "transform": "rotate(45deg)",
                        "backgroundColor": "#3b82f6", "display": "inline-block", "marginRight": "6px"
                    }),
                    html.Span("Ubicaciones", style={"color": "#e2e8f0", "fontSize": "11px"})
                ], style={"marginBottom": "3px", "display": "flex", "alignItems": "center"}),
                
                html.Div([
                    html.Div(style={
                        "width": "12px", "height": "12px", "clipPath": "polygon(50% 0%, 0% 100%, 100% 100%)",
                        "backgroundColor": "#22c55e", "display": "inline-block", "marginRight": "6px"
                    }),
                    html.Span("Industrias", style={"color": "#e2e8f0", "fontSize": "11px"})
                ], style={"display": "flex", "alignItems": "center"})
            ])
        ], style={
            "position": "absolute",
            "bottom": "20px",
            "left": "20px",
            "background": "rgba(15, 23, 42, 0.9)",
            "padding": "12px",
            "borderRadius": "8px",
            "border": "1px solid rgba(255, 255, 255, 0.1)",
            "zIndex": 1000,
            "minWidth": "120px",
            "backdropFilter": "blur(10px)"
        }),
        
        # Grafo principal
        cyto.Cytoscape(
            id="knowledge-graph",
            elements=elements,  # Esto será actualizado por el callback
            layout=optimized_layout,
            style=default_style,
            stylesheet=working_stylesheet,
            minZoom=0.1,
            maxZoom=3.0,
            wheelSensitivity=0.1,
            boxSelectionEnabled=True,
            autoungrabify=False,
            autounselectify=False
        )
    ], style={"position": "relative"})