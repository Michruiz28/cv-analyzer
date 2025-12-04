"""
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
