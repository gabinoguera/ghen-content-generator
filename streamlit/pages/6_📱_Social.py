"""
📱 Generación de Posts para Redes Sociales
==========================================
Genera posts optimizados para cada red social.
"""

import streamlit as st
import sys
from pathlib import Path

# Añadir el directorio padre al path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

st.set_page_config(
    page_title="Social | GHEN",
    page_icon="📱",
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

st.title("📱 Posts para Redes Sociales")
st.markdown("""
Genera posts optimizados para cada plataforma:
- 🐦 **Twitter/X**: Thread de 5-6 tweets con hooks
- 💼 **LinkedIn**: Post profesional para CTOs
- 🔴 **Reddit**: Post técnico (publicar manual)
- 🧵 **Threads**: Post casual y conversacional
""")

st.markdown("---")

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### ⚙️ Configuración")
    
    # URL del artículo (necesaria para los posts)
    article_url = st.text_input(
        "🔗 URL del artículo publicado",
        value=st.session_state.get("published_article_url", ""),
        placeholder="https://tublog.com/mi-articulo/",
        help="URL pública del artículo en WordPress"
    )
    
    if article_url:
        st.session_state["published_article_url"] = article_url
    
    st.markdown("---")
    st.markdown("### 📊 Selecciona plataformas")
    
    # Checkboxes para cada plataforma
    gen_twitter = st.checkbox("🐦 Twitter/X (Thread)", value=True)
    gen_linkedin = st.checkbox("💼 LinkedIn", value=True)
    gen_reddit = st.checkbox("🔴 Reddit", value=True)
    gen_threads = st.checkbox("🧵 Threads", value=False)
    
    st.markdown("---")
    
    # Info del artículo
    article = st.session_state["generated_article"]
    st.markdown("**📄 Artículo:**")
    st.markdown(f"- Palabras: {len(article.split()):,}")
    st.markdown(f"- Caracteres: {len(article):,}")

with col2:
    st.markdown("### 🚀 Generar Posts")
    
    if not article_url:
        st.warning("⚠️ Introduce la URL del artículo publicado para incluirla en los posts")
    
    platforms_selected = []
    if gen_twitter:
        platforms_selected.append("twitter")
    if gen_linkedin:
        platforms_selected.append("linkedin")
    if gen_reddit:
        platforms_selected.append("reddit")
    if gen_threads:
        platforms_selected.append("threads")
    
    if not platforms_selected:
        st.info("Selecciona al menos una plataforma")
    else:
        if st.button(f"📱 **Generar posts para {len(platforms_selected)} plataforma(s)**", type="primary", use_container_width=True):
            with st.spinner("Generando posts..."):
                try:
                    # Guardar artículo temporalmente
                    temp_path = str(parent_dir / "streamlit" / "temp_article_for_social.md")
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        f.write(article)
                    
                    from longcontent_generator.social import generate_all_social_posts
                    
                    social_posts = generate_all_social_posts(
                        article_path=temp_path,
                        article_url=article_url or "https://tublog.com/articulo",
                        platforms=platforms_selected
                    )
                    
                    if social_posts:
                        st.session_state["social_posts"] = social_posts
                        st.success(f"✅ Posts generados para {len(social_posts)} plataforma(s)")
                    else:
                        st.error("No se pudieron generar los posts")
                        
                except Exception as e:
                    st.error(f"Error: {e}")
                    import traceback
                    with st.expander("Ver error"):
                        st.code(traceback.format_exc())

# ============================================================================
# MOSTRAR POSTS GENERADOS
# ============================================================================

if "social_posts" in st.session_state and st.session_state["social_posts"]:
    st.markdown("---")
    st.markdown("### 📋 Posts Generados")
    
    posts = st.session_state["social_posts"]
    
    # Crear tabs para cada plataforma
    tab_names = []
    tab_data = []
    
    if "twitter" in posts and posts["twitter"]:
        tab_names.append("🐦 Twitter")
        tab_data.append(("twitter", posts["twitter"]))
    
    if "linkedin" in posts and posts["linkedin"]:
        tab_names.append("💼 LinkedIn")
        tab_data.append(("linkedin", posts["linkedin"]))
    
    if "reddit" in posts and posts["reddit"]:
        tab_names.append("🔴 Reddit")
        tab_data.append(("reddit", posts["reddit"]))
    
    if "threads" in posts and posts["threads"]:
        tab_names.append("🧵 Threads")
        tab_data.append(("threads", posts["threads"]))
    
    if tab_names:
        tabs = st.tabs(tab_names)
        
        for i, (platform, data) in enumerate(tab_data):
            with tabs[i]:
                if platform == "twitter":
                    st.markdown("#### 🐦 Thread de Twitter")
                    thread = data.get("thread", [])
                    
                    if thread:
                        for j, tweet in enumerate(thread, 1):
                            st.markdown(f"**Tweet {j}:**")
                            st.text_area(f"tweet_{j}", tweet, height=100, key=f"tw_{j}", label_visibility="collapsed")
                            char_count = len(tweet)
                            color = "green" if char_count <= 280 else "red"
                            st.markdown(f":{color}[{char_count}/280 caracteres]")
                            st.markdown("---")
                        
                        # Copiar todo el thread
                        full_thread = "\n\n---\n\n".join(thread)
                        st.download_button(
                            "📋 Descargar thread completo",
                            full_thread,
                            file_name="twitter_thread.txt",
                            mime="text/plain"
                        )
                
                elif platform == "linkedin":
                    st.markdown("#### 💼 Post de LinkedIn")
                    post = data.get("post", "")
                    
                    st.text_area("LinkedIn post", post, height=300, key="linkedin_post")
                    st.markdown(f"📊 {len(post)} caracteres")
                    
                    st.download_button(
                        "📋 Descargar post",
                        post,
                        file_name="linkedin_post.txt",
                        mime="text/plain"
                    )
                
                elif platform == "reddit":
                    st.markdown("#### 🔴 Post de Reddit")
                    
                    title = data.get("title", "")
                    body = data.get("body", "")
                    subreddits = data.get("suggested_subreddits", [])
                    
                    st.markdown("**Título:**")
                    st.text_input("Reddit title", title, key="reddit_title", label_visibility="collapsed")
                    
                    st.markdown("**Cuerpo:**")
                    st.text_area("Reddit body", body, height=250, key="reddit_body", label_visibility="collapsed")
                    
                    if subreddits:
                        st.markdown("**📍 Subreddits sugeridos:**")
                        for sub in subreddits:
                            st.markdown(f"- r/{sub}")
                    
                    st.warning("⚠️ **Importante:** Publica manualmente en Reddit. Los posts automatizados pueden resultar en ban.")
                    
                    full_post = f"# {title}\n\n{body}"
                    st.download_button(
                        "📋 Descargar post",
                        full_post,
                        file_name="reddit_post.md",
                        mime="text/markdown"
                    )
                
                elif platform == "threads":
                    st.markdown("#### 🧵 Post de Threads")
                    post = data.get("post", "")
                    
                    st.text_area("Threads post", post, height=200, key="threads_post")
                    st.markdown(f"📊 {len(post)} caracteres")
                    
                    st.download_button(
                        "📋 Descargar post",
                        post,
                        file_name="threads_post.txt",
                        mime="text/plain"
                    )

# ============================================================================
# NAVEGACIÓN
# ============================================================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Volver a Imagen", use_container_width=True):
        st.switch_page("pages/5_🎨_Imagen.py")

with col2:
    if st.button("🔄 Regenerar posts", use_container_width=True):
        if "social_posts" in st.session_state:
            del st.session_state["social_posts"]
        st.rerun()

with col3:
    if st.button("📤 Ir a Publicar", use_container_width=True):
        st.switch_page("pages/2_📤_Publicar.py")
