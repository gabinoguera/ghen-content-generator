"""
Social Media Adapters - Transforma artículos en posts para cada red social.

Características por plataforma:
- Twitter/X: Thread de 5-7 tweets, máx 280 chars c/u, emojis, hashtags
- LinkedIn: Post profesional, máx 3000 chars, tono corporativo
- Reddit: Formato texto largo, sin emojis comerciales, valor para comunidad
- Threads: Similar a Twitter pero más casual, hasta 500 chars

Uso:
    from longcontent_generator.social import generate_all_social_posts
    
    posts = generate_all_social_posts(
        article_path="outputs/articulo_ghen_generado.md",
        article_url="https://ghendigital.com/articulo-slug",
        platforms=["twitter", "linkedin", "reddit", "threads"]
    )
"""

import os
import re
from typing import Optional
from ..config import model, CONFIG

# ============================================================================
# CONFIGURACIÓN POR PLATAFORMA
# ============================================================================

PLATFORM_CONFIG = {
    "twitter": {
        "max_chars": 280,
        "thread_size": 5,  # tweets por thread (sin contar el final con link)
        "tone": "técnico pero accesible, directo, con gancho",
        "emoji_style": "moderado",  # 1-2 por tweet
        "hashtags": 2,  # máximo por tweet
    },
    "linkedin": {
        "max_chars": 2500,  # Dejamos margen del límite de 3000
        "tone": "profesional, insights de valor, orientado a decisores tech",
        "emoji_style": "mínimo",  # solo para estructura visual
        "hashtags": 5,  # al final del post
    },
    "reddit": {
        "max_chars": 1500,
        "tone": "técnico puro, sin marketing, valor para la comunidad",
        "emoji_style": "ninguno",  # Reddit odia emojis comerciales
        "hashtags": 0,
        "subreddits": ["MachineLearning", "artificial", "LocalLLaMA", "Python"],
    },
    "threads": {
        "max_chars": 500,
        "tone": "casual técnico, conversacional, storytelling",
        "emoji_style": "natural",
        "hashtags": 3,
    },
}


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def generate_all_social_posts(
    article_path: str,
    article_url: str,
    article_title: Optional[str] = None,
    platforms: list = None
) -> dict:
    """
    Genera posts para todas las plataformas especificadas.
    
    Args:
        article_path: Ruta al archivo markdown del artículo
        article_url: URL canónica del artículo en WordPress
        article_title: Título del artículo (se extrae si no se proporciona)
        platforms: Lista de plataformas ["twitter", "linkedin", "reddit", "threads"]
    
    Returns:
        dict: {
            "twitter": {"thread": [...], "raw": "..."},
            "linkedin": {"post": "...", "raw": "..."},
            ...
        }
    """
    if platforms is None:
        platforms = ["twitter", "linkedin"]  # Default más comunes
    
    # Leer artículo
    if not os.path.exists(article_path):
        print(f"❌ No se encontró el artículo: {article_path}")
        return {}
    
    with open(article_path, 'r', encoding='utf-8') as f:
        article_content = f.read()
    
    # Extraer título si no se proporciona
    if not article_title:
        title_match = re.search(r'^#\s+(.+)$', article_content, re.MULTILINE)
        article_title = title_match.group(1) if title_match else "Nuevo artículo"
    
    print(f"\n{'='*60}")
    print(f"📱 GENERANDO POSTS PARA REDES SOCIALES")
    print(f"{'='*60}")
    print(f"📄 Artículo: {article_title[:50]}...")
    print(f"🔗 URL: {article_url}")
    print(f"📊 Plataformas: {', '.join(platforms)}")
    
    results = {}
    
    # Generar para cada plataforma
    generators = {
        "twitter": generate_twitter_thread,
        "linkedin": generate_linkedin_post,
        "reddit": generate_reddit_post,
        "threads": generate_threads_post,
    }
    
    for platform in platforms:
        if platform in generators:
            print(f"\n🔄 Generando para {platform.upper()}...")
            results[platform] = generators[platform](
                article_content=article_content,
                article_title=article_title,
                article_url=article_url
            )
            if results[platform]:
                print(f"   ✅ {platform.capitalize()} generado")
            else:
                print(f"   ❌ Error generando {platform}")
        else:
            print(f"   ⚠️ Plataforma no soportada: {platform}")
    
    # Guardar resultados
    _save_social_posts(results, article_title)
    
    return results


