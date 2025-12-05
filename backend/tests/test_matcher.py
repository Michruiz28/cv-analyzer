# tests/test_matcher.py
from agents.cv_matcher import CVMatcherAgent
from models.job import JobAnalysis  # si existe
import json

# Carga job desde tu archivo generado por job_analyzer
with open("job_analysis_from_pdf.json", "r", encoding="utf-8") as f:
    job_json = json.load(f)

# si tienes clase JobAnalysis que acepta dict -> úsala; si no, pasa el dict tal cual
job = JobAnalysis(**job_json["analysis"]) if hasattr(JobAnalysis, "__name__") else job_json["analysis"]

# carga un candidate (ejemplo desde extractor)
with open("sample_candidate.json", "r", encoding="utf-8") as f:
    candidate = json.load(f)

matcher = CVMatcherAgent(use_openai=True)  # primero prueba sin OpenAI (más barato)
result = matcher.match_candidate(job, candidate)
print(json.dumps(result, indent=2, ensure_ascii=False))
