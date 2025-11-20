# 🚀 Content Generator - Sistema GHEN Digital

Sistema inteligente de generación de contenido long-form técnico con personalidad definida para **GHEN Digital**.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-Private-red)

---

## 📋 Descripción

Content Generator es un sistema modular de generación de contenido SEO-optimizado que utiliza **Google Gemini AI** para crear artículos técnicos de alta calidad dirigidos a desarrolladores, CTOs, consultores de IA y profesionales tech.

### ✨ Características Principales

- **🤖 Personalidad Técnica GHEN**: Contenido práctico basado en experiencia real (código, arquitecturas, proyectos)
- **🎯 Tres Métodos de Generación**:
  - Tópico → Keyword → Artículo
  - Keyword → Investigación → Artículo  
  - Newsletter → Análisis → Artículo
- **🔍 Research Automático**: Scraping de Google SERP y análisis de competencia
- **📊 Análisis SEO**: Evaluación automática con Gemini
- **✅ Quality Assurance**: Sistema de mejora post-QA
- **📝 WordPress Integration**: Publicación automática en ghendigital.com

---

## 🏗️ Arquitectura

```
content-generator/
├── .github/                      # Documentación y configuración
│   └── copilot-instructions.md  # Guía para AI coding agents
│
├── GHEN/                        # Personalidad de contenido GHEN
│   └── personalidad.md          # Definición de 5 pilares técnicos
│
├── longcontent_generator/       # Módulo principal
│   ├── __init__.py
│   ├── config.py               # Configuración
│   ├── core.py                 # Funciones principales (17 funciones)
│   ├── scraper.py              # Google SERP scraper
│   ├── utils.py                # Utilidades
│   └── wordpress.py            # Integración WordPress
│
├── outputs/                     # Directorio de archivos generados
│   ├── README.md               # Documentación de outputs
│   └── .gitkeep
│
├── Pipeline_GHEN_Enhanced.ipynb # 🔥 Workflow principal
├── CHANGELOG.md                # Historial de cambios
└── README.md                   # Este archivo
```

---

## 🚀 Inicio Rápido

### 1️⃣ Requisitos

- Python 3.10+
- Google Gemini API Key
- Google Custom Search API Key (opcional)
- Virtual environment (recomendado)

### 2️⃣ Instalación

```bash
# Clonar repositorio
git clone https://github.com/ArchivoFinal/content-generator.git
cd content-generator

# Crear virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# 🆕 Instalar dependencias de Gmail API (opcional)
./install_gmail_deps.sh
```

### 3️⃣ Configuración

Crear archivo `.env` en la raíz:

```env
GEMINI_API_KEY="tu_api_key_de_gemini"
API_KEY="tu_google_custom_search_api_key"
API_CUSTOM_SEARCH_ID="tu_search_engine_id"

# Opcional: Para publicación WordPress
WORDPRESS_LOGIN_GHEN="tu_usuario"
WORDPRESS_PASSWORD_GHEN="tu_app_password"

# 🆕 Opcional: Para generación de imágenes con Vertex AI Imagen 3
PROJECT_ID="tu-proyecto-gcp"
LOCATION="us-central1"
SERVICE_ACCOUNT_KEY="ruta-a-service-account.json"
```

**🆕 Gmail API (Opcional - Para Método 3: Newsletter)**

Si quieres leer newsletters desde Gmail:

1. Sigue la guía completa: [`GMAIL_SETUP.md`](GMAIL_SETUP.md)
2. Descarga `credentials.json` desde Google Cloud Console
3. Coloca `credentials.json` en la raíz del proyecto
4. Primera ejecución: autoriza en navegador → genera `token.pickle`

**🎨 Vertex AI Imagen 3 (Opcional - Para generación de imágenes destacadas)**

Si quieres generar imágenes destacadas automáticamente:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Habilita **Vertex AI API** en tu proyecto
3. Crea una **Service Account** con rol "Vertex AI User"
4. Descarga la clave JSON y guárdala en la raíz del proyecto
5. Agrega las variables de entorno en `.env` (ver arriba)
6. Costo: ~$0.04 USD por imagen generada

### 4️⃣ Uso

**Opción 1: Jupyter Notebook (Recomendado)**

```bash
jupyter notebook Pipeline_GHEN_Enhanced.ipynb
```

1. Selecciona tu método en la celda de configuración:
   - `metodo_seleccionado = "topico"` - Tema amplio → keyword sugerida
   - `metodo_seleccionado = "keyword"` - Keyword específica → artículo técnico
   - `metodo_seleccionado = "newsletter"` - Newsletter tech → análisis de tendencias

2. Ejecuta las celdas secuencialmente

**Opción 2: Python Scripts**

```python
from longcontent_generator import core

# Cargar contexto de GHEN
leo_context = core.load_leo_context()

# Método 1: Desde tópico técnico
keyword = core.suggest_keyword_from_topic(
    "Arquitectura de agentes con LangGraph", 
    leo_context
)

# Método 3: Desde newsletter tech
analysis = core.extract_and_summarize_url(
    "https://newsletter-tech-url.com",
    leo_context
)

# Generar artículo técnico
article = core.generate_article_with_context(
    keyword="deploying llms to production",
    context_sources=["contexto 1", "contexto 2"],
    leo_context=leo_context
)
```

