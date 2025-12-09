"""
🚀 GHEN Content Generator - Streamlit App
==========================================
Generador de contenido técnico multi-blog con IA.

Cada usuario configura:
1. Su personalidad de blog (System Prompt - como un Gem)
2. Sus credenciales de WordPress
3. Su API key de Gemini (o usa la compartida)
"""

import streamlit as st
import sys
from pathlib import Path

# Añadir el directorio padre al path para importar longcontent_generator
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Configuración de la página
st.set_page_config(
    page_title="GHEN Content Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# INICIALIZACIÓN DE SESSION STATE
# ============================================================================

# Personalidad del blog (System Prompt editable)
if "blog_personality" not in st.session_state:
    st.session_state.blog_personality = """Eres un experto en tecnología y desarrollo de software con experiencia en:
- Inteligencia Artificial y Machine Learning
- Desarrollo de software y arquitectura
- Cloud computing y DevOps
- Mejores prácticas de ingeniería

Tu estilo de escritura es:
- Técnico pero accesible
- Basado en evidencia y experiencia práctica
- Orientado a desarrolladores y CTOs
- Con ejemplos de código cuando sea relevante

Escribes en español, con un tono profesional pero cercano."""

# Credenciales WordPress
if "wp_url" not in st.session_state:
    st.session_state.wp_url = ""
if "wp_user" not in st.session_state:
    st.session_state.wp_user = ""
if "wp_password" not in st.session_state:
    st.session_state.wp_password = ""

# API Key de Gemini (opcional si hay una por defecto)
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""

# Nivel de personalidad
if "personality_level" not in st.session_state:
    st.session_state.personality_level = "base"

# ============================================================================
# SIDEBAR - CONFIGURACIÓN GLOBAL
# ============================================================================

def get_secret(key: str, default: str = "") -> str:
    """Obtiene un secret de forma segura sin crashear."""
    try:
        value = st.secrets.get(key, default)
        return value if value else default
    except Exception:
        return default

with st.sidebar:
    st.image("https://ghendigital.com/wp-content/uploads/2024/01/logo-ghen.png", width=150)
    st.markdown("---")
    
    # Estado de conexión
    st.markdown("### 🔌 Estado")
    
    # Verificar Gemini
    gemini_status = "✅" if st.session_state.gemini_api_key or get_secret("GEMINI_API_KEY") else "⚠️"
    st.markdown(f"{gemini_status} **Gemini API**")
    
    # Verificar WordPress
    wp_status = "✅" if st.session_state.wp_url and st.session_state.wp_user else "⚠️"
    st.markdown(f"{wp_status} **WordPress**")
    
    # Verificar personalidad
    personality_status = "✅" if len(st.session_state.blog_personality) > 50 else "⚠️"
    st.markdown(f"{personality_status} **Personalidad**")
    
    st.markdown("---")
    st.markdown("### 📚 Navegación")
    st.markdown("""
    1. **🏠 Home** - Configura tu blog
    2. **📝 Generar** - Crea artículos
    3. **📤 Publicar** - Envía a WordPress
    4. **🔍 QA** - Evalúa calidad
    5. **🔗 Linking** - Auto-enlaces
    6. **🎨 Imagen** - Genera imagen
    7. **📱 Social** - Posts redes
    """)

# ============================================================================
# CONTENIDO PRINCIPAL
# ============================================================================

st.title("🚀 GHEN Content Generator")
st.markdown("### Generador de contenido técnico multi-blog con IA")

st.markdown("---")

# ============================================================================
# SECCIÓN 1: PERSONALIDAD DEL BLOG (SYSTEM PROMPT)
# ============================================================================

st.markdown("## 🎭 Personalidad de tu Blog")
st.markdown("""
> **Como un Gem personalizado de Google**: Define el estilo, tono y expertise de tu blog.
> Este texto se usa como "System Prompt" para Gemini en cada generación.
""")

col1, col2 = st.columns([3, 1])

with col1:
    new_personality = st.text_area(
        "System Prompt (personalidad del blog)",
        value=st.session_state.blog_personality,
        height=300,
        help="Define el estilo, expertise y tono de tu blog. Este prompt se envía a Gemini antes de cada generación.",
        key="personality_input"
    )
    
    if new_personality != st.session_state.blog_personality:
        st.session_state.blog_personality = new_personality
        st.success("✅ Personalidad actualizada")

with col2:
    st.markdown("### 📋 Plantillas")
    
    if st.button("🎯 Blog Técnico", use_container_width=True):
        st.session_state.blog_personality = """Eres un experto en tecnología con 10+ años de experiencia en:
- Desarrollo de software y arquitectura de sistemas
- Inteligencia Artificial, ML y GenAI
- Cloud computing (GCP, AWS, Azure)
- DevOps, MLOps y mejores prácticas

Tu estilo:
- Técnico y profundo, con código real
- Basado en experiencia en producción
- Para desarrolladores senior y CTOs
- Ejemplos prácticos, no solo teoría

Idioma: Español
Tono: Profesional, directo, con opiniones fundamentadas"""
        st.rerun()
    
    if st.button("📰 Blog Divulgativo", use_container_width=True):
        st.session_state.blog_personality = """Eres un divulgador tecnológico que hace accesible la IA y el desarrollo:
- Explicas conceptos complejos de forma simple
- Usas analogías del mundo real
- Tu audiencia son profesionales no-técnicos
- Evitas jerga innecesaria

Tu estilo:
- Claro y pedagógico
- Con ejemplos cotidianos
- Enfocado en el "para qué sirve"
- Sin código, o muy básico

Idioma: Español
Tono: Cercano, entusiasta, educativo"""
        st.rerun()
    
    if st.button("💼 Blog Empresarial", use_container_width=True):
        st.session_state.blog_personality = """Eres un consultor de transformación digital para empresas:
- Enfocado en ROI y resultados de negocio
- Cases studies y métricas reales
- Tu audiencia son CTOs, CIOs y directivos
- Conectas tecnología con estrategia

Tu estilo:
- Ejecutivo y orientado a decisiones
- Con datos y benchmarks
- Frameworks y metodologías
- Sin tecnicismos innecesarios

Idioma: Español
Tono: Profesional, consultivo, orientado a acción"""
        st.rerun()

st.markdown("---")

# ============================================================================
# SECCIÓN 2: CREDENCIALES
# ============================================================================

st.markdown("## 🔐 Credenciales")

tab1, tab2 = st.tabs(["🤖 Gemini API", "📝 WordPress"])

with tab1:
    st.markdown("""
    **API Key de Gemini** - Necesaria para generar contenido.
    
    > 💡 Si dejas vacío, se usará la API key por defecto (si está configurada en secrets).
    """)
    
    gemini_key = st.text_input(
        "API Key de Gemini",
        value=st.session_state.gemini_api_key,
        type="password",
        placeholder="AIza...",
        help="Obtén tu API key en: https://makersuite.google.com/app/apikey"
    )
    
    if gemini_key != st.session_state.gemini_api_key:
        st.session_state.gemini_api_key = gemini_key
    
    # Mostrar estado
    if st.session_state.gemini_api_key:
        st.success("✅ API Key de Gemini configurada")
    elif get_secret("GEMINI_API_KEY"):
        st.info("ℹ️ Usando API Key por defecto de secrets")
    else:
        st.warning("⚠️ Configura tu API Key de Gemini para continuar")

with tab2:
    st.markdown("""
    **Credenciales de WordPress** - Para publicar artículos como borrador.
    
    > 💡 Necesitas una **Application Password** de WordPress, no tu contraseña normal.
    > Ve a: Tu perfil → Application Passwords → Crear nueva
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        wp_url = st.text_input(
            "URL de WordPress",
            value=st.session_state.wp_url,
            placeholder="https://tublog.com",
            help="URL base de tu WordPress (sin /wp-admin)"
        )
        if wp_url != st.session_state.wp_url:
            st.session_state.wp_url = wp_url
        
        wp_user = st.text_input(
            "Usuario de WordPress",
            value=st.session_state.wp_user,
            placeholder="admin",
            help="Tu nombre de usuario de WordPress"
        )
        if wp_user != st.session_state.wp_user:
            st.session_state.wp_user = wp_user
    
    with col2:
        wp_password = st.text_input(
            "Application Password",
            value=st.session_state.wp_password,
            type="password",
            placeholder="xxxx xxxx xxxx xxxx xxxx xxxx",
            help="Application Password (no tu contraseña normal)"
        )
        if wp_password != st.session_state.wp_password:
            st.session_state.wp_password = wp_password
        
        # Botón para probar conexión
        if st.button("🔌 Probar conexión", use_container_width=True):
            if wp_url and wp_user and wp_password:
                with st.spinner("Probando conexión..."):
                    try:
                        import requests
                        import base64
                        
                        auth = base64.b64encode(f"{wp_user}:{wp_password}".encode()).decode()
                        headers = {"Authorization": f"Basic {auth}"}
                        
                        response = requests.get(
                            f"{wp_url}/wp-json/wp/v2/users/me",
                            headers=headers,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            user_data = response.json()
                            st.success(f"✅ Conectado como: {user_data.get('name', wp_user)}")
                        else:
                            st.error(f"❌ Error {response.status_code}: {response.text[:100]}")
                    except Exception as e:
                        st.error(f"❌ Error de conexión: {e}")
            else:
                st.warning("Completa todos los campos primero")
    
    # Mostrar estado
    if st.session_state.wp_url and st.session_state.wp_user and st.session_state.wp_password:
        st.success("✅ Credenciales de WordPress configuradas")
    else:
        st.warning("⚠️ Configura tus credenciales de WordPress para publicar")

st.markdown("---")

# ============================================================================
# SECCIÓN 3: RESUMEN Y SIGUIENTE PASO
# ============================================================================

st.markdown("## ✅ Estado de Configuración")

col1, col2, col3 = st.columns(3)

with col1:
    if len(st.session_state.blog_personality) > 50:
        st.success("🎭 **Personalidad**\n\nConfigurada")
    else:
        st.error("🎭 **Personalidad**\n\nMuy corta")

with col2:
    if st.session_state.gemini_api_key or get_secret("GEMINI_API_KEY"):
        st.success("🤖 **Gemini**\n\nListo")
    else:
        st.error("🤖 **Gemini**\n\nFalta API Key")

with col3:
    if st.session_state.wp_url and st.session_state.wp_user and st.session_state.wp_password:
        st.success("📝 **WordPress**\n\nConfigurado")
    else:
        st.warning("📝 **WordPress**\n\nOpcional")

# Botón para ir a generar
st.markdown("---")

if st.button("📝 **Ir a Generar Artículo** →", type="primary", use_container_width=True):
    st.switch_page("pages/1_📝_Generar.py")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
    GHEN Content Generator v1.0 | 
    <a href="https://ghendigital.com" target="_blank">GHEN Digital</a>
</div>
""", unsafe_allow_html=True)
