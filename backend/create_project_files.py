# create_project_files.py
"""
Script para crear todos los archivos necesarios del proyecto Job Analyzer
Ejecutar desde: C:\Proyecto IAAI\cv-analyzer\backend
"""
import os

def create_file(path, content):
    """Crea un archivo con el contenido especificado"""
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f" Creado: {path}")

# ============================================================================
# SERVICES
# ============================================================================

# services/__init__.py
services_init = '''"""Services package"""
from .azure_openai_service import AzureOpenAIService
from .document_intelligence_service import DocumentIntelligenceService

__all__ = ['AzureOpenAIService', 'DocumentIntelligenceService']
'''

# services/azure_openai_service.py
azure_openai_service = '''"""
Servicio para interactuar con Azure OpenAI
"""
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

class AzureOpenAIService:
    """Servicio para interactuar con Azure OpenAI"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    
    def chat_completion(self, messages, temperature=0.3, response_format=None):
        """
        Realiza una llamada al modelo de chat
        
        Args:
            messages: Lista de mensajes en formato OpenAI
            temperature: Control de creatividad (0-1)
            response_format: Formato de respuesta (None o {"type": "json_object"})
        
        Returns:
            str: Respuesta del modelo
        """
        try:
            params = {
                "model": self.deployment_name,
                "messages": messages,
                "temperature": temperature,
            }
            
            if response_format:
                params["response_format"] = response_format
            
            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"Error en Azure OpenAI: {str(e)}")
    
    def analyze_with_system_prompt(self, system_prompt, user_content, temperature=0.3, json_mode=False):
        """
        Método simplificado para análisis con system prompt
        
        Args:
            system_prompt: Instrucciones del sistema
            user_content: Contenido a analizar
            temperature: Control de creatividad
            json_mode: Si debe devolver JSON
        
        Returns:
            str: Respuesta del modelo
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        response_format = {"type": "json_object"} if json_mode else None
        
        return self.chat_completion(messages, temperature, response_format)
'''

# services/document_intelligence_service.py
document_intelligence_service = '''"""
Servicio para extraer texto de documentos con Azure Document Intelligence
"""
import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

class DocumentIntelligenceService:
    """Servicio para extraer texto de documentos con Azure Document Intelligence"""
    
    def __init__(self):
        endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        
        self.client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extrae texto de un archivo PDF
        
        Args:
            pdf_path: Ruta al archivo PDF
        
        Returns:
            dict: {
                "text": str,
                "pages": int,
                "tables": list,
                "key_value_pairs": dict
            }
        """
        try:
            with open(pdf_path, "rb") as f:
                poller = self.client.begin_analyze_document(
                    "prebuilt-layout", 
                    analyze_request=f,
                    content_type="application/pdf"
                )
            
            result = poller.result()
            
            # Extraer texto completo
            full_text = result.content if hasattr(result, 'content') else ""
            
            # Información de páginas
            pages_count = len(result.pages) if hasattr(result, 'pages') else 0
            
            # Extraer tablas si existen
            tables = []
            if hasattr(result, 'tables') and result.tables:
                for table in result.tables:
                    table_data = {
                        "row_count": table.row_count,
                        "column_count": table.column_count,
                        "cells": []
                    }
                    for cell in table.cells:
                        table_data["cells"].append({
                            "row_index": cell.row_index,
                            "column_index": cell.column_index,
                            "content": cell.content
                        })
                    tables.append(table_data)
            
            # Extraer pares clave-valor si existen
            key_value_pairs = {}
            if hasattr(result, 'key_value_pairs') and result.key_value_pairs:
                for kv_pair in result.key_value_pairs:
                    if kv_pair.key and kv_pair.value:
                        key = kv_pair.key.content
                        value = kv_pair.value.content
                        key_value_pairs[key] = value
            
            return {
                "text": full_text,
                "pages": pages_count,
                "tables": tables,
                "key_value_pairs": key_value_pairs
            }
        
        except Exception as e:
            raise Exception(f"Error al extraer texto del PDF: {str(e)}")
    
    def extract_text_from_bytes(self, file_bytes):
        """
        Extrae texto de bytes de un archivo
        
        Args:
            file_bytes: Bytes del archivo
        
        Returns:
            dict: Mismo formato que extract_text_from_pdf
        """
        try:
            poller = self.client.begin_analyze_document(
                "prebuilt-layout",
                analyze_request=file_bytes,
                content_type="application/pdf"
            )
            
            result = poller.result()
            
            full_text = result.content if hasattr(result, 'content') else ""
            pages_count = len(result.pages) if hasattr(result, 'pages') else 0
            
            return {
                "text": full_text,
                "pages": pages_count,
                "tables": [],
                "key_value_pairs": {}
            }
        
        except Exception as e:
            raise Exception(f"Error al extraer texto: {str(e)}")
'''

