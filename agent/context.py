# ./agent/context.py
# Módulo responsable únicamente de construir contexto a partir de chunks

import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class ContextBuilder:
    """
    Responsable únicamente de construir contexto a partir de chunks recuperados.
    """
    
    def __init__(self, max_context_length: int = 4000):
        self.max_context_length = max_context_length
    
    def build_context(self, chunks: List[Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
        """
        Construye contexto a partir de chunks recuperados.
        
        Args:
            chunks: Lista de chunks con 'text', 'score', 'source', etc.
            
        Returns:
            Tuple de (contexto_texto, información_educativa)
        """
        try:
            if not chunks:
                return "", {
                    "step": "context_building",
                    "error": "No chunks provided",
                    "success": False
                }
            
            # Construir contexto gradualmente
            context_parts = []
            total_length = 0
            chunks_used = 0
            
            for i, chunk in enumerate(chunks, 1):
                chunk_text = chunk.get('text', '')
                score = chunk.get('score', 0)
                source = chunk.get('source', 'Unknown')
                
                # Formato del chunk en el contexto
                formatted_chunk = f"[Fragmento {i} - Relevancia: {score:.3f} - Fuente: {source}]\n{chunk_text}\n"
                
                # Verificar si excede límite
                if total_length + len(formatted_chunk) > self.max_context_length:
                    logger.warning(f"Context length limit reached at chunk {i}")
                    break
                
                context_parts.append(formatted_chunk)
                total_length += len(formatted_chunk)
                chunks_used += 1
            
            # Unir todas las partes
            final_context = "\n".join(context_parts)
            
            # Calcular estadísticas
            avg_score = sum(chunk.get('score', 0) for chunk in chunks[:chunks_used]) / chunks_used if chunks_used > 0 else 0
            unique_sources = len(set(chunk.get('source', '') for chunk in chunks[:chunks_used]))
            
            # Información educativa
            context_info = {
                "step": "context_building",
                "chunks_provided": len(chunks),
                "chunks_used": chunks_used,
                "chunks_excluded": len(chunks) - chunks_used,
                "total_length": len(final_context),
                "max_allowed_length": self.max_context_length,
                "avg_relevance_score": round(avg_score, 4),
                "unique_sources": unique_sources,
                "context_preview": final_context[:200] + "..." if len(final_context) > 200 else final_context,
                "success": True
            }
            
            logger.info(f"Context built: {chunks_used} chunks, {len(final_context)} chars")
            return final_context, context_info
            
        except Exception as e:
            logger.error(f"Error building context: {e}")
            error_info = {
                "step": "context_building",
                "error": str(e),
                "success": False
            }
            return "", error_info
    
    def format_chunk(self, chunk: Dict[str, Any], index: int) -> str:
        """
        Formatea un chunk individual para el contexto.
        
        Args:
            chunk: Diccionario con información del chunk
            index: Índice del chunk
            
        Returns:
            String formateado del chunk
        """
        text = chunk.get('text', '')
        score = chunk.get('score', 0)
        source = chunk.get('source', 'Unknown')
        
        return f"[Fragmento {index} - Relevancia: {score:.3f} - Fuente: {source}]\n{text}\n"
    
    def get_context_stats(self, context: str, chunks: List[Dict]) -> Dict[str, Any]:
        """
        Calcula estadísticas del contexto construido.
        
        Args:
            context: Texto del contexto
            chunks: Chunks utilizados
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            word_count = len(context.split())
            line_count = len(context.split('\n'))
            char_count = len(context)
            
            # Estadísticas de chunks
            if chunks:
                scores = [chunk.get('score', 0) for chunk in chunks]
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                
                sources = set(chunk.get('source', '') for chunk in chunks)
            else:
                avg_score = max_score = min_score = 0
                sources = set()
            
            return {
                "char_count": char_count,
                "word_count": word_count,
                "line_count": line_count,
                "chunk_count": len(chunks),
                "avg_relevance": round(avg_score, 4),
                "max_relevance": round(max_score, 4),
                "min_relevance": round(min_score, 4),
                "unique_sources": len(sources),
                "source_list": list(sources)
            }
            
        except Exception as e:
            logger.error(f"Error calculating context stats: {e}")
            return {"error": str(e)}