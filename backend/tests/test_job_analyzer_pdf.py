import os
from agents.job_analyzer import JobAnalyzerAgent

print("\n🚀 INICIANDO TEST DESDE PDF")
print("=" * 70)

agent = JobAnalyzerAgent()

# Ruta a un PDF real
pdf_path = r"C:\Users\michr\Downloads\oferta.pdf"

if not os.path.exists(pdf_path):
    raise Exception("❌ No se encontró el archivo PDF. Verifica la ruta.")

job = agent.process_job_from_pdf(pdf_path)

print("\n📌 TÍTULO:", job.analysis.title)
print("📌 EMPRESA:", job.analysis.company)
print("📌 RESPONSABILIDADES:", len(job.analysis.responsibilities))
print("📌 REQUISITOS:", len(job.analysis.technical_requirements))

# Guardar análisis para verificar
agent.save_analysis(job, "job_analysis_from_pdf.json")

print("\n✅ TEST COMPLETADO. Archivo generado: job_analysis_from_pdf.json")
