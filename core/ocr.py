# ./core/ocr.py
# Procesamiento de OCR usando Docling (local) y Tesseract OCR (fallback)
# Devuelve una lista de chunks de texto extraídos del documento

import os
from dotenv import load_dotenv
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader

# Para Docling OCR
try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("❌ Docling no está instalado. Instálalo con: pip install docling")

# Para Tesseract OCR (fallback)
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    pytesseract = None

load_dotenv()

def run_docling_ocr(file_path):
    """
    Procesa el archivo usando Docling.
    Soporta PDF, DOCX, PPTX, HTML y más.
    Devuelve texto extraído como string.
    """
    if not DOCLING_AVAILABLE:
        raise ImportError("Docling no está disponible. Instálalo con: pip install docling")
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        print(f"🔄 Procesando documento con Docling: {os.path.basename(file_path)}")
        
        # Inicializar convertidor
        converter = DocumentConverter()
        
        # Convertir documento
        result = converter.convert(file_path)
        
        # Exportar a markdown (preserva estructura)
        text = result.document.export_to_markdown()
        
        print(f"✅ Docling completado. Texto extraído: {len(text)} caracteres")
        return text
        
    except Exception as e:
        raise RuntimeError(f"Error en Docling: {e}")

def run_tesseract_ocr(file_path, lang="eng"):
    """
    Procesa el archivo usando Tesseract OCR local (fallback).
    Soporta imágenes y PDFs convertidos a imágenes.
    Devuelve texto extraído como string.
    """
    if not TESSERACT_AVAILABLE:
        raise ImportError("pytesseract o Pillow no están instalados.")
    
    # Si es PDF, conviértelo primero a imágenes
    if file_path.lower().endswith(".pdf"):
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(file_path)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img, lang=lang) + "\n"
            return text
        except ImportError:
            raise ImportError("pdf2image no está instalado. Instálalo con: pip install pdf2image")
    else:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img, lang=lang)

def extract_text(file_path, ocr_method="docling", lang="eng"):
    """
    Selector de OCR: elige entre Docling (principal) o Tesseract (fallback)
    Si el archivo es texto plano, lo lee directamente sin OCR.
    """
    # Verificar si es un archivo de texto plano
    text_extensions = ['.txt', '.md', '.py', '.js', '.json', '.csv', '.log']
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension in text_extensions:
        # Es un archivo de texto, leerlo directamente
        print(f"📄 Leyendo archivo de texto: {os.path.basename(file_path)}")
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    # Es documento/imagen, usar OCR
    if ocr_method == "docling":
        return run_docling_ocr(file_path)
    elif ocr_method == "tesseract":
        return run_tesseract_ocr(file_path, lang=lang)
    else:
        # Si método no reconocido, usar Docling por defecto
        print(f"⚠️ Método OCR '{ocr_method}' no reconocido. Usando Docling.")
        return run_docling_ocr(file_path)

import re

def chunk_text_semantic(text, openai_api_key, max_chunk_size=1000):
    """
    Divide el texto en chunks semánticos usando LangChain SemanticChunker.
    Requiere clave de OpenAI.
    """
    try:
        embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        # SemanticChunker no usa chunk_size, usa otros parámetros
        chunker = SemanticChunker(
            embeddings, 
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=95  # Solo divide cuando hay gran diferencia semántica
        )
        # LangChain espera un "Document", así que lo creamos
        from langchain_core.documents import Document
        doc = Document(page_content=text)
        chunks = chunker.split_documents([doc])
        
        # Si los chunks son muy grandes, dividirlos adicionalmente
        final_chunks = []
        for chunk in chunks:
            if len(chunk.page_content) > max_chunk_size:
                # Dividir chunks grandes en trozos más pequeños
                content = chunk.page_content
                for i in range(0, len(content), max_chunk_size):
                    final_chunks.append(content[i:i+max_chunk_size])
            else:
                final_chunks.append(chunk.page_content)
        
        print(f"✅ Chunking semántico exitoso: {len(final_chunks)} chunks creados")
        return final_chunks
        
    except Exception as e:
        # Fallback a chunking simple si falla el semántico
        print(f"⚠️ Error en chunking semántico: {e}")
        print("🔄 Usando chunking simple como fallback...")
        return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]