# ./core/llm.py
# Lógica para extracción de entidades y relaciones usando LLMs (OpenAI GPT, Claude, etc.)

import os
import json
import re
import logging
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_DEFAULT = os.getenv("LLM_DEFAULT", "openai")

def create_entity_prompt(text):
    """
    Crea el prompt para extracción de entidades EN ESPAÑOL.
    """
    return f"""Extrae entidades y relaciones del siguiente texto. Responde TODO EN ESPAÑOL.

Responde ÚNICAMENTE con JSON válido en este formato exacto:

{{
  "entities": [
    {{"id": "ent1", "type": "Person", "text": "Juan"}},
    {{"id": "ent2", "type": "Organization", "text": "Microsoft"}}
  ],
  "relations": [
    {{"source_id": "ent1", "target_id": "ent2", "type": "trabaja_en", "text": "trabaja en"}}
  ]
}}

IMPORTANTE: Las relaciones deben estar en español (trabaja_en, ubicado_en, opera_en, etc.)

Texto: {text}

JSON:"""

def extract_json_from_text(text):
    """
    Extrae JSON de manera robusta, maneja markdown code blocks.
    """
    logging.debug(f"Extrayendo JSON del texto: {repr(text[:100])}...")
    
    # Limpiar texto básico
    text = text.strip()
    
    # Estrategia 1: Parsing directo
    try:
        result = json.loads(text)
        logging.debug("JSON parseado directamente")
        return result
    except json.JSONDecodeError:
        logging.debug("Parsing directo falló, probando otras estrategias...")
    
    # Estrategia 2: Remover markdown code blocks (PRIMERO)
    cleaned_text = text
    if "```json" in text:
        logging.debug("Detectado ```json wrapper")
        parts = text.split("```json")
        if len(parts) > 1:
            # Tomar la parte después de ```json y antes del siguiente ```
            json_candidate = parts[1].split("```")[0].strip()
            logging.debug(f"JSON extraído de markdown: {repr(json_candidate[:100])}...")
            try:
                result = json.loads(json_candidate)
                logging.debug("JSON extraído de código markdown")
                return result
            except json.JSONDecodeError as e:
                logging.debug(f"JSON de markdown falló: {e}")
                cleaned_text = json_candidate  # Usar para próximas estrategias
    elif "```" in text:
        logging.debug("Detectado ``` wrapper genérico")
        parts = text.split("```")
        if len(parts) >= 3:
            # Tomar la parte del medio
            json_candidate = parts[1].strip()
            logging.debug(f"JSON extraído de código genérico: {repr(json_candidate[:100])}...")
            try:
                result = json.loads(json_candidate)
                logging.debug("JSON extraído de código genérico")
                return result
            except json.JSONDecodeError as e:
                logging.debug(f"JSON de código genérico falló: {e}")
                cleaned_text = json_candidate
    
    # Estrategia 3: Buscar entre llaves en texto limpio
    start = cleaned_text.find('{')
    end = cleaned_text.rfind('}')
    
    if start != -1 and end != -1 and end > start:
        json_text = cleaned_text[start:end+1]
        logging.debug(f"JSON entre llaves: {repr(json_text[:100])}...")
        try:
            result = json.loads(json_text)
            logging.debug("JSON extraído entre llaves")
            return result
        except json.JSONDecodeError as e:
            logging.debug(f"JSON entre llaves falló: {e}")
    
    # Si todo falla, retornar estructura vacía
    logging.warning("No se pudo extraer JSON, retornando estructura vacía")
    return {"entities": [], "relations": []}

def validate_json_structure(data):
    """
    Valida la estructura del JSON.
    """
    if not isinstance(data, dict):
        return {"entities": [], "relations": []}
    
    # Asegurar claves principales
    if "entities" not in data:
        data["entities"] = []
    if "relations" not in data:
        data["relations"] = []
    
    # Validar entidades
    valid_entities = []
    for entity in data.get("entities", []):
        if isinstance(entity, dict) and "id" in entity:
            if "type" not in entity:
                entity["type"] = "Entity"
            if "text" not in entity:
                entity["text"] = entity["id"]
            valid_entities.append(entity)
    
    # Validar relaciones
    valid_relations = []
    entity_ids = {e["id"] for e in valid_entities}
    
    for relation in data.get("relations", []):
        if (isinstance(relation, dict) and 
            "source_id" in relation and 
            "target_id" in relation):
            # Solo incluir si las entidades existen
            if (relation["source_id"] in entity_ids and 
                relation["target_id"] in entity_ids):
                if "type" not in relation:
                    relation["type"] = "related_to"
                if "text" not in relation:
                    relation["text"] = f"{relation['source_id']} -> {relation['target_id']}"
                valid_relations.append(relation)
    
    return {
        "entities": valid_entities,
        "relations": valid_relations
    }