# ============================================================================
# GENERADORES POR PLATAFORMA
# ============================================================================

def generate_twitter_thread(
    article_content: str,
    article_title: str,
    article_url: str
) -> dict:
    """
    Genera un thread de Twitter/X optimizado.
    
    Returns:
        dict: {
            "thread": [tweet1, tweet2, ...],
            "raw": "texto completo del thread"
        }
    """
    if not model:
        return None
    
    config = PLATFORM_CONFIG["twitter"]
    
    prompt = f"""Transforma este artículo técnico en un thread de Twitter/X.

## Artículo
Título: {article_title}
URL: {article_url}

{article_content[:6000]}

## Instrucciones ESTRICTAS

Genera exactamente {config['thread_size']} tweets + 1 tweet final con el link.

### Estructura del thread:
1. **Tweet 1 (Hook)**: Pregunta provocadora o dato impactante que genere curiosidad
2. **Tweets 2-{config['thread_size']}**: Puntos clave del artículo, insights técnicos
3. **Tweet final**: CTA + link al artículo completo

### Reglas por tweet:
- MÁXIMO {config['max_chars']} caracteres (CRÍTICO - Twitter trunca)
- 1-2 emojis máximo por tweet (al inicio o para bullets)
- Numeración: 1/, 2/, etc. al inicio
- Último tweet: incluir exactamente "{article_url}"
- Máximo {config['hashtags']} hashtags (solo en tweet 1 y último)

### Tono:
- Técnico pero accesible
- Directo, sin rodeos
- Genera curiosidad para leer el artículo completo
- NO uses "Hilo:" o "Thread:" al inicio

### Formato de salida:
Cada tweet separado por una línea con "---"

Ejemplo:
1/ 🚀 [Hook impactante aquí]
---
2/ [Insight clave]
---
...
---
6/ 📖 Artículo completo: {article_url} #IA #Tech
"""

    try:
        response = model.generate_content(prompt)
        raw_thread = response.text.strip()
        
        # Parsear tweets
        tweets = [t.strip() for t in raw_thread.split('---') if t.strip()]
        
        # Validar longitud de cada tweet
        validated_tweets = []
        for i, tweet in enumerate(tweets):
            if len(tweet) > config['max_chars']:
                # Truncar si es necesario
                tweet = tweet[:config['max_chars']-3] + "..."
            validated_tweets.append(tweet)
        
        return {
            "thread": validated_tweets,
            "raw": raw_thread,
            "tweet_count": len(validated_tweets)
        }
        
    except Exception as e:
        print(f"   ❌ Error generando Twitter thread: {e}")
        return None


def generate_linkedin_post(
    article_content: str,
    article_title: str,
    article_url: str
) -> dict:
    """
    Genera un post de LinkedIn profesional.
    
    Returns:
        dict: {
            "post": "texto del post",
            "raw": "texto completo"
        }
    """
    if not model:
        return None
    
    config = PLATFORM_CONFIG["linkedin"]
    
    prompt = f"""Transforma este artículo técnico en un post de LinkedIn.

## Artículo
Título: {article_title}
URL: {article_url}

{article_content[:6000]}

## Instrucciones ESTRICTAS

Genera UN SOLO post de LinkedIn optimizado.

### Estructura:
1. **Hook (1-2 líneas)**: Insight provocador o pregunta que detenga el scroll
2. **Cuerpo (5-8 bullets)**: Puntos clave con valor inmediato
3. **CTA + Link**: Invitación a leer más + URL
4. **Hashtags**: 3-5 hashtags relevantes al final

### Reglas:
- MÁXIMO {config['max_chars']} caracteres totales
- Usa saltos de línea para legibilidad (LinkedIn los respeta)
- Bullets con → o • (no emojis excesivos)
- Tono profesional pero no corporativo aburrido
- Dirigido a: CTOs, Tech Leads, Developers seniors
- Primera línea CRUCIAL (es lo único que se ve antes de "ver más")

### Tono:
- Profesional y técnico
- Insights de valor real (no fluff)
- Orientado a quien toma decisiones técnicas
- Evita: "¡Increíble!", "No te lo pierdas", clickbait

### Formato:
- Primera línea: hook potente
- Línea vacía
- Bullets o párrafos cortos
- Línea vacía
- Link
- Hashtags

Incluir exactamente esta URL: {article_url}
"""

    try:
        response = model.generate_content(prompt)
        post = response.text.strip()
        
        # Validar longitud
        if len(post) > config['max_chars']:
            post = post[:config['max_chars']-50] + f"\n\n📖 {article_url}"
        
        return {
            "post": post,
            "raw": post,
            "char_count": len(post)
        }
        
    except Exception as e:
        print(f"   ❌ Error generando LinkedIn post: {e}")
        return None


