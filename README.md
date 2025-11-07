# 🚀 Content Generator - Sistema LEO

Sistema inteligente de generación de contenido long-form con personalidad LEO (Lector Editorial Online) para **Archivo Final**.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-Private-red)

---

## 📋 Descripción

Content Generator es un sistema modular de generación de contenido SEO-optimizado que utiliza **Google Gemini AI** con una personalidad editorial definida (LEO). Ofrece tres flujos de trabajo diferentes para crear artículos de alta calidad dirigidos a escritores y autores.

### ✨ Características Principales

- **🤖 Personalidad LEO**: 5 pilares de personalidad editorial consistente
- **🎯 Tres Métodos de Generación**:
  - Tópico → Keyword → Artículo
  - Keyword → Investigación → Artículo  
  - Newsletter → Análisis → Artículo
- **🔍 Research Automático**: Scraping de Google SERP y análisis de competencia
- **📊 Análisis SEO**: Evaluación automática con Gemini
- **✅ Quality Assurance**: Sistema de mejora post-QA
- **📝 WordPress Integration**: Publicación automática

---

## 🏗️ Arquitectura

```
content-generator/
├── .github/                      # Documentación y configuración
│   ├── copilot-instructions.md  # Guía para AI coding agents
│   ├── IMPLEMENTATION_SUMMARY.md # Guía de implementación
│   ├── project-definitions.md    # Contexto Archivo Final
│   └── perfilado_cliente.md     # Perfil audiencia
│
├── LEO/                         # Personalidad de LEO
│   └── personalidad.md          # Definición de 5 pilares
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
├── bk/                         # Backup de versiones anteriores
│
├── Pipeline_LEO_Enhanced.ipynb # 🔥 Workflow principal
├── test_leo_enhanced.py        # Suite de tests
├── test_qa_improvement.py      # Test de mejora QA
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
```

### 3️⃣ Configuración

Crear archivo `.env` en la raíz:

```env
GEMINI_API_KEY="tu_api_key_de_gemini"
API_KEY="tu_google_custom_search_api_key"
API_CUSTOM_SEARCH_ID="tu_search_engine_id"

# Opcional: Para publicación WordPress
WORDPRESS_LOGIN_AF="tu_usuario"
WORDPRESS_PASSWORD_AF="tu_app_password"
```

### 4️⃣ Uso

**Opción 1: Jupyter Notebook (Recomendado)**

```bash
jupyter notebook Pipeline_LEO_Enhanced.ipynb
```

1. Selecciona tu método en la celda de configuración:
   - `metodo_seleccionado = "topico"`
   - `metodo_seleccionado = "keyword"`
   - `metodo_seleccionado = "newsletter"`

2. Ejecuta las celdas secuencialmente

**Opción 2: Python Scripts**

```python
from longcontent_generator import core

# Cargar contexto de LEO
leo_context = core.load_leo_context()

# Método 1: Desde tópico
keyword = core.suggest_keyword_from_topic(
    "IA en la escritura creativa", 
    leo_context
)

# Método 3: Desde newsletter
analysis = core.extract_and_summarize_url(
    "https://newsletter-url.com",
    leo_context
)

# Generar artículo
article = core.generate_article_with_context(
    keyword="keyword principal",
    context_sources=["contexto 1", "contexto 2"],
    leo_context=leo_context
)
```

---

## 🎯 Tres Métodos de Generación

### Método 1: Tópico → Keyword → Artículo

**Caso de uso**: Tienes un tema amplio y necesitas una keyword SEO óptima.

```python
topico = "Inteligencia Artificial en la industria editorial"
keyword = core.suggest_keyword_from_topic(topico, leo_context)
# → "Inteligencia artificial en la escritura creativa"
```

### Método 2: Keyword → Investigación → Artículo

**Caso de uso**: Ya tienes una keyword específica y quieres generar contenido.

```python
keyword = "cómo publicar tu primer libro"
# → Scraping de keywords relacionadas
# → Búsqueda de artículos competencia
# → Análisis SEO
# → Generación de artículo
```

### Método 3: Newsletter → Análisis → Artículo

**Caso de uso**: Quieres generar contenido basado en una newsletter o artículo.

```python
url = "https://newsletter-url.com"
analysis = core.extract_and_summarize_url(url, leo_context)
# → Resumen ejecutivo
# → Puntos clave
# → Temas sugeridos para artículos
```

---

## 🤖 Personalidad LEO

LEO (Lector Editorial Online) es la inteligencia editorial que genera todo el contenido. Su personalidad se basa en **5 pilares**:

1. **Objetivo y Analítico** - Datos, métricas y hechos concretos
2. **Empático y Respetuoso** - Valida el esfuerzo creativo
3. **Visionario y Estratégico** - Proyecta el potencial de las obras
4. **Narrador de Datos** - Transforma métricas en historias (inspirado en Prodigioso Volcán)
5. **Curador de Conocimiento** - Filtra ruido, sintetiza información (inspirado en Proyecto451)

**Contexto inyectado en cada generación**:
- `LEO/personalidad.md` (4,731 caracteres)
- `.github/project-definitions.md` (4,598 caracteres)
- `.github/perfilado_cliente.md` (2,491 caracteres)

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

### Artículos sin personalidad LEO

Solución: Verifica que los archivos de contexto existan:
- `LEO/personalidad.md`
- `.github/project-definitions.md`
- `.github/perfilado_cliente.md`

---

## 🤝 Contribuir

Este es un proyecto privado de **Archivo Final**. Para contribuciones:

1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'feat: Nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📝 Licencia

Proyecto privado de **Archivo Final**. Todos los derechos reservados.

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
