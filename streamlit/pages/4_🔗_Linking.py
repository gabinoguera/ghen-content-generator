"""
🔗 Auto-Linking
===============
Inserta automáticamente links internos y externos en el artículo.
"""

import streamlit as st
import sys
from pathlib import Path

# Añadir el directorio padre al path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

st.set_page_config(
    page_title="Auto-Linking | GHEN",
    page_icon="🔗",
    layout="wide"
)

# ============================================================================
# VERIFICACIONES
# ============================================================================

if "generated_article" not in st.session_state:
    st.warning("⚠️ **No hay artículo generado**")
    if st.button("📝 Ir a Generar"):
        st.switch_page("pages/1_📝_Generar.py")
    st.stop()

# ============================================================================
# HEADER
# ============================================================================

st.title("🔗 Auto-Linking Inteligente")
st.markdown("""
Inserta automáticamente links en el artículo:
- 🌐 **Links Externos**: Herramientas, librerías, frameworks → URL oficial
- 🏠 **Links Internos**: Conexión con artículos existentes del blog
""")

st.markdown("---")

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

article = st.session_state["generated_article"]

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### ⚙️ Configuración")
    
    min_external = st.slider("🌐 Links externos (mín)", 1, 10, 3)
    max_external = st.slider("🌐 Links externos (máx)", min_external, 15, 6)
    
    st.markdown("---")
    
    min_internal = st.slider("🏠 Links internos (mín)", 1, 10, 3)
    max_internal = st.slider("🏠 Links internos (máx)", min_internal, 15, 5)
    
    st.markdown("---")
    
    # Contar links existentes
    try:
        from longcontent_generator.linking import count_links_in_article
        existing_links = count_links_in_article(article)
        
        st.markdown("**📊 Links actuales:**")
        st.markdown(f"- Internos: {existing_links.get('internal', 0)}")
        st.markdown(f"- Externos: {existing_links.get('external', 0)}")
        st.markdown(f"- Total: {existing_links.get('total', 0)}")
    except Exception as e:
        st.warning(f"No se pudo contar links: {e}")

with col2:
    st.markdown("### 📄 Artículo")
    
    # Preview del artículo
    with st.expander("👁️ Ver artículo actual", expanded=False):
        st.markdown(article[:3000] + "..." if len(article) > 3000 else article)
    
    # Botón para ejecutar auto-linking
    if st.button("🔗 **Ejecutar Auto-Linking**", type="primary", use_container_width=True):
        with st.spinner("Analizando artículo e insertando links..."):
            try:
                from longcontent_generator.linking import auto_link_article, count_links_in_article
                
                articulo_con_links, link_report = auto_link_article(
                    article_text=article,
                    min_external=min_external,
                    min_internal=min_internal,
                    max_external=max_external,
                    max_internal=max_internal
                )
                
                # Verificar integridad
                if link_report.get('integrity_check') == 'passed':
                    # Guardar reporte en sesión
                    st.session_state["link_report"] = link_report
                    st.session_state["article_with_links"] = articulo_con_links
                    
                    st.success("✅ Auto-linking completado")
                else:
                    st.error(f"❌ Error de integridad: {link_report.get('error', 'desconocido')}")
                    
            except Exception as e:
                st.error(f"Error: {e}")
                import traceback
                st.code(traceback.format_exc())

# ============================================================================
# RESULTADOS
# ============================================================================

if "link_report" in st.session_state and st.session_state.get("article_with_links"):
    st.markdown("---")
    st.markdown("### ✅ Resultado del Auto-Linking")
    
    report = st.session_state["link_report"]
    linked_article = st.session_state["article_with_links"]
    
    # Estadísticas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌐 Externos añadidos", report['stats'].get('external_added', 0))
    with col2:
        st.metric("🏠 Internos añadidos", report['stats'].get('internal_added', 0))
    with col3:
        st.metric("📏 Longitud original", f"{report.get('original_length', 0):,}")
    with col4:
        diff = report.get('final_length', 0) - report.get('original_length', 0)
        st.metric("📏 Longitud final", f"{report.get('final_length', 0):,}", delta=f"+{diff}")
    
    # Tabs con detalles
    tab1, tab2, tab3 = st.tabs(["🌐 Links externos", "🏠 Links internos", "📄 Artículo con links"])
    
    with tab1:
        external_links = report.get('external_links', [])
        if external_links:
            for link in external_links:
                st.markdown(f"- **{link.get('anchor_text', '')}** → [{link.get('url', '')[:50]}...]({link.get('url', '')})")
        else:
            st.info("No se añadieron links externos")
    
    with tab2:
        internal_links = report.get('internal_links', [])
        if internal_links:
            for link in internal_links:
                st.markdown(f"- **{link.get('anchor_text', '')}** → {link.get('post_title', '')[:50]}...")
        else:
            st.info("No se añadieron links internos")
    
    with tab3:
        st.text_area("Artículo con links", linked_article, height=400, disabled=True)
    
    # Acciones
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ **Aceptar y aplicar links**", type="primary", use_container_width=True):
            st.session_state["generated_article"] = linked_article
            st.success("✅ Links aplicados al artículo")
            # Limpiar estados temporales
            del st.session_state["link_report"]
            del st.session_state["article_with_links"]
            st.rerun()
    
    with col2:
        if st.button("❌ Descartar links", use_container_width=True):
            del st.session_state["link_report"]
            del st.session_state["article_with_links"]
            st.info("Links descartados. El artículo original se mantiene.")
            st.rerun()

# ============================================================================
# NAVEGACIÓN
# ============================================================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Volver a QA", use_container_width=True):
        st.switch_page("pages/3_🔍_QA.py")

with col2:
    if st.button("🎨 Ir a Imagen", use_container_width=True):
        st.switch_page("pages/5_🎨_Imagen.py")

with col3:
    if st.button("📤 Ir a Publicar", use_container_width=True):
        st.switch_page("pages/2_📤_Publicar.py")
