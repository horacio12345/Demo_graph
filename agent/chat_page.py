# ./agent/chat_page.py
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.chat_interface import chat_interface
from components.rag_process_panel import rag_process_panel
from components.llm_selector import llm_selector # Importar si lo usas directamente aquí

def layout():
    """
    Define el layout para la página de chat RAG educativo.
    NOTA: Los stores principales se definen en app.py para compartir entre pestañas.
    """
    return dbc.Container([       
        dcc.Store(id='rag-process-data', storage_type='memory', data={}),  

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
        className="mt-4",  # Añadido margen superior aquí
        style={"height": "calc(100vh - 100px)"} # Altura total de la fila de contenido
        )

    ], fluid=True, style={"height": "100vh", "paddingTop": "20px", "background": "#f1f5f9"})