def generate_reddit_post(
    article_content: str,
    article_title: str,
    article_url: str
) -> dict:
    """
    Genera un post para Reddit (estilo técnico, sin marketing).
    
    Returns:
        dict: {
            "title": "título para Reddit",
            "body": "cuerpo del post",
            "suggested_subreddits": [...]
        }
    """
    if not model:
        return None
    
    config = PLATFORM_CONFIG["reddit"]
    
    prompt = f"""Transforma este artículo en un post para Reddit técnico.

## Artículo
Título original: {article_title}
URL: {article_url}

{article_content[:6000]}

## Instrucciones para Reddit

Reddit ODIA el contenido promocional. El post debe aportar valor ANTES de linkear.

### Genera:
1. **Título para Reddit**: Directo, técnico, sin clickbait (máx 300 chars)
2. **Cuerpo del post**: Resumen técnico que aporte valor por sí mismo

### Reglas del cuerpo:
- MÁXIMO {config['max_chars']} caracteres
- SIN emojis (Reddit técnico los odia)
- SIN hashtags
- Formato: TL;DR al inicio, luego desarrollo
- Incluir código/ejemplos si el artículo los tiene
- Al final: "Full article: [link]" de forma natural, no promocional

### Tono Reddit:
- Técnico puro, como si hablaras con peers
- Humilde (evita "revolucionario", "increíble")
- Directo al grano
- Acepta críticas implícitamente

### Formato de salida:
TITLE: [título aquí]
---
BODY:
[cuerpo aquí]
---
SUBREDDITS: r/MachineLearning, r/Python, etc.

URL a incluir: {article_url}
"""

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        
        # Parsear respuesta
        title_match = re.search(r'TITLE:\s*(.+?)(?=---|\n\n)', raw, re.DOTALL)
        body_match = re.search(r'BODY:\s*(.+?)(?=---|\nSUBREDDITS:)', raw, re.DOTALL)
        subs_match = re.search(r'SUBREDDITS:\s*(.+)', raw)
        
        title = title_match.group(1).strip() if title_match else article_title
        body = body_match.group(1).strip() if body_match else raw
        subreddits = []
        if subs_match:
            subreddits = [s.strip() for s in subs_match.group(1).split(',')]
        
        return {
            "title": title,
            "body": body,
            "suggested_subreddits": subreddits or config["subreddits"],
            "raw": raw
        }
        
    except Exception as e:
        print(f"   ❌ Error generando Reddit post: {e}")
        return None