# ============================================================================
# MODELS
# ============================================================================

# models/__init__.py
models_init = '''"""Models package"""
from .job import Job, JobAnalysis

__all__ = ['Job', 'JobAnalysis']
'''

# models/job.py
job_model = '''"""
Modelos de datos para trabajos
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class JobAnalysis(BaseModel):
    """Modelo para el análisis estructurado de una oferta de trabajo"""
    
    job_id: Optional[str] = None
    title: str = Field(..., description="Título del puesto")
    company: Optional[str] = Field(None, description="Nombre de la empresa")
    seniority_level: Optional[str] = Field(None, description="Nivel de seniority")
    
    responsibilities: List[str] = Field(default_factory=list, description="Responsabilidades")
    technical_requirements: List[str] = Field(default_factory=list, description="Requisitos técnicos")
    
    experience_required: Optional[str] = Field(None, description="Experiencia requerida")
    education: Optional[str] = Field(None, description="Educación requerida")
    
    soft_skills: List[str] = Field(default_factory=list, description="Habilidades blandas")
    ats_keywords: List[str] = Field(default_factory=list, description="Keywords ATS")
    
    location: Optional[str] = Field(None, description="Ubicación")
    work_mode: Optional[str] = Field(None, description="Remote/Hybrid/On-site")
    salary_range: Optional[str] = Field(None, description="Rango salarial")
    
    benefits: List[str] = Field(default_factory=list, description="Beneficios")
    required_languages: List[str] = Field(default_factory=list, description="Idiomas")
    nice_to_have: List[str] = Field(default_factory=list, description="Requisitos deseables")
    
    analyzed_at: Optional[datetime] = Field(default_factory=datetime.now)


class Job(BaseModel):
    """Modelo completo de un trabajo"""
    
    id: Optional[str] = None
    user_id: Optional[str] = None
    
    original_text: str = Field(..., description="Texto del documento original")
    document_metadata: dict = Field(default_factory=dict, description="Metadatos")
    
    analysis: JobAnalysis = Field(..., description="Análisis estructurado")
    
    status: str = Field(default="analyzed", description="Estado")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
'''

# ============================================================================
# UTILS
# ============================================================================

# utils/__init__.py
utils_init = '''"""Utils package"""
'''

