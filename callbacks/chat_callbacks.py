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
    def handle_chat_message(n_clicks, question, llm_method, current_conversation_children, current_rag_data):
        if not n_clicks or not question or not question.strip():
            raise PreventUpdate
        
        question = question.strip()
        logger.info(f"Processing chat question: {question[:50]} with LLM: {llm_method}")
        
        # Determinar la conversación actual, manejando el placeholder inicial
        new_conversation = []
        if current_conversation_children and isinstance(current_conversation_children, list):
            is_placeholder = False
            if len(current_conversation_children) == 1 and isinstance(current_conversation_children[0], dict):
                try:
                    component_props = current_conversation_children[0].get('props', {})
                    if component_props:
                        children_of_component = component_props.get('children', [])
                        if children_of_component and isinstance(children_of_component, list) and len(children_of_component) == 1:
                            p_component = children_of_component[0]
                            if isinstance(p_component, dict):
                                p_props = p_component.get('props', {})
                                if p_props:
                                    placeholder_text = p_props.get('children', '')
                                    if placeholder_text == "Aquí verás la respuesta a tu pregunta...":
                                        is_placeholder = True
                except Exception as e:
                    logger.debug(f"Error checking placeholder: {e}")
                    pass 
            if not is_placeholder:
                new_conversation = current_conversation_children.copy()
        
        # Añadir mensaje del usuario a la conversación
        new_conversation.append(create_user_message(question))
        
        # (Opcional) Aquí se podría añadir un mensaje de carga si se desea una respuesta en dos pasos
        # Por ahora, se llamará directamente al orchestrator.

        try:
            # Llamar al RAG orchestrator para obtener la respuesta del LLM
            logger.info(f"Calling RAG orchestrator for: {question[:30]}")
            result = rag_orchestrator.process_question(question, llm_method or "default_llm") # Asegúrate que llm_method tenga un valor
            logger.info(f"RAG orchestrator result: Success={result.get('success')}")

            if result.get("success"):
                bot_answer = result.get("answer", "No se pudo generar una respuesta del LLM.")
                new_conversation.append(create_bot_message(bot_answer, show_process=True))
                
                rag_steps_data = result.get("rag_steps", {})
                rag_panel_content = create_complete_process_view(rag_steps_data)
                status_message = "✅ Pregunta respondida por el LLM"
                rag_data_to_store = rag_steps_data
            else:
                error_msg = result.get("error", "Error desconocido del RAG orchestrator.")
                new_conversation.append(create_error_message(error_msg))
                rag_panel_content = create_initial_state() # O un panel de error específico
                status_message = f"❌ Error RAG: {error_msg[:50]}"
                rag_data_to_store = {"error": error_msg}
        
        except Exception as e:
            logger.error(f"Exception calling RAG orchestrator or processing its result: {e}", exc_info=True)
            critical_error_msg = f"Error crítico en el servidor: {str(e)[:100]}"
            new_conversation.append(create_error_message(critical_error_msg))
            rag_panel_content = create_initial_state() # O un panel de error crítico
            status_message = "❌ Error Crítico en el Servidor"
            rag_data_to_store = {"error": critical_error_msg}

        return (
            new_conversation,
            status_message,
            rag_panel_content,
            rag_data_to_store,
            ""  # Limpiar el campo de entrada
        )

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