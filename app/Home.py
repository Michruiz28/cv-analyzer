import streamlit as st
from PIL import Image

st.set_page_config(page_title="Inicio - CV Analyzer", layout="centered")

st.title("Sistema Inteligente de Análisis y Matching de CVs")

st.markdown("""
Bienvenido al sistema de análisis de currículums vitae mediante agentes inteligentes.
Este proyecto integra tecnologías de IA para optimizar el proceso de reclutamiento,
automatizando tareas que son repetitivas, lentas y propensas a errores humanos.
""")

st.markdown("---")

# ============================================================
# INTRODUCCIÓN, JUSTIFICACIÓN Y MISIÓN
# ============================================================

st.header("Justificación del Servicio")
st.markdown("""
Los procesos de selección tradicionales requieren revisar manualmente decenas o cientos de hojas de vida,
analizar requisitos de vacantes y comparar perfiles sin una estructura clara. Esto genera demoras,
decisiones poco consistentes y una alta carga operativa.

Nuestro sistema surge para resolver esa problemática mediante la automatización del análisis
tanto de ofertas laborales como de currículums, permitiendo evaluaciones más rápidas, objetivas
t y basadas en información estructurada.
""")

# Mostrar imagen Misión
image = Image.open("app/assets/mision.jpg")
st.image(image, use_column_width=True)

st.header("Misión del Sistema")
st.markdown("""
Proveer una plataforma confiable que transforme texto desestructurado en conocimiento accionable,
facilitando a los equipos de selección identificar a los mejores candidatos mediante análisis
inteligente, transparente y reproducible.
""")

st.header("¿En qué consiste nuestro servicio?")

# Mostrar imagen del flujo general
image = Image.open("app/assets/electiva.jpg")
st.image(image, use_column_width=True)

st.markdown("""
El sistema utiliza agentes especializados que trabajan de forma coordinada:

1. **Análisis de Vacantes (Job Analyzer Agent):**  
   Procesa la descripción de un puesto y extrae información esencial como habilidades técnicas,
   responsabilidades, experiencia requerida, educación y palabras clave ATS.  
   El resultado es un perfil estructurado del cargo en formato JSON.

2. **Extracción de Información de CVs (Extractor Agent):**  
   Recibe CVs en PDF y utiliza tecnologías de extracción documental y modelos de lenguaje
   para obtener información limpia y organizada: skills, educación, experiencia, idiomas y datos de contacto.  
   Cada CV se convierte en un perfil estandarizado.
""")

# Mostrar imagen del agente 1
image = Image.open("app/assets/agente1.jpg")
st.image(image, use_column_width=True)

st.markdown("""
3. **Matching Inteligente (CV Matcher Agent):**  
   Compara la vacante estructurada con cada candidato, calcula un puntaje objetivo y genera
   fortalezas, brechas y una justificación detallada.  
   El resultado es un ranking final que prioriza a los candidatos según su afinidad con el cargo.

Este flujo convierte el análisis manual de horas en un proceso automatizado de minutos,
con criterios medibles y consistentes.
""")

# Mostrar imagen del agente 2
image = Image.open("app/assets/agente2.jpg")
st.image(image, use_column_width=True)

st.markdown("---")

# ============================================================
# FUNCIONALIDADES
# ============================================================

st.header("Funcionalidades Principales")

st.markdown("""
- **Procesamiento Automático de Vacantes:**  
  Análisis semántico avanzado para obtener un perfil limpio del puesto.

- **Procesamiento por Lotes de CVs:**  
  Subida múltiple de archivos PDF y análisis simultáneo mediante agentes de extracción.

- **Estandarización de Información:**  
  Conversión del contenido de los CVs y vacantes a estructuras JSON comparables.

- **Matching Inteligente y Ranking:**  
  Comparación entre candidatos y vacantes para generar un puntaje objetivo
  y recomendaciones basadas en datos.

- **Visualización y Reportes:**  
  Nubes de palabras, estadísticas agregadas y exportación de resultados.
""")

st.markdown("---")
