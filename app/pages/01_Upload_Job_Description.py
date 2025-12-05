import sys
import os
import tempfile
import streamlit as st

# Ruta absoluta al directorio raíz del proyecto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

sys.path.append(PROJECT_ROOT)
sys.path.append(BACKEND_DIR)

from backend.agents.job_analyzer import JobAnalyzerAgent

# ------------------------------------------------------------
# Inicialización del Session State
# ------------------------------------------------------------
if "processed_jobs" not in st.session_state:
    st.session_state.processed_jobs = []

# ------------------------------------------------------------
# Procesamiento del archivo PDF
# ------------------------------------------------------------
def process_job_file(uploaded_file):
    try:
        agent = JobAnalyzerAgent()
    except Exception as e:
        st.error(f"⚠️ Error inicializando JobAnalyzerAgent: {e}")
        return

    # Guardar PDF temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    try:
        job_obj = agent.process_job_from_pdf(temp_path, generate_summary=True)
        st.session_state.processed_jobs.append(job_obj)
        st.success(f"✔️ Procesado correctamente: {uploaded_file.name}")

    except Exception as e:
        st.error(f"❌ Error procesando {uploaded_file.name}: {e}")

    finally:
        os.unlink(temp_path)

# ------------------------------------------------------------
# Interfaz Streamlit
# ------------------------------------------------------------
st.set_page_config(
    page_title="Job Analyzer",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Analizador de Ofertas Laborales")
st.write("Sube un archivo PDF con la oferta laboral y obtén un análisis completo en texto.")
st.markdown("---")

# ------------------------------------------------------------
# Upload PDF
# ------------------------------------------------------------
uploaded_pdf = st.file_uploader("Sube el PDF de la oferta laboral", type=["pdf"])

if uploaded_pdf:
    st.info(f"Archivo listo: **{uploaded_pdf.name}**")
    if st.button("🚀 Procesar Oferta Laboral"):
        process_job_file(uploaded_pdf)

st.markdown("---")

# ------------------------------------------------------------
# Mostrar Resultados
# ------------------------------------------------------------
st.header("📄 Análisis de Ofertas")

if st.session_state.processed_jobs:
    for idx, job in enumerate(st.session_state.processed_jobs, 1):
        analysis = job.analysis

        st.markdown(f"## 📝 Oferta {idx}: {analysis.title or 'Sin título'}")

                # Datos clave al inicio
        cols = st.columns([3, 1, 1])  # columna más grande para la empresa
        with cols[0]:
            if analysis.company:
                st.markdown(f"**🏢 Empresa:** {analysis.company}")

        with cols[1]:
            if analysis.seniority_level:
                st.markdown(f"**💼 Seniority:** {analysis.seniority_level}")

        with cols[2]:
            if analysis.location:
                st.markdown(f"**📍 Ubicación:** {analysis.location}")

        st.markdown("---")

        # Responsabilidades y requisitos
        left_col, right_col = st.columns(2)

        if analysis.responsibilities:
            with left_col:
                st.subheader("⚡ Responsabilidades")
                for r in analysis.responsibilities:
                    st.write(f"- {r}")

        if analysis.technical_requirements or analysis.soft_skills:
            with right_col:
                if analysis.technical_requirements:
                    st.subheader("🛠 Requisitos Técnicos")
                    st.write(", ".join(analysis.technical_requirements))
                if analysis.soft_skills:
                    st.subheader("💡 Soft Skills")
                    st.write(", ".join(analysis.soft_skills))

        # Resumen ejecutivo destacado
        if "executive_summary" in job.document_metadata:
            st.markdown("### 📌 Resumen Ejecutivo")
            st.info(job.document_metadata["executive_summary"])

        st.markdown("─" * 80)


else:
    st.info("No hay ofertas procesadas todavía. Sube un archivo para comenzar.")