---

## 🎯 Tres Métodos de Generación

### Método 1: Tópico → Keyword → Artículo

**Caso de uso**: Tienes un tema técnico amplio y necesitas una keyword SEO óptima.

```python
topico = "Implementación de RAG con vector databases"
keyword = core.suggest_keyword_from_topic(topico, leo_context)
# → "ChromaDB vs Pinecone for production RAG systems"
```

### Método 2: Keyword → Investigación → Artículo

**Caso de uso**: Ya tienes una keyword técnica específica y quieres generar contenido.

```python
keyword = "mlops best practices for llm deployment"
# → Scraping de keywords relacionadas
# → Búsqueda de artículos competencia
# → Análisis SEO
# → Generación de artículo con código y arquitecturas
```

### Método 3: Newsletter → Análisis → Artículo

**Caso de uso**: Quieres generar contenido basado en una newsletter técnica o release notes.

**Opción A: Gmail API** (🆕 Recomendado para newsletters privados)

```python
# Lee newsletters directamente desde tu Gmail
gmail_url = "https://mail.google.com/mail/u/0/#inbox/1849085179733622850"
analysis = core.extract_newsletter_from_gmail(gmail_url, ghen_context)
# → Extracción OAuth desde inbox
# → Análisis con Gemini
# → Artículo "Actualidad y Tendencias" en IA/desarrollo
```

**Opción B: URL Pública**

```python
url = "https://ai-newsletter-url.com"
analysis = core.extract_and_summarize_url(url, ghen_context)
# → Resumen ejecutivo de tendencias
# → Puntos clave técnicos
# → Artículo "Actualidad y Tendencias" en IA/desarrollo
```

---

## 🤖 Personalidad GHEN

El contenido se genera con una personalidad técnica definida basada en **5 pilares**:

1. **Técnico y Práctico** - Código real, arquitecturas probadas, ejemplos ejecutables
2. **Pedagógico y Claro** - Conceptos complejos explicados sin oversimplificar
3. **Experiencial** - Basado en proyectos reales (hackathons, consultoría, producción)
4. **Orientado a Resultados** - Enfoque en ROI, métricas, decisiones arquitectónicas
5. **Actualizado** - Cutting-edge: GenAI, LLMs, LangChain, MLOps, cloud-native

**Contexto inyectado en cada generación**:
- `GHEN/personalidad.md` (Definición completa de los 5 pilares)

**Audiencia objetivo**: Desarrolladores, CTOs, consultores de IA, arquitectos cloud, ingenieros ML

**Tono**: Consultor técnico profesional - primera persona en experiencias ("En mi implementación de..."), instruccional en tutoriales. Equilibra teoría con práctica.

**Temas core**:
- **IA/GenAI**: LLMs, RAG, agents, prompt engineering, fine-tuning
- **MLOps/LLMOps**: Deployment, evaluation, monitoring, CI/CD para ML
- **CODE**: Python (FastAPI), APIs, microservicios, arquitecturas cloud
- **Casos Prácticos**: Hackathons, microservicios en producción, chatbots, automatización

---

## 📊 Funciones Principales

### Core Functions (`longcontent_generator/core.py`)

#### Context & Personality
- `load_leo_context()` - Carga personalidad, proyecto y audiencia
- `build_system_prompt(leo_context)` - Construye prompt con contexto LEO

#### Content Generation
- `suggest_keyword_from_topic(topic, leo_context)` - Genera keyword desde tópico
- `extract_and_summarize_url(url, leo_context)` - Analiza newsletters/artículos
- `generate_article_with_context(keyword, sources, leo_context)` - Genera artículos con LEO
- `generate_article_from_outline(outline, plan, keywords)` - Genera desde outline

#### Research & Analysis
- `google_custom_search(query, country, max_results)` - Búsqueda Google
- `scrape_article(url)` - Extrae contenido de URL
- `analyze_articles_batch(df)` - Análisis SEO batch con Gemini
- `analyze_combined_context(df, keywords, query)` - Análisis competencia

#### Quality Assurance
- `qa_article_coverage(article, keywords, query)` - Análisis QA de cobertura
- `improve_article_based_on_qa(article, qa_report)` - Mejora post-QA
- `suggest_related_articles(qa_report, keywords, query)` - Sugerencias

---

## 🧪 Testing

### Suite Completa

```bash
source .venv/bin/activate
python test_leo_enhanced.py
```

**Tests incluidos**:
- ✅ Carga de contexto LEO (3 archivos)
- ✅ Construcción de system prompt
- ✅ Sugerencia de keyword desde tópico
- ✅ Generación de artículo con personalidad LEO

### Test de Mejora QA

```bash
python test_qa_improvement.py
```

---

## 📁 Outputs

