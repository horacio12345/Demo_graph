# ./core/ocr.py
# Procesamiento de OCR usando Mistral OCR (API) o Tesseract OCR (local)
# Devuelve una lista de chunks de texto extraídos del documento

import os
from dotenv import load_dotenv
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader

# Para Mistral OCR
import requests
import base64

# Para Tesseract OCR
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None

load_dotenv()

MISTRAL_OCR_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_OCR_URL = "https://api.mistral.ai/v1/ocr"  # Endpoint corregido

def run_mistral_ocr(file_path):
    """
    Procesa el archivo usando Mistral OCR API.
    Devuelve texto extraído como string.
    Solo funciona con imágenes (JPG, PNG) y PDFs.
    """
    # Verificar que el archivo sea compatible con OCR
    file_extension = os.path.splitext(file_path)[1].lower()
    supported_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    
    if file_extension not in supported_extensions:
        raise ValueError(f"Archivo {file_extension} no es compatible con Mistral OCR. "
                        f"Formatos soportados: {supported_extensions}")
    
    headers = {
        "Authorization": f"Bearer {MISTRAL_OCR_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Convertir archivo a base64
    with open(file_path, "rb") as file:
        file_content = base64.b64encode(file.read()).decode('utf-8')
    
    # Determinar el tipo de archivo correcto
    if file_extension in ['.jpg', '.jpeg']:
        media_type = "image/jpeg"
    elif file_extension == '.png':
        media_type = "image/png"
    elif file_extension == '.pdf':
        media_type = "application/pdf"
    else:
        raise ValueError(f"Formato {file_extension} no soportado")
    
    payload = {
        "model": "mistral-ocr-latest",
        "document": {
            "image_url": f"data:{media_type};base64,{file_content}",
            "type": "image_url"
        }
    }
    
    response = requests.post(MISTRAL_OCR_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Mistral OCR error: {response.status_code} {response.text}")
    
    result = response.json()
    
    # Extraer el texto del resultado
    if "document_annotation" in result and result["document_annotation"]:
        return result["document_annotation"]
    elif "pages" in result and len(result["pages"]) > 0:
        text = ""
        for page in result["pages"]:
            if "content" in page:
                text += page["content"] + "\n"
        return text
    else:
        return result.get("text", "")

def run_tesseract_ocr(file_path, lang="eng"):
    """
    Procesa el archivo usando Tesseract OCR local.
    Soporta imágenes y PDFs convertidos a imágenes.
    Devuelve texto extraído como string.
    """
    if not pytesseract:
        raise ImportError("pytesseract o Pillow no están instalados.")
    # Si es PDF, conviértelo primero a imágenes (puedes ampliar esto si quieres multi-página)
    if file_path.lower().endswith(".pdf"):
        # Se requiere pdf2image: pip install pdf2image
        from pdf2image import convert_from_path
        images = convert_from_path(file_path)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img, lang=lang)
        return text
    else:
        img = Image.open(file_path)
        return pytesseract.image_to_string(img, lang=lang)

def extract_text(file_path, ocr_method="mistral", lang="eng"):
    """
    Selector de OCR: elige entre Mistral OCR (API) o Tesseract (local)
    Si el archivo es texto plano, lo lee directamente sin OCR.
    """
    # Verificar si es un archivo de texto plano
    text_extensions = ['.txt', '.md', '.py', '.js', '.json', '.csv', '.log']
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension in text_extensions:
        # Es un archivo de texto, leerlo directamente
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    # Es imagen/PDF, usar OCR
    if ocr_method == "mistral":
        return run_mistral_ocr(file_path)
    elif ocr_method == "tesseract":
        return run_tesseract_ocr(file_path, lang=lang)
    else:
        raise ValueError(f"OCR method '{ocr_method}' no soportado")

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
        
        print(f"Chunking semántico exitoso: {len(final_chunks)} chunks creados")
        return final_chunks
        
    except Exception as e:
        # Fallback a chunking simple si falla el semántico
        print(f"Error en chunking semántico: {e}")
        print("Usando chunking simple como fallback...")
        return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]