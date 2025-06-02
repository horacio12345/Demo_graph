# ./core/rag_orchestrator.py
# Orquestador que coordina todos los módulos del agente RAG

import logging
from typing import Dict, Any
from agent import SemanticSearcher, ContextBuilder, ResponseGenerator

logger = logging.getLogger(__name__)

class RAGOrchestrator:
    """
    Coordina todos los módulos del agente RAG de manera modular y profesional.
    Cada módulo tiene una responsabilidad específica.
    """
    
    def __init__(self, 
                 max_chunks: int = 5,
                 max_context_length: int = 4000,
                 prompts_file: str = "agent/prompts.yaml"):
        """
        Inicializa el orquestador con los módulos especializados.
        
        Args:
            max_chunks: Máximo número de chunks a recuperar
            max_context_length: Longitud máxima del contexto
            prompts_file: Archivo de configuración de prompts
        """
        self.max_chunks = max_chunks
        
        # Inicializar módulos especializados
        self.searcher = SemanticSearcher()
        self.context_builder = ContextBuilder(max_context_length=max_context_length)
        self.response_generator = ResponseGenerator(prompts_file=prompts_file)
        
        logger.info("RAG Orchestrator initialized with modular components")
    
    def process_question(self, question: str, llm_method: str = "openai") -> Dict[str, Any]:
        """
        Procesa una pregunta a través del pipeline RAG completo.
        
        Args:
            question: Pregunta del usuario
            llm_method: Método LLM a usar ('openai' o 'claude')
            
        Returns:
            Diccionario completo con todos los pasos del proceso
        """
        logger.info(f"Processing question: {question[:50]}...")
        
        # Estructura del resultado
        result = {
            "question": question,
            "llm_method": llm_method,
            "steps": {},
            "final_answer": "",
            "success": False,
            "error": None
        }
        
        try:
            # PASO 1: Búsqueda semántica
            logger.debug("Step 1: Semantic search")
            chunks, search_info = self.searcher.search_query(question, top_k=self.max_chunks)
            result["steps"]["search"] = search_info
            
            if not search_info.get("overall_success", False):
                result["error"] = "Error en búsqueda semántica"
                return result
            
            # PASO 2: Construcción de contexto
            logger.debug("Step 2: Context building")
            context, context_info = self.context_builder.build_context(chunks)
            result["steps"]["context"] = context_info
            
            if not context_info.get("success", False):
                result["error"] = "Error construyendo contexto"
                return result
            
            # PASO 3: Generación de respuesta
            logger.debug("Step 3: Response generation")
            response, response_info = self.response_generator.generate_response(
                question, context, llm_method
            )
            result["steps"]["response"] = response_info
            
            if not response_info.get("success", False):
                result["error"] = "Error generando respuesta"
                return result
            
            # PASO 4: Información de fuentes
            logger.debug("Step 4: Source information")
            sources_info = self._extract_sources_info(chunks)
            result["steps"]["sources"] = sources_info
            
            # Resultado final
            result["final_answer"] = response
            result["success"] = True
            
            logger.info("Question processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG orchestrator: {e}")
            result["error"] = str(e)
            return result
    
    def _extract_sources_info(self, chunks: list) -> Dict[str, Any]:
        """
        Extrae información educativa sobre las fuentes utilizadas.
        
        Args:
            chunks: Lista de chunks recuperados
            
        Returns:
            Información sobre las fuentes
        """
        try:
            if not chunks:
                return {
                    "step": "sources",
                    "total_sources": 0,
                    "sources": [],
                    "success": True
                }
            
            # Procesar información de fuentes
            sources_detail = []
            unique_sources = set()
            
            for i, chunk in enumerate(chunks, 1):
                source_info = {
                    "chunk_number": i,
                    "source_file": chunk.get('source', 'Unknown'),
                    "chunk_index": chunk.get('chunk_index', 0),
                    "relevance_score": round(chunk.get('score', 0), 4),
                    "text_preview": chunk.get('text', '')[:150] + "..."
                }
                sources_detail.append(source_info)
                unique_sources.add(chunk.get('source', 'Unknown'))
            
            return {
                "step": "sources",
                "total_chunks_used": len(chunks),
                "unique_documents": len(unique_sources),
                "document_list": list(unique_sources),
                "sources_detail": sources_detail,
                "avg_relevance": round(sum(c.get('score', 0) for c in chunks) / len(chunks), 4),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error extracting sources info: {e}")
            return {
                "step": "sources",
                "error": str(e),
                "success": False
            }
    
    def get_process_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera un resumen educativo del proceso RAG.
        
        Args:
            result: Resultado del proceso completo
            
        Returns:
            Resumen educativo del proceso
        """
        try:
            if not result.get("success", False):
                return {
                    "status": "error",
                    "error": result.get("error", "Unknown error"),
                    "steps_completed": len([s for s in result.get("steps", {}).values() if s.get("success", False)])
                }
            
            steps = result.get("steps", {})
            
            summary = {
                "status": "success",
                "question_length": len(result.get("question", "")),
                "llm_used": result.get("llm_method", "unknown"),
                "total_chunks_found": steps.get("search", {}).get("search", {}).get("total_found", 0),
                "chunks_used_in_context": steps.get("context", {}).get("chunks_used", 0),
                "context_length": steps.get("context", {}).get("total_length", 0),
                "response_length": len(result.get("final_answer", "")),
                "unique_sources": steps.get("sources", {}).get("unique_documents", 0),
                "avg_relevance": steps.get("sources", {}).get("avg_relevance", 0),
                "process_time": "N/A"  # Se podría añadir timing
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating process summary: {e}")
            return {"status": "error", "error": str(e)}
    
    def reload_configuration(self, prompts_file: str = "agent/prompts.yaml") -> bool:
        """
        Recarga la configuración de prompts.
        
        Args:
            prompts_file: Archivo de prompts a recargar
            
        Returns:
            True si se recargó exitosamente
        """
        try:
            success = self.response_generator.reload_prompts(prompts_file)
            if success:
                logger.info("Configuration reloaded successfully")
            return success
        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")
            return False

# Instancia global del orquestador
rag_orchestrator = RAGOrchestrator()