Todos los archivos generados se guardan en `outputs/`:

### Artículos
- `articulo_completo.md` - Artículo final
- `articulo_leo_generado.md` - Artículo con personalidad LEO
- `articulo_mejorado_qa.md` - Versión mejorada post-QA

### Análisis
- `esquema_articulo.md` - Outline del artículo
- `qa_report.md` - Reporte de calidad
- `articulos_sugeridos.md` - Sugerencias relacionadas

### Research (CSV)
- `keywords_scraped.csv` - Keywords de SERP
- `search_results.csv` - Resultados de búsqueda
- `scraped_articles.csv` - Artículos competencia
- `SEO_Analysis_Results.csv` - Análisis SEO

---

## ⚙️ Configuración

Edita `longcontent_generator/config.py`:

```python
CONFIG = {
    # Gemini
    "gemini_model": "gemini-2.5-flash",
    "temperature": 0.7,
    "max_output_tokens": 12000,
    
    # Search
    "default_country": "ES",
    "max_search_results": 10,
    
    # Outputs
    "output_dir": "outputs",
    "output_language": "spanish",
}
```

---

## 🔄 Workflow Completo (Método 2)

```python
# 1. Configuración
from longcontent_generator import core, scraper
leo_context = core.load_leo_context()

# 2. Research de Keywords
kw_scraper = scraper.GoogleKeywordScraper(
    keyword="publicar libro",
    language="es",
    country="es"
)
keywords_df = kw_scraper.run()

# 3. Búsqueda de Artículos
search_results = core.google_custom_search("publicar libro", max_results=10)

# 4. Scraping de Contenido
scraped_df = core.scrape_articles_batch(search_results)

# 5. Análisis SEO
analyzed_df = core.analyze_articles_batch(scraped_df)

# 6. Plan de Contenido
plan = core.create_intelligent_content_plan(
    combined_analysis,
    "publicar libro",
    keywords_context
)

# 7. Outline
outline = core.generate_article_outline(
    "publicar libro",
    search_results,
    keywords_context,
    plan
)

# 8. Generar Artículo
article = core.generate_article_from_outline(outline, plan, keywords_context)

# 9. QA
qa_report = core.qa_article_coverage(article, keywords_context, "publicar libro")

# 10. Mejora
final_article = core.improve_article_based_on_qa(article, qa_report)
```

---

## 📚 Documentación Adicional

- [CHANGELOG.md](CHANGELOG.md) - Historial de versiones
- [.github/IMPLEMENTATION_SUMMARY.md](.github/IMPLEMENTATION_SUMMARY.md) - Guía de implementación
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Para AI agents
- [outputs/README.md](outputs/README.md) - Documentación de outputs

---

## 🐛 Troubleshooting

### Error: "GEMINI_API_KEY no encontrada"

Solución: Verifica que el archivo `.env` existe y contiene la API key.

### Error al scrapear artículos

Solución: Algunos sitios bloquean scraping. El sistema usa `newspaper3k` con fallback a BeautifulSoup.

### Artículos sin personalidad GHEN

Solución: Verifica que el archivo de contexto exista:
- `GHEN/personalidad.md`

### Gmail API: "credentials.json not found"

Solución: 
1. Sigue la guía completa: `GMAIL_SETUP.md`
2. Descarga `credentials.json` desde Google Cloud Console
3. Coloca en raíz del proyecto

### Gmail API: "This app isn't verified"

Solución: Normal para apps en desarrollo. Clic en "Avanzado" → "Ir a [nombre app] (no seguro)"

---

## 📚 Documentación Adicional

- **[GMAIL_SETUP.md](GMAIL_SETUP.md)** - Configuración paso a paso de Gmail API
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Resumen de mejoras implementadas
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - Guía completa para AI coding agents
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de cambios del proyecto

---

## 🤝 Contribuir

Este es un proyecto privado de **GHEN Digital**. Para contribuciones:

1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'feat: Nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📝 Licencia

Proyecto privado de **GHEN Digital** (Gabriel Noguera). Todos los derechos reservados.

---

## 🆕 Novedades v2.1.0

- ✅ **Gmail API Integration**: Lee newsletters directamente desde Gmail inbox
- ✅ **Auto-Referencias**: Extracción automática de URLs y generación de sección de fuentes
- ✅ **3 Formatos de URL Gmail**: Soporta #inbox/, permmsgid=, y message ID directo
- ✅ **OAuth 2.0 Persistence**: Token guardado en `token.pickle` para reuso
- ✅ **Filtros de Newsletter**: Búsqueda por remitente, asunto, fecha
- ✅ **Documentación Expandida**: GMAIL_SETUP.md con 5 pasos de configuración

---

## 👥 Autores

- **Archivo Final Team**
- **LEO** - Inteligencia Editorial

---

## 🔗 Enlaces

- [Archivo Final](https://archivofinal.com) - Plataforma principal
- [Documentación Completa](.github/IMPLEMENTATION_SUMMARY.md)

---

**Versión 2.0.0** - Noviembre 2025
