"""
🔍 Quality Assurance
====================
Evaluación objetiva del artículo generado (juez ciego).
"""

import streamlit as st
import sys
from pathlib import Path

# Añadir el directorio padre al path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

st.set_page_config(
    page_title="QA | GHEN",
    page_icon="🔍",
    layout="wide"
)

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_secret(key: str, default: str = "") -> str:
    """Obtiene un secret de forma segura."""
    try:
        value = st.secrets.get(key, default)
        return value if value else default
    except Exception:
        return default

def get_active_api_key():
    """Obtiene la API key activa."""
    return st.session_state.get("gemini_api_key") or get_secret("GEMINI_API_KEY", "")

# ============================================================================
# VERIFICACIONES
# ============================================================================

if "generated_article" not in st.session_state:
    st.warning("⚠️ **No hay artículo generado**")
    st.markdown("Primero genera un artículo.")
    if st.button("📝 Ir a Generar"):
        st.switch_page("pages/1_📝_Generar.py")
    st.stop()

# ============================================================================
# HEADER
# ============================================================================

st.title("🔍 Quality Assurance")
st.markdown("""
**Evaluación objetiva del artículo** - El QA actúa como juez ciego:
- ✅ Evalúa SOLO el resultado final (sin acceso a fuentes)
- ✅ Mide: narrativa, fluidez, tono, repeticiones, valor, estructura
- ✅ Genera reporte objetivo con problemas específicos
""")

st.markdown("---")

# ============================================================================
# INFORMACIÓN DEL ARTÍCULO
# ============================================================================

article = st.session_state["generated_article"]
word_count = len(article.split())
char_count = len(article)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📝 Palabras", f"{word_count:,}")
with col2:
    st.metric("📊 Caracteres", f"{char_count:,}")
with col3:
    keyword = st.session_state.get("generated_keyword", "N/A")
    st.metric("🔑 Keyword", keyword[:30] + "..." if len(keyword) > 30 else keyword)

# ============================================================================
# EVALUACIÓN QA
# ============================================================================

st.markdown("---")
st.markdown("### 📊 Evaluación de Calidad")

# Inicializar estado de QA
if "qa_report" not in st.session_state:
    st.session_state.qa_report = None

col1, col2 = st.columns([2, 1])

with col2:
    st.markdown("**Criterios de evaluación:**")
    st.markdown("""
    - 📖 Narrativa y fluidez
    - 🎯 Claridad del mensaje
    - 🔄 Repeticiones innecesarias
    - 📋 Listas vs párrafos
    - 💡 Valor aportado
    - 🏗️ Estructura lógica
    - 🎨 Tono y voz
    """)
    
    if st.button("🔍 **Ejecutar Evaluación QA**", type="primary", use_container_width=True):
        with st.spinner("Analizando artículo..."):
            try:
                # Importar función QA
                from longcontent_generator.core import qa_article_coverage
                
                qa_report = qa_article_coverage(
                    article_content=article,
                    related_keywords_context=None,  # QA ciego
                    main_query=None
                )
                
                if qa_report:
                    st.session_state.qa_report = qa_report
                    st.success("✅ Evaluación completada")
                else:
                    st.error("No se pudo generar el reporte")
                    
            except Exception as e:
                st.error(f"Error: {e}")

with col1:
    if st.session_state.qa_report:
        st.markdown("#### 📋 Reporte de Calidad")
        
        # Mostrar reporte en tabs
        tab1, tab2 = st.tabs(["📄 Reporte completo", "✏️ Editar artículo"])
        
        with tab1:
            st.markdown(st.session_state.qa_report)
            
            # Descargar reporte
            st.download_button(
                "💾 Descargar reporte QA",
                st.session_state.qa_report,
                file_name="qa_report.md",
                mime="text/markdown"
            )
        
        with tab2:
            st.markdown("**Edita el artículo basándote en las observaciones del QA:**")
            
            edited = st.text_area(
                "Artículo",
                value=st.session_state["generated_article"],
                height=400,
                key="qa_editor"
            )
            
            if edited != st.session_state["generated_article"]:
                if st.button("💾 Guardar cambios", type="primary"):
                    st.session_state["generated_article"] = edited
                    st.success("✅ Artículo actualizado")
                    st.rerun()
    else:
        st.info("👆 Haz clic en 'Ejecutar Evaluación QA' para analizar el artículo")
        
        # Preview del artículo
        with st.expander("👁️ Ver artículo actual", expanded=True):
            st.markdown(article[:2000] + "..." if len(article) > 2000 else article)

# ============================================================================
# NAVEGACIÓN
# ============================================================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Volver a Generar", use_container_width=True):
        st.switch_page("pages/1_📝_Generar.py")

with col2:
    if st.button("🔗 Ir a Auto-Linking", use_container_width=True):
        st.switch_page("pages/4_🔗_Linking.py")

with col3:
    if st.button("📤 Ir a Publicar", use_container_width=True):
        st.switch_page("pages/2_📤_Publicar.py")
