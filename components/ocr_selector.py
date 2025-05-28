# ./components/ocr_selector.py
# Dropdown selector para elegir el motor OCR (Mistral o Tesseract)

from dash import dcc, html

def ocr_selector(default='mistral'):
    return html.Div([
        html.Label("Selecciona el motor OCR:"),
        dcc.Dropdown(
            id='ocr-method',
            options=[
                {'label': 'Mistral OCR (API)', 'value': 'mistral'},
                {'label': 'Tesseract OCR (Local)', 'value': 'tesseract'}
            ],
            value=default,
            clearable=False,
            style={'width': '100%', 'margin-bottom': '10px'}
        )
    ])