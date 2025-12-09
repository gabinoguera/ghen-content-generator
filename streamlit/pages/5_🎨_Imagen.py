"""
🎨 Generación de Imagen Destacada
=================================
Genera imagen con Gemini 2.0 Flash (imagen nativa).
"""

import streamlit as st
import sys
import os
from pathlib import Path
from io import BytesIO
from PIL import Image

# Añadir el directorio padre al path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

st.set_page_config(
    page_title="Imagen | GHEN",
    page_icon="🎨",
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
    if st.button("📝 Ir a Generar"):
        st.switch_page("pages/1_📝_Generar.py")
    st.stop()

api_key = get_active_api_key()
if not api_key:
    st.error("⚠️ **Configura tu API Key de Gemini primero**")
    if st.button("Ir a configuración"):
        st.switch_page("🏠_Home.py")
    st.stop()

# ============================================================================
# HEADER
# ============================================================================

st.title("🎨 Generación de Imagen Destacada")
st.markdown("""
Genera una imagen única usando **Gemini 2.0 Flash** con generación nativa de imágenes.

**Proceso:**
1. 🧠 Gemini analiza el artículo y crea una **metáfora visual creativa**
2. 🎨 Genera un prompt artístico (no tech genérico)
3. 🖼️ Crea la imagen directamente con Gemini
""")

st.markdown("---")

# ============================================================================
# INFORMACIÓN DEL ARTÍCULO
# ============================================================================

article = st.session_state["generated_article"]
keyword = st.session_state.get("generated_keyword", "Artículo técnico")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📄 Artículo")
    st.metric("🔑 Keyword", keyword[:50] + "..." if len(keyword) > 50 else keyword)
    st.metric("📊 Caracteres", f"{len(article):,}")
    
    with st.expander("👁️ Ver artículo", expanded=False):
        st.markdown(article[:2000] + "..." if len(article) > 2000 else article)

with col2:
    st.markdown("### ℹ️ Info")
    st.info("""
    **Gemini genera prompts creativos:**
    - Metáforas visuales (no chips genéricos)
    - Estilos artísticos variados
    - Paletas de color únicas
    
    El estilo se elige automáticamente basándose en el contenido.
    """)

# ============================================================================
# GENERACIÓN DE IMAGEN
# ============================================================================

st.markdown("---")
st.markdown("### 🎨 Generar Imagen")

# Estados
if "generated_image_data" not in st.session_state:
    st.session_state.generated_image_data = None
if "generated_image_prompt" not in st.session_state:
    st.session_state.generated_image_prompt = None

col1, col2 = st.columns([3, 1])

with col1:
    if st.button("🎨 **Generar Imagen con Gemini**", type="primary", use_container_width=True):
        with st.spinner("Generando imagen... (puede tardar 20-40 segundos)"):
            try:
                from google import genai
                from google.genai import types
                from PIL import Image
                genai_client = genai.Client(api_key=api_key)
                # PASO 1: Generar prompt creativo usando la función del core
                st.info("🧠 Analizando artículo y creando metáfora visual...")
                from longcontent_generator.core import generate_featured_image_prompt
                image_prompt = generate_featured_image_prompt(
                    article_text=article,
                    article_title=keyword
                )
                if not image_prompt:
                    st.error("No se pudo generar el prompt visual")
                    st.stop()
                st.session_state.generated_image_prompt = image_prompt
                st.success(f"✅ Prompt creativo generado")
                with st.expander("Ver prompt generado"):
                    st.code(image_prompt)
                # PASO 2: Generar imagen con Gemini 2.5 Flash Image
                st.info("🖼️ Generando imagen con Gemini 2.5 Flash Image...")
                response = genai_client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=[image_prompt],
                )
                image_data = None
                for part in response.parts:
                    if part.inline_data is not None:
                        image = part.as_image()
                        buf = BytesIO()
                        image.save(buf, format="PNG")
                        image_data = buf.getvalue()
                        break
                if image_data:
                    st.session_state.generated_image_data = image_data
                    st.success("✅ ¡Imagen generada correctamente!")
                else:
                    st.error("La respuesta no contiene imagen. Intenta de nuevo.")
            except ImportError as e:
                st.error(f"Error de importación: {e}")
                st.info("Asegúrate de tener instalado: `pip install google-generativeai Pillow`.")
            except Exception as e:
                error_msg = str(e)
                st.error(f"Error: {error_msg}")
                if "not found" in error_msg.lower() or "not supported" in error_msg.lower():
                    st.warning("""
                    **El modelo de imagen puede no estar disponible aún.**
                    
                    Alternativa: Copia el prompt generado y úsalo en:
                    - [ImageFX](https://aitestkitchen.withgoogle.com/tools/image-fx)
                    - [Ideogram](https://ideogram.ai/)
                    - [DALL-E](https://labs.openai.com/)
                    """)

