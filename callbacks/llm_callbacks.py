# ./callbacks/llm_callbacks.py
# Callbacks para extracción de entidades/relaciones por LLM a partir de los chunks

from dash import Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate
from core import llm, utils
import dash

def register_llm_callbacks(app):

    @app.callback(
        Output("progress-info", "children", allow_duplicate=True),
        Input("llm-method", "value"),
        State("progress-info", "children"),
        prevent_initial_call=True
    )
    def process_llm(llm_method, prev_status):
        # Aquí deberías tener acceso a los chunks generados (en memoria o disco temporal)
        # Por demo, se asume una variable global o cache (ajustar a tu flujo real)
        from flask import g
        chunks = getattr(g, "chunks", None)
        if not chunks:
            return no_update
        try:
            all_entities, all_relations = [], []
            for chunk in chunks:
                out = llm.extract_entities_relations(chunk, llm_method=llm_method)
                all_entities.extend(out.get("entities", []))
                all_relations.extend(out.get("relations", []))
            g.entities, g.relations = all_entities, all_relations
            return f"Extracción LLM completa. {len(all_entities)} entidades, {len(all_relations)} relaciones."
        except Exception as e:
            return f"Error en LLM: {e}"