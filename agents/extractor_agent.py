import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from openai import AzureOpenAI
import json

# Cargar entorno (intentará buscar .env en la raiz)
load_dotenv(override=True)

class ExtractorAgent:
    def __init__(self, 
                 doc_endpoint=None, 
                 doc_key=None, 
                 openai_endpoint=None, 
                 openai_key=None, 
                 deployment_name="gpt-5-mini"): # <--- TU DEPLOYMENT FIJO AQUI
        
        print("\n--- Inicializando ExtractorAgent ---")

        # 1. Prioridad: Argumentos directos -> Luego: Variables de Entorno -> Error
        self.doc_endpoint = doc_endpoint or os.getenv("AZURE_DOC_ENDPOINT")
        self.doc_key = doc_key or os.getenv("AZURE_DOC_KEY")
        
        self.aoai_endpoint = openai_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.aoai_key = openai_key or os.getenv("AZURE_OPENAI_KEY")
        self.aoai_deployment = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT")
        
        # DEBUG: Ver qué credenciales está usando realmente
        print(f"Deployment a usar: '{self.aoai_deployment}'")
        print(f"Endpoint OpenAI: {self.aoai_endpoint}")

        # Validaciones
        if not self.aoai_deployment:
            raise ValueError("❌ El deployment está vacío.")

        # Clientes
        self.doc_client = DocumentAnalysisClient(
            endpoint=self.doc_endpoint,
            credential=AzureKeyCredential(self.doc_key)
        )

        self.ai_client = AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint=self.aoai_endpoint,
            api_key=self.aoai_key,
        )
        
        # Prompt del sistema
        self.system_prompt = """
        Eres un extractor experto de CVs. Devuelve JSON válido.
        Estructura requerida:
        {
          "nombre": "string", "correo": "string", "telefono": "string", "linkedin": "string",
          "idiomas": ["string"], "skills_tecnicas": ["string"], "soft_skills": ["string"],
          "anios_experiencia": null,
          "educacion": [{"institucion": "", "titulo": "", "anio": ""}],
          "experiencia_laboral": [{"cargo": "", "empresa": "", "periodo": "", "descripcion": ""}]
        }
        """

    def _extract_text_from_pdf(self, file_path):
        try:
            with open(file_path, "rb") as f:
                poller = self.doc_client.begin_analyze_document("prebuilt-read", document=f)
            result = poller.result()
            return " ".join([line.content for page in result.pages for line in page.lines])
        except Exception as e:
            print(f"Error OCR: {e}")
            return None

    def process_cv(self, file_path):
        raw_text = self._extract_text_from_pdf(file_path)
        if not raw_text: return {"error": "OCR falló"}
        
        try:
            response = self.ai_client.chat.completions.create(
                model=self.aoai_deployment, # Aquí usa la variable limpia
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"CV Text:\n{raw_text}"}
                ],
            )
            content = response.choices[0].message.content.replace("```json", "").replace("```", "")
            return json.loads(content)
        except Exception as e:
            return {"error": f"GPT falló: {str(e)}"}