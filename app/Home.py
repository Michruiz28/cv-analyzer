import sys
import os

# Agregar la raíz del proyecto al sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

import streamlit as st
from agents.extractor_agent import ExtractorAgent
import tempfile

st.set_page_config(page_title="CV Analyzer", page_icon="🧠", layout="centered")

st.title("📄 CV Analyzer")
st.write("Sube un archivo PDF y el agente extraerá la información clave.")

uploaded_file = st.file_uploader("Sube tu CV (PDF)", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Procesando el archivo... ⏳"):
        # Guardar PDF temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name

        # Ejecutar agente
        agent = ExtractorAgent()
        resultado = agent.process_cv(temp_path)

    st.success("¡Procesado exitosamente!")

    # Mostrar resultado como JSON bonito
    st.subheader("Resultado del análisis:")
    st.json(resultado)

    # Opcional: Mostrar secciones más bonitas
    if "nombre" in resultado:
        st.write(f"### 👤 {resultado['nombre']}")

    if "skills_tecnicas" in resultado:
        st.write("### 🛠️ Skills Técnicas")
        st.write(", ".join(resultado["skills_tecnicas"]))

    if "soft_skills" in resultado:
        st.write("### 🤝 Soft Skills")
        st.write(", ".join(resultado["soft_skills"]))

    if "experiencia_laboral" in resultado:
        st.write("### 💼 Experiencia Laboral")
        for job in resultado["experiencia_laboral"]:
            st.write(f"**{job['cargo']} — {job['empresa']}**")
            st.write(f"{job['periodo']}")
            st.write(job["descripcion"])
            st.write("---")
