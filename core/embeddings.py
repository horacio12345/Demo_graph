# ./core/embeddings.py
# Lógica para conexión, almacenamiento, consulta y eliminación de embeddings en Pinecone serverless

import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX")
PINECONE_ENV = os.getenv("PINECONE_ENV")
DIMENSION = 1536  # Cambia si tu modelo de embedding tiene otra dimensión

if not PINECONE_API_KEY or not PINECONE_INDEX_NAME:
    raise ValueError("Faltan variables de entorno para Pinecone: PINECONE_API_KEY y PINECONE_INDEX son requeridas")

# Inicializa cliente Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

def upsert_embedding(vector_id, vector_values, document_id, metadata=None):
    """
    Inserta o actualiza un embedding en Pinecone, asociando un document_id.
    """
    meta = metadata or {}
    meta["document_id"] = str(document_id)
    vectors = [{"id": str(vector_id), "values": vector_values, "metadata": meta}]
    
    try:
        result = index.upsert(vectors=vectors)
        return result
    except Exception as e:
        print(f"❌ Error guardando embedding: {e}")
        raise

def query_embedding(query_vector, top_k=5, include_metadata=True):
    """
    Busca los embeddings más cercanos al vector de consulta.
    """
    return index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=include_metadata
    )

def delete_all_embeddings():
    """
    Borra todos los vectores del índice Pinecone (¡operación destructiva!).
    """
    index.delete(delete_all=True)

def delete_embeddings_by_document_id(document_id):
    """
    Borra todos los embeddings asociados a un document_id dado.
    (Pensado para demos o volúmenes bajos; si tienes muchos vectores, implementa paginación)
    """
    # Busca los IDs de los vectores con ese document_id
    result = index.query(
        vector=[0]*DIMENSION,  # Vector dummy (no usado en filtrado)
        filter={"document_id": {"$eq": str(document_id)}},
        top_k=1000,  # Ajusta según lo que esperes por documento
        include_values=False,
        include_metadata=True
    )
    ids_to_delete = [m["id"] for m in result.get("matches", [])]
    if ids_to_delete:
        index.delete(ids=ids_to_delete)

def get_index_stats():
    """
    Obtiene estadísticas del índice (útil para debugging).
    """
    return index.describe_index_stats()

def test_connection():
    """
    Prueba la conexión con Pinecone.
    """
    try:
        stats = get_index_stats()

        return True
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False