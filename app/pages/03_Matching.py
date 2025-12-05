import sys
import os

from backend.agents.cv_matcher import CVMatcherAgent

import json
import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# Importar backend
# ------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

sys.path.append(PROJECT_ROOT)
sys.path.append(BACKEND_DIR)

from backend.agents.cv_matcher import CVMatcherAgent

# ------------------------------------------------------------
# Configuración Streamlit
# ------------------------------------------------------------
st.set_page_config(page_title="Match Vacante ↔ CVs", layout="wide")
st.title(" Matcher de Vacantes y Candidatos")
st.write("Compara la oferta laboral con los CVs procesados y genera un ranking inteligente.")
st.markdown("---")

# ------------------------------------------------------------
# Validar que existan datos procesados
# ------------------------------------------------------------
if "processed_jobs" not in st.session_state or len(st.session_state.processed_jobs) == 0:
    st.warning(" Primero sube y procesa una oferta en **'Upload Job Description'**.")
    st.stop()

if "processed_cvs" not in st.session_state or len(st.session_state.processed_cvs) == 0:
    st.warning(" Primero sube y procesa CVs en **'Upload CVs'**.")
    st.stop()

# ------------------------------------------------------------
# Selección de la vacante a utilizar
# ------------------------------------------------------------
st.subheader("Selecciona la Oferta Laboral")

job_options = [
    f"{idx+1}. {job.analysis.title or 'Sin título'} — {job.analysis.company or 'Empresa desconocida'}"
    for idx, job in enumerate(st.session_state.processed_jobs)
]

selected_index = st.selectbox("Oferta:", options=list(range(len(job_options))), 
                              format_func=lambda i: job_options[i])

selected_job = st.session_state.processed_jobs[selected_index].analysis

st.success(f"Oferta seleccionada: **{selected_job.title}** — {selected_job.company}")
st.markdown("---")

# ------------------------------------------------------------
# Ejecutar el matching
# ------------------------------------------------------------
st.subheader(" Ejecutar Matching")

use_openai = st.checkbox("Usar OpenAI para refinamiento avanzado", value=True)

if st.button(" Generar Ranking de Candidatos"):
    
    matcher = CVMatcherAgent(use_openai=use_openai)

    candidates = st.session_state.processed_cvs
    
    with st.spinner("Analizando candidatos…"):
        ranking = matcher.match_batch(job=selected_job, candidates=candidates)

    st.session_state["match_results"] = ranking
    st.success(" Matching completado")

# ------------------------------------------------------------
# Mostrar resultados
# ------------------------------------------------------------
if "match_results" in st.session_state:

    results = st.session_state["match_results"]

    st.header("Ranking Final")
    st.markdown("---")

    for item in results:
        score = item["match_score"]
        cand = item["candidate"]
        rank = item["rank"]

        st.markdown(f"Candidato {rank} — Score: **{score}/100**")
        
        st.progress(score / 100)

        cols = st.columns(3)

        with cols[0]:
            st.markdown("Fortalezas")
            if item["strengths"]:
                for s in item["strengths"]:
                    st.write(f"- {s}")
            else:
                st.write("—")

        with cols[1]:
            st.markdown("Gaps")
            if item["gaps"]:
                for g in item["gaps"]:
                    st.write(f"- {g}")
            else:
                st.write("—")

        with cols[2]:
            st.markdown("Info del Candidato")
            st.write(f"Nombre: {cand.get('nombre', 'No disponible')}")
            st.write(f"Correo: {cand.get('correo', 'No disponible')}")
            st.write(f"Teléfono: {cand.get('telefono', '--')}")
            st.write(f"LinkedIn: {cand.get('linkedin', '--')}")

        if item.get("justification"):
            st.markdown("Justificación del Modelo")
            st.info(item["justification"])

        with st.expander(" Ver JSON completo del match"):
            st.json(item)

        st.markdown("---")

    # --------------------------------------------------------
    # Exportación de resultados
    # --------------------------------------------------------
    st.subheader("Exportar resultados")

    df_export = pd.DataFrame([
        {
            "rank": r["rank"],
            "score": r["match_score"],
            "nombre": r["candidate"].get("nombre"),
            "correo": r["candidate"].get("correo"),
            "skills": ", ".join(r["candidate"].get("skills_tecnicas", [])),
            "soft_skills": ", ".join(r["candidate"].get("soft_skills", [])),
        }
        for r in results
    ])

    st.download_button(
        "Descargar CSV",
        df_export.to_csv(index=False).encode("utf-8"),
        file_name="ranking_candidatos.csv",
        mime="text/csv"
    )