# utils/prompts.py
prompts = '''"""
Prompts templates para Azure OpenAI
"""

JOB_ANALYSIS_SYSTEM_PROMPT = """Eres un experto analizador de ofertas de trabajo con 15+ años de experiencia.

Analiza descripciones de trabajo y extrae información estructurada de manera precisa.

INSTRUCCIONES:
1. Lee toda la descripción cuidadosamente
2. Extrae cada elemento solicitado
3. Sé específico y preciso
4. Si no hay información, usa null o []
5. Identifica ATS keywords (términos técnicos, herramientas, habilidades)
6. Distingue requisitos obligatorios vs deseables

FORMATO JSON EXACTO:
{
  "title": "Título del puesto",
  "company": "Nombre de la empresa o null",
  "seniority_level": "Junior/Mid/Senior/Lead o null",
  "responsibilities": ["Resp 1", "Resp 2"],
  "technical_requirements": ["Tech 1", "Tech 2"],
  "experience_required": "X años",
  "education": "Nivel educativo",
  "soft_skills": ["Skill 1", "Skill 2"],
  "ats_keywords": ["keyword1", "keyword2"],
  "location": "Ciudad, País",
  "work_mode": "Remote/Hybrid/On-site",
  "salary_range": "Rango o null",
  "benefits": ["Beneficio 1"],
  "required_languages": ["Idioma 1"],
  "nice_to_have": ["Requisito deseable 1"]
}

IMPORTANTE:
- No inventes información
- Mantén términos técnicos exactos
- Incluye variaciones de keywords (ej: JS y JavaScript)
"""

JOB_SUMMARY_SYSTEM_PROMPT = """Eres un consultor de carrera experto.

Crea resúmenes ejecutivos de ofertas laborales (150-200 palabras, 3-4 párrafos):

Párrafo 1: Resumen general del rol y empresa
Párrafo 2: Responsabilidades principales
Párrafo 3: Requisitos críticos
Párrafo 4: Aspectos destacables

ESTILO:
- Claro y directo
- Profesional pero accesible
- Objetivo (no vendas ni desanimes)
- Sin bullet points, usa prosa

El candidato debe poder responder:
- ¿Cumplo los requisitos?
- ¿Me interesa?
- ¿Vale la pena aplicar?
"""

def get_job_analysis_prompt(job_text: str) -> str:
    """Genera prompt para analizar trabajo"""
    return f"""Analiza esta descripción de trabajo:

{job_text}

Devuelve SOLO el JSON estructurado."""

def get_summary_prompt(analysis_dict: dict) -> str:
    """Genera prompt para resumen ejecutivo"""
    import json
    analysis_json = json.dumps(analysis_dict, indent=2, ensure_ascii=False)
    
    return f"""Crea un resumen ejecutivo de esta oferta:

{analysis_json}

Escribe en prosa natural, sin bullet points."""
'''

# ============================================================================
# AGENTS
# ============================================================================

# agents/__init__.py
agents_init = '''"""Agents package"""
from .job_analyzer import JobAnalyzerAgent

__all__ = ['JobAnalyzerAgent']
'''

# agents/job_analyzer.py - PARTE 1
job_analyzer_part1 = '''"""
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
                temperature=0.2,
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
                temperature=0.5,
                json_mode=False
            )
            
            logger.info(" Resumen generado")
            return summary.strip()
        
        except Exception as e:
            logger.error(f" Error: {str(e)}")
            raise
'''

# agents/job_analyzer.py - PARTE 2
job_analyzer_part2 = '''    
    def process_job_from_pdf(self, pdf_path: str, generate_summary: bool = True) -> Job:
        """Procesa trabajo desde PDF"""
        logger.info("\\n" + "="*70)
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
            logger.info(f"\\n COMPLETADO en {duration:.2f}s\\n")
            
            return job
        
        except Exception as e:
            logger.error(f"\\n ERROR: {str(e)}\\n")
            raise
    
    def process_job_from_text(self, job_text: str, generate_summary: bool = True) -> Job:
        """Procesa trabajo desde texto"""
        logger.info("\\n" + "="*70)
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
            logger.info(f"\\n COMPLETADO en {duration:.2f}s\\n")
            
            return job
        
        except Exception as e:
            logger.error(f"\\n ERROR: {str(e)}\\n")
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
        
        print("\\n" + "="*70)
        print(" RESUMEN DEL ANÁLISIS")
        print("="*70)
        
        print(f"\\n Título: {analysis.title}")
        if analysis.company:
            print(f" Empresa: {analysis.company}")
        if analysis.seniority_level:
            print(f" Nivel: {analysis.seniority_level}")
        if analysis.location:
            print(f" Ubicación: {analysis.location}")
        
        print(f"\\n Responsabilidades ({len(analysis.responsibilities)}):")
        for i, resp in enumerate(analysis.responsibilities[:5], 1):
            print(f"   {i}. {resp}")
        
        print(f"\\n Requisitos Técnicos ({len(analysis.technical_requirements)}):")
        print(f"   {', '.join(analysis.technical_requirements[:10])}")
        
        print(f"\\n ATS Keywords ({len(analysis.ats_keywords)}):")
        print(f"   {', '.join(analysis.ats_keywords[:15])}")
        
        if "executive_summary" in job.document_metadata:
            print(f"\\n RESUMEN EJECUTIVO:")
            print("-" * 70)
            print(job.document_metadata["executive_summary"])
        
        print("\\n" + "="*70 + "\\n")
'''

