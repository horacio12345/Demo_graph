def register_chat_callbacks(app):
    
    # ⭐ CALLBACK PRINCIPAL - CON MANEJO ROBUSTO DE ERRORES ⭐
    @app.callback(
        [Output("chat-conversation", "children", allow_duplicate=True),
         Output("chat-status", "children", allow_duplicate=True),
         Output("rag-process-content", "children", allow_duplicate=True),
         Output("rag-process-data", "data", allow_duplicate=True),
         Output("chat-input", "value", allow_duplicate=True)],
        [Input("chat-send-btn", "n_clicks")],
        [State("chat-input", "value"),
         State("chat-llm-selector", "value"),
         State("chat-conversation", "children"),
         State("rag-process-data", "data"),
         State("url", "pathname")],  # ⭐ AÑADIR ESTADO DE URL ⭐
        prevent_initial_call=True
    )
    def handle_chat_message(n_clicks, question, llm_method, current_conversation_children, current_rag_data, pathname):
        
        # ⭐ VALIDAR QUE ESTAMOS EN LA PÁGINA CORRECTA ⭐
        if pathname != "/chat":
            raise PreventUpdate
            
        if not n_clicks or not question or not question.strip():
            raise PreventUpdate
        
        try:
            question = question.strip()
            llm_method = llm_method or "openai"  # Asegurar que no sea None
            
            # Determinar la conversación actual, manejando el placeholder inicial
            new_conversation = []
            if current_conversation_children and isinstance(current_conversation_children, list):
                is_placeholder = False
                try:
                    # Verificar si es el placeholder inicial
                    if len(current_conversation_children) == 1:
                        first_element = current_conversation_children[0]
                        if isinstance(first_element, dict):
                            props = first_element.get('props', {})
                            if 'children' in props:
                                children = props['children']
                                if isinstance(children, list) and len(children) == 1:
                                    p_element = children[0]
                                    if isinstance(p_element, dict):
                                        p_props = p_element.get('props', {})
                                        if p_props.get('children') == "Aquí verás la respuesta a tu pregunta...":
                                            is_placeholder = True
                except Exception:
                    is_placeholder = False
                
                if not is_placeholder:
                    new_conversation = current_conversation_children.copy()
            
            # Añadir mensaje del usuario a la conversación
            new_conversation.append(create_user_message(question))
            
            try:
                # Importar el orquestrador aquí para evitar problemas circulares
                from core.rag_orchestrator import rag_orchestrator
                
                # Llamar al RAG orchestrator para obtener la respuesta del LLM
                result = rag_orchestrator.process_question(question, llm_method)

                if result.get("success"):
                    bot_answer = result.get("final_answer", "No se pudo generar una respuesta del LLM.")
                    
                    # VERIFICAR QUE LA RESPUESTA NO ESTÉ VACÍA
                    if not bot_answer or not bot_answer.strip():
                        bot_answer = "Lo siento, no pude generar una respuesta basada en la información disponible."
                    
                    new_conversation.append(create_bot_message(bot_answer, show_process=True))
                    
                    # DATOS PARA EL PANEL RAG - FORMATO CORRECTO
                    rag_panel_data = {
                        "success": True,
                        "steps": result.get("steps", {}),
                        "final_answer": bot_answer,
                        "llm_method": llm_method
                    }
                    
                    rag_panel_content = create_complete_process_view(rag_panel_data)
                    status_message = "✅ Pregunta respondida por el LLM"
                    rag_data_to_store = result.get("steps", {})

                else:
                    error_msg = result.get("error", "Error desconocido del RAG orchestrator.")
                    new_conversation.append(create_error_message(error_msg))
                    rag_panel_content = create_initial_state()
                    status_message = f"❌ Error RAG: {error_msg[:50]}"
                    rag_data_to_store = {"error": error_msg}
            
            except Exception as e:
                critical_error_msg = f"Error crítico en el servidor: {str(e)[:100]}"
                new_conversation.append(create_error_message(critical_error_msg))
                rag_panel_content = create_initial_state()
                status_message = "❌ Error Crítico en el Servidor"
                rag_data_to_store = {"error": critical_error_msg}

            return (
                new_conversation,
                status_message,
                rag_panel_content,
                rag_data_to_store,
                ""  # Limpiar el campo de entrada
            )
            
        except Exception as e:
            # Retornar valores por defecto seguros
            return (
                [create_error_message(f"Error crítico: {str(e)[:100]}")],
                "❌ Error Crítico",
                create_initial_state(),
                {"error": str(e)},
                ""
            )

    def trigger_send_on_enter(n_submit, current_clicks, pathname):
        try:
            if pathname != "/chat":
                raise PreventUpdate
                
            if n_submit:
                return (current_clicks or 0) + 1
            raise PreventUpdate
        except Exception:
            raise PreventUpdate

    # ⭐ CALLBACK DE INPUT VALUE - CON VALIDACIÓN Y MANEJO DE ERRORES ⭐
    @app.callback(
        Output("chat-input", "value", allow_duplicate=True),
        Input("chat-input", "n_submit"),
        [State("chat-input", "value"),
         State("url", "pathname")],
        prevent_initial_call=True
    )
    def handle_enter_key(n_submit, current_value, pathname):
        try:
            if pathname != "/chat":
                raise PreventUpdate
                
            if n_submit and current_value and current_value.strip():
                return current_value
            raise PreventUpdate
        except Exception:
            raise PreventUpdate
    
    # ⭐ CALLBACK DE MOSTRAR PROCESO - CON VALIDACIÓN Y MANEJO DE ERRORES ⭐
    @app.callback(
        [Output("chat-conversation", "children", allow_duplicate=True),
         Output("rag-process-content", "children", allow_duplicate=True)],
        Input("show-process-btn", "n_clicks"),
        [State("rag-process-data", "data"),
         State("url", "pathname")],
        prevent_initial_call=True
    )
    def show_detailed_process(n_clicks, rag_data, pathname):
        try:
            if pathname != "/chat" or not n_clicks or not rag_data:
                raise PreventUpdate
            
            # Formato correcto para el panel
            panel_data = {
                "success": True,
                "steps": rag_data,
                "llm_method": "openai"  # Default
            }
            detailed_panel = create_complete_process_view(panel_data)
            return (no_update, detailed_panel)
        except Exception:
            raise PreventUpdate
    
    # ⭐ CALLBACK DE ESTADO - CON VALIDACIÓN Y MANEJO DE ERRORES ⭐
    @app.callback(
        Output("chat-status", "children", allow_duplicate=True),
        [Input("chat-input", "value")],
        [State("url", "pathname")],
        prevent_initial_call=True
    )
    def update_chat_status(input_value, pathname):
        try:
            if pathname != "/chat":
                raise PreventUpdate
                
            if not input_value or not input_value.strip():
                return "💤 Esperando pregunta..."
            char_count = len(input_value.strip())
            if char_count < 10:
                return "✏️ Escribe una pregunta más específica..."
            elif char_count > 500:
                return "⚠️ Pregunta muy larga, será truncada"
            else:
                return "✅ Pregunta lista para enviar"
        except Exception:
            raise PreventUpdate
    
    # ⭐ CALLBACK DE INICIALIZACIÓN - CON VALIDACIÓN Y MANEJO DE ERRORES ⭐
    @app.callback(
        [Output("rag-process-content", "children", allow_duplicate=True),
         Output("rag-process-data", "data", allow_duplicate=True)],
        Input("url", "pathname"),
        prevent_initial_call=True
    )
    def init_chat_page_panel(pathname):
        try:
            if pathname != "/chat":
                raise PreventUpdate
                
            try:
                from core.embeddings import get_index_stats
                stats = get_index_stats()
                total_vectors = stats.get('total_vector_count', 0)
                
                panel = create_initial_state()
                return (panel, {})
                
            except Exception as e:
                logger.error(f"Error checking documents: {e}")
                return (create_initial_state(), {})
        except Exception:
            raise PreventUpdate

