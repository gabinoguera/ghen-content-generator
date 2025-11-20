# 📝 Changelog - Content Generator GHEN Digital

Todos los cambios notables en este proyecto se documentan aquí.

---

## [2.3.0] - 2024-11-20

### 🎭 Agregado - Sistema Híbrido de Personalidad

- **Dos niveles de personalidad**: Base (neutral) y Full (experiencias personales)
- **`personalidad_base.md`**: Voz técnica neutral sin proyectos personales
  * Stack-agnostic con múltiples opciones tecnológicas
  * Basado en evidencia pública (benchmarks, papers, docs oficiales)
  * Sin primera persona ni referencias a proyectos privados
  * Ideal para: actualidad, comparativas, explicaciones técnicas
- **`personalidad_completa.md`**: Voz con experiencia personal
  * Referencias a proyectos específicos (Cofares, consultoría)
  * Stack tecnológico definido (FastAPI, LangChain, Gemini)
  * Primera persona en retrospectivas
  * Ideal para: tutoriales, case studies, lecciones aprendidas
- **`load_ghen_context(level)`**: Parámetro `level="base|full"` para seleccionar personalidad
- **README_PERSONALIDAD.md**: Guía completa del sistema híbrido

### 🔧 Mejorado

- Notebook actualizado con selector de nivel de personalidad
- Mensajes de consola muestran nivel de personalidad cargado
- Guía contextual en notebook según nivel seleccionado

### 📚 Documentación

- Guía detallada de cuándo usar cada nivel
- Ejemplos de output para ambos niveles
- Tabla de decisión: tipo de contenido → nivel recomendado

---

## [2.2.0] - 2024-11-19

### 🎨 Agregado - Generación de Imágenes Destacadas

- **Nuevo módulo `imagen.py`**: Integración con Vertex AI Imagen 3 para generación automática de imágenes destacadas
- **`generate_image_from_prompt()`**: Genera imágenes en formato 16:9 optimizadas para WordPress
- **`optimize_image_for_wordpress()`**: Redimensiona y comprime imágenes (max 1920px, quality 85)
- **`generate_featured_image_prompt()`** en `core.py`: Usa Gemini para crear prompts optimizados basados en contenido del artículo
- **Soporte en WordPress**: `upload_featured_image_to_wordpress()` sube imagen y `publish_article_from_markdown_cleaned()` ahora acepta parámetro `featured_image_path`
- **Nueva celda en notebook**: Paso 7 opcional para generar imagen destacada antes de publicar
- **Script de prueba**: `test_imagen.sh` para validar configuración de Vertex AI

### 🔧 Mejorado

- `publish_article_from_markdown_cleaned()` retorna dict con detalles completos (`post_id`, `post_url`, `featured_media_id`)
- Variables de WordPress actualizadas a `WORDPRESS_LOGIN_GHEN` y `WORDPRESS_PASSWORD_GHEN`
- Notebook actualizado con verificación de imagen destacada antes de publicar

### 📚 Documentación

- README actualizado con sección de configuración de Vertex AI Imagen 3
- Instrucciones de setup para Service Account en Google Cloud
- Costos documentados: ~$0.04 USD por imagen generada

---

## [2.1.0] - 2024-11-18

### 🆕 Agregado - Integración con Gmail API

- **Nuevo módulo `gmail.py`**: Autenticación OAuth 2.0 y extracción de newsletters
- **`extract_newsletter_from_gmail()`**: Lee newsletters directamente desde Gmail usando message ID o URL
- **`list_gmail_newsletters()`**: Lista newsletters con filtros (sender, subject, fecha)
- **Conversión de IDs**: Soporta URLs de Gmail en 3 formatos (decimal → hex para API)
- **Método Newsletter mejorado**: Opción de usar Gmail API o URL pública

### 🔧 Mejorado

- **`clean_article_metatext()`**: Elimina meta-comentarios del modelo al inicio del artículo
- **`add_source_links_to_article()`**: Filtrado mejorado de URLs de tracking (resend-links, click.*, track.*)
- **Prompts optimizados**: Adaptados para audiencia GHEN (desarrolladores, arquitectos, CTOs)
- **Regeneración de virtual environment**: Fix para error de dependencias después de rename de directorio

### 📚 Documentación

- `GMAIL_SETUP.md`: Guía completa para configurar OAuth 2.0 Desktop App
- Instrucciones de setup en copilot-instructions.md

---

## [2.0.0] - 2024-11-15

### 🚀 Lanzamiento Inicial - GHEN Digital

- **Pipeline completo**: Topic → Keyword → Research → Article → QA → WordPress
- **3 métodos de generación**: Tópico, Keyword, Newsletter
- **Sistema de personalidad**: `GHEN/personalidad.md` con 5 pilares técnicos
- **Análisis SEO con Gemini**: Evaluación automática de competencia
- **Scraping de SERP**: Google Keywords + artículos de competidores
- **Quality Assurance**: Sistema de evaluación y mejora post-QA
- **WordPress Integration**: Publicación automática con limpieza de formato
- **Módulo modular**: `longcontent_generator/` con 17 funciones core
- **Notebook workflow**: `Pipeline_GHEN_Enhanced.ipynb` con celdas secuenciales

---

## Formato

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).
