# ./components/llm_selector.py
# Dropdown selector para elegir el modelo LLM (OpenAI o Claude)

from dash import dcc, html

def llm_selector(default='openai'):
    return html.Div([
        html.Label("Selecciona el LLM:"),
        dcc.Dropdown(
            id='llm-method',
            options=[
                {'label': 'OpenAI GPT-4o', 'value': 'openai'},
                {'label': 'Claude Sonnet 4', 'value': 'claude'}
            ],
            value=default,
            clearable=False,
            style={'width': '100%', 'margin-bottom': '10px'}
        )
    ])