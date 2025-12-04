import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv

load_dotenv()

# Cargar las variables
endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT") or os.getenv("AZURE_DOC_ENDPOINT")
key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY") or os.getenv("AZURE_DOC_KEY")

print("🔎 ENDPOINT:", endpoint)
print("🔑 KEY:", "(cargada)" if key else "❌ NO CARGADA")

if not endpoint or not key:
    print("❌ ERROR: Las variables del .env no están cargando")
    exit()

# Crear cliente
client = DocumentAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
)

# Ruta al PDF
file_path = r"C:\Users\michr\Downloads\oferta.pdf"   # ← CAMBIA ESTO SI QUIERES

print("\n📄 Leyendo archivo:", file_path)

with open(file_path, "rb") as f:
    print("⏳ Enviando a Azure Document Intelligence...")
    poller = client.begin_analyze_document(
        model_id="prebuilt-read",
        document=f
    )

print("⏳ Esperando resultado...")
result = poller.result()

# Extraer texto
text = ""
for page in result.pages:
    for line in page.lines:
        text += line.content + "\n"

print("\n✅ EXTRACCIÓN EXITOSA")
print("📝 Primeros 10000 caracteres extraídos:")
print(text[:10000])
