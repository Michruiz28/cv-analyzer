import json
import os

from agents.extractor_agent import ExtractorAgent

# Ruta del CV que quieres usar como ejemplo
PDF_PATH = r"C:\Users\michr\Downloads\HOJADEVIDA.pdf.pdf"

# Salida del archivo
OUTPUT_JSON = "sample_candidate.json"

print("\n==============================")
print("  🧪 GENERANDO SAMPLE CANDIDATE")
print("==============================\n")

# Crear instancia del extractor exactamente como está definida
agent = ExtractorAgent()

print(f"📄 Procesando CV: {PDF_PATH} ...")

result = agent.process_cv(PDF_PATH)

print("✅ Extracción completada.")

# Guardar JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n📁 Archivo generado → {OUTPUT_JSON}")
