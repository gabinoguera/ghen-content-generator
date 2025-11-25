"""
Funciones principales del módulo LongContent Generator
"""

import os
import requests
import pandas as pd
import time
from typing import List, Dict
from bs4 import BeautifulSoup
from newspaper import Article
from .config import CONFIG, model

# Importar módulo Gmail (con manejo de error si no está instalado)
try:
    from . import gmail
    GMAIL_AVAILABLE = True
except ImportError as e:
    # print(f"⚠️  Módulo Gmail no disponible: {e}")
    GMAIL_AVAILABLE = False
    gmail = None


def google_custom_search(query, country=None, max_results=10):
    """
    Search Google using Custom Search API and return top results.
    
    Args:
        query (str): Search query
        country (str): Country code (default: from CONFIG)
        max_results (int): Number of results to retrieve (default: 10)
    
    Returns:
        pd.DataFrame: DataFrame with columns ['title', 'link']
    """
    API_KEY = os.getenv('API_KEY')
    API_CUSTOM_SEARCH_ID = os.getenv('API_CUSTOM_SEARCH_ID')
    
    if not API_KEY or not API_CUSTOM_SEARCH_ID:
        print("❌ Error: API Key o ID de búsqueda no están configurados")
        return pd.DataFrame()
    
    country = country or CONFIG["default_country"]
    
    # Para hasta 10 resultados, una sola petición
    if max_results <= 10:
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={API_CUSTOM_SEARCH_ID}&q={query}&start=1&gl={country}"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"❌ Error en la petición: {response.status_code}")
            return pd.DataFrame()
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            print("⚠️  No se encontraron resultados")
            return pd.DataFrame()
        
        df = pd.DataFrame(items, columns=['title', 'link'])
        print(f"✅ {len(df)} resultados obtenidos para '{query}'")
        return df
    
    # Para más de 10 resultados, múltiples peticiones
    else:
        search_results = []
        max_requests = min(10, (max_results + 9) // 10)
        
        for i in range(1, max_requests * 10, 10):
            url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={API_CUSTOM_SEARCH_ID}&q={query}&start={i}&gl={country}"
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"❌ Error en petición {i}: {response.status_code}")
                break
            
            data = response.json()
            items = data.get("items", [])
            
            if not items:
                break
            
            search_results.extend(items)
        
        if search_results:
            df = pd.DataFrame(search_results, columns=['title', 'link'])
            df = df.head(max_results)
            print(f"✅ {len(df)} resultados obtenidos para '{query}'")
            return df
        else:
            print("⚠️  No se encontraron resultados")
            return pd.DataFrame()


