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
    Extract text content from a URL using newspaper library with BeautifulSoup fallback.
    
    Args:
        url (str): URL to scrape
    
    Returns:
        str: Extracted text content
    """
    try:
        # Try with newspaper first
        article = Article(url)
        article.download()
        article.parse()
        
        if article.text:
            return article.text
        
        # Fallback to BeautifulSoup
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, 'html.parser')
        article_text = ' '.join([p.get_text() for p in soup.find_all(['p', 'div'])])
        
        return article_text
    
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


def qa_article_coverage(article_content, related_keywords_context, main_query):
    """
    QA agent que revisa la cobertura del artículo vs keywords relacionadas.
    
    Args:
        article_content: Contenido del artículo generado
        related_keywords_context: Contexto de keywords y preguntas
        main_query: Query principal
    
    Returns:
        str: Reporte QA
    """
    keywords = related_keywords_context.get('keywords', [])
    questions = related_keywords_context.get('questions', [])
    
    keywords_text = ", ".join(keywords[:50])
    questions_text = "\n".join([f"- {q}" for q in questions[:30]])
    
    prompt = f"""Genera un reporte QA completo de contenido SEO. Responde DIRECTAMENTE con el reporte en formato markdown, sin introducciones.

**QUERY PRINCIPAL:** {main_query}

**ARTÍCULO A REVISAR:**
{article_content[:10000]}

**KEYWORDS RELACIONADAS QUE DEBÍAN CUBRIRSE:**
{keywords_text}

**PREGUNTAS QUE DEBÍAN RESPONDERSE:**
{questions_text}

**FORMATO REQUERIDO:**

### 1. COBERTURA DE KEYWORDS
- Keywords naturalmente integradas ✅
- Keywords forzadas o mal integradas ⚠️
- Keywords faltantes ❌
- Puntuación: X/10

### 2. COBERTURA DE PREGUNTAS
- Preguntas bien respondidas ✅
- Preguntas parcialmente respondidas ⚠️
- Preguntas no respondidas ❌
- Puntuación: X/10

### 3. COMPLETITUD SEMÁNTICA
- Cobertura del landscape semántico
- Gaps en autoridad topical
- Balance fundamentals vs. avanzado
- Puntuación: X/10

### 4. CALIDAD DEL CONTENIDO
- Coherencia y flujo narrativo
- Profundidad y valor único
- Estructura y legibilidad
- Puntuación: X/10

### 5. RECOMENDACIONES ESPECÍFICAS
- Secciones a expandir
- Keywords a integrar mejor
- Preguntas a responder
- Mejoras estructurales

**IMPORTANTE:** Comienza directamente con el reporte. NO uses frases como "Como experto", "Aquí tienes", etc.

Idioma: {CONFIG["output_language"]}

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