# ============================================================================
# TEST SCRIPT
# ============================================================================

test_script = '''"""
Script de prueba para Job Analyzer Agent
"""
from agents.job_analyzer import JobAnalyzerAgent

def test_job_analyzer():
    """Prueba el Job Analyzer con un ejemplo"""
    
    sample_job = """
    Senior Full-Stack Developer
    TechCorp Inc. - Remote
    
    We are seeking an experienced Senior Full-Stack Developer.
    
    Responsibilities:
    - Design and develop web applications using React and Node.js
    - Lead technical discussions and code reviews
    - Mentor junior developers
    - Optimize performance and scalability
    
    Requirements:
    - 5+ years of full-stack development experience
    - Strong proficiency in JavaScript, React, Node.js, TypeScript
    - Experience with AWS or Azure
    - Knowledge of Docker and Kubernetes
    - Bachelor's degree in Computer Science
    
    Nice to Have:
    - Experience with microservices
    - Knowledge of Python or Go
    - AWS certifications
    
    Benefits:
    - Salary: $140k - $180k
    - Full remote work
    - Health insurance
    - Professional development budget
    """
    
    print(" INICIANDO TEST DEL JOB ANALYZER AGENT")
    print("="*70 + "\\n")
    
    try:
        # Crear agente
        agent = JobAnalyzerAgent()
        
        # Procesar trabajo
        job = agent.process_job_from_text(sample_job, generate_summary=True)
        
        # Mostrar resultados
        agent.print_analysis_summary(job)
        
        # Guardar
        agent.save_analysis(job, "test_job_analysis.json")
        
        print(" TEST COMPLETADO EXITOSAMENTE")
        print(" Revisa 'test_job_analysis.json' para ver el resultado\\n")
        
    except Exception as e:
        print(f"❌ TEST FALLÓ: {str(e)}\\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_job_analyzer()
'''

# ============================================================================
# MAIN - CREAR TODOS LOS ARCHIVOS
# ============================================================================

def create_all_files():
    """Crea todos los archivos del proyecto"""
    print("\\n" + "="*70)
    print(" CREANDO ARCHIVOS DEL PROYECTO")
    print("="*70 + "\\n")
    
    files = [
        # Services
        ("services/__init__.py", services_init),
        ("services/azure_openai_service.py", azure_openai_service),
        ("services/document_intelligence_service.py", document_intelligence_service),
        
        # Models
        ("models/__init__.py", models_init),
        ("models/job.py", job_model),
        
        # Utils
        ("utils/__init__.py", utils_init),
        ("utils/prompts.py", prompts),
        
        # Agents
        ("agents/__init__.py", agents_init),
        ("agents/job_analyzer.py", job_analyzer_part1 + job_analyzer_part2),
        
        # Test
        ("test_job_analyzer.py", test_script),
    ]
    
    for filepath, content in files:
        try:
            create_file(filepath, content)
        except Exception as e:
            print(f" Error creando {filepath}: {str(e)}")
    
    print("\\n" + "="*70)
    print(" TODOS LOS ARCHIVOS CREADOS")
    print("="*70 + "\\n")
    
    print("PRÓXIMOS PASOS:\\n")
    print("1. Verifica que tu .env tenga las credenciales correctas")
    print("2. Ejecuta: python test_job_analyzer.py")
    print("3. Revisa el archivo test_job_analysis.json generado")
    print()

if __name__ == "__main__":
    create_all_files()