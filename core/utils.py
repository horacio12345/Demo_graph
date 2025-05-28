# ./core/utils.py
# Utilidades generales para manejo de archivos, textos, IDs y formatos en el pipeline RAG

import os
import uuid
import hashlib
import tempfile
import re

def get_temp_file_path(suffix=""):
    """
    Devuelve una ruta temporal segura para guardar archivos subidos o generados.
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path

def get_file_extension(filename):
    """
    Obtiene la extensión (incluyendo el punto) del archivo.
    """
    return os.path.splitext(filename)[1].lower()

def safe_filename(filename):
    """
    Sanitiza un nombre de archivo para evitar problemas en el sistema de archivos.
    """
    return re.sub(r'[^A-Za-z0-9_.-]', '_', filename)

def generate_chunk_id(text, document_id=None):
    """
    Genera un ID único para cada chunk, opcionalmente usando el document_id.
    """
    base = (document_id or "") + text
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:12]

def generate_document_id(filename):
    """
    Genera un ID único para cada documento (por ejemplo, hash del nombre y tiempo).
    """
    unique = f"{filename}_{uuid.uuid4()}"
    return hashlib.sha256(unique.encode("utf-8")).hexdigest()[:12]

def clean_text(text):
    """
    Limpia el texto eliminando espacios redundantes y caracteres problemáticos.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def ensure_utf8(text):
    """
    Asegura que el texto sea UTF-8 (importante para API y almacenamiento).
    """
    if isinstance(text, bytes):
        return text.decode("utf-8", errors="replace")
    return text

def is_pdf(filename):
    """
    Determina si un archivo es PDF por su extensión.
    """
    return filename.lower().endswith('.pdf')

def is_image(filename):
    """
    Determina si un archivo es imagen común.
    """
    return filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.gif'))

def get_chunks_from_text(text, chunk_size=1000):
    """
    Divide el texto en trozos de tamaño fijo (como backup si el chunker semántico falla).
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def json_stringify_safe(obj):
    """
    Convierte a JSON seguro para logs/debug (evita errores con tipos no serializables).
    """
    import json
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"<Error dumping JSON: {e}>"

def log_event(message):
    """
    Loguea un evento relevante para debugging.
    """
    print(f"[DEMO RAG] {message}")