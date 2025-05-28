# ./core/ocr.py
# Procesamiento de OCR usando Mistral OCR (API) o Tesseract OCR (local)
# Devuelve una lista de chunks de texto extraídos del documento

import os
from dotenv import load_dotenv
from langchain.text_splitter import SemanticChunker
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader

# Para Mistral OCR
import requests

# Para Tesseract OCR
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None

load_dotenv()

MISTRAL_OCR_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_OCR_URL = os.getenv("MISTRAL_OCR_URL") or "https://api.mistral.ai/ocr"  # Cambia si tu endpoint es distinto

def run_mistral_ocr(file_path):
    """
    Procesa el archivo usando Mistral OCR API.
    Devuelve texto extraído como string.
    """
    headers = {"Authorization": f"Bearer {MISTRAL_OCR_API_KEY}"}
    files = {"file": open(file_path, "rb")}
    response = requests.post(MISTRAL_OCR_URL, headers=headers, files=files)
    if response.status_code != 200:
        raise RuntimeError(f"Mistral OCR error: {response.status_code} {response.text}")
    result = response.json()
    # Asume que el texto viene en result["text"], adáptalo según la API real
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
    """
    if ocr_method == "mistral":
        return run_mistral_ocr(file_path)
    elif ocr_method == "tesseract":
        return run_tesseract_ocr(file_path, lang=lang)
    else:
        raise ValueError(f"OCR method '{ocr_method}' no soportado")

import re

def chunk_text_semantic(text, openai_api_key, chunk_size=1000):
    """
    Divide el texto en chunks semánticos usando LangChain SemanticChunker.
    Requiere clave de OpenAI.
    """
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    chunker = SemanticChunker(embeddings, breakpoint_threshold_type="standard", chunk_size=chunk_size)
    # LangChain espera un "Document", así que lo creamos
    from langchain_core.documents import Document
    doc = Document(page_content=text)
    chunks = chunker.split_documents([doc])
    # Devuelve solo el texto de cada chunk
    return [chunk.page_content for chunk in chunks]