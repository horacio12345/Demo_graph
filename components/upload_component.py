# ./components/upload_component.py
# Componente de Dash para la subida de documentos locales o por link web

from dash import dcc, html

def upload_component():
    return html.Div([
        html.H4("Sube tu documento o ingresa un enlace"),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Arrastra o ',
                html.A('selecciona un archivo')
            ]),
            style={
                'width': '100%',
                'height': '80px',
                'lineHeight': '80px',
                'borderWidth': '2px',
                'borderStyle': 'dashed',
                'borderRadius': '10px',
                'textAlign': 'center',
                'margin-bottom': '10px',
                'backgroundColor': '#f3f4f6'
            },
            multiple=False
        ),
        html.Div([
            dcc.Input(
                id='input-url',
                type='url',
                placeholder='...o pega aquí un enlace a un PDF o imagen',
                style={'width': '100%', 'padding': '8px', 'margin-top': '8px'}
            ),
            html.Button('Procesar enlace', id='process-url-btn', n_clicks=0, style={
                'width': '100%', 'margin-top': '8px'
            })
        ])
    ], style={'margin-bottom': '32px'})