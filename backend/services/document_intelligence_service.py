import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient


class DocumentIntelligenceService:
    """Servicio para extraer texto de documentos con Azure Document Intelligence (Form Recognizer)"""

    def __init__(self):
        self.endpoint = os.getenv("AZURE_DOC_ENDPOINT")
        self.key = os.getenv("AZURE_DOC_KEY")

        if not self.endpoint or not self.key:
            raise ValueError("❌ Faltan AZURE_DOC_ENDPOINT o AZURE_DOC_KEY en el .env")

        print(f"[DocumentIntelligence] Endpoint cargado: {self.endpoint}")

        # ✔ Cliente correcto (el que sí funciona en tu prueba manual)
        self.client = DocumentAnalysisClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key)
        )

    def extract_text_from_pdf(self, pdf_path: str):
        """Extrae texto de un PDF usando el modelo prebuilt-read"""

        if not os.path.exists(pdf_path):
            raise Exception(f"❌ Archivo no encontrado: {pdf_path}")

        print(f"[DocumentIntelligence] Analizando PDF: {pdf_path}")

        with open(pdf_path, "rb") as f:
            poller = self.client.begin_analyze_document(
                model_id="prebuilt-read",  # ✔ Modelo correcto
                document=f
            )

        result = poller.result()

        # Extraer texto
        text = ""
        for page in result.pages:
            for line in page.lines:
                text += line.content + "\n"

        return {
            "text": text,
            "pages": len(result.pages),
            "tables": getattr(result, "tables", [])
        }