# ⭐ FUNCIÓN AUXILIAR PARA VERIFICAR SI ESTAMOS EN LA PÁGINA CORRECTA ⭐
def is_on_chat_page(pathname):
    """
    Verifica si estamos en la página de chat.
    """
    return pathname == "/chat"

# ⭐ FUNCIÓN AUXILIAR PARA MANEJO SEGURO DE CALLBACKS ⭐
def safe_callback_execution(func):
    """
    Decorador para manejo seguro de callbacks que pueden fallar.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in callback {func.__name__}: {e}")
            raise PreventUpdate
    return wrapper# ./callbacks/chat_callbacks.py
# Callbacks para el sistema de chat RAG educativo - CORREGIDO para layouts dinámicos

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
    create_complete_process_view,
    create_initial_state
)

logger = logging.getLogger(__name__)


def register_chat_callbacks(app):
    
    # ⭐ CALLBACK PRINCIPAL - CON VALIDACIÓN DE LAYOUT ⭐
    @app.callback(
        [Output("chat-conversation", "children", allow_duplicate=True),
         Output("chat-status", "children", allow_duplicate=True),
         Output("rag-process-content", "children", allow_duplicate=True),
         Output("rag-process-data", "data", allow_duplicate=True),
         Output("chat-input", "value", allow_duplicate=True)],
        [Input("chat-send-btn", "n_clicks")],
        [State("chat-input", "value"),
         State("chat-llm-selector", "value"),
         State("chat-conversation", "children"),
         State("rag-process-data", "data"),
         State("url", "pathname")],  # ⭐ AÑADIR ESTADO DE URL ⭐
        prevent_initial_call=True
    )
    def handle_chat_message(n_clicks, question, llm_method, current_conversation_children, current_rag_data, pathname):
        
        # ⭐ VALIDAR QUE ESTAMOS EN LA PÁGINA CORRECTA ⭐
        if pathname != "/chat":
            raise PreventUpdate
            
        if not n_clicks or not question or not question.strip():
            raise PreventUpdate
        
        question = question.strip()
        llm_method = llm_method or "openai"  # Asegurar que no sea None
        
        # Determinar la conversación actual, manejando el placeholder inicial
        new_conversation = []
        if current_conversation_children and isinstance(current_conversation_children, list):
            is_placeholder = False
            try:
                # Verificar si es el placeholder inicial
                if len(current_conversation_children) == 1:
                    first_element = current_conversation_children[0]
                    if isinstance(first_element, dict):
                        props = first_element.get('props', {})
                        if 'children' in props:
                            children = props['children']
                            if isinstance(children, list) and len(children) == 1:
                                p_element = children[0]
                                if isinstance(p_element, dict):
                                    p_props = p_element.get('props', {})
                                    if p_props.get('children') == "Aquí verás la respuesta a tu pregunta...":
                                        is_placeholder = True
            except Exception:
                is_placeholder = False
            
            if not is_placeholder:
                new_conversation = current_conversation_children.copy()
        
        # Añadir mensaje del usuario a la conversación
        new_conversation.append(create_user_message(question))
        
        try:
            # Importar el orquestrador aquí para evitar problemas circulares
            from core.rag_orchestrator import rag_orchestrator
            
            # Llamar al RAG orchestrator para obtener la respuesta del LLM
            result = rag_orchestrator.process_question(question, llm_method)

            if result.get("success"):
                bot_answer = result.get("final_answer", "No se pudo generar una respuesta del LLM.")
                
                # VERIFICAR QUE LA RESPUESTA NO ESTÉ VACÍA
                if not bot_answer or not bot_answer.strip():
                    bot_answer = "Lo siento, no pude generar una respuesta basada en la información disponible."

                new_conversation.append(create_bot_message(bot_answer, show_process=True))
                
                # DATOS PARA EL PANEL RAG - FORMATO CORRECTO
                rag_panel_data = {
                    "success": True,
                    "steps": result.get("steps", {}),
                    "final_answer": bot_answer,
                    "llm_method": llm_method
                }
                
                rag_panel_content = create_complete_process_view(rag_panel_data)
                status_message = "✅ Pregunta respondida por el LLM"
                rag_data_to_store = result.get("steps", {})
                
            else:
                error_msg = result.get("error", "Error desconocido del RAG orchestrator.")
                new_conversation.append(create_error_message(error_msg))
                rag_panel_content = create_initial_state()
                status_message = f"❌ Error RAG: {error_msg[:50]}"
                rag_data_to_store = {"error": error_msg}
        
        except Exception as e:
            critical_error_msg = f"Error crítico en el servidor: {str(e)[:100]}"
            new_conversation.append(create_error_message(critical_error_msg))
            rag_panel_content = create_initial_state()
            status_message = "❌ Error Crítico en el Servidor"
            rag_data_to_store = {"error": critical_error_msg}

        return (
            new_conversation,
            status_message,
            rag_panel_content,
            rag_data_to_store,
            ""  # Limpiar el campo de entrada
        )

    # ⭐ CALLBACK DE ENTER - CON VALIDACIÓN ⭐
    @app.callback(
        Output("chat-send-btn", "n_clicks", allow_duplicate=True),
        Input("chat-input", "n_submit"),
        [State("chat-send-btn", "n_clicks"),
         State("url", "pathname")],
        prevent_initial_call=True
    )
    def trigger_send_on_enter(n_submit, current_clicks, pathname):
        if pathname != "/chat":
            raise PreventUpdate
            
        if n_submit:
            return (current_clicks or 0) + 1
        raise PreventUpdate

    # ⭐ CALLBACK DE INPUT VALUE - CON VALIDACIÓN ⭐
    @app.callback(
        Output("chat-input", "value", allow_duplicate=True),
        Input("chat-input", "n_submit"),
        [State("chat-input", "value"),
         State("url", "pathname")],
        prevent_initial_call=True
    )
    def handle_enter_key(n_submit, current_value, pathname):
        if pathname != "/chat":
            raise PreventUpdate
            
        if n_submit and current_value and current_value.strip():
            return current_value
        raise PreventUpdate
    
    # ⭐ CALLBACK DE MOSTRAR PROCESO - CON VALIDACIÓN ⭐
    @app.callback(
        [Output("chat-conversation", "children", allow_duplicate=True),
         Output("rag-process-content", "children", allow_duplicate=True)],
        Input("show-process-btn", "n_clicks"),
        [State("rag-process-data", "data"),
         State("url", "pathname")],
        prevent_initial_call=True
    )
    def show_detailed_process(n_clicks, rag_data, pathname):
        if pathname != "/chat" or not n_clicks or not rag_data:
            raise PreventUpdate
        
        # Formato correcto para el panel
        panel_data = {
            "success": True,
            "steps": rag_data,
            "llm_method": "openai"  # Default
        }
        detailed_panel = create_complete_process_view(panel_data)
        return (no_update, detailed_panel)
    
    # ⭐ CALLBACK DE ESTADO - CON VALIDACIÓN ⭐
    @app.callback(
        Output("chat-status", "children", allow_duplicate=True),
        [Input("chat-input", "value")],
        [State("url", "pathname")],
        prevent_initial_call=True
    )
    def update_chat_status(input_value, pathname):
        if pathname != "/chat":
            raise PreventUpdate
            
        if not input_value or not input_value.strip():
            return "💤 Esperando pregunta..."
        char_count = len(input_value.strip())
        if char_count < 10:
            return "✏️ Escribe una pregunta más específica..."
        elif char_count > 500:
            return "⚠️ Pregunta muy larga, será truncada"
        else:
            return "✅ Pregunta lista para enviar"
    
    # ⭐ CALLBACK DE INICIALIZACIÓN - CON VALIDACIÓN ⭐
    @app.callback(
        [Output("rag-process-content", "children", allow_duplicate=True),
         Output("rag-process-data", "data", allow_duplicate=True)],
        Input("url", "pathname"),
        prevent_initial_call=True
    )
    def init_chat_page_panel(pathname):
        if pathname != "/chat":
            raise PreventUpdate
            
        try:
            from core.embeddings import get_index_stats
            stats = get_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            
            panel = create_initial_state()
            return (panel, {})
            
        except Exception as e:
            logger.error(f"Error checking documents: {e}")
            return (create_initial_state(), {})