# Copilot Instructions

## Project Overview

This project is a Python-based long-form content generator powered by the Gemini API, featuring **LEO** - an AI content assistant with a defined personality and editorial intelligence.

The system supports **three content generation workflows**:
1. **Topic-Based Generation**: Define a broad topic → LEO suggests an optimal SEO keyword → Full pipeline
2. **Keyword-Based Generation**: Start with a specific keyword → Research and generate content
3. **Newsletter-Based Generation**: Analyze newsletter content → Extract insights → Generate related articles

The core workflow consists of:
1. **Keyword Research**: Scrapes Google SERPs for related keywords using `longcontent_generator.scraper`
2. **Content Aggregation**: Searches top articles via Google Custom Search API and scrapes content
3. **Content Generation**: Uses Gemini API with LEO's personality to generate articles
4. **QA & Refinement**: Quality assurance step to improve generated content
5. **Publishing**: Publishes to WordPress via REST API (`longcontent_generator.wordpress`)

## LEO's Personality

LEO (Lector Editorial Online) is the content creation assistant with a well-defined personality based on 5 pillars:
- **Objective & Analytical**: Provides data, metrics, and facts
- **Empathetic & Respectful**: Professional, human, never condescending
- **Visionary & Strategic**: Uses trend knowledge to project potential
- **Data Storyteller**: Transforms metrics into narratives (inspired by Prodigioso Volcán)
- **Knowledge Curator**: Filters noise, synthesizes information (inspired by Proyecto451 newsletter)

**Key Context Files**:
- `LEO/personalidad.md` - LEO's personality definition
- `.github/project-definitions.md` - Project context (Archivo Final)
- `.github/perfilado_cliente.md` - Target audience profile

These files are **automatically loaded** and injected into every Gemini API call to ensure consistent tone and relevance.

## Key Modules

-   **`config.py`**: Manages configurations (API settings, search params, output paths). Loads API keys from `.env`.
-   **`core.py`**: Core application logic. Contains functions for Google/Gemini API interaction and content generation orchestration.
    - **NEW**: `load_leo_context()` - Loads personality, project, and audience files
    - **NEW**: `build_system_prompt()` - Constructs Gemini system prompt with LEO's context
    - **NEW**: `suggest_keyword_from_topic()` - Generates SEO keyword from broad topic
    - **NEW**: `extract_and_summarize_url()` - Analyzes newsletter/URL content
    - **NEW**: `generate_article_with_context()` - Generates articles with LEO's personality
-   **`scraper.py`**: Selenium-based scraper for Google SERP keyword research.
-   **`utils.py`**: Helper functions for file I/O, previews, and cleanup.
-   **`wordpress.py`**: WordPress REST API integration for publishing.

## Developer Workflow

### Environment Setup

1.  **Dependencies**: Python project. Key dependencies: `google-generativeai`, `pandas`, `requests`, `beautifulsoup4`, `newspaper3k`, `selenium`, `python-dotenv`.
    - **Action needed**: Create and maintain a `requirements.txt` file.
2.  **Environment Variables**: Create `.env` file in root with:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    API_KEY="YOUR_GOOGLE_CUSTOM_SEARCH_API_KEY"
    API_CUSTOM_SEARCH_ID="YOUR_GOOGLE_CUSTOM_SEARCH_ID"
    WORDPRESS_LOGIN_AF="YOUR_WORDPRESS_USERNAME"
    WORDPRESS_PASSWORD_AF="YOUR_WORDPRESS_APP_PASSWORD"
    ```
3.  **Virtual Environment**: Use `.venv` for dependencies
    ```bash
    source .venv/bin/activate  # macOS/Linux
    ```

### Running the Pipeline

**Primary Interface**: Jupyter Notebook `Pipeline_LEO_Enhanced.ipynb`

**Three Generation Methods**:

1. **Topic Method** (`metodo_seleccionado = "topico"`):
   - Define broad topic → LEO suggests keyword → Full pipeline
   
2. **Keyword Method** (`metodo_seleccionado = "keyword"`):
   - Define specific keyword → Research articles → Generate content
   
3. **Newsletter Method** (`metodo_seleccionado = "newsletter"`):
   - Paste newsletter URL → Extract insights → Suggest topics → Generate

**Alternative**: Use functions directly from `core.py` in Python scripts.

### Testing

Run automated tests:
```bash
source .venv/bin/activate
python test_leo_enhanced.py
```

All tests should pass. This verifies:
- Context loading (personality, project, audience)
- System prompt construction
- Keyword suggestion from topics
- Article generation with LEO's personality

### Modifying the Pipeline

-   **Add new functions**: Create in appropriate module (`core.py`, `scraper.py`, etc.)
-   **Update personality**: Edit `LEO/personalidad.md` - changes apply immediately
-   **Add context**: Update `.github/project-definitions.md` or `.github/perfilado_cliente.md`
-   **New configurations**: Add to `config.py` and load from `.env` if sensitive

### Conventions

-   **DataFrames**: pandas DataFrames manage URLs and keywords lists
-   **Markdown Output**: Generated content stored in `.md` files before publishing
-   **Environment Variables**: All secrets/credentials in `.env`, never in code
-   **Context Injection**: Every Gemini call includes LEO's full context (personality + project + audience)
-   **Entry Point**: `Pipeline_LEO_Enhanced.ipynb` for manual workflows
-   **Modular Design**: Core logic in modules, notebooks orchestrate workflows

## Important Files

### Configuration
- `.env` - API keys and credentials (DO NOT commit)
- `longcontent_generator/config.py` - Application configuration

### LEO Context (Auto-loaded)
- `LEO/personalidad.md` - LEO's 5-pillar personality
- `.github/project-definitions.md` - Archivo Final project context
- `.github/perfilado_cliente.md` - Target audience (writers/authors)

### Workflows
- `Pipeline_LEO_Enhanced.ipynb` - **Main workflow** (3 methods)
- `Pipeline_Control_Manual.ipynb` - Original pipeline (reference)

### Testing & Documentation
- `test_leo_enhanced.py` - Automated test suite
- `.github/IMPLEMENTATION_SUMMARY.md` - Detailed implementation guide
- `.github/copilot-instructions.md` - This file
