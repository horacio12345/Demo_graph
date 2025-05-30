# ./app.py
# Entry point de la aplicación Dash: layout principal y registro de callbacks

from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from components.upload_component import upload_component
from components.ocr_selector import ocr_selector
from components.llm_selector import llm_selector
from components.progress_bar import progress_bar
from components.graph_view import graph_view
from components.embedding_view import embedding_view

from callbacks.ocr_callbacks import register_ocr_callbacks
from callbacks.llm_callbacks import register_llm_callbacks
from callbacks.graph_callbacks import register_graph_callbacks
from callbacks.embedding_callbacks import register_embedding_callbacks

import os

app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR], suppress_callback_exceptions=True)

# ---- Layout principal ----
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("RAG Demo - Knowledge Graph Extraction", style={'color': 'black'}),
            html.Hr(),
            upload_component(),
            ocr_selector(),
            llm_selector(),
            progress_bar(),
            html.Button("Reset Pinecone", id="btn-reset-pinecone", n_clicks=0, style={
                "margin": "8px 0", "background": "#e11d48", "color": "white", "borderRadius": "8px"
            }),
        ], width=3, style={"backgroundColor": "#f8fafc", "padding": "16px", "borderRadius": "12px", "minHeight": "96vh"}),
        dbc.Col([
            graph_view(),
            html.Div(id="embedding-panel", style={"marginTop": "32px"})
        ], width=9, style={"padding": "24px"})
    ])
], fluid=True, style={"background": "#f1f5f9", "minHeight": "100vh"})

# ---- Registro de callbacks ----
register_ocr_callbacks(app)
register_llm_callbacks(app)
register_graph_callbacks(app)
register_embedding_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=False)