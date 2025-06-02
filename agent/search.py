# ./agent/search.py
# Módulo responsable únicamente de la búsqueda semántica

import os
import logging
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
from openai import OpenAI
from core.embeddings import query_embedding

load_dotenv()
logger = logging.getLogger(__name__)

class SemanticSearcher:
    """
    Responsable únicamente de vectorizar queries y buscar chunks similares.
    """
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def vectorize_query(self, question: str) -> Tuple[List[float], Dict[str, Any]]:
        """
        Convierte la pregunta del usuario en un vector de embeddings.
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            Tuple de (vector, información_educativa)
        """
        try:
            response = self.openai_client.embeddings.create(
                input=question,
                model="text-embedding-ada-002"
            )
            
            embedding = response.data[0].embedding
            
            # Información para propósitos educativos
            vectorization_info = {
                "step": "vectorization",
                "model_used": "text-embedding-ada-002",
                "dimensions": len(embedding),
                "first_values": embedding[:10],
                "question_length": len(question),
                "success": True
            }
            
            logger.debug(f"Query vectorized: {len(embedding)} dimensions")
            return embedding, vectorization_info
            
        except Exception as e:
            logger.error(f"Error vectorizing query: {e}")
            error_info = {
                "step": "vectorization",
                "error": str(e),
                "success": False
            }
            return [], error_info
    
    def search_similar_chunks(self, query_vector: List[float], top_k: int = 5) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Busca chunks similares en la base de datos vectorial.
        
        Args:
            query_vector: Vector de la pregunta
            top_k: Número de resultados a devolver
            
        Returns:
            Tuple de (resultados, información_educativa)
        """
        try:
            # Realizar búsqueda en Pinecone
            search_results = query_embedding(
                query_vector=query_vector,
                top_k=top_k,
                include_metadata=True
            )
            
            matches = search_results.get('matches', [])
            
            # Procesar resultados para formato estándar
            processed_matches = []
            for match in matches:
                processed_match = {
                    'id': match['id'],
                    'score': match['score'],
                    'text': match['metadata'].get('chunk_text', ''),
                    'source': match['metadata'].get('filename', 'Unknown'),
                    'chunk_index': match['metadata'].get('chunk_index', 0)
                }
                processed_matches.append(processed_match)
            
            # Información educativa
            search_info = {
                "step": "search",
                "method": "cosine_similarity",
                "total_found": len(matches),
                "top_scores": [round(m['score'], 4) for m in matches[:3]],
                "avg_score": round(sum(m['score'] for m in matches) / len(matches), 4) if matches else 0,
                "unique_sources": len(set(m['source'] for m in processed_matches)),
                "success": True
            }
            
            logger.info(f"Found {len(matches)} similar chunks")
            return processed_matches, search_info
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            error_info = {
                "step": "search",
                "error": str(e),
                "success": False
            }
            return [], error_info
    
    def search_query(self, question: str, top_k: int = 5) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Método de conveniencia que combina vectorización y búsqueda.
        
        Args:
            question: Pregunta del usuario
            top_k: Número de resultados
            
        Returns:
            Tuple de (resultados, información_completa)
        """
        # Vectorizar pregunta
        query_vector, vectorization_info = self.vectorize_query(question)
        
        if not vectorization_info['success']:
            return [], vectorization_info
        
        # Buscar chunks similares
        matches, search_info = self.search_similar_chunks(query_vector, top_k)
        
        # Combinar información educativa
        combined_info = {
            "vectorization": vectorization_info,
            "search": search_info,
            "overall_success": vectorization_info['success'] and search_info['success']
        }
        
        return matches, combined_info