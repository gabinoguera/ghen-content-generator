# 📝 Changelog - Content Generator GHEN Digital

Todos los cambios notables en este proyecto se documentan aquí.

---

## [2.6.1] - 2024-12-04

### 🔧 Agregado - Normalización de Código y Links

#### Nueva Función: `normalize_code_blocks()`

Soluciona problemas comunes de formato en bloques de código generados por LLMs:

- **Bloques sin cerrar**: Detecta y añade ``` de cierre faltantes
- **Sin especificar lenguaje**: Detecta automáticamente Python, JavaScript, Bash, SQL, etc.
- **Backticks inconsistentes**: Normaliza uso de ` vs ```
- **Detección inteligente**: Patrones regex para identificar lenguajes (import, def, const, SELECT, etc.)

#### Nueva Función: `normalize_external_links()`

Integrada automáticamente en `auto_link_article()`:

- **Normaliza TODOS los links externos** (no solo los auto-insertados)
- **HTML links**: `<a href="...">` → añade `target="_blank" rel="nofollow noopener"`
- **Markdown links**: `[text](url)` → convierte a HTML con atributos
- **Preserva links internos** (ghendigital.com) sin nofollow

#### Pipeline Actualizado

- PASO 4: Ahora incluye `normalize_code_blocks()` automáticamente
- PASO 4.7: `auto_link_article()` ahora incluye `normalize_external_links()`

---

## [2.6.0] - 2024-12-04

### 🔗 Agregado - Auto-Linking Inteligente

Sistema de inserción automática de links internos y externos sin regenerar el artículo.

#### Nuevo Módulo: `linking.py`

- **`auto_link_article()`**: Función principal que ejecuta el proceso completo
- **`fetch_wordpress_posts()`**: Obtiene artículos existentes via WordPress API
- **`identify_external_links()`**: Gemini identifica herramientas/librerías → URLs oficiales
- **`identify_internal_links()`**: Gemini matchea con artículos existentes del blog
- **`inject_links_to_article()`**: Reemplaza texto por mismo texto con `<a>` tags
- **`count_links_in_article()`**: Cuenta links existentes en un artículo

#### Características Clave

- **NO regenera el artículo** - Solo hace reemplazos puntuales de texto
- **Verificación de integridad** - El texto solo puede crecer (por tags `<a>`)
- **Links externos**: `target="_blank" rel="nofollow noopener"`
- **Links internos**: Sin nofollow para pasar link juice
- **Configurable**: `MIN_EXTERNAL_LINKS`, `MIN_INTERNAL_LINKS`, etc.

#### Nueva Celda en Notebook

- **PASO 4.7**: Auto-Linking (después de QA, antes de Imagen)
- Muestra links antes/después
- Reporte de integridad con verificación de longitud

---

## [2.5.0] - 2024-11-21

### 🔧 Corregido - Sistema de QA Reimplementado

- **PROBLEMA**: El sistema QA anterior (`apply_qa_improvements_surgical`) enviaba el artículo completo a Gemini para "edición quirúrgica", pero Gemini reescribía todo el artículo y lo acortaba significativamente, fallando las validaciones de longitud.

- **SOLUCIÓN (Opción C)**: En lugar de editar el artículo existente, ahora regeneramos el artículo pasando el feedback del QA como instrucciones adicionales al generador original.

### 🆕 Nuevas Funciones

- **`generate_article_with_qa_feedback()`**: Nueva función en `core.py` que regenera el artículo incorporando el feedback del QA como instrucciones adicionales. Mantiene la longitud correcta (1500-2000 palabras) y la estructura genera correctamente desde el principio.

- **`_extract_qa_improvements()`**: Función auxiliar que extrae solo las mejoras específicas del reporte QA (sugerencias, recomendaciones, puntos a mejorar) para pasarlas al generador.

### 🔄 Modificaciones

- **`improve_article_based_on_qa()`**: Reimplementada para usar el nuevo enfoque de regeneración en lugar de edición quirúrgica. Ahora acepta parámetro opcional `keyword` para mejor contexto.

- **Celda QA del Notebook**: Actualizada con mensajes informativos sobre el nuevo enfoque y ahora pasa el `keyword` si está disponible.

### 💡 Ventajas del Nuevo Enfoque

1. El artículo mantiene la longitud correcta (1500-2000 palabras)
2. La estructura se genera correctamente desde el principio
3. El feedback del QA se incorpora de forma natural
4. No hay problemas de "reescritura" involuntaria que acorte el artículo
5. Se mantiene compatibilidad con `APPLY_QA_IMPROVEMENTS = True`

---

## [2.4.0] - 2024-11-20

### 📱 Agregado - Adaptadores para Redes Sociales

- **Nuevo módulo `social/`**: Sistema de adaptadores para generar posts en múltiples plataformas
- **Twitter**: Genera threads (1-5 tweets de max 280 caracteres cada uno)
- **LinkedIn**: Posts profesionales de 2000-2500 caracteres con CTA
- **Reddit**: Posts informativos de 1200-1500 caracteres para r/MachineLearning
- **Threads**: Posts concisos de max 500 caracteres para compartir casual
- **`generate_all_social_posts()`**: Genera para todas las plataformas de una vez
- **Nueva celda PASO 7**: Generación de posts sociales en el notebook
- **SOCIAL_SETUP.md**: Guía de configuración de APIs de redes sociales

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
