# ./callbacks/ocr_callbacks.py
# Callbacks para procesar archivos subidos/enlaces y lanzar OCR+chunking

from dash import Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate
import dash
import base64
import os
import tempfile
from core import ocr, utils

def register_ocr_callbacks(app):

    @app.callback(
        Output("progress-info", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("ocr-method", "value"),
        prevent_initial_call=True
    )
    def handle_uploaded_file(contents, filename, ocr_method):
        if not contents or not filename:
            raise PreventUpdate

        # Guarda archivo temporalmente
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        tmp_path = utils.get_temp_file_path(suffix=utils.get_file_extension(filename))
        with open(tmp_path, "wb") as f:
            f.write(decoded)

        # Ejecuta OCR (elige motor)
        try:
            text = ocr.extract_text(tmp_path, ocr_method=ocr_method)
            # Chunking semántico (usa OpenAI key del entorno)
            from core.utils import clean_text
            from core.ocr import chunk_text_semantic
            from dotenv import load_dotenv
            load_dotenv()
            import os
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            chunks = chunk_text_semantic(clean_text(text), OPENAI_API_KEY)
            return f"Documento procesado. {len(chunks)} chunks extraídos."
        except Exception as e:
            return f"Error en OCR: {e}"

    @app.callback(
        Output("progress-info", "children", allow_duplicate=True),
        Input("process-url-btn", "n_clicks"),
        State("input-url", "value"),
        State("ocr-method", "value"),
        prevent_initial_call=True
    )
    def handle_url_upload(n_clicks, url, ocr_method):
        if not n_clicks or not url:
            raise PreventUpdate
        # Descarga archivo a temporal
        try:
            tmp_path = utils.get_temp_file_path(suffix=".pdf")
            import requests
            r = requests.get(url)
            if r.status_code == 200:
                with open(tmp_path, "wb") as f:
                    f.write(r.content)
                text = ocr.extract_text(tmp_path, ocr_method=ocr_method)
                from core.utils import clean_text
                from core.ocr import chunk_text_semantic
                from dotenv import load_dotenv
                load_dotenv()
                OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
                chunks = chunk_text_semantic(clean_text(text), OPENAI_API_KEY)
                return f"Documento web procesado. {len(chunks)} chunks extraídos."
            else:
                return f"Error al descargar archivo: status {r.status_code}"
        except Exception as e:
            return f"Error procesando enlace: {e}"