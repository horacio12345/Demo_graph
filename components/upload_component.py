# ./components/upload_component.py
# Componente de Dash para la subida de documentos locales o por link web

from dash import dcc, html

def upload_component():
    return html.Div([
        html.Div(className="upload-area", children=[
            dcc.Upload(
                id='upload-data',
                className='upload-area',
                children=html.Div(
                    'Arrastra o selecciona un archivo', 
                    style={'color': 'var(--accent-blue)', 'textDecoration': 'underline'}
                ),
                style={
                    'width': '100%',
                    'height': '100%',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'cursor': 'pointer',
                    'border': 'none',
                    'background': 'transparent',
                    'padding': '20px',
                    'textAlign': 'center',
                    'fontSize': '1rem',
                    'transition': 'var(--transition)'
                },
                multiple=False
            ),
        ]),
        html.Div([
            dcc.Input(
                id='input-url',
                type='url',
                placeholder='...o pega aquí el enlace a un texto',
                style={
                    'width': '100%',
                    'maxWidth': '100%',  
                    'boxSizing': 'border-box',  
                    'padding': '12px',
                    'margin': '16px 0 8px 0',
                    'borderRadius': 'var(--border-radius)',
                    'border': '1px solid var(--bg-tertiary)',
                    'background': 'var(--bg-secondary)',
                    'color': 'var(--text-primary)',
                    'fontSize': '0.95rem',
                    'transition': 'var(--transition)'
                }
            ),
            html.Button('Procesar enlace', 
                id='process-url-btn', 
                n_clicks=0, 
                className='btn btn-primary',
                style={
                    'width': '100%',
                    'margin': '8px 0',
                    'padding': '12px',
                    'fontWeight': '500',
                    'borderRadius': 'var(--border-radius)',
                    'border': 'none',
                    'cursor': 'pointer',
                    'transition': 'var(--transition)',
                    'background': 'var(--accent-blue)',
                    'color': 'white'
                }
            )
        ])
    ], style={'marginBottom': '24px'})