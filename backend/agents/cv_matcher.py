"""
CV Matcher Agent - Compara CVs contra una oferta y devuelve score + justificación
"""
import re
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from services.azure_openai_service import AzureOpenAIService

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    # Solo para el editor / type checkers
    from models.job import JobAnalysis
else:
    # En tiempo de ejecución, si no existe la importación, usamos Any
    JobAnalysis = Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ================================================================
# HELPERS
# ================================================================
def _normalize_list(lst: List[str]) -> List[str]:
    """Normaliza texto: lower, strip, quitar duplicados"""
    out = []
    for s in lst or []:
        if not s:
            continue
        s2 = re.sub(r'[^\w\s\-+]', '', s.lower()).strip()
        if s2 and s2 not in out:
            out.append(s2)
    return out


def _overlap_ratio(list_a: List[str], list_b: List[str]) -> float:
    """Devuelve ratio de solapamiento entre 0 y 1"""
    if not list_a:
        return 0.0
    a = set(_normalize_list(list_a))
    b = set(_normalize_list(list_b))
    inter = a.intersection(b)
    return len(inter) / max(1, len(a))


def _normalize_json(obj: Any):
    """
    Convierte cualquier objeto no-serializable (datetime, Pydantic, etc)
    en valores válidos para JSON.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()

    if hasattr(obj, "model_dump"):  # pydantic
        return obj.model_dump()

    return str(obj)


# ================================================================
# AGENTE PRINCIPAL
# ================================================================
class CVMatcherAgent:
    """
    Agente que compara un JobAnalysis con candidatos
    """

    def __init__(self, use_openai: bool = True):
        logger.info("Inicializando CVMatcherAgent...")
        self.openai = AzureOpenAIService() if use_openai else None
        self.use_openai = use_openai and (self.openai is not None)
        logger.info(f"CVMatcherAgent listo (use_openai={self.use_openai})")

        # pesos (ajustables)
        self.weights = {
            "technical_requirements": 0.45,
            "ats_keywords": 0.20,
            "experience": 0.15,
            "education": 0.10,
            "soft_skills": 0.10
        }

    # ================================================================
    # SCORE HEURÍSTICO BASE
    # ================================================================
    def _heuristic_score(self, job: JobAnalysis, candidate: Dict[str, Any]) -> Dict[str, Any]:
        job_tech = job.technical_requirements or []
        job_ats = job.ats_keywords or []
        job_soft = job.soft_skills or []
        job_experience_req = job.experience_required or ""

        cand_tech = candidate.get("skills_tecnicas", []) or []
        cand_soft = candidate.get("soft_skills", []) or []
        cand_education = candidate.get("educacion", []) or []
        cand_years = candidate.get("anios_experiencia", None)

        tech_ratio = _overlap_ratio(job_tech, cand_tech)
        ats_ratio = _overlap_ratio(job_ats, cand_tech + (cand_soft or []))
        soft_ratio = _overlap_ratio(job_soft, cand_soft)

        # experiencia
        req_years = None
        m = re.search(r'(\d+)', str(job_experience_req))
        if m:
            req_years = int(m.group(1))

        if req_years is None or cand_years is None:
            exp_score = 0.5
        else:
            exp_score = 1.0 if cand_years >= req_years else max(0.0, cand_years / req_years)

        # educación
        edu_score = 0.0
        job_edu_text = (job.education or "").lower() if isinstance(job.education, str) else ""
        if job_edu_text:
            for e in cand_education:
                joined = " ".join(e.values()).lower() if isinstance(e, dict) else str(e).lower()
                if any(word in joined for word in job_edu_text.split()):
                    edu_score = 1.0
                    break
        else:
            edu_score = 0.5

        w = self.weights
        base_score = (
            tech_ratio * w["technical_requirements"] +
            ats_ratio * w["ats_keywords"] +
            exp_score * w["experience"] +
            edu_score * w["education"] +
            soft_ratio * w["soft_skills"]
        )

        match_score = int(round(base_score * 100))

        strengths = []
        gaps = []

        if tech_ratio >= 0.6:
            strengths.append("Skills técnicas alineadas con los requisitos clave")
        if ats_ratio >= 0.5:
            strengths.append("Coincidencia con keywords ATS importantes")
        if exp_score >= 0.9:
            strengths.append("Experiencia suficiente")
        if edu_score >= 0.9:
            strengths.append("Educación acorde a lo solicitado")
        if soft_ratio >= 0.6:
            strengths.append("Habilidades blandas alineadas")

        if tech_ratio < 0.4:
            gaps.append("Faltan skills técnicas importantes")
        if ats_ratio < 0.25:
            gaps.append("Poca coincidencia con keywords ATS")
        if req_years and (cand_years is None or cand_years < req_years * 0.6):
            gaps.append("Experiencia por debajo del nivel esperado")
        if edu_score < 0.5 and job_edu_text:
            gaps.append("Educación no se ajusta completamente")
        if soft_ratio < 0.3:
            gaps.append("Habilidades blandas limitadas")

        return {
            "match_score": match_score,
            "base_components": {
                "technical_ratio": round(tech_ratio, 3),
                "ats_ratio": round(ats_ratio, 3),
                "experience_score": round(exp_score, 3),
                "education_score": round(edu_score, 3),
                "soft_ratio": round(soft_ratio, 3)
            },
            "strengths": strengths,
            "gaps": gaps
        }

    # ================================================================
    # OPENAI – REFINAMIENTO DEL MATCH
    # ================================================================
    def _openai_refine(self, job: JobAnalysis, candidate: Dict[str, Any], base_result: Dict[str, Any]) -> Dict[str, Any]:

        if not self.use_openai:
            return base_result

        # normalizar todo a JSON seguro
        job_clean = job.model_dump() if hasattr(job, "model_dump") else job
        cand_clean = candidate
        base_clean = json.loads(json.dumps(base_result, default=_normalize_json))

        # payload para el modelo
        user_content = {
            "job_profile": job_clean,
            "candidate_profile": cand_clean,
            "base_evaluation": base_clean
        }

        user_text = json.dumps(user_content, indent=2, ensure_ascii=False, default=_normalize_json)

        system_prompt = (
            "Eres un experto en reclutamiento. Ajusta el score del candidato basado en criterios "
            "técnicos, experiencia, educación y habilidades. Devuelve SOLO JSON válido con:\n"
            "{ match_score, strengths, gaps, justification }"
        )

        try:
            response = self.openai.analyze_with_system_prompt(
                system_prompt=system_prompt,
                user_content=user_text,
                temperature=None,
                json_mode=True,
            )

            raw = response.replace("```json", "").replace("```", "").strip()
            refined = json.loads(raw)

            if "match_score" in refined:
                refined["match_score"] = int(round(float(refined["match_score"])))

            return refined

        except Exception as e:
            logger.warning(f"[OpenAI] Error refinando match: {e}")
            return base_result

    # ================================================================
    # API PRINCIPALES
    # ================================================================
    def match_candidate(self, job: JobAnalysis, candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        base = self._heuristic_score(job, candidate_profile)

        if not self.use_openai:
            return {
                **base,
                "justification": None
            }

        refined = self._openai_refine(job, candidate_profile, base)

        return {
            "match_score": refined.get("match_score", base["match_score"]),
            "strengths": refined.get("strengths", base["strengths"]),
            "gaps": refined.get("gaps", base["gaps"]),
            "justification": refined.get("justification", ""),
            "base_components": base["base_components"],
            "raw_refined": refined
        }

    def match_batch(self, job: JobAnalysis, candidates: List[Dict[str, Any]], top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        results = []
        for cand in candidates:
            r = self.match_candidate(job, cand)
            r["candidate"] = cand
            results.append(r)

        results.sort(key=lambda x: x["match_score"], reverse=True)

        for i, r in enumerate(results, 1):
            r["rank"] = i

        return results[:top_k] if top_k else results
