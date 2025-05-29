#!/usr/bin/env python3
# test_extraction.py
# Script para probar la extracción de entidades y relaciones

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.llm import extract_entities_relations, test_extraction
import json

def test_with_different_texts():
    """
    Prueba la extracción con diferentes tipos de texto.
    """
    test_texts = [
        "Juan Pérez trabaja en Microsoft España como ingeniero de software.",
        "La empresa Apple fue fundada por Steve Jobs en Cupertino, California.",
        "El Real Madrid ganó la Champions League en 2022 bajo la dirección de Carlo Ancelotti.",
        "OpenAI desarrolló ChatGPT, un modelo de lenguaje basado en GPT-4.",
        "María García estudió en la Universidad Complutense de Madrid y ahora vive en Barcelona."
    ]
    
    print("🧪 INICIANDO PRUEBAS DE EXTRACCIÓN DE ENTIDADES")
    print("=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 PRUEBA {i}:")
        print(f"Texto: {text}")
        print("-" * 40)
        
        try:
            result = extract_entities_relations(text)
            
            print(f"✅ Entidades encontradas: {len(result.get('entities', []))}")
            for entity in result.get('entities', []):
                print(f"   - {entity.get('text', 'N/A')} ({entity.get('type', 'N/A')})")
            
            print(f"✅ Relaciones encontradas: {len(result.get('relations', []))}")
            for relation in result.get('relations', []):
                print(f"   - {relation.get('source_id', 'N/A')} -> {relation.get('target_id', 'N/A')} ({relation.get('type', 'N/A')})")
            
        except Exception as e:
            print(f"❌ Error en prueba {i}: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBAS COMPLETADAS")

def test_json_parsing():
    """
    Prueba específica para el parsing de JSON.
    """
    from core.llm import extract_json_from_text, validate_and_fix_json_structure
    
    print("\n🧪 PROBANDO PARSING DE JSON")
    print("-" * 40)
    
    # Casos de prueba para JSON
    test_cases = [
        '{"entities": [{"id": "test", "type": "Person", "text": "Test"}], "relations": []}',
        'Aquí está el JSON: {"entities": [], "relations": []}',
        '```json\n{"entities": [{"id": "e1", "text": "Entity"}], "relations": []}\n```',
        'La respuesta es:\n{\n  "entities": [],\n  "relations": []\n}',
        '{"entities": [{"id": "malformed"'  # JSON malformado
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nCaso {i}: {case[:50]}...")
        try:
            result = extract_json_from_text(case)
            validated = validate_and_fix_json_structure(result)
            print(f"✅ Extraído: {len(validated['entities'])} entidades, {len(validated['relations'])} relaciones")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Verificar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    claude_key = os.getenv("ANTHROPIC_API_KEY")
    
    print("🔧 VERIFICACIÓN DE CONFIGURACIÓN:")
    print(f"OpenAI API Key: {'✅ Configurada' if openai_key else '❌ Faltante'}")
    print(f"Claude API Key: {'✅ Configurada' if claude_key else '❌ Faltante'}")
    
    if not openai_key and not claude_key:
        print("❌ No hay claves API configuradas. Configura al menos una en tu archivo .env")
        sys.exit(1)
    
    # Ejecutar pruebas
    test_json_parsing()
    test_with_different_texts()