# ./core/llm.py
# Lógica para extracción de entidades y relaciones usando LLMs (OpenAI GPT, Claude, etc.)

import os
from dotenv import load_dotenv
import openai
import requests

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LLM_DEFAULT = os.getenv("LLM_DEFAULT", "openai")  # 'openai' o 'claude'

# --- Helper: prompt para extracción de entidades/relaciones ---
ENTITY_RELATION_PROMPT = """
Extrae todas las entidades principales (personas, organizaciones, lugares, conceptos) y las relaciones entre ellas en el siguiente texto. Devuelve el resultado en formato JSON:
{
  "entities": [
    {"id": "ent1", "type": "Person", "text": "John Smith"},
    ...
  ],
  "relations": [
    {"source_id": "ent1", "target_id": "ent2", "type": "works_at", "text": "trabaja en"},
    ...
  ]
}
Texto:
\"\"\"{text}\"\"\"
"""

# --- OpenAI LLM (GPT-4o, GPT-4) ---
def openai_extract_entities_relations(text, model="gpt-4o"):
    openai.api_key = OPENAI_API_KEY
    prompt = ENTITY_RELATION_PROMPT.format(text=text)
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": "Eres un experto en extracción de conocimiento."},
                  {"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=1000,
    )
    # Asume respuesta JSON válida en el mensaje del assistant
    import json
    raw = response.choices[0].message["content"]
    try:
        return json.loads(raw)
    except Exception as e:
        raise RuntimeError(f"Error al parsear la respuesta del LLM: {e}\nRespuesta: {raw}")

# --- Claude (Anthropic) LLM ---
def claude_extract_entities_relations(text, model="claude-3-sonnet-20240229"):
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    system_prompt = "Eres un experto en extracción de conocimiento."
    prompt = ENTITY_RELATION_PROMPT.format(text=text)
    payload = {
        "model": model,
        "max_tokens": 1000,
        "temperature": 0.0,
        "system": system_prompt,
        "messages": [{"role": "user", "content": prompt}],
    }
    url = "https://api.anthropic.com/v1/messages"
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        raise RuntimeError(f"Claude API error: {resp.status_code} {resp.text}")
    import json
    msg = resp.json()["content"][0]["text"]
    try:
        return json.loads(msg)
    except Exception as e:
        raise RuntimeError(f"Error al parsear la respuesta de Claude: {e}\nRespuesta: {msg}")

def extract_entities_relations(text, llm_method=LLM_DEFAULT):
    """
    Llama al LLM elegido y devuelve las entidades y relaciones extraídas del texto.
    """
    if llm_method == "openai":
        return openai_extract_entities_relations(text)
    elif llm_method == "claude":
        return claude_extract_entities_relations(text)
    else:
        raise ValueError(f"LLM method '{llm_method}' no soportado")