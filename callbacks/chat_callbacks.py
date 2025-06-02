# ./callbacks/chat_callbacks.py
# Callbacks para el sistema de chat RAG educativo - VERSIÓN CORREGIDA

from dash import Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate
import logging
from datetime import datetime

from components.chat_interface import (
    create_user_message, 
    create_bot_message, 
    create_loading_message, 
    create_error_message
)
from components.rag_process_panel import (
    create_processing_state,
    create_complete_process_view,
    create_initial_state
)
from core.rag_orchestrator import rag_orchestrator

logger = logging.getLogger(__name__)


def register_chat_callbacks(app):
    @app.callback(
        [Output("chat-conversation", "children"),
         Output("chat-status", "children"),
         Output("rag-process-content", "children"),
         Output("rag-process-data", "data"),
         Output("chat-input", "value")],
        [Input("chat-send-btn", "n_clicks")],
        [State("chat-input", "value"),
         State("chat-llm-selector", "value"),
         State("chat-conversation", "children"),
         State("rag-process-data", "data")],
        prevent_initial_call=True
    )
    def handle_chat_message(n_clicks, question, llm_method, current_conversation, current_rag_data):
        if not n_clicks or not question or not question.strip():
            raise PreventUpdate
        
        question = question.strip()
        logger.info(f"Processing chat question: {question[:50]}...")
        
        try:
            new_conversation = current_conversation.copy() if current_conversation else []
            new_conversation.append(create_user_message(question))
            new_conversation.append(create_loading_message())
            
            # Ejecutar proceso RAG directamente aquí
            try:
                result = rag_orchestrator.process_question(question, llm_method or "openai")
                logger.info(f"RAG processing completed: success={result.get('success')}")
                
                # Remover mensaje de loading
                if new_conversation and "Procesando tu pregunta" in str(new_conversation[-1]):
                    new_conversation.pop()
                
                if result.get("success"):
                    answer = result.get("final_answer", "No se pudo generar respuesta")
                    new_conversation.append(create_bot_message(answer, show_process=True))
                    process_panel = create_complete_process_view(result)
                    status = "✅ Respuesta generada correctamente"
                else:
                    error_msg = result.get("error", "Error desconocido en el proceso RAG")
                    new_conversation.append(create_error_message(error_msg))
                    from components.rag_process_panel import create_error_view
                    process_panel = create_error_view(error_msg)
                    status = "❌ Error en el proceso RAG"
                
                updated_rag_data = result.copy()
                updated_rag_data["processing"] = False
                
                return (new_conversation, status, process_panel, updated_rag_data, "")
                
            except Exception as e:
                logger.error(f"Error in RAG processing: {e}")
                if new_conversation and "Procesando tu pregunta" in str(new_conversation[-1]):
                    new_conversation.pop()
                error_msg = f"Error procesando pregunta: {str(e)}"
                new_conversation.append(create_error_message(error_msg))
                from components.rag_process_panel import create_error_view
                error_panel = create_error_view(error_msg)
                return (new_conversation, "❌ Error en procesamiento", error_panel, {"error": str(e), "processing": False}, question)
                
        except Exception as e:
            logger.error(f"Error in chat callback: {e}")
            error_conversation = current_conversation.copy() if current_conversation else []
            error_conversation.append(create_error_message(f"Error procesando mensaje: {str(e)}"))
            return (
                error_conversation,
                "❌ Error procesando mensaje",
                create_initial_state(),
                {},
                question
            )
    
    @app.callback(
        Output("chat-input", "value", allow_duplicate=True),
        Input("chat-input", "n_submit"),
        State("chat-input", "value"),
        prevent_initial_call=True
    )
    def handle_enter_key(n_submit, current_value):
        if n_submit and current_value and current_value.strip():
            return current_value
        raise PreventUpdate
    
    @app.callback(
        Output("chat-send-btn", "n_clicks", allow_duplicate=True),
        Input("chat-input", "n_submit"),
        State("chat-send-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def trigger_send_on_enter(n_submit, current_clicks):
        if n_submit:
            return (current_clicks or 0) + 1
        raise PreventUpdate
    
    @app.callback(
        [Output("chat-conversation", "children", allow_duplicate=True),
         Output("rag-process-content", "children", allow_duplicate=True)],
        Input("show-process-btn", "n_clicks"),
        State("rag-process-data", "data"),
        prevent_initial_call=True
    )
    def show_detailed_process(n_clicks, rag_data):
        if not n_clicks or not rag_data:
            raise PreventUpdate
        detailed_panel = create_complete_process_view(rag_data)
        return (no_update, detailed_panel)
    
    @app.callback(
        Output("chat-status", "children", allow_duplicate=True),
        [Input("chat-input", "value")],
        prevent_initial_call=True
    )
    def update_chat_status(input_value):
        if not input_value or not input_value.strip():
            return "💤 Esperando pregunta..."
        char_count = len(input_value.strip())
        if char_count < 10:
            return "✏️ Escribe una pregunta más específica..."
        elif char_count > 500:
            return "⚠️ Pregunta muy larga, será truncada"
        else:
            return "✅ Pregunta lista para enviar"
    
    @app.callback(
        [Output("rag-process-content", "children", allow_duplicate=True),
         Output("rag-process-data", "data", allow_duplicate=True)],
        Input("url", "pathname"),
        prevent_initial_call=True
    )
    def init_chat_page_panel(pathname):
        if pathname == "/chat":
            try:
                from core.embeddings import get_index_stats
                stats = get_index_stats()
                total_vectors = stats.get('total_vector_count', 0)
                
                if total_vectors == 0:
                    panel = create_initial_state()
                else:
                    panel = create_initial_state()
                
                return (panel, {})
                
            except Exception as e:
                logger.error(f"Error checking documents: {e}")
                return (create_initial_state(), {})
        
        raise PreventUpdate

    logger.info("Chat callbacks registered successfully")