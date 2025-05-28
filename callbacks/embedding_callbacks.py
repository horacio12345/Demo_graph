# ./callbacks/embedding_callbacks.py
# Callbacks para visualización de embedding y control admin (borrado de BBDD)

from dash import Input, Output, State, no_update
from core import embeddings
import dash

def register_embedding_callbacks(app):

    @app.callback(
        Output("progress-info", "children", allow_duplicate=True),
        Input("btn-reset-pinecone", "n_clicks"),
        prevent_initial_call=True
    )
    def reset_pinecone(n_clicks):
        if not n_clicks:
            return no_update
        try:
            embeddings.delete_all_embeddings()
            return "Base de datos Pinecone borrada correctamente."
        except Exception as e:
            return f"Error borrando Pinecone: {e}"