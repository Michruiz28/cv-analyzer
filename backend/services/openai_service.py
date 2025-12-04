"""
Servicio centralizado para interactuar con OpenAI API o Azure OpenAI.
"""
import json
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from config import settings
from openai import OpenAI, AzureOpenAI
from typing import Optional, Dict, Any, List



class OpenAIService:
    """
    Cliente unificado para OpenAI API y Azure OpenAI.
    Detecta automáticamente cuál usar según la configuración.
    """
    
    def __init__(self):
        """Inicializa el cliente según la configuración disponible"""
        self.client_type = settings.get_openai_client_type()
        
        if self.client_type == "azure":
            self.client = AzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_KEY,
                api_version=settings.AZURE_OPENAI_API_VERSION
            )
            self.model = settings.AZURE_OPENAI_DEPLOYMENT
            print(f"Usando Azure OpenAI: {self.model}")
            
        elif self.client_type == "openai":
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
            print(f"Usando OpenAI API: {self.model}")
            
        else:
            raise ValueError(
                "No se encontró configuración válida de OpenAI. "
                "Por favor configura OPENAI_API_KEY o Azure OpenAI en .env"
            )
    
    def get_completion(
        self,
        prompt: str,
        system_message: str = "Eres un asistente experto en análisis de recursos humanos.",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Obtiene una respuesta de texto del modelo.
        
        Args:
            prompt: El mensaje del usuario
            system_message: Instrucciones del sistema
            temperature: Creatividad (0-1)
            max_tokens: Máximo de tokens en la respuesta
            
        Returns:
            Respuesta en texto plano
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"Error al llamar a OpenAI: {str(e)}")
    
    def get_structured_output(
        self,
        prompt: str,
        system_message: str = "Eres un asistente que responde en formato JSON.",
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Obtiene una respuesta estructurada en formato JSON.
        
        Args:
            prompt: El mensaje del usuario (debe incluir instrucciones de formato JSON)
            system_message: Instrucciones del sistema
            temperature: Creatividad (0-1, usar bajo para JSON consistente)
            max_tokens: Máximo de tokens en la respuesta
            
        Returns:
            Diccionario con la respuesta parseada
        """
        try:
            # Asegurarse de que el prompt pida JSON
            if "JSON" not in prompt and "json" not in prompt:
                prompt += "\n\nResponde ÚNICAMENTE en formato JSON válido, sin texto adicional."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}  # Fuerza respuesta JSON
            )
            
            content = response.choices[0].message.content.strip()
            
            # Intentar parsear JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Si falla, intentar limpiar y parsear de nuevo
                content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(content)
        
        except Exception as e:
            raise Exception(f"Error al obtener respuesta estructurada: {str(e)}")
    
    def get_batch_completions(
        self,
        prompts: List[str],
        system_message: str = "Eres un asistente experto en análisis de recursos humanos.",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> List[str]:
        """
        Procesa múltiples prompts en paralelo (útil para procesar varios CVs).
        
        Args:
            prompts: Lista de prompts a procesar
            system_message: Instrucciones del sistema
            temperature: Creatividad
            max_tokens: Máximo de tokens por respuesta
            
        Returns:
            Lista de respuestas en el mismo orden
        """
        results = []
        
        for prompt in prompts:
            try:
                result = self.get_completion(
                    prompt=prompt,
                    system_message=system_message,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                results.append(result)
            except Exception as e:
                print(f"Error procesando prompt: {str(e)}")
                results.append(None)
        
        return results
    
    def count_tokens(self, text: str) -> int:
        """
        Estima el número de tokens en un texto.
        Regla aproximada: 1 token ≈ 4 caracteres en inglés
        
        Args:
            text: Texto a analizar
            
        Returns:
            Número aproximado de tokens
        """
        # Aproximación simple (para uso más preciso, instalar tiktoken)
        return len(text) // 4


# Instancia global del servicio
openai_service = OpenAIService()


# Función de prueba
def test_openai_service():
    """Función para probar que el servicio funciona correctamente"""
    print("\nProbando OpenAI Service\n")
    
    try:
        # Test 1: Respuesta simple
        print("Test 1: Respuesta de texto simple")
        response = openai_service.get_completion(
            prompt="Di 'Hola' si me puedes leer",
            system_message="Eres un asistente útil.",
            temperature=0.3,
            max_tokens=50
        )
        print(f" Respuesta: {response}\n")
        
        # Test 2: Respuesta estructurada JSON
        print("Test 2: Respuesta en formato JSON")
        json_response = openai_service.get_structured_output(
            prompt="""
            Analiza esta información y responde en JSON:
            Candidato: Juan Pérez, 5 años de experiencia en Python
            
            Formato esperado:
            {
                "nombre": "...",
                "experiencia_años": ...,
                "skills": [...]
            }
            """,
            temperature=0.3
        )
        print(f"Respuesta JSON: {json.dumps(json_response, indent=2, ensure_ascii=False)}\n")
        
        print("Todos los tests pasaron correctamente!")
        return True
        
    except Exception as e:
        print(f"Error en los tests: {str(e)}")
        return False


if __name__ == "__main__":
    test_openai_service()