def scrape_article(url):
    """
    Extract text content from a URL using requests + BeautifulSoup with newspaper fallback.
    
    Args:
        url (str): URL to scrape
    
    Returns:
        str: Extracted text content
    """
    # Headers para evitar bloqueos anti-scraping
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        # Método 1: requests + BeautifulSoup (mejor para newsletters)
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Eliminar scripts, estilos, y elementos no deseados
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
            element.decompose()
        
        # Extraer texto de párrafos, divs, artículos
        text_elements = []
        
        # Priorizar contenido de artículos y main
        for tag in ['article', 'main', '[role="main"]']:
            content = soup.select(tag)
            if content:
                for elem in content:
                    text_elements.extend([p.get_text(strip=True) for p in elem.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li'])])
                break
        
        # Si no encuentra article/main, buscar todo
        if not text_elements:
            text_elements = [p.get_text(strip=True) for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li', 'div'])]
        
        # Filtrar elementos vacíos y juntar
        article_text = '\n'.join([text for text in text_elements if text and len(text) > 20])
        
        if article_text and len(article_text) > 100:
            return article_text
        
        # Método 2: newspaper3k como fallback
        print(f"   ⚠️  Poco contenido con BeautifulSoup, intentando con newspaper3k...")
        article = Article(url)
        article.download()
        article.parse()
        
        if article.text and len(article.text) > 100:
            return article.text
        
        # Si newspaper tampoco funciona, devolver lo que tengamos
        return article_text if article_text else ""
    
    except requests.exceptions.Timeout:
        print(f"❌ Timeout al acceder a {url}")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión en {url}: {str(e)}")
        return ""
    except Exception as e:
        print(f"❌ Error al scrapear {url}: {str(e)}")
        return ""


def scrape_articles_batch(df):
    """
    Scrape all articles in a DataFrame with 'link' column.
    
    Args:
        df (pd.DataFrame): DataFrame with 'link' column
    
    Returns:
        pd.DataFrame: DataFrame with added 'scraped_text' column
    """
    if 'link' not in df.columns:
        print("❌ Error: DataFrame debe tener columna 'link'")
        return df
    
    scraped_texts = []
    total = len(df)
    
    print(f"🔄 Scrapeando {total} artículos...")
    
    for idx, url in enumerate(df['link'], 1):
        print(f"   [{idx}/{total}] {url[:60]}...")
        text = scrape_article(url)
        scraped_texts.append(text)
        
        time.sleep(1)  # Be respectful
    
    df['scraped_text'] = scraped_texts
    
    # Count successful scrapes
    successful = df['scraped_text'].str.strip().astype(bool).sum()
    print(f"✅ Scraping completado: {successful}/{total} exitosos")
    
    return df


def analyze_seo_with_gemini(text):
    """
    Analyze article for SEO using Gemini.
    
    Args:
        text (str): Article text to analyze
    
    Returns:
        str: SEO analysis
    """
    prompt = f"""You are an expert in semantic SEO optimization and content strategy.

Analyze the following article and extract:
1. Main keywords, semantic clusters, and related terms
2. Content structure and hierarchy
3. User intent addressed
4. Topical authority signals
5. Gaps or weaknesses in coverage

This analysis will be used to create superior content that outranks this article.

Article: {text[:8000]}

Provide a concise but comprehensive analysis focusing on semantic SEO elements.
"""
    
    try:
        response = model.generate_content(prompt)
        # Usar response.text directamente para evitar el error finish_message
        if hasattr(response, 'text'):
            return response.text
        else:
            # Fallback para versiones anteriores
            return str(response)
    except Exception as e:
        print(f"❌ Error en análisis SEO: {str(e)}")
        return f"Error al generar análisis SEO: {str(e)}"


def analyze_articles_batch(df):
    """
    Analyze all scraped articles in DataFrame using Gemini.
    
    Args:
        df (pd.DataFrame): DataFrame with 'scraped_text' column
    
    Returns:
        pd.DataFrame: DataFrame with added 'SEO Analysis' column
    """
    if df.empty:
        print("❌ DataFrame vacío")
        return df
    
    if 'scraped_text' not in df.columns:
        print("❌ Error: DataFrame debe tener columna 'scraped_text'")
        return df
    
    print(f"🔄 Analizando {len(df)} artículos con Gemini...")
    
    for index, row in df.iterrows():
        article_text = row['scraped_text']
        
        if not article_text.strip():
            print(f"   ⚠️  [{index + 1}/{len(df)}] Artículo vacío, omitiendo")
            df.at[index, 'SEO Analysis'] = "No se pudo scrapear el texto del artículo"
            continue
        
        print(f"   [{index + 1}/{len(df)}] Analizando: {row.get('title', 'Sin título')[:60]}...")
        analysis = analyze_seo_with_gemini(article_text)
        df.at[index, 'SEO Analysis'] = analysis
        
        time.sleep(CONFIG["api_delay"])
    
    # Save to CSV
    output_file = CONFIG["output_analysis_csv"]
    df.to_csv(output_file, index=False)
    print(f"✅ Análisis completado y guardado en {output_file}")
    
    return df


def analyze_combined_context(df, related_keywords_context, main_query):
    """
    Analyze competition + related keywords to create comprehensive context.
    
    Args:
        df (pd.DataFrame): DataFrame with 'SEO Analysis' column
        related_keywords_context (dict): Related keywords and questions
        main_query (str): Main keyword/query
    
    Returns:
        str: Combined analysis for content planning
    """
    if 'SEO Analysis' not in df.columns:
        print("❌ Error: Columna 'SEO Analysis' no encontrada")
        return ""
    
    # Concatenate all SEO analyses
    seo_context = "\n\n".join(df['SEO Analysis'].dropna().tolist())
    
    # Prepare related keywords context
    keywords_text = ", ".join(related_keywords_context.get('keywords', [])[:50])  # Limitar para no saturar
    questions_text = "\n".join([f"- {q}" for q in related_keywords_context.get('questions', [])[:30]])
    
    prompt = f"""You are an expert at Semantic SEO and content strategy.

**MAIN QUERY:** {main_query}

**COMPETITION ANALYSIS (Top-ranking content):**
{seo_context[:6000]}

**RELATED KEYWORDS TO INTEGRATE:**
{keywords_text}

**USER QUESTIONS TO ANSWER:**
{questions_text}

**YOUR TASK:**
Create a strategic content brief that:
1. Identifies content gaps in current top-ranking articles
2. Maps semantic clusters from related keywords
3. Determines optimal content structure for topical authority
4. Suggests unique angles to outperform competitors
5. Outlines how to naturally integrate related keywords and answer questions

Focus on creating a blueprint for content that Google will recognize as the most comprehensive resource on "{main_query}".

Output Language: {CONFIG["output_language"]}
Format: Structured markdown
"""
    
    try:
        print("🔄 Generando análisis combinado de contexto...")
        response = model.generate_content(prompt)
        # Usar response.text directamente para evitar el error finish_message
        if hasattr(response, 'text'):
            analysis = response.text
        else:
            analysis = str(response)
        print("✅ Análisis combinado generado")
        return analysis
    except Exception as e:
        print(f"❌ Error en análisis combinado: {str(e)}")
        return f"Error al generar análisis combinado: {str(e)}"


def create_intelligent_content_plan(combined_analysis, main_query, related_keywords_context):
    """
    Create intelligent content plan based on combined analysis.
    
    Args:
        combined_analysis (str): Combined analysis from competition + keywords
        main_query (str): Main keyword/query
        related_keywords_context (dict): Related keywords and questions
    
    Returns:
        str: Intelligent content plan
    """
    keywords_sample = ", ".join(related_keywords_context.get('keywords', [])[:30])
    questions_sample = "\n".join([f"- {q}" for q in related_keywords_context.get('questions', [])[:20]])
    
    prompt = f"""You are an expert content strategist and semantic SEO specialist.

**MAIN QUERY:** {main_query}

**STRATEGIC BRIEF:**
{combined_analysis}

**KEY SEMANTIC ELEMENTS TO COVER:**
Keywords: {keywords_sample}

Questions: 
{questions_sample}

**YOUR TASK:**
Create a comprehensive content plan that:
1. Establishes complete topical authority for "{main_query}"
2. Naturally integrates related keywords through semantic clusters
3. Addresses all user questions thoroughly
4. Outperforms current top-ranking content
5. Creates clear content sections with semantic purpose

The plan should guide content creation to ensure:
- No keyword stuffing, only natural semantic integration
- Progressive depth from fundamentals to advanced concepts
- Clear answer to user intent at each stage
- Comprehensive coverage that Google rewards

Output Language: {CONFIG["output_language"]}
Format: Structured content plan with clear sections
"""
    
    try:
        print("🔄 Creando plan de contenido inteligente...")
        response = model.generate_content(prompt)
        # Usar response.text directamente para evitar el error finish_message
        if hasattr(response, 'text'):
            plan = response.text
        else:
            plan = str(response)
        print("✅ Plan de contenido inteligente creado")
        return plan
    except Exception as e:
        print(f"❌ Error creando plan: {str(e)}")
        return f"Error al crear plan de contenido: {str(e)}"


def generate_article_outline(
    main_query: str,
    search_results: list,
    related_keywords_context: dict,
    content_plan: str
) -> str:
    """
    Genera un esquema detallado del artículo basado en el análisis de competencia.
    
    Args:
        main_query: Keyword/query principal
        search_results: Resultados de búsqueda analizados
        related_keywords_context: Contexto de keywords relacionadas
        content_plan: Plan de contenido inteligente
    
    Returns:
        str: Esquema del artículo en formato markdown
    """
    
    # Preparar contexto de keywords
    keywords_text = ", ".join(related_keywords_context.get('keywords', [])[:20])
    questions_text = "\n".join([f"- {q}" for q in related_keywords_context.get('questions', [])[:10]])
    
    # Preparar contexto de competencia
    competition_context = ""
    if search_results:
        competition_context = f"""
**ANÁLISIS DE COMPETENCIA:**
{len(search_results)} resultados analizados. Principales temas cubiertos:
{chr(10).join([f"- {r.get('title', 'Sin título')[:80]}..." for r in search_results[:5]])}
"""

    prompt = f"""Eres un experto en SEO y estructura de contenido. Tu tarea es crear UNICAMENTE un esquema de artículo en formato Markdown.

**REGLAS ESTRICTAS:**
1. SOLO incluye títulos con #, ##, ###
2. NO incluyas texto explicativo, anotaciones o comentarios
3. NO incluyas "Propósito Semántico:", "Keywords:", etc.
4. Cada sección debe ser un título claro y conciso
5. Máximo 8-12 secciones principales

**TEMA PRINCIPAL:** {main_query}

**KEYWORDS RELACIONADAS:** {keywords_text}

{competition_context}

**PLAN DE CONTENIDO:**
{content_plan}

**TAREA:**
Crea un esquema estructurado que cubra el tema de manera completa y lógica. 

**FORMATO REQUERIDO:**
Título Principal del Artículo
1. Sección Principal 1
1.1 Subsección A
1.2 Subsección B
2. Sección Principal 2
2.1 Subsección A
3. Sección Principal 3
3.1 Subsección A
3.2 Subsección B
4. Sección Principal 4
4.1 Subsección A
4.2 Subsección B
5. Sección Principal 5


**IMPORTANTE:** Responde SOLO con el esquema en formato Markdown, sin texto adicional."""

    try:
        from .config import generation_config
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # Usar response.text directamente para evitar el error finish_message
        if hasattr(response, 'text'):
            outline = response.text.strip()
        else:
            outline = str(response).strip()
        
        # Verificar si la respuesta se cortó por límite de tokens
        if 'finish_reason' in str(response) and 'MAX_TOKENS' in str(response):
            print("⚠️  Advertencia: Respuesta cortada por límite de tokens")
            print("💡 Aumentando límite de tokens para mejor generación")
        
        # Validación básica
        if not outline.startswith('#'):
            print("⚠️  Advertencia: El esquema generado no tiene formato markdown correcto")
            print(f"📝 Primeros 200 caracteres: {outline[:200]}")
        
        # Limpiar respuesta si contiene metadatos de Gemini
        if 'GenerateContentResponse' in outline or 'candidates' in outline:
            print("🔧 Limpiando respuesta de metadatos de Gemini...")
            # Intentar extraer solo el contenido del texto
            lines = outline.split('\n')
            cleaned_lines = []
            for line in lines:
                if not any(x in line for x in ['GenerateContentResponse', 'candidates', 'finish_reason', 'usage_metadata']):
                    cleaned_lines.append(line)
            outline = '\n'.join(cleaned_lines).strip()
        
        return outline
        
    except Exception as e:
        print(f"❌ Error generando esquema: {str(e)}")
        return f"Error generando esquema: {str(e)}"


def parse_outline_to_sections(outline_md: str) -> List[Dict[str, str]]:
    """
    Convierte un esquema markdown en una lista ordenada de secciones.
    Soporta encabezados ('#','##','###') y bullets ('* ','- ').
    Devuelve [{'title': str, 'block': str}].
    """
    lines = outline_md.splitlines()
    sections: List[Dict[str, str]] = []
    current_title: str | None = None
    current_block: List[str] = []

    def push_section():
        nonlocal current_title, current_block
        if current_title and current_block:
            sections.append({
                'title': current_title.strip(),
                'block': "\n".join(current_block).strip()
            })
        current_title, current_block = None, []

    for ln in lines:
        stripped = ln.lstrip()
        is_heading = stripped.startswith(('#', '##', '###', '####'))
        is_bullet = stripped.startswith(('* ', '- ', '+ '))
        
        if is_heading or (is_bullet and current_title is None):
            if current_title is not None:
                push_section()
            current_title = ln.strip()
            current_block = [ln]
        elif current_title is not None:
            current_block.append(ln)

    if current_title is not None:
        push_section()

    if not sections and outline_md.strip():
        sections = [{'title': 'Artículo Completo', 'block': outline_md.strip()}]

    print(f"✅ {len(sections)} secciones parseadas del esquema")
    return sections


def generate_section_content_with_context(
    section_title: str,
    section_block: str,
    content_plan: str,
    article_so_far: str,
    remaining_keywords: List[str]
) -> str:
    """
    Genera contenido para una sección con contexto pleno del artículo ya escrito.
    
    Args:
        section_title: Título de la sección
        section_block: Bloque del esquema para esta sección
        content_plan: Plan de contenido global
        article_so_far: Todo el contenido generado hasta ahora
        remaining_keywords: Keywords aún no cubiertas
    
    Returns:
        str: Contenido de la sección en markdown
    """
    # Limitar keywords para no saturar el prompt
    keywords_sample = ", ".join([kw for kw in remaining_keywords[:15] if isinstance(kw, str)])
    
    # Contexto reciente (últimos 3000 caracteres para no saturar)
    recent_context = article_so_far[-3000:] if article_so_far else "Este es el inicio del artículo."
    
    prompt = f"""Genera el contenido de la siguiente sección de artículo SEO. Responde DIRECTAMENTE con el contenido en markdown, sin introducciones ni explicaciones.

**PLAN DE CONTENIDO GLOBAL:**
{content_plan[:2000]}

**CONTEXTO DEL ARTÍCULO (para coherencia):**
{recent_context}

**SECCIÓN A DESARROLLAR:**
{section_title}
{section_block}

**KEYWORDS A INTEGRAR (solo si es natural):**
{keywords_sample if keywords_sample else "Todas ya cubiertas"}

**REQUISITOS:**
- Contenido directo en markdown
- Párrafos de 3-5 líneas desarrollados
- Coherencia con el contexto anterior
- NO repetir información previa
- Integrar keywords de forma natural
- Tono profesional y claro

**IMPORTANTE:** Comienza directamente con el contenido de la sección. NO uses frases como "Aquí tienes", "La siguiente sección", etc.

Idioma: {CONFIG["output_language"]}

CONTENIDO DE LA SECCIÓN:"""
    
    try:
        response = model.generate_content(prompt)
        # Usar response.text directamente para evitar el error finish_message
        if hasattr(response, 'text'):
            content = response.text
        else:
            content = str(response)
        
        # Limpiar respuestas conversacionales
        content = clean_conversational_response(content)
        
        return content
        
    except Exception as e:
        print(f"❌ Error generando sección: {str(e)}")
        return f"## {section_title}\n\nError al generar esta sección: {str(e)}"


def clean_conversational_response(text: str) -> str:
    """
    Limpia respuestas conversacionales de Gemini que no deberían aparecer en el contenido.
    """
    if not text:
        return text
    
    # Patrones de respuestas conversacionales a eliminar
    conversational_patterns = [
        r"^Aquí tienes.*?:\s*",
        r"^La siguiente sección.*?:\s*",
        r"^Esta sección.*?:\s*",
        r"^Contenido de la sección.*?:\s*",
        r"^A continuación.*?:\s*",
        r"^Siguiendo.*?:\s*",
    ]
    
    import re
    cleaned_text = text
    
    for pattern in conversational_patterns:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Eliminar líneas vacías al inicio
    cleaned_text = cleaned_text.lstrip('\n')
    
    return cleaned_text


def generate_article_from_outline(
    outline_md: str,
    content_plan: str,
    related_keywords_context: dict
) -> str:
    """
    Genera el artículo completo sección por sección con contexto acumulado.
    Sin paso de mejora posterior para evitar duplicaciones.
    
    Args:
        outline_md: Esquema del artículo en markdown
        content_plan: Plan de contenido inteligente
        related_keywords_context: Contexto de keywords relacionadas
    
    Returns:
        str: Artículo completo
    """
    sections = parse_outline_to_sections(outline_md)
    if not sections:
        print("❌ Esquema vacío o no reconocido.")
        return ""

    all_keywords = [kw.strip() for kw in related_keywords_context.get('keywords', []) if isinstance(kw, str)]
    article_so_far = ""
    sections_content: List[str] = []

    def get_remaining_keywords(text: str) -> List[str]:
        """Devuelve keywords que aún no aparecen en el texto."""
        text_lower = (text or "").lower()
        return [kw for kw in all_keywords if kw and kw.lower() not in text_lower]

    total = len(sections)
    print(f"🔄 Generando contenido secuencial para {total} secciones...")
    print(f"📊 Keywords totales a integrar: {len(all_keywords)}")
    
    for idx, sec in enumerate(sections, start=1):
        remaining = get_remaining_keywords(article_so_far)
        coverage = ((len(all_keywords) - len(remaining)) / len(all_keywords) * 100) if all_keywords else 100
        
        print(f"\n   [{idx}/{total}] {sec['title'][:70]}...")
        print(f"   📈 Cobertura keywords: {coverage:.1f}% ({len(all_keywords) - len(remaining)}/{len(all_keywords)})")
        
        # Generar contenido con contexto (SIN mejora posterior para evitar duplicaciones)
        section_content = generate_section_content_with_context(
            section_title=sec['title'],
            section_block=sec['block'],
            content_plan=content_plan,
            article_so_far=article_so_far,
            remaining_keywords=remaining
        )
        
        sections_content.append(section_content)
        
        # Actualizar contexto acumulado
        article_so_far = (article_so_far + "\n\n" + section_content).strip()
        
        time.sleep(CONFIG["api_delay"])

    # Combinar todas las secciones
    complete_article = "\n\n".join(sections_content)

    # Guardar artículo
    output_file = CONFIG["output_article_md"]
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(complete_article)

    final_coverage = ((len(all_keywords) - len(get_remaining_keywords(complete_article))) / len(all_keywords) * 100) if all_keywords else 100
    print(f"\n✅ Artículo completo generado y guardado en {output_file}")
    print(f"📊 Cobertura final de keywords: {final_coverage:.1f}%")
    
    return complete_article


def qa_article_coverage(article_content, related_keywords_context=None, main_query=None):
    """
    QA agent CIEGO que evalúa la calidad del artículo sin contexto de fuentes.
    Actúa como juez independiente evaluando SOLO el resultado final.
    
    Args:
        article_content: Contenido del artículo generado (ÚNICO input necesario)
        related_keywords_context: (IGNORADO - mantenido por compatibilidad)
        main_query: (IGNORADO - mantenido por compatibilidad)
    
    Returns:
        str: Reporte QA objetivo
    """
    # QA CIEGO: Solo evalúa el artículo final sin contexto externo
    prompt = f"""Eres un editor técnico senior evaluando la calidad de este artículo. 
NO tienes acceso a instrucciones originales ni fuentes. Evalúa SOLO lo que lees.

# ARTÍCULO A EVALUAR

{article_content}

# CRITERIOS DE EVALUACIÓN

Genera un reporte QA objetivo evaluando estos aspectos. Responde DIRECTAMENTE con el reporte.

## 1. NARRATIVA Y FLUIDEZ (Puntuación: X/10)

**Análisis:**
- ¿El texto fluye naturalmente de un párrafo a otro?
- ¿Las transiciones son suaves o abruptas?
- ¿Se siente como una conversación experta o como un listado?
- ¿Hay ritmo variado en las oraciones?

**Problemas detectados:**
- [Lista específica de problemas de fluidez]

**Puntuación justificada:** X/10

---

## 2. EQUILIBRIO LISTAS vs PÁRRAFOS (Puntuación: X/10)

**Análisis:**
- Ratio estimado: X% listas, Y% párrafos narrativos
- ¿Se abusa de viñetas cuando podrían ser párrafos?
- ¿Las listas se usan solo cuando son necesarias?
- ¿Hay suficiente contenido narrativo que desarrolle ideas?

**Secciones problemáticas:**
- [Identificar secciones con exceso de listas]

**Puntuación justificada:** X/10

---

## 3. TONO Y CALIDEZ (Puntuación: X/10)

**Análisis:**
- ¿El tono es cálido y conversacional o frío y distante?
- ¿Se siente humano o generado automáticamente?
- ¿Hay voz personal o es completamente impersonal?
- ¿El lenguaje invita a seguir leyendo?

**Observaciones:**
- [Ejemplos de tono frío o cálido encontrados]

**Puntuación justificada:** X/10

---

## 4. REPETICIONES Y VARIEDAD LÉXICA (Puntuación: X/10)

**Análisis:**
- ¿Se repiten frases o estructuras de oración?
- ¿Hay variedad en el vocabulario técnico?
- ¿Las ideas se repiten sin aportar valor nuevo?
- ¿Cada párrafo avanza la narrativa?

**Repeticiones detectadas:**
- [Lista de frases/estructuras repetitivas si las hay]

**Puntuación justificada:** X/10

---

## 5. VALOR Y PROFUNDIDAD (Puntuación: X/10)

**Análisis:**
- ¿Cada sección aporta insights únicos?
- ¿Hay profundidad técnica real o solo superficie?
- ¿Se conectan conceptos de forma significativa?
- ¿El lector aprende algo valioso?

**Observaciones:**
- [Identificar secciones con alto/bajo valor]

**Puntuación justificada:** X/10

---

## 6. ESTRUCTURA Y ORGANIZACIÓN (Puntuación: X/10)

**Análisis:**
- ¿La estructura es lógica y fácil de seguir?
- ¿Los títulos y subtítulos son claros?
- ¿Hay jerarquía clara de información?
- ¿El artículo tiene introducción, desarrollo y conclusión coherentes?

**Observaciones:**
- [Comentarios sobre estructura]

**Puntuación justificada:** X/10

---

## PUNTUACIÓN GLOBAL: X/10

**Promedio de los 6 criterios**

---

## RECOMENDACIONES PRIORITARIAS

### 🔴 CRÍTICAS (Deben corregirse)
1. [Problema más grave identificado]
2. [Segundo problema más grave]

### 🟡 MEJORAS SUGERIDAS
1. [Mejora recomendada 1]
2. [Mejora recomendada 2]
3. [Mejora recomendada 3]

### ✅ FORTALEZAS
1. [Aspecto bien logrado 1]
2. [Aspecto bien logrado 2]

---

## INSTRUCCIONES PARA MEJORA

**Para aumentar narrativa:**
[Instrucciones específicas basadas en el artículo]

**Para mejorar tono:**
[Instrucciones específicas basadas en el artículo]

**Para eliminar repeticiones:**
[Instrucciones específicas basadas en el artículo]

---

**IMPORTANTE:** Sé honesto y crítico. Este es un proceso interno de mejora.

Idioma: español

REPORTE QA:
"""
    
    try:
        print("🔄 Ejecutando QA del artículo...")
        response = model.generate_content(prompt)
        # Usar response.text directamente para evitar el error finish_message
        if hasattr(response, 'text'):
            qa_report = response.text
        else:
            qa_report = str(response)
        
        # Limpiar respuesta si contiene metadatos de Gemini
        if 'GenerateContentResponse' in qa_report or 'candidates' in qa_report:
            print("🔧 Limpiando respuesta QA de metadatos de Gemini...")
            qa_report = clean_conversational_response(qa_report)
        
        # Save QA report
        output_file = CONFIG["output_qa_report"]
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(qa_report)
        
        print(f"✅ Reporte QA generado y guardado en {output_file}")
        return qa_report
    except Exception as e:
        print(f"❌ Error en QA: {str(e)}")
        return f"Error al generar reporte QA: {str(e)}"


def suggest_related_articles(qa_report, related_keywords_context, main_query):
    """
    Sugiere artículos relacionados para construir autoridad topical.
    
    Args:
        qa_report: Reporte QA del artículo
        related_keywords_context: Contexto de keywords relacionadas
        main_query: Query principal
    
    Returns:
        str: Sugerencias de artículos relacionados
    """
    keywords = related_keywords_context.get('keywords', [])
    questions = related_keywords_context.get('questions', [])
    
    keywords_sample = ", ".join(keywords[:40])
    questions_sample = "\n".join([f"- {q}" for q in questions[:25]])
    
    prompt = f"""Genera sugerencias de artículos relacionados para construir autoridad topical. Responde DIRECTAMENTE con las sugerencias en formato markdown, sin introducciones.

**QUERY PRINCIPAL:** {main_query}

**REPORTE QA DEL ARTÍCULO PRINCIPAL:**
{qa_report[:3000]}

**KEYWORDS RELACIONADAS:**
{keywords_sample}

**PREGUNTAS RELACIONADAS:**
{questions_sample}

**OBJETIVO:**
Sugiere 5-7 artículos relacionados que:
1. Complementen el artículo principal
2. Cubran keywords/preguntas no abordadas
3. Construyan un content cluster coherente
4. Establezcan autoridad topical completa

Para cada artículo sugerido, proporciona:

### Artículo N: [Título SEO-optimizado]
- **Keywords objetivo:** [primarias y secundarias]
- **Ángulo de contenido:** [enfoque único]
- **Relación semántica:** [cómo se conecta con el tema principal]
- **Prioridad:** Alta/Media/Baja
- **Esquema breve:** 
  - Sección 1
  - Sección 2
  - Sección 3-5

**IMPORTANTE:** Comienza directamente con las sugerencias. NO uses frases como "Como estratega", "Aquí tienes", etc.

Idioma: {CONFIG["output_language"]}

SUGERENCIAS DE ARTÍCULOS:
"""
    
    try:
        print("🔄 Generando sugerencias de artículos relacionados...")
        response = model.generate_content(prompt)
        # Usar response.text directamente para evitar el error finish_message
        if hasattr(response, 'text'):
            suggestions = response.text
        else:
            suggestions = str(response)
        
        # Limpiar respuesta si contiene metadatos de Gemini
        if 'GenerateContentResponse' in suggestions or 'candidates' in suggestions:
            print("🔧 Limpiando respuesta de sugerencias de metadatos de Gemini...")
            suggestions = clean_conversational_response(suggestions)
        
        # Save suggestions
        output_file = CONFIG["output_suggestions"]
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(suggestions)
        
        print(f"✅ Sugerencias generadas y guardadas en {output_file}")
        return suggestions
    except Exception as e:
        print(f"❌ Error generando sugerencias: {str(e)}")
        return f"Error al generar sugerencias: {str(e)}"


def improve_article_based_on_qa(
    article_content: str, 
    qa_report: str,
    context_sources: list = None,
    ghen_context: dict = None
) -> str:
    """
    Mejora el artículo aplicando las observaciones del QA de forma quirúrgica.
    Solo modifica las áreas específicas identificadas por el análisis QA.
    
    FASE 1 (ya ejecutada): QA ciego evaluó calidad objetivamente
    FASE 2 (esta función): Mejoras quirúrgicas CON contexto para preservar precisión técnica
    
    IMPORTANTE: No regenera el artículo completo, solo aplica mejoras específicas
    preservando el contenido original intacto.
    
    Args:
        article_content: Contenido actual del artículo
        qa_report: Reporte QA con observaciones específicas
        context_sources: Fuentes originales (newsletter/artículos) para verificar precisión
        ghen_context: Contexto de personalidad GHEN para mantener tono
    
    Returns:
        str: Artículo mejorado con las correcciones aplicadas
    """
    if not article_content or not qa_report:
        return article_content
    
    print("🔧 Aplicando mejoras basadas en análisis QA...")
    print("⚠️  MODO QUIRÚRGICO: Solo se modificarán las secciones específicas mencionadas en el QA")
    print("📚 Contexto disponible para precisión técnica: {}".format("Sí" if context_sources else "No"))
    print("🎭 Personalidad GHEN disponible: {}\n".format("Sí" if ghen_context else "No"))
    
    # Usar Gemini para aplicar mejoras de forma inteligente y quirúrgica
    improved_content = apply_qa_improvements_surgical(
        article_content, 
        qa_report,
        context_sources=context_sources,
        ghen_context=ghen_context
    )
    
    # Validar que el contenido mejorado no sea el análisis del newsletter
    if "## Resumen Ejecutivo" in improved_content and "## Puntos Clave" in improved_content:
        print("❌ ERROR: Gemini regeneró contenido incorrecto (análisis de newsletter)")
        print("✅ Retornando artículo original sin cambios")
        return article_content
    
    # Validar longitud mínima (debe ser similar al original)
    if len(improved_content) < len(article_content) * 0.7:
        print(f"❌ ERROR: Contenido mejorado muy corto ({len(improved_content)} vs {len(article_content)} chars)")
        print("✅ Retornando artículo original sin cambios")
        return article_content
    
    # Guardar versión mejorada
    output_file = "outputs/articulo_mejorado_qa.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(improved_content)
    
    print(f"\n✅ Artículo mejorado guardado en: {output_file}")
    print(f"📊 Longitud original: {len(article_content)} caracteres")
    print(f"📊 Longitud mejorada: {len(improved_content)} caracteres")
    return improved_content


def apply_qa_improvements_surgical(
    article_content: str, 
    qa_report: str,
    context_sources: list = None,
    ghen_context: dict = None
) -> str:
    """
    Aplica mejoras del QA de forma quirúrgica usando Gemini (versión robusta con validaciones).
    
    CRÍTICO: No regenera el artículo, solo aplica las mejoras específicas del QA.
    FASE 2: Tiene acceso al contexto original para mantener precisión técnica.
    
    Validaciones implementadas:
    - Detecta si Gemini regeneró contenido incorrecto (newsletter analysis)
    - Valida que la longitud sea similar al original (±30%)
    - Verifica que preserve secciones principales del artículo (>70%)
    - Detecta cambios de tema o estructura
    - Valida longitud mínima absoluta (>2000 chars)
    - Verifica preservación del inicio del artículo
    
    Args:
        article_content: Artículo original completo
        qa_report: Reporte QA con recomendaciones específicas
        context_sources: Fuentes originales para verificar precisión técnica
        ghen_context: Personalidad GHEN para mantener tono
    
    Returns:
        str: Artículo con mejoras aplicadas quirúrgicamente, o artículo original si falla validación
    """
    print("🔬 Aplicando mejoras quirúrgicas con Gemini...")
    print("📚 Usando contexto original para mantener precisión técnica\n")
    
    # Extraer títulos principales del artículo original para validación
    import re
    original_h2_titles = re.findall(r'^##\s+([^\n]+)', article_content, re.MULTILINE)
    
    # Preparar contexto condensado (primeros 2000 chars de cada fuente)
    context_preview = ""
    if context_sources:
        context_preview = "\n\n---\n\n".join(
            [source[:2000] + "..." for source in context_sources[:2]]
        )
    
    # Preparar personalidad GHEN
    personality_preview = ""
    if ghen_context and ghen_context.get('personality'):
        personality_preview = ghen_context['personality'][:1000]
    
    prompt = f"""Eres un editor técnico experto. Tu tarea es aplicar ÚNICAMENTE las mejoras específicas mencionadas en el reporte QA al artículo existente.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## CONTEXTO DISPONIBLE (para mantener precisión técnica)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### FUENTES ORIGINALES (newsletter/artículos):
{context_preview if context_preview else "No disponible"}

### PERSONALIDAD GHEN (tono y voz):
{personality_preview if personality_preview else "No disponible"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## REPORTE QA CON MEJORAS A APLICAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{qa_report}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## ARTÍCULO ORIGINAL COMPLETO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{article_content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## INSTRUCCIONES CRÍTICAS - CAMBIOS MÍNIMOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### REGLA DE ORO: PRESERVA EL 95% DEL CONTENIDO ORIGINAL

1. **NO REGENERES EL ARTÍCULO** - Solo aplica las mejoras específicas mencionadas en el QA
2. **CAMBIOS QUIRÚRGICOS** - Si el QA dice "mejorar transición en párrafo 3 de sección X":
   - Modifica SOLO ese párrafo específico
   - Mantén TODOS los demás párrafos EXACTAMENTE iguales (palabra por palabra)
3. **PRESERVA INFORMACIÓN TÉCNICA** - Mantén todos los detalles técnicos de las fuentes:
   - Nombres de herramientas (Whisper.cpp, FastAPI, PyAudio, etc.)
   - Parámetros y configuraciones
   - Ejemplos de código (si existen)
   - Cifras y benchmarks
4. **MANTÉN ESTRUCTURA EXACTA** - No cambies:
   - Títulos de sección (## headers)
   - Orden de secciones
   - Longitud general del artículo (±5%)
5. **RESPETA PERSONALIDAD GHEN** - Si existe contexto de personalidad:
   - Mantén primera persona en experiencias ("En mi experiencia...")
   - Preserva referencias a proyectos específicos
   - Mantén tono técnico-pedagógico
6. **KEYWORDS**: 
   - Si QA menciona keywords ❌ faltantes: intégralas en 1-2 frases nuevas
   - Si QA menciona keywords ⚠️ forzadas: suaviza SOLO esas menciones específicas
   - NO elimines keywords que el QA no mencionó
7. **MISMO TEMA Y LONGITUD** - El artículo mejorado debe:
   - Tratar EXACTAMENTE el mismo tema
   - Tener longitud similar (diferencia máxima ±10%)
   - Mantener todas las secciones originales

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## EJEMPLOS CONCRETOS DE MODIFICACIONES QUIRÚRGICAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### CASO 1: QA dice "Mejorar transición en sección 'Optimización'"

❌ INCORRECTO (regenera toda la sección):
Reescribir los 5 párrafos de la sección "Optimización" con nuevo contenido

✅ CORRECTO (cambio quirúrgico):
Modificar SOLO la frase de transición al inicio de la sección.
Ejemplo: "Ahora veamos..." → "Estos conceptos nos llevan a considerar..."
MANTENER los otros 4 párrafos EXACTAMENTE iguales.

### CASO 2: QA dice "Reducir repetición de 'cuantización' (aparece 4 veces)"

❌ INCORRECTO:
Reescribir los párrafos donde aparece "cuantización"

✅ CORRECTO:
Reemplazar 2 de las 4 menciones con sinónimos:
- "cuantización" → "reducción de precisión" (1 vez)
- "cuantización" → "optimización" (1 vez)
- Mantener "cuantización" en las otras 2 menciones
DEJAR el resto del texto INTACTO.

### CASO 3: QA dice "Integrar keyword faltante: 'edge computing'"

❌ INCORRECTO:
Reescribir múltiples secciones para forzar la keyword

✅ CORRECTO:
Añadir 1 frase natural en una sección apropiada:
"Este enfoque de edge computing permite latencias mínimas."
MANTENER todo lo demás SIN CAMBIOS.

### CASO 4: QA dice "Mejorar narrativa en lista de bullets de sección X"

❌ INCORRECTO:
Reescribir toda la sección X desde cero

✅ CORRECTO:
Convertir los 5 bullets en 2 párrafos narrativos, manteniendo:
- TODA la información técnica de los bullets
- El orden lógico original
- Los ejemplos y cifras mencionadas
MANTENER las otras secciones EXACTAMENTE iguales.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## LO QUE NUNCA DEBES HACER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Regenerar el artículo completo
❌ Cambiar el tema del artículo
❌ Añadir secciones nuevas ("## Resumen Ejecutivo", "## Conclusión")
❌ Eliminar información técnica de las fuentes originales
❌ Cambiar títulos de sección (## headers)
❌ Modificar párrafos que el QA no mencionó
❌ Reducir significativamente la longitud (>10%)
❌ Convertir el artículo en resumen/análisis/newsletter
❌ Eliminar ejemplos de código o cifras específicas
❌ Cambiar el tono GHEN (si existe en el original)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## TU RESPUESTA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Devuelve SOLO el artículo mejorado completo en formato markdown.

REQUISITOS:
- Incluye TODAS las secciones originales
- Aplica ÚNICAMENTE las mejoras específicas del QA
- Preserva el 95% del contenido original palabra por palabra
- Mantén longitud similar (±5%)
- No incluyas explicaciones, solo el artículo

COMIENZA AHORA con el artículo mejorado:"""

    try:
        time.sleep(CONFIG["api_delay"])
        response = model.generate_content(prompt)
        
        if not hasattr(response, 'text') or not response.text:
            print("❌ No se obtuvo respuesta válida de Gemini")
            return article_content
        
        improved = clean_conversational_response(response.text)
        
        # VALIDACIÓN 1: Detectar si regeneró contenido tipo newsletter/resumen
        newsletter_patterns = [
            "## Resumen Ejecutivo",
            "## Puntos Clave",
            "## Conclusiones Principales",
            "## Ideas Destacadas",
            "## Aspectos Destacados"
        ]
        if any(pattern in improved for pattern in newsletter_patterns):
            print("❌ ERROR: Gemini regeneró contenido tipo newsletter/resumen en lugar de mejorar el artículo")
            print("   Devolviendo artículo original sin cambios")
            return article_content
        
        # VALIDACIÓN 2: Longitud similar (±30% del original)
        min_length = len(article_content) * 0.7
        max_length = len(article_content) * 1.3
        if not (min_length <= len(improved) <= max_length):
            print(f"❌ ERROR: Longitud inválida - Original: {len(article_content)} chars, Mejorado: {len(improved)} chars")
            print(f"   Rango esperado: {min_length:.0f} - {max_length:.0f} chars")
            print("   El artículo mejorado debe tener longitud similar al original")
            return article_content
        
        # VALIDACIÓN 3: Verificar que preserva títulos principales (debe mantener al menos 70%)
        improved_h2_titles = re.findall(r'^##\s+([^\n]+)', improved, re.MULTILINE)
        if len(improved_h2_titles) < len(original_h2_titles) * 0.7:
            print(f"❌ ERROR: Se perdieron secciones - Original: {len(original_h2_titles)} secciones, Mejorado: {len(improved_h2_titles)}")
            print(f"   Secciones originales: {original_h2_titles[:3]}")
            print(f"   Secciones mejoradas: {improved_h2_titles[:3]}")
            return article_content
        
        # VALIDACIÓN 4: Respuesta demasiado corta (menos de 2000 chars mínimo absoluto)
        if len(improved) < 2000:
            print(f"❌ Respuesta demasiado corta ({len(improved)} chars < 2000 mínimo)")
            print("   Un artículo técnico debe tener al menos 2000 caracteres")
            return article_content
        
        # VALIDACIÓN 5: Verificar que contiene el inicio del artículo original
        # (para detectar si solo devolvió el final)
        original_start = article_content[:200].strip()
        if original_start not in improved:
            print("❌ ERROR: El contenido mejorado no contiene el inicio del artículo original")
            print("   Posible causa: Gemini devolvió solo un fragmento")
            print(f"   Inicio original: {original_start[:100]}...")
            return article_content
        
        # VALIDACIÓN 6: Detectar si el artículo fue regenerado completo (cambios < 5%)
        # Un cambio quirúrgico real debería modificar ~5-15% del contenido
        change_percent = abs((len(improved) - len(article_content)) / len(article_content) * 100)
        if change_percent < 1.0:
            print(f"⚠️  ADVERTENCIA: Cambios muy mínimos ({change_percent:.1f}%)")
            print("   Esto podría indicar que Gemini regeneró el artículo en lugar de aplicar mejoras")
            print("   Comparando similitud estructural...")
            
            # Comparar párrafos únicos para detectar regeneración
            original_paragraphs = set([p.strip() for p in article_content.split('\n\n') if len(p.strip()) > 50])
            improved_paragraphs = set([p.strip() for p in improved.split('\n\n') if len(p.strip()) > 50])
            
            matching_paragraphs = len(original_paragraphs & improved_paragraphs)
            total_paragraphs = len(original_paragraphs)
            similarity = (matching_paragraphs / total_paragraphs * 100) if total_paragraphs > 0 else 0
            
            print(f"   📊 Similitud de párrafos: {similarity:.1f}% ({matching_paragraphs}/{total_paragraphs} idénticos)")
            
            if similarity > 95:
                print("   ❌ RECHAZADO: Artículo prácticamente idéntico (>{similarity:.0f}% similar)")
                print("   El QA sugirió mejoras pero Gemini no las aplicó significativamente")
                return article_content
            else:
                print(f"   ✅ Cambios sutiles pero detectables ({100-similarity:.1f}% modificado)")
        
        # Validaciones pasadas ✅
        print("✅ Mejoras aplicadas quirúrgicamente y validadas")
        print(f"   📏 Longitud: {len(article_content)} → {len(improved)} chars ({len(improved)/len(article_content)*100:.1f}%)")
        print(f"   📑 Secciones: {len(original_h2_titles)} → {len(improved_h2_titles)} (preservadas)")
        print(f"   ✅ Inicio del artículo preservado")
        print(f"   📝 Cambio de contenido: {change_percent:.1f}%")
        return improved
            
    except Exception as e:
        print(f"❌ Error al aplicar mejoras: {str(e)}")
        return article_content


def extract_qa_improvements(qa_report: str) -> List[Dict[str, str]]:
    """
    [FUNCIÓN LEGACY - Ya no se usa, se mantiene por compatibilidad]
    
    Extrae las mejoras específicas del reporte QA.
    Nota: La nueva función apply_qa_improvements_surgical() usa Gemini directamente.
    
    Args:
        qa_report: Reporte QA completo
    
    Returns:
        List[Dict]: Lista de mejoras a aplicar
    """
    # Esta función ya no se usa en el flujo principal
    # Se mantiene por compatibilidad con código legacy
    return []


def apply_qa_improvements(article_content: str, improvements: List[Dict[str, str]]) -> str:
    """
    [FUNCIÓN LEGACY - Ya no se usa]
    
    La funcionalidad de aplicar mejoras ahora la maneja apply_qa_improvements_surgical()
    que es más robusta y previene regeneración completa del contenido.
    """
    return article_content


def integrate_missing_keyword(content: str, keyword: str, description: str) -> str:
    """
    [FUNCIÓN LEGACY - Ya no se usa]
    """
    return content


def smooth_keyword_integration(content: str, keyword: str) -> str:
    """
    [FUNCIÓN LEGACY - Ya no se usa]
    """
    return content


def expand_section_content(content: str, section: str) -> str:
    """
    [FUNCIÓN LEGACY - Ya no se usa]
    """
    return content


def load_seo_keywords_from_analysis(csv_path):
    """
    Carga keywords desde SEO_Analysis_Results.csv priorizando análisis de competencia.
    
    Args:
        csv_path: Ruta al archivo SEO_Analysis_Results.csv
    
    Returns:
        dict: Diccionario con keywords extraídas del análisis SEO
    """
    try:
        df = pd.read_csv(csv_path)
        print(f"📊 Análisis SEO cargado: {len(df)} resultados analizados")
        
        # Extraer keywords del análisis SEO
        all_keywords = []
        all_questions = []
        
        for _, row in df.iterrows():
            seo_analysis = str(row.get('SEO Analysis', ''))
            
            # Extraer keywords mencionadas en el análisis
            keywords_in_analysis = extract_keywords_from_seo_analysis(seo_analysis)
            all_keywords.extend(keywords_in_analysis)
            
            # Extraer preguntas mencionadas en el análisis
            questions_in_analysis = extract_questions_from_seo_analysis(seo_analysis)
            all_questions.extend(questions_in_analysis)
        
        # Limpiar y deduplicar
        unique_keywords = list(set([k for k in all_keywords if len(k) > 3]))
        unique_questions = list(set([q for q in all_questions if len(q) > 10]))
        
        print(f"🔑 Keywords SEO extraídas: {len(unique_keywords)}")
        print(f"❓ Preguntas SEO extraídas: {len(unique_questions)}")
        
        return {
            'keywords': unique_keywords[:50],  # Top 50 keywords más relevantes
            'questions': unique_questions[:20]  # Top 20 preguntas más relevantes
        }
        
    except Exception as e:
        print(f"❌ Error cargando análisis SEO: {str(e)}")
        return {'keywords': [], 'questions': []}


def extract_keywords_from_seo_analysis(analysis_text):
    """Extrae keywords mencionadas en el análisis SEO."""
    keywords = []
    lines = analysis_text.split('\n')
    
    # Patrones para buscar keywords (en inglés y español)
    keyword_patterns = [
        'Keywords:', 'keywords:', 'Key terms:', 'key terms:',
        'Main keywords:', 'main keywords:', 'Primary keywords:',
        'Keywords extracted:', 'keywords extracted:'
    ]
    
    for line in lines:
        line_lower = line.lower()
        for pattern in keyword_patterns:
            if pattern.lower() in line_lower:
                # Extraer texto después del patrón
                parts = line.split(':', 1)
                if len(parts) > 1:
                    keyword_text = parts[1].strip()
                    # Dividir por comas, puntos, guiones y limpiar
                    for separator in [',', '.', '-', ';', '|']:
                        keyword_text = keyword_text.replace(separator, ',')
                    
                    for kw in keyword_text.split(','):
                        kw_clean = kw.strip().strip('`').strip('"').strip("'").strip('*').strip()
                        if len(kw_clean) > 3 and kw_clean.lower() not in [k.lower() for k in keywords]:
                            keywords.append(kw_clean)
    
    # Si no encontramos keywords con patrones, buscar palabras clave comunes
    if not keywords:
        # Buscar palabras relacionadas con escritura
        writing_keywords = [
            'writing', 'write', 'escritura', 'escribir', 'redacción', 'redactar',
            'book', 'libro', 'article', 'artículo', 'content', 'contenido',
            'story', 'historia', 'narrative', 'narrativa', 'creative', 'creativo',
            'author', 'autor', 'writer', 'escritor', 'publishing', 'publicación'
        ]
        
        text_lower = analysis_text.lower()
        for kw in writing_keywords:
            if kw in text_lower and kw not in [k.lower() for k in keywords]:
                keywords.append(kw.title())
    
    return keywords[:20]  # Limitar a 20 keywords


def extract_questions_from_seo_analysis(analysis_text):
    """Extrae preguntas mencionadas en el análisis SEO."""
    questions = []
    lines = analysis_text.split('\n')
    
    # Patrones para buscar preguntas (en inglés y español)
    question_patterns = [
        '- ', '• ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ',
        'Q:', 'Question:', 'Pregunta:', '¿', '?'
    ]
    
    for line in lines:
        line_stripped = line.strip()
        
        # Buscar líneas que contengan preguntas
        if '?' in line_stripped:
            # Limpiar la línea y extraer la pregunta
            for pattern in question_patterns:
                if line_stripped.startswith(pattern):
                    question = line_stripped[len(pattern):].strip()
                    if len(question) > 10 and question not in questions:
                        questions.append(question)
                    break
            else:
                # Si no empieza con un patrón, pero contiene '?', tomarla completa
                if len(line_stripped) > 10 and line_stripped not in questions:
                    questions.append(line_stripped)
    
    # NO generar preguntas hardcodeadas - solo usar las que se encuentren en el análisis
    return questions[:15]  # Limitar a 15 preguntas


def extract_keywords_from_search_titles(search_results_df):
    """
    Extrae keywords relevantes de los títulos de los resultados de búsqueda.
    
    Args:
        search_results_df: DataFrame con los resultados de búsqueda
    
    Returns:
        list: Lista de keywords extraídas de los títulos
    """
    keywords = []
    
    if search_results_df.empty:
        return keywords
    
    for title in search_results_df['title'].dropna():
        title_lower = title.lower()
        
        # Extraer palabras clave relevantes
        relevant_words = []
        
        # Palabras relacionadas con escritura
        writing_terms = [
            'escribir', 'escritura', 'libro', 'autor', 'escritor', 'redacción',
            'historia', 'narrativa', 'creativo', 'contenido', 'texto',
            'manuscrito', 'publicar', 'editorial', 'publicación'
        ]
        
        # Buscar términos relevantes en el título
        for term in writing_terms:
            if term in title_lower:
                relevant_words.append(term)
        
        # Agregar palabras de longitud media (4-15 caracteres)
        words = title_lower.split()
        for word in words:
            clean_word = ''.join(c for c in word if c.isalnum())
            if 4 <= len(clean_word) <= 15 and clean_word not in ['para', 'como', 'que', 'con', 'sin', 'desde', 'hasta']:
                relevant_words.append(clean_word)
        
        keywords.extend(relevant_words)
    
    # Limpiar y deduplicar
    unique_keywords = list(set([kw for kw in keywords if len(kw) > 3]))
    
    return unique_keywords[:20]  # Limitar a 20 keywords


# ============================================================================
# NUEVAS FUNCIONES PARA LEO CONTENT GENERATION
# ============================================================================

def load_leo_context(level="full"):
    """
    Carga los archivos de contexto de GHEN (personalidad técnica).
    Mantiene nombre leo_context por compatibilidad con código existente.
    
    Sistema híbrido con dos niveles:
    - "base": Voz técnica neutral sin proyectos personales (personalidad_base.md)
    - "full": Voz con experiencia personal y stack específico (personalidad_completa.md)
    
    Args:
        level (str): "base" para contenido neutral, "full" para contenido con experiencia personal
    
    Returns:
        dict: Diccionario con las claves 'personality', 'project', 'audience', 'level'
    """
    context = {
        'personality': '',
        'project': '',
        'audience': '',
        'level': level
    }
    
    try:
        # Seleccionar archivo según nivel
        if level == "base":
            personality_path = 'GHEN/personalidad_base.md'
            print("✅ Personalidad técnica de GHEN cargada (NIVEL BASE: neutral, sin proyectos personales)")
        else:  # level == "full" (default)
            personality_path = 'GHEN/personalidad_completa.md'
            print("✅ Personalidad técnica de GHEN cargada (NIVEL COMPLETO: con experiencias y proyectos)")
        
        # Cargar personalidad técnica de GHEN
        with open(personality_path, 'r', encoding='utf-8') as f:
            context['personality'] = f.read()
    except FileNotFoundError:
        print(f"⚠️  Archivo {personality_path} no encontrado, usando personalidad por defecto")
        context['personality'] = 'Contenido técnico profesional para desarrolladores y arquitectos.'
    
    # Los archivos project y audience son opcionales
    # Si existen, se cargan; si no, quedan vacíos
    try:
        with open('.github/project-definitions.md', 'r', encoding='utf-8') as f:
            context['project'] = f.read()
        print("✅ Definición del proyecto cargada")
    except FileNotFoundError:
        pass  # Opcional
    
    try:
        with open('.github/perfilado_cliente.md', 'r', encoding='utf-8') as f:
            context['audience'] = f.read()
        print("✅ Perfil de audiencia cargado")
    except FileNotFoundError:
        pass  # Opcional
    
    return context


# Alias para compatibilidad
load_ghen_context = load_leo_context


def build_system_prompt(leo_context):
    """
    Construye contexto adicional para el prompt (complementa system_instruction de config.py).
    
    NOTA: La personalidad base está definida como system_instruction en config.py.
    Esta función añade contexto adicional solo cuando se usa nivel "full".
    
    Args:
        leo_context (dict): Diccionario con el contexto de GHEN (personalidad técnica)
    
    Returns:
        str: Contexto adicional (vacío si es nivel base, completo si es full)
    """
    # Si es nivel base, la personalidad ya está en system_instruction
    # Solo añadimos contexto adicional si es nivel "full"
    if leo_context.get('level') == 'base':
        return ""  # System instruction ya tiene la personalidad base
    
    # Nivel "full": añadir contexto de proyectos y experiencia personal
    additional_context = f"""
# CONTEXTO ADICIONAL (Nivel Full)

{leo_context.get('project', '')}

# AUDIENCIA ESPECÍFICA

{leo_context.get('audience', '')}

# EXPERIENCIA PERSONAL AUTORIZADA
En el nivel "full", puedes hacer referencias a experiencia personal cuando sea relevante:
- Proyectos de consultoría, hackathons, implementaciones reales
- Primera persona en lecciones aprendidas y retrospectivas
- Stack tecnológico preferido con justificación técnica
"""
    
    return additional_context


def suggest_keyword_from_topic(topic, leo_context=None):
    """
    Sugiere una keyword semilla óptima a partir de un tópico.
    
    Args:
        topic (str): El tópico general del que se quiere escribir
        leo_context (dict, optional): Contexto de LEO
    
    Returns:
        str: Keyword sugerida
    """
    if not model:
        print("❌ Modelo Gemini no configurado")
        return None
    
    # Cargar contexto si no se proporciona
    if leo_context is None:
        leo_context = load_leo_context()
    
    system_prompt = build_system_prompt(leo_context)
    
    prompt = f"""Basándote en el siguiente tópico, sugiere UNA keyword semilla ideal para crear contenido SEO optimizado.

Tópico: {topic}

La keyword debe:
- Tener volumen de búsqueda potencial
- Ser específica y relevante para nuestra audiencia (escritores y autores)
- Ser natural y conversacional
- Estar relacionada con escritura, edición, publicación o el mundo editorial

Responde SOLAMENTE con la keyword sugerida, sin explicaciones adicionales."""

    try:
        # Construir el prompt completo
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = model.generate_content(full_prompt)
        keyword = response.text.strip()
        
        print(f"✅ Keyword sugerida para '{topic}': {keyword}")
        return keyword
        
    except Exception as e:
        print(f"❌ Error al sugerir keyword: {str(e)}")
        return None


def extract_and_summarize_url(url, leo_context=None):
    """
    Extrae el contenido de una URL y genera un resumen con puntos clave.
    
    Args:
        url (str): URL del newsletter o artículo
        leo_context (dict, optional): Contexto de LEO
    
    Returns:
        dict: {'summary': str, 'key_points': list, 'suggested_topics': list, 'raw_analysis': str, 'original_content': str}
    """
    if not model:
        print("❌ Modelo Gemini no configurado")
        return None
    
    # Cargar contexto si no se proporciona
    if leo_context is None:
        leo_context = load_leo_context()
    
    print(f"🔍 Extrayendo contenido de: {url}")
    
    # Extraer contenido
    content = scrape_article(url)
    
    if not content or len(content) < 100:
        print("❌ No se pudo extraer contenido suficiente de la URL")
        return None
    
    print(f"✅ Contenido extraído: {len(content)} caracteres")
    
    system_prompt = build_system_prompt(leo_context)
    
    prompt = f"""Analiza el siguiente contenido de un newsletter o artículo y:

1. Genera un resumen ejecutivo (máximo 200 palabras)
2. Extrae 5 puntos clave o insights principales
3. Sugiere 3 temas de artículos que podríamos crear basados en este contenido

Contenido:
{content[:8000]}

Responde en formato:

## Resumen
[tu resumen aquí]

## Puntos Clave
1. [punto 1]
2. [punto 2]
3. [punto 3]
4. [punto 4]
5. [punto 5]

## Temas Sugeridos
1. [tema 1]
2. [tema 2]
3. [tema 3]
"""

    try:
        full_prompt = f"{system_prompt}\n\n{prompt}"
        response = model.generate_content(full_prompt)
        
        analysis = response.text
        
        print("✅ Análisis del contenido completado")
        
        # Parsear la respuesta y guardar TODO el contenido original
        result = {
            'raw_analysis': analysis,
            'original_content': content,  # CAMBIO: Guardar TODO el contenido, no solo 2000 chars
            'url': url
        }
        
        return result
        
    except Exception as e:
        print(f"❌ Error al analizar contenido: {str(e)}")
        return None


def generate_article_with_context(keyword, context_sources, leo_context=None):
    """
    Genera un artículo usando keyword y fuentes de contexto adicionales.
    
    Args:
        keyword (str): Keyword principal
        context_sources (list): Lista de strings con contexto adicional
        leo_context (dict, optional): Contexto de LEO
    
    Returns:
        str: Artículo generado
    """
    if not model:
        print("❌ Modelo Gemini no configurado")
        return None
    
    # Cargar contexto si no se proporciona
    if leo_context is None:
        leo_context = load_leo_context()
    
    system_prompt = build_system_prompt(leo_context)
    
    # Construir el contexto combinado
    combined_context = "\n\n---\n\n".join(context_sources)
    
    # Detectar si es un artículo de actualidad/tendencias (basado en contexto de newsletter)
    is_newsletter_based = any('NEWSLETTER' in source or 'ANÁLISIS DEL NEWSLETTER' in source for source in context_sources)
    
    if is_newsletter_based:
        # Prompt especializado para artículos de Actualidad y Tendencias
        prompt = f"""Genera un artículo técnico profesional sobre: "{keyword}"

## Contexto: Newsletter y Análisis

{combined_context[:12000]}

## Instrucciones

Crea un artículo de actualidad técnica basado en el contenido del newsletter.

**Requisitos:**
- 1500-2000 palabras
- Sintetiza las tendencias técnicas clave
- Analiza implicaciones prácticas para producción
- Incluye insights aplicables (arquitectura, código, decisiones)
- Termina con conclusión sobre impacto técnico

**Formato:**
- Empieza DIRECTAMENTE con # Título (sin meta-comentarios)
- Usa ## y ### para organizar secciones
- No copies textualmente - analiza y añade perspectiva

Formato: Markdown"""
    else:
        # Prompt estándar para artículos basados en investigación
        prompt = f"""Genera un artículo técnico completo sobre: "{keyword}"

## Contexto de Investigación

{combined_context[:10000]}

## Instrucciones

**Requisitos:**
- 1500-2000 palabras en español
- Incluye ejemplos de código o arquitectura cuando sea relevante
- Termina con conclusión sobre implicaciones prácticas

**Formato:**
- Empieza DIRECTAMENTE con # Título (sin meta-comentarios)
- Usa ## y ### para estructura clara

Formato: Markdown"""

    try:
        # Si hay contexto adicional (nivel full), añadirlo al prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        article_type = "actualidad" if is_newsletter_based else "investigación"
        print(f"🎨 Generando artículo de {article_type}...")
        response = model.generate_content(full_prompt)
        
        article = response.text
        
        print(f"✅ Artículo generado ({len(article)} caracteres)")
        return article
        
    except Exception as e:
        print(f"❌ Error al generar artículo: {str(e)}")
        return None


def extract_newsletter_from_gmail(gmail_url, leo_context=None):
    """
    Extrae y analiza un newsletter directamente desde Gmail usando Gmail API.
    
    Args:
        gmail_url (str): URL de Gmail (e.g., https://mail.google.com/mail/u/0/#inbox/1849085179733622850)
        leo_context (dict, optional): Contexto de GHEN
    
    Returns:
        dict: {'raw_analysis': str, 'original_content': str, 'url': str, 'subject': str}
    """
    try:
        from . import gmail
        
        # Extraer message ID de la URL
        message_id = gmail.extract_message_id_from_url(gmail_url)
        
        if not message_id:
            print("❌ No se pudo extraer el ID del mensaje de la URL")
            print("   Formatos soportados:")
            print("   - https://mail.google.com/mail/u/0/#inbox/123456789")
            print("   - https://mail.google.com/mail/u/0/?...&permmsgid=msg-f:123456789")
            return None
        
        print(f"📧 Extrayendo newsletter con ID: {message_id}")
        
        # Autenticar con Gmail API
        service = gmail.authenticate_gmail()
        if not service:
            return None
        
        # Obtener el contenido del newsletter
        newsletter_data = gmail.get_newsletter_by_message_id(service, message_id)
        
        if not newsletter_data:
            return None
        
        # Usar el contenido HTML si está disponible, sino el texto
        content = newsletter_data['html'] if newsletter_data['html'] else newsletter_data['body']
        
        if not content:
            print("⚠️  El newsletter no tiene contenido")
            return None
        
        print(f"✅ Newsletter obtenido: {len(content)} caracteres")
        print(f"📋 Asunto: {newsletter_data['subject']}")
        print(f"📨 De: {newsletter_data['from']}")
        
        # Analizar con Gemini (reutilizar lógica de extract_and_summarize_url)
        if leo_context is None:
            leo_context = load_leo_context()
        
        system_prompt = build_system_prompt(leo_context)
        
        prompt = f"""Analiza el siguiente newsletter técnico y extrae la información clave.

Asunto: {newsletter_data['subject']}
De: {newsletter_data['from']}

Contenido:
{content[:15000]}

# Instrucciones

Genera un análisis estructurado que incluya:

1. **Resumen Ejecutivo**: Síntesis de los temas principales (2-3 párrafos)
2. **Puntos Clave**: 5 insights o temas técnicos más relevantes
3. **Temas Sugeridos para Artículos**: 3 ideas de artículos técnicos que podrían generarse a partir de este contenido

Formato:

## Resumen
[tu resumen aquí]

## Puntos Clave
1. [punto 1]
2. [punto 2]
3. [punto 3]
4. [punto 4]
5. [punto 5]

## Temas Sugeridos
1. [tema 1]
2. [tema 2]
3. [tema 3]
"""
        
        full_prompt = f"{system_prompt}\n\n{prompt}"
        response = model.generate_content(full_prompt)
        
        analysis = response.text
        
        print("✅ Análisis del newsletter completado")
        
        return {
            'raw_analysis': analysis,
            'original_content': content,
            'url': newsletter_data['url'],
            'subject': newsletter_data['subject'],
            'from': newsletter_data['from']
        }
        
    except ImportError as e:
        print(f"❌ Error: Módulo gmail no disponible. Detalle: {e}")
        print("   Instala las dependencias: pip install google-auth google-auth-oauthlib google-api-python-client")
        return None
    except Exception as e:
        print(f"❌ Error al extraer newsletter desde Gmail: {str(e)}")
        return None


def list_gmail_newsletters(sender_filter=None, max_results=10, only_primary=True):
    """
    Lista newsletters disponibles en Gmail (helper para selección interactiva).
    
    Args:
        sender_filter (str or list, optional): Filtrar por remitente(s)
        max_results (int): Número máximo de newsletters a listar
        only_primary (bool): Si True, busca solo en bandeja Principal (excluye Promociones)
    
    Returns:
        list: Lista de dicts con info de newsletters
    """
    try:
        from . import gmail
        
        service = gmail.authenticate_gmail()
        if not service:
            return []
        
        newsletters = gmail.list_newsletters(
            service,
            sender_filter=sender_filter,
            max_results=max_results,
            only_primary=only_primary
        )
        
        return newsletters
        
    except ImportError:
        print("❌ Error: Módulo gmail no disponible")
        return []
    except Exception as e:
        print(f"❌ Error al listar newsletters: {str(e)}")
        return []


def add_source_links_to_article(article_text, context_sources):
    """
    Agrega una sección de referencias al final del artículo con links a las fuentes.
    
    Args:
        article_text (str): Texto del artículo generado
        context_sources (list): Lista de strings con contexto (deben contener URLs)
    
    Returns:
        str: Artículo con sección de referencias agregada
    """
    import re
    
    if not context_sources:
        return article_text
    
    # Extraer URLs y títulos de las fuentes
    sources = []
    
    for source in context_sources:
        # Buscar URLs en el contexto
        urls = re.findall(r'https?://[^\s<>"\\)\\]]+', source)
        
        # Buscar títulos (líneas que empiezan con # )
        titles = re.findall(r'^# (.+)$', source, re.MULTILINE)
        
        # Emparejar URLs con títulos cuando sea posible
        for i, url in enumerate(urls):
            # Limpiar URL de caracteres finales comunes
            url = url.rstrip('.,;:!?')
            
            # Intentar encontrar un título relevante
            title = None
            if i < len(titles):
                title = titles[i].strip()
            
            # Extraer dominio como título si no hay otro
            if not title:
                domain_match = re.search(r'https?://(?:www\\.)?([^/]+)', url)
                if domain_match:
                    title = domain_match.group(1)
            
            sources.append({
                'url': url,
                'title': title or url,
                'source_text': source[:200]  # Guardar snippet para contexto
            })
    
    # Eliminar duplicados (misma URL)
    seen_urls = set()
    unique_sources = []
    for source in sources:
        if source['url'] not in seen_urls:
            seen_urls.add(source['url'])
            unique_sources.append(source)
    
    # Si no hay fuentes con URLs, retornar sin cambios
    if not unique_sources:
        return article_text
    
    # Construir sección de referencias
    references_section = "\n\n---\n\n## 📚 Referencias y Fuentes\n\n"
    references_section += "Este artículo se ha elaborado consultando las siguientes fuentes:\n\n"
    
    for i, source in enumerate(unique_sources, 1):
        references_section += f"{i}. [{source['title']}]({source['url']})\n"
    
    # Agregar al final del artículo
    article_with_refs = article_text + references_section
    
    print(f"✅ Agregadas {len(unique_sources)} referencias al artículo")
    
    return article_with_refs



def clean_article_metatext(article_text):
    """
    Elimina meta-texto del modelo (reflexiones internas) del inicio del artículo.
    
    Args:
        article_text (str): Texto del artículo generado
    
    Returns:
        str: Artículo sin meta-texto
    """
    import re
    
    # Buscar el primer encabezado de nivel 1 (título del artículo)
    match = re.search(r'^#\s+[^#]', article_text, re.MULTILINE)
    
    if match:
        # Si hay un título H1, cortar todo lo anterior
        article_text = article_text[match.start():]
        print("✅ Meta-texto eliminado del artículo")
    
    return article_text


def add_source_links_to_article(article_text, context_sources):
    """
    Agrega una sección de referencias al final del artículo con links a las fuentes.
    Filtra URLs de tracking y solo incluye dominios relevantes.
    
    Args:
        article_text (str): Texto del artículo generado
        context_sources (list): Lista de strings con contexto (deben contener URLs)
    
    Returns:
        str: Artículo con sección de referencias agregada
    """
    import re
    
    if not context_sources:
        return article_text
    
    # Dominios de tracking a excluir
    tracking_domains = [
        'resend-links.com',
        'click.', 
        'track.',
        'redirect.',
        'unsubscribe.',
        'email.'
    ]
    
    # Extraer URLs y títulos de las fuentes
    sources = []
    
    for source in context_sources:
        # Buscar URLs en el contexto
        urls = re.findall(r'https?://[^\s<>"\)\]]+', source)
        
        # Buscar títulos (líneas que empiezan con # )
        titles = re.findall(r'^# (.+)$', source, re.MULTILINE)
        
        # Emparejar URLs con títulos cuando sea posible
        for i, url in enumerate(urls):
            # Limpiar URL de caracteres finales comunes
            url = url.rstrip('.,;:!?')
            
            # Filtrar URLs de tracking
            is_tracking = any(domain in url.lower() for domain in tracking_domains)
            if is_tracking:
                continue
            
            # Intentar encontrar un título relevante
            title = None
            if i < len(titles):
                title = titles[i].strip()
            
            # Extraer dominio como título si no hay otro
            if not title:
                domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                if domain_match:
                    title = domain_match.group(1)
            
            sources.append({
                'url': url,
                'title': title or url,
                'source_text': source[:200]  # Guardar snippet para contexto
            })
    
    # Eliminar duplicados (misma URL)
    seen_urls = set()
    unique_sources = []
    for source in sources:
        if source['url'] not in seen_urls:
            seen_urls.add(source['url'])
            unique_sources.append(source)
    
    # Si no hay fuentes con URLs, retornar sin cambios
    if not unique_sources:
        print("⚠️  No se encontraron URLs válidas para referencias")
        return article_text
    
    # Construir sección de referencias
    references_section = "\n\n---\n\n## 📚 Referencias y Fuentes\n\n"
    references_section += "Este artículo se ha elaborado consultando las siguientes fuentes:\n\n"
    
    for i, source in enumerate(unique_sources, 1):
        references_section += f"{i}. [{source['title']}]({source['url']})\n"
    
    # Agregar al final del artículo
    article_with_refs = article_text + references_section
    
    print(f"✅ Agregadas {len(unique_sources)} referencias al artículo")
    
    return article_with_refs


def generate_featured_image_prompt(article_text, article_title):
    """
    Genera un prompt optimizado para crear una imagen destacada del artículo usando Gemini.
    
    ENFOQUE: Metáforas visuales creativas, estilos artísticos variados, NO ilustraciones
    técnicas genéricas tipo "chip con rayitos".
    
    Args:
        article_text (str): Texto completo del artículo
        article_title (str): Título del artículo
    
    Returns:
        str: Prompt optimizado para generación de imagen, o None si falla
    """
    import random
    
    # ESTILOS ARTÍSTICOS CREATIVOS (rotamos para variedad)
    artistic_styles = [
        "street art mural style, bold spray paint textures, urban graffiti aesthetic",
        "vintage science poster from 1960s, retro futurism, paper texture, faded colors",
        "collage art style, mixed media with cut paper shapes, analog textures",
        "risograph print style, limited color palette with halftone dots, slight misregistration",
        "editorial illustration style, bold geometric shapes, magazine cover aesthetic",
        "woodblock print inspired, strong lines, japanese ukiyo-e influence with modern twist",
        "surrealist painting style, unexpected juxtapositions, dreamlike quality",
        "bauhaus design style, primary colors, geometric forms, constructivist influence",
        "low-poly 3D render style, faceted surfaces, soft gradients, minimal aesthetic",
        "linocut print style, hand-carved texture, high contrast, folk art influence"
    ]
    
    # PALETAS DE COLOR CREATIVAS (no siempre azul/violeta tech)
    color_palettes = [
        "burnt orange, deep teal, and cream",
        "electric coral, midnight blue, and gold",
        "sage green, terracotta, and warm white",
        "hot pink, electric yellow, and black",
        "dusty rose, navy, and copper",
        "lime green, purple, and off-white",
        "rust red, olive green, and sand",
        "cyan, magenta, and bright yellow",
        "forest green, burnt sienna, and beige",
        "indigo, peach, and silver"
    ]
    
    # Seleccionar estilo y paleta (semi-aleatorio pero consistente por artículo)
    # Usar hash del título para consistencia si se regenera
    style_seed = hash(article_title) % len(artistic_styles)
    color_seed = hash(article_title[::-1]) % len(color_palettes)  # reverse para variar
    
    selected_style = artistic_styles[style_seed]
    selected_colors = color_palettes[color_seed]
    
    try:
        print("🎨 Generando prompt para imagen destacada...")
        print(f"   🎭 Estilo seleccionado: {selected_style.split(',')[0]}")
        print(f"   🎨 Paleta: {selected_colors}")
        print("   📊 Analizando artículo para crear METÁFORA visual única...\n")
        
        # PASO 1: Extraer METÁFORA CONCEPTUAL (no literal)
        metaphor_prompt = f"""Eres un director creativo de una revista de arte.

**ARTÍCULO (fragmento):**
{article_text[:4000]}

**TÍTULO:** {article_title}

**TU TAREA:** Piensa en una METÁFORA VISUAL CREATIVA para este artículo. 

NO quiero representaciones literales de tecnología (nada de chips, circuitos, cables, pantallas brillantes, rayos de luz, robots, cerebros digitales).

SÍ quiero metáforas usando:
- Objetos cotidianos transformados (e.g., "tetera sirviendo datos como té")
- Escenas de la naturaleza reimaginadas (e.g., "bosque donde los árboles son columnas de código")
- Situaciones absurdas/surrealistas (e.g., "biblioteca donde los libros flotan ordenándose solos")
- Personajes haciendo actividades inesperadas (e.g., "chef cocinando con ingredientes que son APIs")
- Máquinas vintage haciendo cosas modernas (e.g., "máquina de escribir antigua generando hologramas")

**EJEMPLOS DE BUENAS METÁFORAS:**

Artículo sobre "RAG y retrieval": 
→ "Un bibliotecario gigante pescando libros específicos de un océano infinito con una red dorada"

Artículo sobre "MLOps pipelines":
→ "Una fábrica de caramelos estilo Willy Wonka donde las cintas transportadoras llevan modelos de ML como dulces"

Artículo sobre "Prompt engineering":
→ "Un director de orquesta dirigiendo instrumentos musicales que son burbujas de chat flotantes"

Artículo sobre "Code execution with MCP":
→ "Un mago callejero haciendo trucos donde las cartas son fragmentos de código que se transforman en pájaros"

**RESPONDE CON:**
1. Una descripción de escena metafórica (2-3 oraciones)
2. El elemento central/protagonista de la imagen
3. Un detalle pequeño pero memorable

Solo responde con estos 3 puntos, sin introducción."""

        print("   🔍 Extrayendo metáfora creativa...")
        metaphor_response = model.generate_content(metaphor_prompt)
        time.sleep(CONFIG["api_delay"])
        
        metaphor = metaphor_response.text.strip()
        print(f"   ✅ Metáfora extraída:\n{metaphor}\n")
        
        # PASO 2: Convertir metáfora en prompt de imagen
        final_prompt_request = f"""Convierte esta metáfora visual en un prompt de imagen EN INGLÉS.

**METÁFORA CONCEPTUAL:**
{metaphor}

**ESTILO ARTÍSTICO OBLIGATORIO:**
{selected_style}

**PALETA DE COLORES OBLIGATORIA:**
{selected_colors}

**REGLAS DEL PROMPT:**
1. Máximo 80 palabras
2. Describir la ESCENA, no conceptos abstractos
3. Incluir el ESTILO ARTÍSTICO al final
4. Incluir los COLORES específicos
5. Añadir "16:9 aspect ratio, high quality, no text, no logos"
6. PROHIBIDO: chips, circuitos, código binario, pantallas brillantes, rayos de luz azul, cerebros, robots humanoides
7. El prompt debe sonar como arte, no como tech

**EJEMPLO DE OUTPUT:**

"A giant clockmaker in a steampunk workshop carefully assembling a pocket watch made of tiny dialogue bubbles, each bubble containing miniature conversations, {selected_style}, color palette of {selected_colors}, 16:9 aspect ratio, high quality, no text, no logos"

Genera SOLO el prompt en inglés, sin explicaciones ni comillas."""

        print("   🎨 Generando prompt visual creativo...")
        response = model.generate_content(final_prompt_request)
        time.sleep(CONFIG["api_delay"])
        
        generated_prompt = response.text.strip()
        
        # Limpiar posibles comillas o marcadores de código
        generated_prompt = generated_prompt.strip('"\'`')
        if generated_prompt.startswith('"') or generated_prompt.startswith("'"):
            generated_prompt = generated_prompt[1:]
        if generated_prompt.endswith('"') or generated_prompt.endswith("'"):
            generated_prompt = generated_prompt[:-1]
        
        print(f"\n✅ Prompt creativo generado ({len(generated_prompt)} chars):")
        print(f"   {generated_prompt[:200]}...")
        
        return generated_prompt
        
    except Exception as e:
        print(f"❌ Error al generar prompt de imagen: {str(e)}")
        return None

