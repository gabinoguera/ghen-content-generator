"""
📝 Generar Artículo
===================
Genera contenido técnico usando la personalidad configurada.
"""

import streamlit as st
import sys
from pathlib import Path

# Añadir el directorio padre al path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

st.set_page_config(
    page_title="Generar Artículo | GHEN",
    page_icon="📝",
    layout="wide"
)

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_secret(key: str, default: str = "") -> str:
    """Obtiene un secret de forma segura sin crashear."""
    try:
        value = st.secrets.get(key, default)
        return value if value else default
    except Exception:
        return default

# ============================================================================
# VERIFICACIONES INICIALES
# ============================================================================

# Verificar que tenemos API key
has_gemini = st.session_state.get("gemini_api_key") or get_secret("GEMINI_API_KEY")

if not has_gemini:
    st.error("⚠️ **Configura tu API Key de Gemini primero**")
    if st.button("Ir a configuración"):
        st.switch_page("🏠_Home.py")
    st.stop()

# ============================================================================
# INICIALIZAR GEMINI CON LA PERSONALIDAD
# ============================================================================

@st.cache_resource
def get_gemini_model(api_key: str):
    """Inicializa el modelo Gemini con la API key."""
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

def get_active_api_key():
    """Obtiene la API key activa (sesión o secrets)."""
    return st.session_state.get("gemini_api_key") or get_secret("GEMINI_API_KEY", "")

# ============================================================================
# HEADER
# ============================================================================

st.title("📝 Generar Artículo")
st.markdown("Crea contenido técnico SEO-optimizado con tu personalidad de blog.")

# Mostrar personalidad activa (resumen)
with st.expander("🎭 Ver personalidad activa", expanded=False):
    personality = st.session_state.get("blog_personality", "No configurada")
    st.text_area("System Prompt activo", personality, height=150, disabled=True)

st.markdown("---")

# ============================================================================
# SELECCIÓN DE MÉTODO
# ============================================================================

st.markdown("### 🎯 Método de Generación")

metodo = st.radio(
    "¿Cómo quieres generar el artículo?",
    options=["📌 Keyword directo", "💡 Desde un tema", "📰 Desde URL/Newsletter"],
    horizontal=True,
    help="Cada método tiene un flujo diferente de investigación y generación"
)

st.markdown("---")

# ============================================================================
# MÉTODO 1: KEYWORD DIRECTO
# ============================================================================

