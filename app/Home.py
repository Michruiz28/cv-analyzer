import streamlit as st

st.set_page_config(page_title="Inicio - CV Analyzer", page_icon="👋", layout="centered")

st.title("Sistema de Análisis de CVs 🧠")
st.write("Bienvenido al sistema de procesamiento de currículums vitae. Utiliza la barra lateral para navegar o el enlace de abajo.")

st.markdown("""
---
### 🚀 Funcionalidades Principales

* **Procesamiento por Lotes:** Sube múltiples archivos PDF.
* **Extracción con IA:** Un agente avanzado extrae información estructurada (skills, experiencia, contacto).
* **Visualización de Datos:** Genera gráficos de Nube de Palabras para identificar tendencias en el mercado.

---
""")

# Opción 1: Usar un enlace de Markdown
# Streamlit usa la estructura de archivos de la carpeta 'pages' para crear los enlaces de la barra lateral.
# Solo necesitas decirle al usuario que vaya a la barra lateral o hacer el enlace explícito.

# NOTA: Si Streamlit está configurado con páginas, el enlace aparecerá automáticamente
# en la barra lateral izquierda bajo el nombre del archivo (ej. 'Analisis Cv').

# Opción 2: Botón (Si no quieres usar la barra lateral)
# Streamlit no soporta enlaces de botones directos a páginas internas, pero puedes guiar al usuario.

if st.button("Ir al Módulo de Análisis de CVs"):
    # Streamlit maneja la navegación de páginas automáticamente si están en la carpeta 'pages/'.
    # Si quieres una navegación más explícita o si el usuario no ve la barra lateral:
    st.info("Utiliza el **menú de la barra lateral** (👈) o la flecha de página para navegar a **'Análisis de CVs'**.")

# Para una navegación más limpia, basta con un texto simple:
st.markdown("### 👉 **[Navega al Módulo de Análisis de Lote en la barra lateral izquierda.](%s)" % (st.get_option("server.baseUrlPath") + "/analisis_cv"))