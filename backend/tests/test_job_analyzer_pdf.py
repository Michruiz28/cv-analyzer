from agents.job_analyzer import JobAnalyzerAgent

# *** Cambia esta ruta por la de tu PDF ***
pdf_path = r"C:\Users\michr\Downloads\HOJADEVIDA.pdf.pdf"

print("\n=== TEST: Job Analyzer desde PDF ===\n")

try:
    agent = JobAnalyzerAgent()

    job = agent.process_job_from_pdf(pdf_path, generate_summary=True)

    agent.print_analysis_summary(job)

    agent.save_analysis(job, "test_job_analysis_pdf.json")

    print("\n✔ Test completado. Archivo generado: test_job_analysis_pdf.json\n")

except Exception as e:
    print(f"\n❌ ERROR durante el test: {str(e)}\n")
    import traceback
    traceback.print_exc()
