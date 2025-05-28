# ./components/embedding_view.py
# Panel visual para mostrar el embedding de un chunk (primeros 50 valores, gráfico de barras)

from dash import dcc, html
import plotly.graph_objs as go

def embedding_view(embedding, chunk_text=None, vector_id=None):
    """
    Muestra los primeros 50 valores del embedding en un gráfico de barras.
    """
    if embedding is None:
        return html.Div("No hay embedding seleccionado.")
    embedding_short = embedding[:50]  # Solo los primeros 50
    bar = go.Bar(y=embedding_short, marker=dict(color="#6366f1"))
    layout = go.Layout(
        title="Embedding (primeros 50 valores)",
        xaxis=dict(title="Dimensión"),
        yaxis=dict(title="Valor"),
        height=280,
        margin=dict(l=32, r=32, t=40, b=32)
    )
    return html.Div([
        html.H5("Embedding del chunk"),
        html.Pre(chunk_text, style={"backgroundColor": "#f1f5f9", "padding": "8px"}) if chunk_text else None,
        html.Small(f"Vector ID: {vector_id}") if vector_id else None,
        dcc.Graph(figure=go.Figure(data=[bar], layout=layout))
    ], style={'backgroundColor': '#f9fafb', 'padding': '12px', 'borderRadius': '12px', 'boxShadow': '0 1px 8px #ddd'})