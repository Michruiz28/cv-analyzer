import sys
import os
import json
import tempfile
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd # Necesario para aplanamiento de listas

# Ruta absoluta al directorio raíz del proyecto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

# Agregar rutas al sys.path
sys.path.append(PROJECT_ROOT)
sys.path.append(BACKEND_DIR)

from backend.agents.extractor_agent import ExtractorAgent

# --- Inicialización de Session State ---
# Esta es la base de datos temporal de tu aplicación
if 'processed_cvs' not in st.session_state:
    st.session_state.processed_cvs = []

# --- Funciones de Utilidad ---

def create_wordcloud(data_list, title):
    """Genera y muestra un gráfico de Nube de Palabras."""
    if not data_list:
        return st.warning(f"No hay datos suficientes para {title}.")

    # 1. Aplanar lista si es necesario (e.g., [["Python", "Azure"], ["JS"]])
    flat_list = [item.lower() for sublist in data_list for item in sublist]
    text = " ".join(flat_list)

    # 2. Configuración de WordCloud
    wc = WordCloud(
        width=800, 
        height=400, 
        background_color="white", 
        collocations=False, # Evita agrupar palabras (ej: "data" y "science")
        random_state=42 # Para asegurar la forma y posición (horizontal/vertical)
    )
    
    # 3. Generar y mostrar
    wc.generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)
    plt.close()

# --- Funciones de Procesamiento ---

def process_files(uploaded_files):
    """Procesa todos los archivos subidos y actualiza Session State."""
    
    # Inicializa el agente fuera del bucle para no re-crear la conexión en cada CV
    try:
        agent = ExtractorAgent()
    except Exception as e:
        st.error(f"Error al inicializar el agente: {e}")
        return

    st.session_state.processed_cvs = []
    
    # Crea una barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, uploaded_file in enumerate(uploaded_files):
        filename = uploaded_file.name
        
        # Guardar PDF temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name

        status_text.text(f" Procesando: {filename} ({i+1}/{len(uploaded_files)})...")
        
        # Ejecutar agente
        resultado = agent.process_cv(temp_path)
        
        # Limpiar archivo temporal
        os.unlink(temp_path)

        # Si el resultado es JSON válido, almacenar
        if 'error' not in resultado:
            st.session_state.processed_cvs.append(resultado)
            status_text.text(f" Procesado y almacenado: {filename}")
        else:
            st.warning(f" Falló el procesamiento de {filename}. Error: {resultado['error']}")

        # Actualizar barra de progreso
        progress_bar.progress((i + 1) / len(uploaded_files))

    progress_bar.empty()
    status_text.success(f"Proceso completado. {len(st.session_state.processed_cvs)} CVs analizados.")

# --- Estructura de la Aplicación Streamlit ---

st.set_page_config(page_title="CV Analyzer", layout="wide")

st.title("Agente de Análisis de CVs por Lotes")
st.write("Sube múltiples archivos PDF para extraer información clave y generar estadísticas agregadas.")
st.markdown("---")

# --- Sección de Subida de Archivos ---
col1, col2 = st.columns([2, 1])

with col1:
    # 1. Subida Múltiple (clave del requerimiento)
    uploaded_files = st.file_uploader(
        "Sube tus CVs (archivos PDF)", 
        type=["pdf"], 
        accept_multiple_files=True
    )

with col2:
    st.write("") # Espaciador
    st.write("") # Espaciador
    if uploaded_files:
        st.info(f"Archivos listos para procesar: {len(uploaded_files)}")
        # Botón para iniciar el procesamiento por lotes
        if st.button(" Iniciar Análisis de Lote"):
            process_files(uploaded_files)

st.markdown("---")

# --- Sección de Resultados y Estadísticas ---

if st.session_state.processed_cvs:
    
    df_cvs = pd.DataFrame(st.session_state.processed_cvs)
    
    st.header(" Resultados Agregados y Estadísticas")
    
    # 4. Estadísticas Descriptivas (Contador)
    st.metric(
        label="CVs Procesados Correctamente", 
        value=len(st.session_state.processed_cvs)
    )

    st.markdown("---")

    # 5. Generación de Gráficos de Nube de Palabras
    st.subheader("Nube de Palabras de Skills y Habilidades")

    col_skills, col_soft, col_idiomas = st.columns(3)

    # Skills Técnicas
    with col_skills:
        st.info("Skills Técnicas más Comunes")
        tech_skills = df_cvs['skills_tecnicas'].dropna().tolist()
        create_wordcloud(tech_skills, "Skills Técnicas")

    # Soft Skills
    with col_soft:
        st.info("Soft Skills más Comunes")
        soft_skills = df_cvs['soft_skills'].dropna().tolist()
        create_wordcloud(soft_skills, "Soft Skills")

    # Idiomas
    with col_idiomas:
        st.info("Idiomas y Nivel")
        languages = df_cvs['idiomas'].dropna().tolist()
        create_wordcloud(languages, "Idiomas")

    st.markdown("---")
    
    # Opcional: Mostrar la tabla de datos raw
    with st.expander("Ver Datos JSON Crudos (Tabla)"):
        # Limpiamos columnas con estructuras complejas para una mejor visualización de tabla
        display_df = df_cvs.drop(columns=['educacion', 'experiencia_laboral'], errors='ignore')
        st.dataframe(display_df, use_container_width=True)
        
    with st.expander("Ver JSON Completo (Raw Data)"):
        st.json(st.session_state.processed_cvs)

else:
    st.info("Esperando que subas y proceses archivos para mostrar las estadísticas.")