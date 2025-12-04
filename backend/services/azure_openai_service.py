"""
Servicio para interactuar con Azure OpenAI
"""
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

class AzureOpenAIService:
    """Servicio para interactuar con Azure OpenAI"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    
    def chat_completion(self, messages, temperature=None, response_format=None):
        """
        Realiza una llamada al modelo de chat
        
        Args:
            messages: Lista de mensajes en formato OpenAI
            temperature: Control de creatividad (0-1) - None para usar default
            response_format: Formato de respuesta (None o {"type": "json_object"})
        
        Returns:
            str: Respuesta del modelo
        """
        try:
            params = {
                "model": self.deployment_name,
                "messages": messages,
            }
            
            # Solo agregar temperature si no es None
            if temperature is not None:
                params["temperature"] = temperature
            
            if response_format:
                params["response_format"] = response_format
            
            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"Error en Azure OpenAI: {str(e)}")
    
    def analyze_with_system_prompt(self, system_prompt, user_content, temperature=None, json_mode=False):
        """
        Método simplificado para análisis con system prompt
        
        Args:
            system_prompt: Instrucciones del sistema
            user_content: Contenido a analizar
            temperature: Control de creatividad (None para usar default del modelo)
            json_mode: Si debe devolver JSON
        
        Returns:
            str: Respuesta del modelo
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        response_format = {"type": "json_object"} if json_mode else None
        
        return self.chat_completion(messages, temperature, response_format)