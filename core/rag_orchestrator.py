# ./core/rag_orchestrator.py
# Orquestador que coordina todos los módulos del agente RAG - VERSIÓN CORREGIDA

import logging
from typing import Dict, Any

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
        """
        self.max_chunks = max_chunks
        
        # Importar módulos aquí para evitar problemas circulares
        try:
            from agent.search import SemanticSearcher
            from agent.context import ContextBuilder  
            from agent.response import ResponseGenerator
            
            self.searcher = SemanticSearcher()
            self.context_builder = ContextBuilder(max_context_length=max_context_length)
            self.response_generator = ResponseGenerator(prompts_file=prompts_file)
            
            logger.info("RAG Orchestrator initialized with modular components")
        except Exception as e:
            logger.error(f"Error initializing RAG modules: {e}")
            # Fallback a None, se manejarán en process_question
            self.searcher = None
            self.context_builder = None
            self.response_generator = None
    
    def process_question(self, question: str, llm_method: str = "openai") -> Dict[str, Any]:
        """
        Procesa una pregunta a través del pipeline RAG completo.
        
        Args:
            question: Pregunta del usuario
            llm_method: Método LLM a usar ('openai' o 'claude')
            
        Returns:
            Diccionario completo con todos los pasos del proceso
        """
        logger.info(f"Processing question: {question[:30]}...")
        
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
            # Verificar que los módulos estén inicializados
            if not all([self.searcher, self.context_builder, self.response_generator]):
                logger.error("RAG modules not properly initialized")
                result["error"] = "Módulos RAG no inicializados correctamente"
                return result

            # PASO 1: Búsqueda semántica
            logger.debug("Step 1: Semantic search")
            chunks, search_info = self.searcher.search_query(question, top_k=self.max_chunks)
            result["steps"]["search"] = search_info
            
            if not search_info.get("overall_success", False):
                logger.error("Search step failed")
                result["error"] = f"Error en búsqueda semántica: {search_info.get('search', {}).get('error', 'Unknown')}"
                return result
            
            logger.info(f"Found {len(chunks)} similar chunks")

            # PASO 2: Construcción de contexto
            logger.debug("Step 2: Context building")
            context, context_info = self.context_builder.build_context(chunks)
            result["steps"]["context"] = context_info
            
            if not context_info.get("success", False):
                logger.error("Context building failed")
                result["error"] = f"Error construyendo contexto: {context_info.get('error', 'Unknown')}"
                return result
            
            logger.info(f"Context built: {len(context)} chars, {context_info.get('chunks_used', 0)} chunks")

            # PASO 3: Generación de respuesta
            logger.debug("Step 3: Response generation")
            response, response_info = self.response_generator.generate_response(
                question, context, llm_method
            )
            result["steps"]["response"] = response_info
            
            if not response_info.get("success", False):
                logger.error("Response generation failed")
                result["error"] = f"Error generando respuesta: {response_info.get('error', 'Unknown')}"
                return result
            
            logger.info(f"OpenAI response generated: {len(response)} chars")

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
            logger.error(f"Error in RAG orchestrator: {e}", exc_info=True)
            result["error"] = str(e)
            return result
    
    def _extract_sources_info(self, chunks: list) -> Dict[str, Any]:
        """
        Extrae información educativa sobre las fuentes utilizadas.
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

# Instancia global del orquestador
rag_orchestrator = RAGOrchestrator()