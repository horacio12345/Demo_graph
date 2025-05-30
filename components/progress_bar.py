# ./components/progress_bar.py
# Barra de progreso para mostrar avance del procesamiento de documentos

from dash import dcc, html

def progress_bar():
    return html.Div([
        html.Label("Progreso del procesamiento:", style={
            'color': '#64748B',  # Gris oscuro
            'fontSize': '0.9rem',  # Tamaño de letra más pequeño
            'marginBottom': '8px',
            'display': 'block'
        }),
        dcc.Loading(
            id="loading-progress",
            type="default",
            children=html.Div(id="progress-info")
        )
    ], style={'margin-bottom': '24px'})