def generate_threads_post(
    article_content: str,
    article_title: str,
    article_url: str
) -> dict:
    """
    Genera un post para Threads (Meta).
    
    Returns:
        dict: {
            "post": "texto del post",
            "raw": "texto completo"
        }
    """
    if not model:
        return None
    
    config = PLATFORM_CONFIG["threads"]
    
    prompt = f"""Transforma este artículo en un post para Threads.

## Artículo
Título: {article_title}
URL: {article_url}

{article_content[:4000]}

## Instrucciones para Threads

Threads es como Twitter pero más casual y conversacional.

### Reglas:
- MÁXIMO {config['max_chars']} caracteres
- Tono: casual pero técnico, como contándole a un amigo developer
- Emojis: naturales, no forzados (2-3 máximo)
- Hashtags: 2-3 al final
- Una sola publicación (no thread)

### Estructura:
1. Hook conversacional ("Llevo días probando X y...")
2. Insight principal en 1-2 oraciones
3. Pregunta o reflexión que invite a comentar
4. Link al artículo
5. Hashtags

### Tono Threads:
- Personal, como si escribieras desde tu experiencia
- Curioso, invita al debate
- Técnico pero accesible
- Evita sonar como marca corporativa

URL: {article_url}
"""

    try:
        response = model.generate_content(prompt)
        post = response.text.strip()
        
        # Validar longitud
        if len(post) > config['max_chars']:
            post = post[:config['max_chars']-30] + f"\n\n{article_url}"
        
        return {
            "post": post,
            "raw": post,
            "char_count": len(post)
        }
        
    except Exception as e:
        print(f"   ❌ Error generando Threads post: {e}")
        return None


# ============================================================================
# UTILIDADES
# ============================================================================

def _save_social_posts(results: dict, article_title: str) -> None:
    """Guarda los posts generados en archivos."""
    
    output_dir = "outputs/social"
    os.makedirs(output_dir, exist_ok=True)
    
    # Limpiar título para nombre de archivo
    safe_title = re.sub(r'[^\w\s-]', '', article_title)[:30].strip().replace(' ', '_')
    
    print(f"\n💾 Guardando posts en {output_dir}/")
    
    for platform, data in results.items():
        if not data:
            continue
            
        filepath = f"{output_dir}/{platform}_{safe_title}.md"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {platform.upper()} Post\n\n")
            f.write(f"**Generado para:** {article_title}\n\n")
            f.write("---\n\n")
            
            if platform == "twitter":
                f.write("## Thread\n\n")
                for i, tweet in enumerate(data.get("thread", []), 1):
                    f.write(f"### Tweet {i}\n")
                    f.write(f"```\n{tweet}\n```\n")
                    f.write(f"*({len(tweet)} caracteres)*\n\n")
                    
            elif platform == "reddit":
                f.write(f"## Título\n{data.get('title', '')}\n\n")
                f.write(f"## Cuerpo\n{data.get('body', '')}\n\n")
                f.write(f"## Subreddits sugeridos\n")
                for sub in data.get('suggested_subreddits', []):
                    f.write(f"- {sub}\n")
                    
            else:
                f.write(f"## Post\n\n{data.get('post', data.get('raw', ''))}\n\n")
                f.write(f"*({data.get('char_count', len(data.get('post', '')))} caracteres)*\n")
        
        print(f"   ✅ {filepath}")


def preview_social_posts(results: dict) -> None:
    """Muestra preview de todos los posts generados."""
    
    print(f"\n{'='*60}")
    print("📱 PREVIEW DE POSTS GENERADOS")
    print('='*60)
    
    for platform, data in results.items():
        if not data:
            continue
            
        print(f"\n{'─'*40}")
        print(f"📌 {platform.upper()}")
        print('─'*40)
        
        if platform == "twitter":
            for i, tweet in enumerate(data.get("thread", [])[:3], 1):
                print(f"\n[Tweet {i}] ({len(tweet)} chars)")
                print(tweet[:200] + "..." if len(tweet) > 200 else tweet)
            if len(data.get("thread", [])) > 3:
                print(f"\n... y {len(data['thread']) - 3} tweets más")
                
        elif platform == "reddit":
            print(f"\nTítulo: {data.get('title', '')[:100]}")
            print(f"\nCuerpo preview:\n{data.get('body', '')[:300]}...")
            
        else:
            post = data.get('post', data.get('raw', ''))
            print(f"\n{post[:400]}{'...' if len(post) > 400 else ''}")
            print(f"\n({data.get('char_count', len(post))} caracteres)")
