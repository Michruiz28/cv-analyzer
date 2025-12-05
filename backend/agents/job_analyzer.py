"""
Job Analyzer Agent - Agente especializado en analizar ofertas de trabajo
"""
import json
import logging
from typing import Dict
from datetime import datetime

from backend.services.azure_openai_service import AzureOpenAIService
from backend.services.document_intelligence_service import DocumentIntelligenceService
from backend.models.job import Job, JobAnalysis
from backend.utils.prompts import (
    JOB_ANALYSIS_SYSTEM_PROMPT,
    JOB_SUMMARY_SYSTEM_PROMPT,
    get_job_analysis_prompt,
    get_summary_prompt
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobAnalyzerAgent:
    """Agente especializado en analizar ofertas de trabajo"""

    def __init__(self):
        logger.info(" Inicializando Job Analyzer Agent...")
        self.openai_service = AzureOpenAIService()
        self.doc_service = DocumentIntelligenceService()
        logger.info(" Job Analyzer Agent listo")

    # -------------------------------------------------------------------------
    #     PDF → Texto (usando Form Recognizer V3)
    # -------------------------------------------------------------------------
    def extract_text_from_pdf(self, pdf_path: str) -> Dict:
        """Extrae texto desde PDF usando Form Recognizer clásico (prebuilt-read)"""
        logger.info(f" Extrayendo texto de PDF: {pdf_path}")

        try:
            result = self.doc_service.extract_text_from_pdf(pdf_path)

            text = result["text"]
            pages = result["pages"]

            logger.info(f" Extracción completada")
            logger.info(f"   → {len(text)} caracteres")
            logger.info(f"   → {pages} páginas")

            return {
                "text": text,
                "metadata": {
                    "pages": pages,
                    "tables_count": 0
                }
            }

        except Exception as e:
            logger.error(f" Error al extraer texto: {str(e)}")
            raise

    # -------------------------------------------------------------------------
    #     Análisis del job description con Azure OpenAI
    # -------------------------------------------------------------------------
    def analyze_job_description(self, job_text: str) -> JobAnalysis:
        """Analiza la descripción del trabajo con Azure OpenAI"""
        logger.info(" Analizando descripción del trabajo con IA...")

        try:
            user_prompt = get_job_analysis_prompt(job_text)

            response = self.openai_service.analyze_with_system_prompt(
                system_prompt=JOB_ANALYSIS_SYSTEM_PROMPT,
                user_content=user_prompt,
                temperature=None,
                json_mode=True
            )

            analysis_dict = json.loads(response)
            analysis = JobAnalysis(**analysis_dict)

            logger.info(f" Análisis completado → {analysis.title}")
            return analysis

        except json.JSONDecodeError:
            raise Exception("La respuesta del modelo NO contiene JSON válido")
        except Exception as e:
            logger.error(f" Error procesando análisis de IA: {str(e)}")
            raise

    # -------------------------------------------------------------------------
    #     Resumen ejecutivo del job
    # -------------------------------------------------------------------------
    def generate_executive_summary(self, analysis: JobAnalysis) -> str:
        logger.info(" Generando resumen ejecutivo...")

        try:
            data = analysis.model_dump()
            user_prompt = get_summary_prompt(data)

            summary = self.openai_service.analyze_with_system_prompt(
                system_prompt=JOB_SUMMARY_SYSTEM_PROMPT,
                user_content=user_prompt,
                json_mode=False
            )

            return summary.strip()

        except Exception as e:
            logger.error(f" Error generando resumen: {str(e)}")
            raise

    # -------------------------------------------------------------------------
    #     Procesar job desde PDF
    # -------------------------------------------------------------------------
    def process_job_from_pdf(self, pdf_path: str, generate_summary: bool = True) -> Job:
        logger.info("\n" + "=" * 70)
        logger.info(" PROCESANDO TRABAJO DESDE PDF")
        logger.info("=" * 70)

        start = datetime.now()

        try:
            extraction = self.extract_text_from_pdf(pdf_path)
            analysis = self.analyze_job_description(extraction["text"])

            job = Job(
                original_text=extraction["text"],
                document_metadata=extraction["metadata"],
                analysis=analysis,
                status="analyzed"
            )

            if generate_summary:
                summary = self.generate_executive_summary(analysis)
                job.document_metadata["executive_summary"] = summary

            duration = (datetime.now() - start).total_seconds()
            logger.info(f" COMPLETADO en {duration:.2f} segundos\n")

            return job

        except Exception as e:
            logger.error(f" ERROR procesando PDF: {str(e)}")
            raise

    # -------------------------------------------------------------------------
    #     Procesar job desde texto
    # -------------------------------------------------------------------------
    def process_job_from_text(self, job_text: str, generate_summary: bool = True) -> Job:
        logger.info("\n" + "=" * 70)
        logger.info(" PROCESANDO TRABAJO DESDE TEXTO")
        logger.info("=" * 70)

        start = datetime.now()

        try:
            analysis = self.analyze_job_description(job_text)

            job = Job(
                original_text=job_text,
                document_metadata={"source": "text_input"},
                analysis=analysis,
                status="analyzed"
            )

            if generate_summary:
                job.document_metadata["executive_summary"] = self.generate_executive_summary(analysis)

            logger.info(f" COMPLETADO en {(datetime.now() - start).total_seconds():.2f}s\n")
            return job

        except Exception as e:
            logger.error(f" ERROR procesando texto: {str(e)}")
            raise

    # -------------------------------------------------------------------------
    #     Guardado en JSON
    # -------------------------------------------------------------------------
    def save_analysis(self, job: Job, output_path: str = "job_analysis.json"):
        try:
            def default_converter(o):
                if isinstance(o, datetime):
                    return o.isoformat()
                return str(o)
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    job.model_dump(),
                    f,
                    indent=2,
                    ensure_ascii=False,
                    default=default_converter
                    )
            logger.info(f" Guardado en: {output_path}")
        except Exception as e:
            logger.error(f" Error guardando JSON: {str(e)}")
            raise


    # -------------------------------------------------------------------------
    #     Print en consola
    # -------------------------------------------------------------------------
    def print_analysis_summary(self, job: Job):
        analysis = job.analysis

        print("\n" + "=" * 70)
        print(" RESUMEN DEL ANÁLISIS")
        print("=" * 70)

        print(f"\n Título: {analysis.title}")
        if analysis.company:
            print(f" Empresa: {analysis.company}")
        if analysis.seniority_level:
            print(f" Seniority: {analysis.seniority_level}")
        if analysis.location:
            print(f" Ubicación: {analysis.location}")

        print(f"\n Responsabilidades ({len(analysis.responsibilities)}):")
        for r in analysis.responsibilities[:5]:
            print(f"  - {r}")

        print(f"\n Requisitos Técnicos ({len(analysis.technical_requirements)}):")
        print(", ".join(analysis.technical_requirements[:10]))

        if analysis.soft_skills:
            print("\n Soft Skills:")
            print(", ".join(analysis.soft_skills))

        if "executive_summary" in job.document_metadata:
            print("\n" + "-" * 70)
            print(" RESUMEN EJECUTIVO")
            print("-" * 70)
            print(job.document_metadata["executive_summary"])

        print("\n" + "=" * 70 + "\n")
