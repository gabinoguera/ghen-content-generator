"""
📤 Publicar en WordPress
========================
Publica el artículo generado como borrador en WordPress.
"""

import streamlit as st
import requests
import base64
import re
import markdown

st.set_page_config(
    page_title="Publicar | GHEN",
    page_icon="📤",
    layout="wide"
)

# ============================================================================
# VERIFICACIONES
# ============================================================================

# Verificar que hay artículo
if "generated_article" not in st.session_state:
    st.warning("⚠️ **No hay artículo generado**")
    st.markdown("Primero genera un artículo en la página anterior.")
    if st.button("📝 Ir a Generar"):
        st.switch_page("pages/1_📝_Generar.py")
    st.stop()

# Verificar credenciales WordPress
wp_ready = (
    st.session_state.get("wp_url") and 
    st.session_state.get("wp_user") and 
    st.session_state.get("wp_password")
)

# ============================================================================
# HEADER
# ============================================================================

st.title("📤 Publicar en WordPress")
st.markdown("Publica tu artículo como **borrador** en WordPress.")

st.markdown("---")

# ============================================================================
# CONFIGURACIÓN WORDPRESS (si no está lista)
# ============================================================================

if not wp_ready:
    st.warning("⚠️ **Configura las credenciales de WordPress**")
    
    with st.form("wp_credentials"):
        wp_url = st.text_input("URL de WordPress", placeholder="https://tublog.com")
        wp_user = st.text_input("Usuario", placeholder="admin")
        wp_password = st.text_input("Application Password", type="password", placeholder="xxxx xxxx xxxx xxxx")
        
        if st.form_submit_button("💾 Guardar credenciales"):
            st.session_state.wp_url = wp_url
            st.session_state.wp_user = wp_user
            st.session_state.wp_password = wp_password
            st.success("✅ Credenciales guardadas")
            st.rerun()
    
    st.stop()

# ============================================================================
# FUNCIONES DE PUBLICACIÓN
# ============================================================================

def extract_frontmatter(markdown_text: str) -> tuple[dict, str]:
    """Extrae frontmatter YAML del markdown."""
    frontmatter = {}
    content = markdown_text
    
    # Buscar frontmatter
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', markdown_text, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        content = markdown_text[fm_match.end():]
        
        # Parsear YAML simple
        for line in fm_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                frontmatter[key] = value
    
    return frontmatter, content

def markdown_to_html(markdown_text: str) -> str:
    """Convierte markdown a HTML limpio para WordPress."""
    html = markdown.markdown(
        markdown_text,
        extensions=['extra', 'nl2br', 'sane_lists', 'codehilite', 'toc']
    )
    return html

def publish_to_wordpress(title: str, content: str, excerpt: str = "", status: str = "draft") -> dict:
    """Publica un artículo en WordPress."""
    
    url = st.session_state.wp_url.rstrip('/')
    user = st.session_state.wp_user
    password = st.session_state.wp_password
    
    # Crear auth header
    auth = base64.b64encode(f"{user}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }
    
    # Datos del post
    data = {
        "title": title,
        "content": content,
        "excerpt": excerpt,
        "status": status  # draft, publish, pending
    }
    
    # Publicar
    response = requests.post(
        f"{url}/wp-json/wp/v2/posts",
        headers=headers,
        json=data,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        return {"success": True, "data": response.json()}
    else:
        return {"success": False, "error": response.text, "status_code": response.status_code}

# ============================================================================
# PREVIEW Y EDICIÓN
# ============================================================================

st.markdown("### 📄 Artículo a Publicar")

# Extraer frontmatter
article = st.session_state["generated_article"]
frontmatter, content_body = extract_frontmatter(article)

col1, col2 = st.columns([2, 1])

with col2:
    st.markdown("#### ⚙️ Metadatos")
    
    # Título
    default_title = frontmatter.get("title", st.session_state.get("generated_keyword", "Sin título"))
    title = st.text_input("Título del post", value=default_title)
    
    # Extracto
    default_excerpt = frontmatter.get("description", "")
    excerpt = st.text_area("Extracto (SEO)", value=default_excerpt, height=100)
    
    # Estado
    status = st.selectbox(
        "Estado de publicación",
        options=["draft", "pending", "publish"],
        format_func=lambda x: {"draft": "📝 Borrador", "pending": "⏳ Pendiente de revisión", "publish": "🌐 Publicado"}[x]
    )
    
    st.warning("⚠️ Recomendamos publicar como **Borrador** para revisar primero.")

with col1:
    # Preview tabs
    tab1, tab2, tab3 = st.tabs(["📝 Markdown", "🌐 HTML Preview", "✏️ Editar"])
    
    with tab1:
        st.code(content_body[:2000] + "..." if len(content_body) > 2000 else content_body, language="markdown")
    
    with tab2:
        html_content = markdown_to_html(content_body)
        st.markdown(html_content, unsafe_allow_html=True)
    
    with tab3:
        edited_content = st.text_area(
            "Editar contenido",
            value=content_body,
            height=400
        )
        if edited_content != content_body:
            st.session_state["edited_content"] = edited_content

# ============================================================================
# PUBLICACIÓN
# ============================================================================

st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🚀 **Publicar en WordPress**", type="primary", use_container_width=True):
        if not title:
            st.error("El título es obligatorio")
        else:
            with st.spinner("Publicando..."):
                # Usar contenido editado si existe
                final_content = st.session_state.get("edited_content", content_body)
                html_content = markdown_to_html(final_content)
                
                result = publish_to_wordpress(
                    title=title,
                    content=html_content,
                    excerpt=excerpt,
                    status=status
                )
                
                if result["success"]:
                    post_data = result["data"]
                    post_url = post_data.get("link", "")
                    post_id = post_data.get("id", "")
                    
                    st.success(f"✅ Artículo publicado correctamente")
                    st.markdown(f"""
                    **Detalles:**
                    - 🆔 ID: `{post_id}`
                    - 📊 Estado: `{status}`
                    - 🔗 URL: [{post_url}]({post_url})
                    """)
                    
                    # Limpiar estado
                    if st.button("🔄 Generar otro artículo"):
                        for key in ["generated_article", "generated_keyword", "edited_content"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.switch_page("pages/1_📝_Generar.py")
                else:
                    st.error(f"❌ Error al publicar: {result.get('error', 'Error desconocido')}")
                    st.code(f"Status: {result.get('status_code')}")

# ============================================================================
# INFORMACIÓN ADICIONAL
# ============================================================================

st.markdown("---")

with st.expander("ℹ️ Información sobre la publicación"):
    st.markdown("""
    ### Estados de publicación
    
    - **📝 Borrador (draft)**: El artículo se guarda pero no es visible públicamente. 
      Puedes editarlo en WordPress antes de publicar.
    
    - **⏳ Pendiente (pending)**: El artículo queda pendiente de revisión por un editor.
      Útil para workflows con múltiples autores.
    
    - **🌐 Publicado (publish)**: El artículo se publica inmediatamente y es visible 
      para todos los visitantes.
    
    ### Recomendación
    
    Siempre publica como **Borrador** primero para:
    1. Revisar el formato en WordPress
    2. Añadir imágenes destacadas
    3. Configurar categorías y etiquetas
    4. Revisar el SEO con plugins como Yoast
    """)
