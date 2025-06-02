# ./agent/response.py
# Módulo responsable únicamente de generar respuestas con LLMs

import os
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Tuple
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()
logger = logging.getLogger(__name__)

class ResponseGenerator:
    """
    Responsable únicamente de generar respuestas usando LLMs y prompts configurables.
    """
    
    def __init__(self, prompts_file: str = "agent/prompts.yaml"):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.prompts = self._load_prompts(prompts_file)
    
    def _load_prompts(self, prompts_file: str) -> Dict[str, str]:
        """
        Carga prompts desde archivo YAML.
        
        Args:
            prompts_file: Ruta al archivo de prompts
            
        Returns:
            Diccionario con prompts cargados
        """
        try:
            prompts_path = Path(prompts_file)
            if prompts_path.exists():
                with open(prompts_path, 'r', encoding='utf-8') as f:
                    prompts = yaml.safe_load(f)
                logger.info(f"Prompts loaded from {prompts_file}")
                return prompts
            else:
                logger.warning(f"Prompts file not found: {prompts_file}. Using defaults.")
                return self._get_default_prompts()
                
        except Exception as e:
            logger.error(f"Error loading prompts: {e}. Using defaults.")
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict[str, str]:
        """
        Prompts por defecto si no se puede cargar el archivo.
        """
        return {
            "system_prompt": "Eres un asistente especializado en responder preguntas basándote únicamente en el contexto proporcionado.",
            "rag_template": """CONTEXTO:
{context}

PREGUNTA: {question}

INSTRUCCIONES:
- Responde SOLO basándote en la información del contexto
- Si la información no está en el contexto, di "No tengo información suficiente sobre ese tema en los documentos proporcionados"
- Cita fragmentos específicos cuando sea relevante
- Sé claro, preciso y conciso

RESPUESTA:""",
            "no_context_template": "No hay información disponible para responder a la pregunta: {question}"
        }
    
    def generate_response_openai(self, question: str, context: str) -> Tuple[str, Dict[str, Any]]:
        """
        Genera respuesta usando OpenAI.
        
        Args:
            question: Pregunta del usuario
            context: Contexto construido a partir de chunks
            
        Returns:
            Tuple de (respuesta, información_educativa)
        """
        try:
            # Construir prompt usando template
            if context.strip():
                prompt = self.prompts["rag_template"].format(
                    context=context,
                    question=question
                )
            else:
                prompt = self.prompts["no_context_template"].format(question=question)
            
            # Llamada a OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.prompts["system_prompt"]},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Más determinístico para RAG
                max_tokens=800,
                top_p=0.95
            )
            
            answer = response.choices[0].message.content
            
            # Información educativa
            response_info = {
                "step": "response_generation",
                "llm_used": "OpenAI GPT-4o",
                "model": "gpt-4o",
                "temperature": 0.1,
                "max_tokens": 800,
                "prompt_length": len(prompt),
                "response_length": len(answer),
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else "N/A",
                "has_context": bool(context.strip()),
                "success": True
            }
            
            logger.info(f"OpenAI response generated: {len(answer)} chars")
            return answer, response_info
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            error_info = {
                "step": "response_generation",
                "llm_used": "OpenAI GPT-4o",
                "error": str(e),
                "success": False
            }
            return f"Error generando respuesta: {str(e)}", error_info
    
    def generate_response_claude(self, question: str, context: str) -> Tuple[str, Dict[str, Any]]:
        """
        Genera respuesta usando Claude.
        
        Args:
            question: Pregunta del usuario
            context: Contexto construido a partir de chunks
            
        Returns:
            Tuple de (respuesta, información_educativa)
        """
        try:
            if not self.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY no configurada")
            
            # Construir prompt usando template
            if context.strip():
                prompt = self.prompts["rag_template"].format(
                    context=context,
                    question=question
                )
            else:
                prompt = self.prompts["no_context_template"].format(question=question)
            
            # Headers para Claude
            headers = {
                "x-api-key": self.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            
            # Payload para Claude
            payload = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 800,
                "temperature": 0.1,
                "system": self.prompts["system_prompt"],
                "messages": [{"role": "user", "content": prompt}],
            }
            
            # Llamada a Claude
            resp = requests.post(
                "https://api.anthropic.com/v1/messages", 
                headers=headers, 
                json=payload,
                timeout=30
            )
            
            if resp.status_code != 200:
                raise Exception(f"Claude API error: {resp.status_code} - {resp.text}")
            
            answer = resp.json()["content"][0]["text"]
            
            # Información educativa
            response_info = {
                "step": "response_generation",
                "llm_used": "Claude Sonnet 4",
                "model": "claude-sonnet-4-20250514",
                "temperature": 0.1,
                "max_tokens": 800,
                "prompt_length": len(prompt),
                "response_length": len(answer),
                "has_context": bool(context.strip()),
                "success": True
            }
            
            logger.info(f"Claude response generated: {len(answer)} chars")
            return answer, response_info
            
        except Exception as e:
            logger.error(f"Error generating Claude response: {e}")
            error_info = {
                "step": "response_generation",
                "llm_used": "Claude Sonnet 4",
                "error": str(e),
                "success": False
            }
            return f"Error generando respuesta: {str(e)}", error_info
    
    def generate_response(self, question: str, context: str, llm_method: str = "openai") -> Tuple[str, Dict[str, Any]]:
        """
        Genera respuesta usando el LLM especificado.
        
        Args:
            question: Pregunta del usuario
            context: Contexto construido
            llm_method: 'openai' o 'claude'
            
        Returns:
            Tuple de (respuesta, información_educativa)
        """
        if llm_method.lower() == "openai":
            return self.generate_response_openai(question, context)
        elif llm_method.lower() == "claude":
            return self.generate_response_claude(question, context)
        else:
            logger.warning(f"Unknown LLM method: {llm_method}. Using OpenAI.")
            return self.generate_response_openai(question, context)
    
    def reload_prompts(self, prompts_file: str = "agent/prompts.yaml") -> bool:
        """
        Recarga prompts desde archivo.
        
        Args:
            prompts_file: Ruta al archivo de prompts
            
        Returns:
            True si se recargaron exitosamente
        """
        try:
            new_prompts = self._load_prompts(prompts_file)
            self.prompts = new_prompts
            logger.info("Prompts reloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error reloading prompts: {e}")
            return False