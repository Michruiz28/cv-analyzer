"""
Job Analyzer Agent - Agente especializado en analizar ofertas de trabajo
"""
import json
import logging
from typing import Dict
from datetime import datetime

from services.azure_openai_service import AzureOpenAIService
from services.document_intelligence_service import DocumentIntelligenceService
from models.job import Job, JobAnalysis
from utils.prompts import (
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
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict:
        """Extrae texto de un PDF"""
        logger.info(f" Extrayendo texto de: {pdf_path}")
        
        try:
            result = self.doc_service.extract_text_from_pdf(pdf_path)
            logger.info(f" Extraído: {len(result['text'])} chars, {result['pages']} páginas")
            
            return {
                "text": result["text"],
                "metadata": {
                    "pages": result["pages"],
                    "tables_count": len(result.get("tables", [])),
                }
            }
        except Exception as e:
            logger.error(f" Error: {str(e)}")
            raise
    
    def analyze_job_description(self, job_text: str) -> JobAnalysis:
        """Analiza descripción de trabajo con IA"""
        logger.info(" Analizando con IA...")
        
        try:
            user_prompt = get_job_analysis_prompt(job_text)
            
            response = self.openai_service.analyze_with_system_prompt(
                system_prompt=JOB_ANALYSIS_SYSTEM_PROMPT,
                user_content=user_prompt,
                temperature=None,  # Usar temperatura por defecto del modelo
                json_mode=True
            )
            
            analysis_dict = json.loads(response)
            job_analysis = JobAnalysis(**analysis_dict)
            
            logger.info(f" Análisis: {job_analysis.title}")
            logger.info(f"   - {len(job_analysis.responsibilities)} responsabilidades")
            logger.info(f"   - {len(job_analysis.technical_requirements)} requisitos")
            logger.info(f"   - {len(job_analysis.ats_keywords)} keywords")
            
            return job_analysis
        
        except json.JSONDecodeError as e:
            logger.error(f" Error JSON: {str(e)}")
            raise Exception("Respuesta no es JSON válido")
        except Exception as e:
            logger.error(f" Error: {str(e)}")
            raise
    
    def generate_executive_summary(self, analysis: JobAnalysis) -> str:
        """Genera resumen ejecutivo"""
        logger.info(" Generando resumen...")
        
        try:
            analysis_dict = analysis.model_dump()
            user_prompt = get_summary_prompt(analysis_dict)
            
            summary = self.openai_service.analyze_with_system_prompt(
                system_prompt=JOB_SUMMARY_SYSTEM_PROMPT,
                user_content=user_prompt,
                temperature=None,  # Usar temperatura por defecto del modelo
                json_mode=False
            )
            
            logger.info(" Resumen generado")
            return summary.strip()
        
        except Exception as e:
            logger.error(f" Error: {str(e)}")
            raise
    
    def process_job_from_pdf(self, pdf_path: str, generate_summary: bool = True) -> Job:
        """Procesa trabajo desde PDF"""
        logger.info("\n" + "="*70)
        logger.info(" PROCESANDO TRABAJO DESDE PDF")
        logger.info("="*70)
        
        start_time = datetime.now()
        
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
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"\n COMPLETADO en {duration:.2f}s\n")
            
            return job
        
        except Exception as e:
            logger.error(f"\n ERROR: {str(e)}\n")
            raise
    
    def process_job_from_text(self, job_text: str, generate_summary: bool = True) -> Job:
        """Procesa trabajo desde texto"""
        logger.info("\n" + "="*70)
        logger.info(" PROCESANDO TRABAJO DESDE TEXTO")
        logger.info("="*70)
        
        start_time = datetime.now()
        
        try:
            analysis = self.analyze_job_description(job_text)
            
            job = Job(
                original_text=job_text,
                document_metadata={"source": "text_input"},
                analysis=analysis,
                status="analyzed"
            )
            
            if generate_summary:
                summary = self.generate_executive_summary(analysis)
                job.document_metadata["executive_summary"] = summary
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"\n COMPLETADO en {duration:.2f}s\n")
            
            return job
        
        except Exception as e:
            logger.error(f"\n ERROR: {str(e)}\n")
            raise
    
    def save_analysis(self, job: Job, output_path: str = "job_analysis.json"):
        """Guarda análisis en JSON"""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(job.model_dump(), f, indent=2, ensure_ascii=False, default=str)
            logger.info(f" Guardado en: {output_path}")
        except Exception as e:
            logger.error(f" Error guardando: {str(e)}")
            raise
    
    def print_analysis_summary(self, job: Job):
        """Imprime resumen en consola"""
        analysis = job.analysis
        
        print("\n" + "="*70)
        print(" RESUMEN DEL ANÁLISIS")
        print("="*70)
        
        print(f"\n Título: {analysis.title}")
        if analysis.company:
            print(f" Empresa: {analysis.company}")
        if analysis.seniority_level:
            print(f" Nivel: {analysis.seniority_level}")
        if analysis.location:
            print(f" Ubicación: {analysis.location}")
        if analysis.work_mode:
            print(f" Modalidad: {analysis.work_mode}")
        if analysis.salary_range:
            print(f" Salario: {analysis.salary_range}")
        
        print(f"\n Responsabilidades ({len(analysis.responsibilities)}):")
        for i, resp in enumerate(analysis.responsibilities[:5], 1):
            print(f"   {i}. {resp}")
        if len(analysis.responsibilities) > 5:
            print(f"   ... y {len(analysis.responsibilities) - 5} más")
        
        print(f"\n Requisitos Técnicos ({len(analysis.technical_requirements)}):")
        if analysis.technical_requirements:
            print(f"   {', '.join(analysis.technical_requirements[:10])}")
            if len(analysis.technical_requirements) > 10:
                print(f"   ... y {len(analysis.technical_requirements) - 10} más")
        
        if analysis.soft_skills:
            print(f"\n Habilidades Blandas:")
            print(f"   {', '.join(analysis.soft_skills)}")
        
        print(f"\n ATS Keywords ({len(analysis.ats_keywords)}):")
        if analysis.ats_keywords:
            print(f"   {', '.join(analysis.ats_keywords[:15])}")
            if len(analysis.ats_keywords) > 15:
                print(f"   ... y {len(analysis.ats_keywords) - 15} más")
        
        if "executive_summary" in job.document_metadata:
            print(f"\n RESUMEN EJECUTIVO:")
            print("-" * 70)
            print(job.document_metadata["executive_summary"])
        
        print("\n" + "="*70 + "\n")