with col2:
    st.markdown("**Modelo:**")
    st.code("gemini-2.0-flash-exp")
    
    st.markdown("**Costo:**")
    st.markdown("~$0.02 USD")

# ============================================================================
# MOSTRAR PROMPT SI EXISTE (fallback)
# ============================================================================

if st.session_state.generated_image_prompt and not st.session_state.generated_image_data:
    st.markdown("---")
    st.markdown("### 📝 Prompt Generado")
    st.markdown("Puedes usar este prompt en herramientas externas:")
    
    st.code(st.session_state.generated_image_prompt)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("[🎨 ImageFX](https://aitestkitchen.withgoogle.com/tools/image-fx)")
    with col2:
        st.markdown("[🖼️ Ideogram](https://ideogram.ai/)")
    with col3:
        st.markdown("[🤖 DALL-E](https://labs.openai.com/)")

# ============================================================================
# MOSTRAR IMAGEN GENERADA
# ============================================================================

if st.session_state.generated_image_data:
    st.markdown("---")
    st.markdown("### 🖼️ Imagen Generada")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.image(st.session_state.generated_image_data, caption="Imagen destacada generada con Gemini")
    
    with col2:
        st.markdown("**Prompt utilizado:**")
        st.text_area("Prompt", st.session_state.generated_image_prompt or "", height=150, disabled=True)
        
        # Descargar
        st.download_button(
            "💾 Descargar imagen",
            st.session_state.generated_image_data,
            file_name="featured_image.png",
            mime="image/png",
            use_container_width=True
        )
        
        # Guardar para publicación
        if st.button("✅ Usar esta imagen", type="primary", use_container_width=True):
            temp_path = str(Path(__file__).parent.parent / "temp_featured_image.png")
            with open(temp_path, "wb") as f:
                f.write(st.session_state.generated_image_data)
            st.session_state["featured_image_path"] = temp_path
            st.success("✅ Imagen guardada para publicación")
        
        # Regenerar
        if st.button("🔄 Regenerar imagen", use_container_width=True):
            st.session_state.generated_image_data = None
            st.session_state.generated_image_prompt = None
            st.rerun()

# ============================================================================
# SUBIR IMAGEN MANUAL
# ============================================================================

st.markdown("---")
st.markdown("### 📤 O sube tu propia imagen")

uploaded = st.file_uploader("Sube una imagen", type=["png", "jpg", "jpeg", "webp"])

if uploaded:
    st.image(uploaded, caption="Imagen subida", width=400)
    
    if st.button("✅ Usar imagen subida", type="primary"):
        temp_path = str(Path(__file__).parent.parent / "temp_featured_image.png")
        with open(temp_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.session_state["featured_image_path"] = temp_path
        st.success("✅ Imagen guardada para publicación")

# ============================================================================
# NAVEGACIÓN
# ============================================================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬅️ Volver a Linking", use_container_width=True):
        st.switch_page("pages/4_🔗_Linking.py")

with col2:
    if st.button("📱 Ir a Social", use_container_width=True):
        st.switch_page("pages/6_📱_Social.py")

with col3:
    if st.button("📤 Ir a Publicar", use_container_width=True):
        st.switch_page("pages/2_📤_Publicar.py")
