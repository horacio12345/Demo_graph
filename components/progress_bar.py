# ./components/progress_bar.py
# Barra de progreso para mostrar avance del procesamiento de documentos

from dash import dcc, html

def progress_bar():
    return html.Div([
        html.Label("Progreso del procesamiento:"),
        dcc.Loading(
            id="loading-progress",
            type="default",
            children=html.Div(id="progress-info")
        )
    ], style={'margin-bottom': '24px'})