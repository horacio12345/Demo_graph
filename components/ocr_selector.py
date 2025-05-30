# ./components/ocr_selector.py
# Dropdown selector para elegir el motor OCR (Mistral o Tesseract)

from dash import dcc, html

def ocr_selector(default='docling'):
    return html.Div([
        html.Label("Selecciona el procesador de texto:", style={
            'fontSize': '0.9rem',  # Tamaño de letra más pequeño
            'marginBottom': '8px',
            'display': 'block'
        }),
        dcc.Dropdown(
            id='ocr-method',
            options=[
                {'label': 'Docling', 'value': 'docling'},
                {'label': 'Tesseract', 'value': 'tesseract'}
            ],
            value=default,
            clearable=False,
            style={'width': '100%', 'margin-bottom': '10px'}
        )
    ])