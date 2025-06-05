# ./components/graph_view.py
# Componente con colores CORREGIDOS para los nodos + CACHE STORE

import dash_cytoscape as cyto
from dash import html, dcc

def graph_view(elements=[], layout_name="cose", style=None, stylesheet=None):
    """
    Componente simplificado del grafo que garantiza la visualización correcta.
    Incluye Store para persistencia visual entre pestañas.
    """
    
    # Estilo del contenedor - FONDO NEGRO GARANTIZADO
    default_style = {
        "width": "100%",
        "height": "630px",
        "backgroundColor": "#0a0e1a",  # Negro profundo
        "borderRadius": "16px",
        "border": "2px solid #334155",
        "boxShadow": "0 10px 40px rgba(0,0,0,0.8)",
        "margin": "auto"
    }
    
    if style:
        default_style.update(style)

    # STYLESHEET PROFESIONAL - SELECTORES CORREGIDOS
    working_stylesheet = [
        # Nodos base - COLOR AZUL POR DEFECTO
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
        
        # ===== SELECTORES CORREGIDOS POR TIPO =====
        
        # Personas - ROJO VIBRANTE
        {
            "selector": "node[type = \"Person\"]",  # Comillas dobles escapadas
            "style": {
                "background-color": "#ef4444",
                "border-color": "#dc2626",
                "shape": "ellipse"
            }
        },
        
        # Organizaciones - VERDE AZULADO  
        {
            "selector": "node[type = \"Organization\"]",
            "style": {
                "background-color": "#10b981",
                "border-color": "#059669", 
                "shape": "rectangle"
            }
        },
        
        # Ubicaciones - AZUL
        {
            "selector": "node[type = \"Location\"]",
            "style": {
                "background-color": "#3b82f6",
                "border-color": "#2563eb",
                "shape": "diamond"
            }
        },
        
        # Industrias y Conceptos - VERDE CLARO
        {
            "selector": "node[type = \"Industry\"]",
            "style": {
                "background-color": "#22c55e",
                "border-color": "#16a34a",
                "shape": "hexagon"
            }
        },
        {
            "selector": "node[type = \"Concept\"]", 
            "style": {
                "background-color": "#22c55e",
                "border-color": "#16a34a",
                "shape": "hexagon"
            }
        },
        
        # Email, Posición, Roles - NARANJA
        {
            "selector": "node[type = \"Email\"]",
            "style": {
                "background-color": "#f59e0b",
                "border-color": "#d97706",
                "shape": "triangle"
            }
        },
        {
            "selector": "node[type = \"Position\"]",
            "style": {
                "background-color": "#f59e0b",
                "border-color": "#d97706", 
                "shape": "triangle"
            }
        },
        {
            "selector": "node[type = \"Role\"]",
            "style": {
                "background-color": "#f59e0b",
                "border-color": "#d97706",
                "shape": "triangle"  
            }
        },
        
        # Unknown y otros - PÚRPURA (solo para tipos realmente desconocidos)
        {
            "selector": "node[type = \"Unknown\"]",
            "style": {
                "background-color": "#8b5cf6",
                "border-color": "#7c3aed",
                "shape": "octagon"
            }
        },
        
        # ===== SELECTORES ALTERNATIVOS POR CLASE CSS =====
        # Por si los selectores de tipo no funcionan, usar clases
        
        {
            "selector": ".node-person",
            "style": {
                "background-color": "#ef4444",
                "border-color": "#dc2626",
                "shape": "ellipse"
            }
        },
        {
            "selector": ".node-organization", 
            "style": {
                "background-color": "#10b981",
                "border-color": "#059669",
                "shape": "rectangle"
            }
        },
        {
            "selector": ".node-location",
            "style": {
                "background-color": "#3b82f6", 
                "border-color": "#2563eb",
                "shape": "diamond"
            }
        },
        {
            "selector": ".node-industry",
            "style": {
                "background-color": "#22c55e",
                "border-color": "#16a34a", 
                "shape": "hexagon"
            }
        },
        {
            "selector": ".node-concept",
            "style": {
                "background-color": "#22c55e",
                "border-color": "#16a34a",
                "shape": "hexagon"
            }
        },
        {
            "selector": ".node-email",
            "style": {
                "background-color": "#f59e0b",
                "border-color": "#d97706",
                "shape": "triangle"
            }
        },
        {
            "selector": ".node-position",
            "style": {
                "background-color": "#f59e0b", 
                "border-color": "#d97706",
                "shape": "triangle"
            }
        },
        {
            "selector": ".node-role",
            "style": {
                "background-color": "#f59e0b",
                "border-color": "#d97706", 
                "shape": "triangle"
            }
        },
        
        # ===== ARISTAS =====
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
            "selector": "edge[type = \"works_at\"]",
            "style": {
                "line-color": "#ef4444",
                "target-arrow-color": "#ef4444",
                "width": "6px"
            }
        },
        {
            "selector": "edge[type = \"located_in\"]",
            "style": {
                "line-color": "#ef4444",
                "target-arrow-color": "#ef4444", 
                "width": "6px"
            }
        },
        
        # ===== EFECTOS HOVER =====
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

        # PLACEHOLDER PARA LEYENDA DINÁMICA - se llenará desde callback
        html.Div(
            id="dynamic-legend",
            style={
                "position": "absolute",
                "bottom": "20px",
                "left": "20px",
                "zIndex": 1000
            }
        ),
        
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