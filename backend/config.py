from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Configuración centralizada del proyecto.
    Soporta tanto OpenAI API como Azure OpenAI.
    """
    
    # OpenAI API (principal)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"  # Más económico para desarrollo
    
    # Azure OpenAI (alternativa - para cuando lo consigas)
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_KEY: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = "gpt-4"
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    
    # Azure Document Intelligence
    AZURE_DOC_INTELLIGENCE_ENDPOINT: Optional[str] = None
    AZURE_DOC_INTELLIGENCE_KEY: Optional[str] = None
    
    # Application Settings
    MAX_FILE_SIZE_MB: int = 10
    MAX_CVS_PER_ANALYSIS: int = 20
    LOG_LEVEL: str = "INFO"
    
    # Paths
    DATA_DIR: str = "data"
    TEMP_DIR: str = "data/temp"
    SAMPLE_CVS_DIR: str = "data/sample_cvs"
    SAMPLE_JOBS_DIR: str = "data/sample_jobs"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def is_azure_openai_configured(self) -> bool:
        """Verifica si Azure OpenAI está configurado"""
        return bool(self.AZURE_OPENAI_ENDPOINT and self.AZURE_OPENAI_KEY)
    
    def is_openai_configured(self) -> bool:
        """Verifica si OpenAI API está configurado"""
        return bool(self.OPENAI_API_KEY)
    
    def get_openai_client_type(self) -> str:
        """Retorna qué tipo de cliente usar"""
        if self.is_azure_openai_configured():
            return "azure"
        elif self.is_openai_configured():
            return "openai"
        else:
            return "none"

# Instancia global de configuración
settings = Settings()

# Crear directorios necesarios
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.SAMPLE_CVS_DIR, exist_ok=True)
os.makedirs(settings.SAMPLE_JOBS_DIR, exist_ok=True)

# Verificar configuración al importar
def verify_config():
    """Verifica y muestra el estado de la configuración"""
    client_type = settings.get_openai_client_type()
    
    if client_type == "openai":
        print("✅ OpenAI API configurada correctamente")
        print(f"   Modelo: {settings.OPENAI_MODEL}")
    elif client_type == "azure":
        print("✅ Azure OpenAI configurada correctamente")
        print(f"   Endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
    else:
        print("⚠️  No hay API de OpenAI configurada")
        print("   Por favor configura OPENAI_API_KEY en el archivo .env")
    
    if settings.AZURE_DOC_INTELLIGENCE_ENDPOINT:
        print("✅ Azure Document Intelligence configurado")
    else:
        print("⚠️  Azure Document Intelligence no configurado (opcional por ahora)")

# Ejecutar verificación
verify_config()