import os
import json
from dotenv import load_dotenv  # <--- IMPORT THIS
from openai import AzureOpenAI

# Load the .env file variables into the system
load_dotenv() 

class ExtractorAgent:

    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.key = os.getenv("AZURE_OPENAI_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        # Debugging: Print to check if they are loaded (Remove this in production!)
        if not self.key or not self.endpoint:
            raise ValueError("Environment variables not found! Check your .env file.")

        self.client = AzureOpenAI(
            api_key=self.key,
            api_version="2024-02-15-preview",
            azure_endpoint=self.endpoint
        )

    def extract_profile(self, texto_crudo: str):
        system_prompt = """
        Eres un extractor experto de CVs. Devuelve JSON válido.
        Estructura requerida:
        {
          "nombre": "string",
          "correo": "string",
          "telefono": "string",
          "linkedin": "string",
          "idiomas": ["string"],
          "skills_tecnicas": ["string"],
          "soft_skills": ["string"],
          "anios_experiencia": null,
          "educacion": [{"institucion": "", "titulo": "", "anio": ""}],
          "experiencia_laboral": [{"cargo": "", "empresa": "", "periodo": "", "descripcion": ""}]
        }
        """

        try:
            response = self.client.chat.completions.create(
                model=self.deployment, 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": texto_crudo}
                ],
                temperature=0,
                response_format={"type": "json_object"} 
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return {}