if metodo == "📌 Keyword directo":
    st.markdown("### 📌 Generación desde Keyword")
    st.markdown("""
    Introduce el keyword principal para tu artículo. El sistema:
    1. Investigará contenido relacionado
    2. Analizará la competencia SEO
    3. Generará un artículo optimizado
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        keyword = st.text_input(
            "Keyword principal",
            placeholder="Ej: MLOps best practices 2025",
            help="El término de búsqueda principal para tu artículo"
        )
        
        additional_context = st.text_area(
            "Contexto adicional (opcional)",
            placeholder="Información específica que quieres incluir, enfoque particular, etc.",
            height=100
        )
    
    with col2:
        st.markdown("**Opciones**")
        
        do_research = st.checkbox("🔍 Investigar SERP", value=True, 
                                  help="Busca y analiza artículos de la competencia")
        
        include_code = st.checkbox("💻 Incluir código", value=True,
                                   help="Genera ejemplos de código cuando sea relevante")
        
        target_words = st.slider("📏 Palabras objetivo", 1000, 3000, 1800, 100)
    
    if st.button("🚀 **Generar Artículo**", type="primary", use_container_width=True, key="btn_keyword"):
        if not keyword:
            st.warning("Introduce un keyword primero")
        else:
            with st.spinner("Generando artículo..."):
                try:
                    # Obtener modelo y personalidad
                    model = get_gemini_model(get_active_api_key())
                    personality = st.session_state.get("blog_personality", "")
                    
                    # Construir prompt
                    prompt = f"""
{personality}

---

TAREA: Escribe un artículo técnico SEO-optimizado sobre: "{keyword}"

REQUISITOS:
- Extensión: aproximadamente {target_words} palabras
- Estructura: Introducción, secciones con H2/H3, conclusión
- Estilo: Según la personalidad definida arriba
- SEO: Incluye el keyword en título, introducción y headings
{"- Código: Incluye ejemplos de código prácticos cuando sea relevante" if include_code else "- Sin código: Enfócate en conceptos y explicaciones"}

{f"CONTEXTO ADICIONAL: {additional_context}" if additional_context else ""}

FORMATO: Markdown con frontmatter YAML (title, description, keywords)
"""
                    
                    # Generar
                    response = model.generate_content(prompt)
                    article = response.text
                    
                    # Guardar en sesión
                    st.session_state["generated_article"] = article
                    st.session_state["generated_keyword"] = keyword
                    
                    st.success("✅ Artículo generado correctamente")
                    
                except Exception as e:
                    st.error(f"❌ Error al generar: {e}")

# ============================================================================
# MÉTODO 2: DESDE TEMA
# ============================================================================

elif metodo == "💡 Desde un tema":
    st.markdown("### 💡 Generación desde Tema")
    st.markdown("""
    Describe un tema y el sistema:
    1. Sugerirá keywords SEO óptimos
    2. Elegirás el que prefieras
    3. Generará el artículo
    """)
    
    topic = st.text_area(
        "Describe el tema que quieres cubrir",
        placeholder="Ej: Quiero escribir sobre cómo implementar agentes de IA usando LangGraph para automatizar tareas complejas en producción...",
        height=100
    )
    
    if st.button("🔍 Sugerir Keywords", use_container_width=True):
        if not topic:
            st.warning("Describe el tema primero")
        else:
            with st.spinner("Analizando tema y sugiriendo keywords..."):
                try:
                    model = get_gemini_model(get_active_api_key())
                    personality = st.session_state.get("blog_personality", "")
                    
                    prompt = f"""
{personality}

---

Analiza este tema y sugiere 5 keywords SEO óptimos para un artículo:

TEMA: {topic}

Para cada keyword proporciona:
1. El keyword exacto (long-tail preferido)
2. Volumen estimado (alto/medio/bajo)
3. Dificultad SEO (alta/media/baja)
4. Intent de búsqueda (informacional/transaccional/navegacional)
5. Ángulo único que podríamos aportar

Formato: Lista numerada con todos los detalles.
"""
                    
                    response = model.generate_content(prompt)
                    
                    st.session_state["suggested_keywords"] = response.text
                    st.session_state["pending_topic"] = topic
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    # Mostrar sugerencias si existen
    if "suggested_keywords" in st.session_state:
        st.markdown("#### 📋 Keywords Sugeridos")
        st.markdown(st.session_state["suggested_keywords"])
        
        selected_keyword = st.text_input(
            "Escribe o pega el keyword elegido",
            placeholder="Copia aquí el keyword que prefieras"
        )
        
        include_code = st.checkbox("💻 Incluir código", value=True, key="code_topic")
        
        if st.button("🚀 **Generar con este Keyword**", type="primary", use_container_width=True):
            if selected_keyword:
                with st.spinner("Generando artículo..."):
                    try:
                        model = get_gemini_model(get_active_api_key())
                        personality = st.session_state.get("blog_personality", "")
                        topic = st.session_state.get("pending_topic", "")
                        
                        prompt = f"""
{personality}

---

TAREA: Escribe un artículo técnico SEO-optimizado.

TEMA ORIGINAL: {topic}
KEYWORD SEO: {selected_keyword}

REQUISITOS:
- Extensión: 1500-2000 palabras
- Estructura: Introducción, secciones H2/H3, conclusión
- SEO: Keyword en título, intro, headings
{"- Código: Ejemplos prácticos" if include_code else ""}

FORMATO: Markdown con frontmatter YAML
"""
                        
                        response = model.generate_content(prompt)
                        st.session_state["generated_article"] = response.text
                        st.session_state["generated_keyword"] = selected_keyword
                        
                        st.success("✅ Artículo generado")
                        
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

# ============================================================================
# MÉTODO 3: DESDE URL
# ============================================================================

elif metodo == "📰 Desde URL/Newsletter":
    st.markdown("### 📰 Generación desde URL")
    st.markdown("""
    Proporciona una URL de newsletter, artículo o documentación para:
    1. Extraer y analizar el contenido
    2. Identificar temas y ángulos únicos
    3. Generar contenido original basado en esa fuente
    """)
    
    url = st.text_input(
        "URL de la fuente",
        placeholder="https://newsletter.example.com/issue/123",
        help="Newsletter, blog post, documentación, etc."
    )
    
    content_type = st.selectbox(
        "Tipo de contenido",
        ["Newsletter técnico", "Artículo de blog", "Documentación", "Release notes", "Otro"]
    )
    
    focus = st.text_input(
        "Enfoque específico (opcional)",
        placeholder="Ej: Me interesa especialmente la parte de..."
    )
    
    if st.button("📥 Extraer y Analizar", use_container_width=True):
        if not url:
            st.warning("Introduce una URL")
        else:
            with st.spinner("Extrayendo contenido..."):
                try:
                    # Intentar importar el scraper
                    from longcontent_generator.core import scrape_article
                    
                    content = scrape_article(url)
                    
                    if content:
                        st.session_state["scraped_content"] = content
                        st.session_state["scraped_url"] = url
                        st.success(f"✅ Extraídas {len(content)} caracteres")
                        
                        with st.expander("Ver contenido extraído"):
                            st.text_area("Contenido", content[:3000] + "..." if len(content) > 3000 else content, height=200)
                    else:
                        st.error("No se pudo extraer contenido de esa URL")
                        
                except ImportError:
                    st.error("El módulo de scraping no está disponible. Usa otro método.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    # Si hay contenido scrapeado, mostrar opciones de generación
    if "scraped_content" in st.session_state:
        st.markdown("---")
        st.markdown("#### 🎯 Generar artículo desde el contenido")
        
        article_angle = st.text_input(
            "Ángulo/enfoque del artículo",
            placeholder="Ej: Análisis crítico de las tendencias, Tutorial basado en...",
        )
        
        if st.button("🚀 **Generar Artículo**", type="primary", use_container_width=True, key="btn_url"):
            with st.spinner("Generando artículo..."):
                try:
                    model = get_gemini_model(get_active_api_key())
                    personality = st.session_state.get("blog_personality", "")
                    content = st.session_state.get("scraped_content", "")
                    
                    prompt = f"""
{personality}

---

TAREA: Genera un artículo original basado en esta fuente.

TIPO DE FUENTE: {content_type}
URL: {st.session_state.get('scraped_url', '')}
{f"ENFOQUE: {article_angle}" if article_angle else ""}
{f"INTERÉS ESPECÍFICO: {focus}" if focus else ""}

CONTENIDO DE LA FUENTE:
{content[:8000]}

INSTRUCCIONES:
1. NO copies el contenido, genera algo ORIGINAL
2. Aporta tu perspectiva y análisis
3. Si es newsletter, haz un "resumen + análisis" con opiniones
4. Menciona la fuente pero añade valor propio
5. Extensión: 1500-2000 palabras

FORMATO: Markdown con frontmatter YAML
"""
                    
                    response = model.generate_content(prompt)
                    st.session_state["generated_article"] = response.text
                    st.session_state["generated_keyword"] = article_angle or content_type
                    
                    st.success("✅ Artículo generado")
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ============================================================================
# MOSTRAR ARTÍCULO GENERADO
# ============================================================================

st.markdown("---")

if "generated_article" in st.session_state:
    st.markdown("## 📄 Artículo Generado")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown("**Acciones**")
        
        # Copiar al portapapeles (usando JavaScript)
        if st.button("📋 Copiar", use_container_width=True):
            st.code(st.session_state["generated_article"][:100] + "...", language="markdown")
            st.info("Usa Ctrl+A, Ctrl+C en el área de texto")
        
        # Descargar como archivo
        st.download_button(
            "💾 Descargar .md",
            st.session_state["generated_article"],
            file_name="articulo_generado.md",
            mime="text/markdown",
            use_container_width=True
        )
        
        # Ir a publicar
        if st.button("📤 Ir a Publicar", type="primary", use_container_width=True):
            st.switch_page("pages/2_📤_Publicar.py")
        
        # Regenerar
        if st.button("🔄 Regenerar", use_container_width=True):
            if "generated_article" in st.session_state:
                del st.session_state["generated_article"]
            st.rerun()
    
    with col1:
        # Editor del artículo
        edited_article = st.text_area(
            "Edita el artículo si es necesario",
            value=st.session_state["generated_article"],
            height=500,
            key="article_editor"
        )
        
        if edited_article != st.session_state["generated_article"]:
            st.session_state["generated_article"] = edited_article
            st.success("✅ Cambios guardados")
    
    # Preview
    with st.expander("👁️ Preview (renderizado)", expanded=False):
        st.markdown(st.session_state["generated_article"])

# ============================================================================
# ACCIONES POST-GENERACIÓN
# ============================================================================

st.markdown("---")
st.markdown("### 🔧 Siguiente paso")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 Evaluar QA", use_container_width=True):
        st.switch_page("pages/3_🔍_QA.py")

with col2:
    if st.button("🔗 Auto-Linking", use_container_width=True):
        st.switch_page("pages/4_🔗_Linking.py")

with col3:
    if st.button("🎨 Generar Imagen", use_container_width=True):
        st.switch_page("pages/5_🎨_Imagen.py")

with col4:
    if st.button("📱 Posts Sociales", use_container_width=True):
        st.switch_page("pages/6_📱_Social.py")