def openai_extract_entities_relations(text, model="gpt-4o"):
    """
    Extrae entidades usando OpenAI.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY no configurada")
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = create_entity_prompt(text)
        
        logging.debug("Llamando a OpenAI...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un experto en extracción de entidades. Responde solo con JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=1500,
        )
        
        raw_response = response.choices[0].message.content
        logging.debug(f"Respuesta de OpenAI: {raw_response[:200]}...")
        
        # Extraer y validar JSON
        extracted_data = extract_json_from_text(raw_response)
        validated_data = validate_json_structure(extracted_data)
        
        # Solo log del resultado final (importante)
        logging.info(f"Extracción completada: {len(validated_data['entities'])} entidades, {len(validated_data['relations'])} relaciones")
        return validated_data
        
    except Exception as e:
        logging.error(f"Error en OpenAI: {e}")
        import traceback
        logging.debug(traceback.format_exc())
        return {"entities": [], "relations": []}

def claude_extract_entities_relations(text, model="claude-sonnet-4-20250514"):
    """
    Extrae entidades usando Claude.
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY no configurada")
    
    try:
        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        
        prompt = create_entity_prompt(text)
        payload = {
            "model": model,
            "max_tokens": 1500,
            "temperature": 0,
            "system": "Eres un experto en extracción de entidades. Responde solo con JSON válido.",
            "messages": [{"role": "user", "content": prompt}],
        }
        
        logging.debug("Llamando a Claude...")
        resp = requests.post("https://api.anthropic.com/v1/messages", 
                           headers=headers, json=payload)
        
        if resp.status_code != 200:
            logging.error(f"Error Claude API: {resp.status_code} - {resp.text}")
            return {"entities": [], "relations": []}
        
        raw_response = resp.json()["content"][0]["text"]
        logging.debug(f"Respuesta de Claude: {raw_response[:200]}...")
        
        # Extraer y validar JSON
        extracted_data = extract_json_from_text(raw_response)
        validated_data = validate_json_structure(extracted_data)
        
        logging.info(f"Extracción Claude completada: {len(validated_data['entities'])} entidades, {len(validated_data['relations'])} relaciones")
        return validated_data
        
    except Exception as e:
        logging.error(f"Error en Claude: {e}")
        return {"entities": [], "relations": []}

def extract_entities_relations(text, llm_method=LLM_DEFAULT):
    """
    Función principal para extraer entidades y relaciones.
    """
    if not text or not text.strip():
        logging.warning("Texto vacío para extracción")
        return {"entities": [], "relations": []}
    
    # Truncar si es muy largo
    if len(text) > 4000:
        text = text[:4000] + "..."
        logging.warning("Texto truncado a 4000 caracteres")
    
    logging.debug(f"Extrayendo con {llm_method.upper()} - {len(text)} caracteres")
    
    try:
        if llm_method == "openai":
            return openai_extract_entities_relations(text)
        elif llm_method == "claude":
            return claude_extract_entities_relations(text)
        else:
            logging.warning(f"Método '{llm_method}' no soportado, usando OpenAI")
            return openai_extract_entities_relations(text)
    except Exception as e:
        logging.error(f"Error general en extracción: {e}")
        return {"entities": [], "relations": []}

def test_extraction(sample_text="Juan trabaja en Microsoft y vive en Madrid."):
    """
    Función de prueba.
    """
    logging.info(f"Probando extracción con: {sample_text}")
    
    result = extract_entities_relations(sample_text)
    logging.info("Resultado final:")
    logging.info(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result

if __name__ == "__main__":
    test_extraction()