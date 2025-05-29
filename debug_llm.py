#!/usr/bin/env python3
# debug_llm.py
# Script específico para debuggear qué está devolviendo el LLM

import os
import json
import sys
from dotenv import load_dotenv
from openai import OpenAI

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def debug_openai_response():
    """
    Prueba directa con OpenAI para ver qué está devolviendo exactamente.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY no encontrada en .env")
        return
    
    print("🔑 API Key encontrada (primeros 10 chars):", api_key[:10] + "...")
    
    # Prompt super simple y directo
    simple_prompt = """Extrae entidades y relaciones del texto: "Juan trabaja en Microsoft y vive en Madrid."

Responde ÚNICAMENTE con este formato JSON exacto:
{
  "entities": [
    {"id": "juan", "type": "Person", "text": "Juan"},
    {"id": "microsoft", "type": "Organization", "text": "Microsoft"}
  ],
  "relations": [
    {"source_id": "juan", "target_id": "microsoft", "type": "works_at", "text": "trabaja en"}
  ]
}

JSON:"""
    
    try:
        client = OpenAI(api_key=api_key)
        print("🔄 Haciendo llamada a OpenAI...")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": simple_prompt}
            ],
            temperature=0,
            max_tokens=500,
        )
        
        raw_response = response.choices[0].message.content
        print("\n" + "="*60)
        print("📄 RESPUESTA CRUDA COMPLETA:")
        print("="*60)
        print(repr(raw_response))  # repr para ver caracteres especiales
        print("="*60)
        print("📄 RESPUESTA CRUDA COMO TEXTO:")
        print("="*60)
        print(raw_response)
        print("="*60)
        
        # Intentar parsear JSON
        print("\n🔍 INTENTANDO PARSEAR JSON...")
        try:
            parsed = json.loads(raw_response.strip())
            print("✅ JSON parseado exitosamente:")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON: {e}")
            print(f"🔧 Posición del error: {e.pos}")
            if e.pos < len(raw_response):
                print(f"🔧 Carácter problemático: {repr(raw_response[e.pos-5:e.pos+5])}")
            
            # Intentar limpiar el texto
            print("\n🧹 INTENTANDO LIMPIAR...")
            cleaned = raw_response.strip()
            
            # Remover posibles prefijos
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            
            cleaned = cleaned.strip()
            print(f"📝 Texto limpio: {repr(cleaned)}")
            
            try:
                parsed = json.loads(cleaned)
                print("✅ JSON parseado después de limpiar:")
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e2:
                print(f"❌ Aún no se puede parsear: {e2}")
                
                # Buscar JSON manualmente
                start = cleaned.find('{')
                end = cleaned.rfind('}')
                if start != -1 and end != -1 and end > start:
                    json_candidate = cleaned[start:end+1]
                    print(f"🔍 JSON candidato extraído: {repr(json_candidate)}")
                    try:
                        parsed = json.loads(json_candidate)
                        print("✅ JSON extraído exitosamente:")
                        print(json.dumps(parsed, indent=2, ensure_ascii=False))
                    except json.JSONDecodeError as e3:
                        print(f"❌ JSON candidato también falló: {e3}")
        
    except Exception as e:
        print(f"❌ Error en la llamada a OpenAI: {e}")
        print(f"🔍 Tipo de error: {type(e)}")

def test_minimal_prompt():
    """
    Prueba con un prompt aún más minimal.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY no encontrada")
        return
    
    # Prompt súper directo
    prompt = 'Responde solo con JSON válido: {"entities": [{"id": "test", "type": "Person", "text": "Test"}], "relations": []}'
    
    try:
        client = OpenAI(api_key=api_key)
        print("🧪 Probando prompt minimal...")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=200,
        )
        
        raw = response.choices[0].message.content
        print(f"📄 Respuesta minimal: {repr(raw)}")
        
        try:
            parsed = json.loads(raw.strip())
            print("✅ Prompt minimal funcionó:")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"❌ Incluso el prompt minimal falló: {e}")
            
    except Exception as e:
        print(f"❌ Error en prompt minimal: {e}")

def check_environment():
    """
    Verifica el entorno y configuración.
    """
    print("🔧 VERIFICACIÓN DEL ENTORNO:")
    print("-" * 40)
    
    # Variables de entorno
    openai_key = os.getenv("OPENAI_API_KEY")
    claude_key = os.getenv("ANTHROPIC_API_KEY")
    llm_default = os.getenv("LLM_DEFAULT", "openai")
    
    print(f"OpenAI API Key: {'✅ Presente' if openai_key else '❌ Faltante'}")
    print(f"Claude API Key: {'✅ Presente' if claude_key else '❌ Faltante'}")
    print(f"LLM Default: {llm_default}")
    
    # Librerías
    try:
        import openai
        print(f"✅ OpenAI library: {openai.__version__}")
    except ImportError as e:
        print(f"❌ OpenAI library: {e}")
    
    try:
        import requests
        print("✅ Requests library: OK")
    except ImportError as e:
        print(f"❌ Requests library: {e}")

if __name__ == "__main__":
    print("🐛 DEBUGGING LLM RESPONSES")
    print("=" * 50)
    
    check_environment()
    print("\n")
    
    test_minimal_prompt()
    print("\n")
    
    debug_openai_response()