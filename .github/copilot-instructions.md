# Content Generator - AI Coding Agent Instructions

## Project Overview

**Content Generator** is an AI-powered, SEO-optimized long-form content generation system for **GHEN Digital** (Gabriel Noguera's personal brand focused on AI, development, and tech consulting). It uses **Google Gemini 2.5 Flash** with a custom technical personality to create articles targeted at developers, CTOs, AI consultants, and tech professionals.

### Core Architecture

```
Pipeline Flow: Input → Research → Analysis → Content Plan → Article Generation → QA → Publishing
```

- **3 Generation Methods**: Topic→Keyword→Article, Keyword→Research→Article, Newsletter→Analysis→Article
- **Primary Interface**: `Pipeline_GHEN_Enhanced.ipynb` (Jupyter notebook with 3 workflow branches)
- **Core Module**: `longcontent_generator/` (config, core, scraper, utils, wordpress)
- **Personality System**: GHEN context injected into every generation (`GHEN/personalidad.md` - defines technical consultant personality)
- **Content Focus**: AI/GenAI, MLOps, LLMOps, Python development, GitHub Copilot, cloud architecture, software engineering best practices

## Critical Developer Knowledge

### 1. GHEN Personality Context System

**Every content generation MUST load GHEN context first:**

```python
leo_context = core.load_leo_context()  # Loads personality file: GHEN/personalidad.md
article = core.generate_article_with_context(keyword, context_sources, leo_context)
```

**GHEN Content Personality** (defined in `GHEN/personalidad.md`):
1. **Técnico y Práctico** - Hands-on code examples, real implementations, battle-tested patterns
2. **Pedagógico y Claro** - Explains complex concepts accessibly without oversimplifying
3. **Experiencial** - Based on real-world projects (hackathons, client work, production systems)
4. **Orientado a Resultados** - Focus on ROI, business impact, measurable outcomes
5. **Actualizado** - Cutting-edge tech (GenAI, LLMs, cloud-native, modern stacks)

**Target Audience**: Developers building AI solutions, CTOs evaluating tech, consultants implementing GenAI, engineers learning MLOps/LLMOps.

**Tone**: Professional technical consultant - first-person when sharing experiences ("En mi experiencia con..."), instructional when teaching concepts. Balances theory with practical implementation.

### 2. The Three Workflow Methods

**Method 1: Topic-Based** (`metodo_seleccionado = "topico"`)
```python
keyword = core.suggest_keyword_from_topic(topic, leo_context)  # AI suggests SEO keyword
# Example: "Arquitectura de agentes IA" → "ReAct agents with LangGraph"
# Then: scrape related keywords → search articles → analyze → generate
```

**Method 2: Keyword-Based** (`metodo_seleccionado = "keyword"`)
- Direct keyword → scrape Google SERP for related keywords
- Search competitor articles → scrape content → SEO analysis
- Example keywords: "MLOps best practices", "deploying LLMs production", "vector databases comparison"
- Generate technical article with code examples and architecture diagrams

**Method 3: Newsletter-Based** (`metodo_seleccionado = "newsletter"`)
```python
# Option A: Gmail API (recommended for private newsletters)
analysis = core.extract_newsletter_from_gmail(gmail_url, leo_context)  # Reads from Gmail inbox
# Option B: Public URL
analysis = core.extract_and_summarize_url(url, leo_context)  # Extracts summary & key topics

# Analyzes tech newsletters, release notes, or technical blog posts
# Generates "Actualidad y Tendencias" article covering latest AI/dev trends
```

### 3. Key Functions in `core.py` (20 total)

**Research & Scraping:**
- `google_custom_search(query, country, max_results)` - Uses Google Custom Search API
- `scrape_article(url)` - Dual strategy: BeautifulSoup (primary) + newspaper3k (fallback)
- `scrape_articles_batch(df)` - Batch scraping with 1s delay between requests

**Gmail Integration (🆕):**
- `extract_newsletter_from_gmail(gmail_url, leo_context)` - Extracts newsletter content from Gmail via OAuth
- `list_gmail_newsletters(sender_filter, max_results)` - Lists available newsletters with filters
- **Requires**: Google Cloud OAuth credentials in `credentials.json` (see Gmail Setup section below)

**SEO Analysis:**
- `analyze_seo_with_gemini(text)` - Extracts keywords, semantic clusters, user intent, gaps
- `analyze_articles_batch(df)` - Batch analysis → saves to `outputs/SEO_Analysis_Results.csv`
- `analyze_combined_context(df, related_keywords_context, main_query)` - Combines competition + keywords

**Article Generation:**
- `generate_article_outline()` - Creates structured outline with H2/H3
- `parse_outline_to_sections()` - Parses markdown outline to dict list
- `generate_section_content_with_context()` - Generates each section individually
- `generate_article_from_outline()` - Assembles full article from sections
- `generate_article_with_context()` - **Main generation function** with GHEN context injection
- `add_source_links_to_article(article_text, context_sources)` - **🆕** Extracts URLs and adds references section

**Quality Assurance:**
- `qa_article_coverage()` - Evaluates keyword coverage, coherence, depth → `outputs/qa_report.md`
- `improve_article_based_on_qa()` - Post-QA improvement iteration
- `suggest_related_articles()` - Suggests 3 follow-up article topics

### 4. Configuration & Environment

**Environment Variables** (`.env` required):
```bash
GEMINI_API_KEY="your_gemini_key"           # Required for all operations
API_KEY="google_custom_search_key"         # Required for keyword research
API_CUSTOM_SEARCH_ID="search_engine_id"    # Required for keyword research
WORDPRESS_LOGIN_AF="wp_username"           # Optional: for publishing
WORDPRESS_PASSWORD_AF="wp_app_password"    # Optional: for publishing
```

**Config in `config.py`:**
- Model: `gemini-2.5-flash`
- Temperature: 0.7 (balanced creativity/consistency)
- Max tokens: 12,000
- Output dir: `outputs/`
- API delay: 2 seconds (rate limiting)

### 5. Gmail API Setup (for Newsletter Integration)

**Required Setup Steps:**

1. **Create Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing one
   - Enable Gmail API: APIs & Services → Library → Gmail API → Enable

2. **Configure OAuth Consent Screen:**
   - APIs & Services → OAuth consent screen
   - User Type: External (for personal use)
   - Scopes: Add `https://www.googleapis.com/auth/gmail.readonly`
   - Test users: Add your Gmail address

3. **Create OAuth Credentials:**
   - APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Application type: Desktop app
   - Download JSON → Save as `credentials.json` in project root

4. **First-Time Authentication:**
   ```python
   # On first run, Gmail module opens browser for OAuth consent
   # Authorize access → token.pickle saved for future use
   newsletters = core.list_gmail_newsletters(max_results=10)
   ```

**Gmail Module** (`longcontent_generator/gmail.py`):
- `authenticate_gmail()` - OAuth 2.0 flow, saves `token.pickle` for reuse
- `get_newsletter_by_message_id()` - Extracts text + HTML content
- `list_newsletters()` - Search with filters (sender, subject, date)
- `extract_message_id_from_url()` - Supports 3 Gmail URL formats

**Supported URL Formats:**
- `https://mail.google.com/mail/u/0/#inbox/1849085179733622850`
- `https://mail.google.com/mail/u/0/#inbox?permmsgid=msg-f:1849085179733622850`
- Raw message ID: `1849085179733622850`

### 6. Critical Patterns & Conventions

**Output File Structure** (all in `outputs/`):
- `search_results.csv` - Google search results
- `scraped_articles.csv` - Scraped competitor content
- `keywords_scraped.csv` - Related keywords from Google SERP
- `SEO_Analysis_Results.csv` - Gemini SEO analysis of competitors
- `esquema_articulo.md` - Article outline
- `articulo_completo.md` - Full generated article
- `qa_report.md` - Quality assurance report
- `articulos_sugeridos.md` - Suggested follow-up articles

**Error Handling & Resilience:**
- Web scraping uses headers to avoid anti-bot detection (`User-Agent`, `Accept-Language`)
- Dual scraping strategy: BeautifulSoup first, newspaper3k fallback
- Gmail API uses token persistence (`token.pickle`) to avoid repeated OAuth flows
- API calls use `time.sleep(CONFIG["api_delay"])` between requests
- Gemini responses access via `response.text` (not `response.candidates[0].content.parts[0].text`)

**Automatic Source References (🆕):**
- `add_source_links_to_article()` extracts URLs from context sources
- Adds "## Fuentes y Referencias" section at article end
- Removes duplicates, pairs URLs with titles from context
- Automatically called in notebook generation cell (can be toggled)

**Spanish-First Development:**
- All content generation in Spanish
- Country code: `ES` (Spain)
- Output encoding: UTF-8
- Console messages in Spanish with emojis (✅ ❌ ⚠️ 🔄 📊)

**WordPress Publishing**

**Module**: `longcontent_generator/wordpress.py`
- Function: `publish_article_from_markdown_cleaned()`
- Automatic markdown cleaning: removes meta-text, fixes heading levels, cleans backticks
- Converts markdown → HTML with extensions: `extra`, `nl2br`, `sane_lists`, `codehilite`, `toc`
- Posts to `ghendigital.com/wp-json/wp/v2/posts`
- Default status: `draft` (requires manual review before publishing)
- **Note**: Update `wordpress.py` URL from archivofinal.com to ghendigital.com if needed

### 7. Development Workflow

**Primary Development Loop:**
1. Open `Pipeline_GHEN_Enhanced.ipynb`
2. Select method in configuration cell: `metodo_seleccionado = "topico|keyword|newsletter"`
3. Execute cells sequentially (each cell is self-contained)
4. Check outputs in `outputs/` directory
5. Iterate on QA report suggestions if needed

**Testing:**
- `test_leo_enhanced.py` - Full pipeline test suite
- `test_qa_improvement.py` - QA improvement iteration tests
- No automated CI/CD (manual testing workflow)

**Virtual Environment:**
```bash
source .venv/bin/activate  # Always activate before running
```

**Dependencies** (key packages):
- `google-generativeai` - Gemini API
- `google-auth`, `google-auth-oauthlib`, `google-api-python-client` - Gmail API (🆕)
- `requests`, `beautifulsoup4`, `lxml` - Web scraping
- `selenium`, `webdriver-manager` - Google SERP scraping
- `newspaper3k` - Article extraction fallback
- `pandas` - Data manipulation
- `python-dotenv` - Environment variables
- `markdown` - HTML conversion for WordPress

## Common Tasks

### Add New Generation Method
1. Add method branch in `Pipeline_GHEN_Enhanced.ipynb` after cell `#VSC-f4c98cc7`
2. Create context sources list (strings with research data)
3. Call `core.generate_article_with_context(keyword, context_sources, leo_context)`

### Modify GHEN Personality
Edit `GHEN/personalidad.md` - changes propagate to all generations via `load_leo_context()`

### Add New Technical Content Type
1. Add specialized prompt template in `generate_article_with_context()` for content types:
   - Tutorial con código (step-by-step implementation guides)
   - Análisis comparativo (tech stack comparisons)
   - Lecciones aprendidas (post-mortem from real projects)
2. Adjust SEO keywords for tech audience ("cómo implementar", "mejores prácticas", "tutorial")

### Troubleshooting Generation Issues
1. Check `outputs/qa_report.md` for coverage gaps
2. Run `improve_article_based_on_qa()` for auto-improvement
3. If newsletter-based, verify `is_newsletter_based` detection in `generate_article_with_context()`
4. **For tech content**: Ensure code examples are syntactically correct and tested

### Configure Gmail Integration (🆕)
1. Follow Gmail API Setup section (section 5) to create Google Cloud project
2. Download `credentials.json` and place in project root
3. Run `core.list_gmail_newsletters()` - browser will open for OAuth consent
4. Authorize access → `token.pickle` saved for future use
5. Use Gmail URLs in notebook or call `extract_newsletter_from_gmail()` directly

## Project-Specific Gotchas

- **Never** import Gemini model directly - always use `from .config import model`
- **Always** pass `leo_context` to generation functions - missing context breaks personality consistency
- **Newsletter detection** uses string matching (`'NEWSLETTER' in source`) - maintain this keyword in context strings
- **SERP scraper** can hit CAPTCHA - check `google_has_hunted_us` flag in `scraper.py`
- **Article length** target: 1500-2000 words (enforced in generation prompts)
- **Code blocks**: When generating technical tutorials, ensure proper markdown code fencing with language tags
- **Markdown output** is standard - clean before WordPress publish using built-in cleaner
- **Technical accuracy**: For AI/ML content, verify model names, API syntax, and version compatibility
- **Gmail OAuth**: First run opens browser for consent - `credentials.json` required, `token.pickle` generated after auth
- **Auto-references**: URLs extracted via regex from context sources, automatically appended unless disabled

## Content Categories for GHEN Digital

Based on ghendigital.com structure:
- **INTELIGENCIA ARTIFICIAL**: GenAI, LLMs, RAG, agents, prompt engineering
- **CODE**: Python, APIs, microservices, architecture patterns
- **MLOps/LLMOps**: Model deployment, evaluation, monitoring, CI/CD for ML
- **SEO**: Content optimization (meta - for the content generator itself)
- **ANALYTICS**: Data-driven insights, metrics

## Repository Info

- **Owner**: gabrielnoguera (forked from ArchivoFinal project)
- **Repo**: LongContent_Generator_Script
- **Branch**: main
- **Private repo** - Adapted for GHEN Digital personal brand
