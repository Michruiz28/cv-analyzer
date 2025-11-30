import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv
load_dotenv()

endpoint = os.getenv("AZURE_DOC_ENDPOINT")
key = os.getenv("AZURE_DOC_KEY")

client = DocumentAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

# Ruta a tu PDF local
file_path = "sample_cv.pdf"

with open(file_path, "rb") as f:
    poller = client.begin_analyze_document(
        model_id="prebuilt-read",  # ESTE modelo te da texto crudo
        document=f
    )

result = poller.result()

# Extraer todo el texto concatenado
texto = ""
for page in result.pages:
    for line in page.lines:
        texto += line.content + "\n"

print("\n===== TEXTO EXTRAÍDO =====\n")
print(texto)
