# ./agent/chat_page.py
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.chat_interface import chat_interface
from components.rag_process_panel import rag_process_panel
from components.llm_selector import llm_selector # Importar si lo usas directamente aquí

def layout():
    """
    Define el layout para la página de chat RAG educativo.
    """
    return dbc.Container([
        # Puedes añadir un dcc.Store aquí para rag-process-data si no lo tienes globalmente
        # dcc.Store(id='rag-process-data'), # Necesario para los callbacks del chat

        dbc.Row([
            html.H2("🤖 Chat RAG Educativo", className="my-4 text-center"),
        ]),
        dbc.Row([
            dbc.Col(
                chat_interface(),  # Tu componente de interfaz de chat
                md=5,
                style={
                    "height": "calc(100vh - 150px)", # Ajusta la altura según necesites
                    "display": "flex",
                    "flexDirection": "column"
                }
            ),
            dbc.Col(
                rag_process_panel(), # Tu panel de proceso RAG
                md=7,
                style={
                    "height": "calc(100vh - 150px)", # Ajusta la altura según necesites
                    "overflowY": "auto",
                    "paddingLeft": "20px" # Un poco de espacio entre columnas
                }
            )
        ],
        # className="g-0" # Descomenta si quieres que las columnas se peguen sin espacio
        style={"height": "calc(100vh - 100px)"} # Altura total de la fila de contenido
        ),
        # Importante: Incluir el dcc.Store si los callbacks de chat lo necesitan aquí
        # Si 'rag-process-data' es usado por callbacks que solo se activan en esta página,
        # es buena práctica incluirlo en el layout de esta página.
        # Si ya está en el layout principal y es global, no es necesario duplicarlo.
        # Por la estructura de tus callbacks, parece que es mejor que esté disponible cuando esta página cargue.
        dcc.Store(id='rag-process-data')

    ], fluid=True, style={"height": "100vh", "paddingTop": "20px"})