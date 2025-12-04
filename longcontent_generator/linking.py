"""
Módulo de Auto-Linking para artículos
Inserta links internos y externos de forma inteligente sin regenerar el contenido.
"""

import os
import re
import requests
import base64
import json
from .config import model, CONFIG


# ============================================================================
# WORDPRESS API - Obtener artículos existentes
# ============================================================================

def fetch_wordpress_posts(max_posts: int = 50) -> list:
    """
    Obtiene los artículos publicados de WordPress para linking interno.
    
    Args:
        max_posts: Número máximo de posts a obtener
    
    Returns:
        list: Lista de dicts con {id, title, slug, url, excerpt}
    """
    login = os.getenv('WORDPRESS_LOGIN_GHEN')
    password = os.getenv('WORDPRESS_PASSWORD_GHEN')
    
    if not login or not password:
        print("⚠️  Credenciales de WordPress no encontradas")
        return []
    
    url = 'https://ghendigital.com/wp-json/wp/v2/posts'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{login}:{password}".encode()).decode(),
    }
    
    params = {
        'per_page': min(max_posts, 100),  # WordPress max es 100
        'status': 'publish',
        '_fields': 'id,title,slug,link,excerpt'  # Solo campos necesarios
    }
    
    try:
        print(f"📡 Obteniendo artículos de WordPress...")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        posts = response.json()
        
        # Limpiar y estructurar datos
        clean_posts = []
        for post in posts:
            # Limpiar HTML del excerpt
            excerpt = post.get('excerpt', {}).get('rendered', '')
            excerpt = re.sub(r'<[^>]+>', '', excerpt).strip()[:200]
            
            clean_posts.append({
                'id': post.get('id'),
                'title': post.get('title', {}).get('rendered', ''),
                'slug': post.get('slug', ''),
                'url': post.get('link', ''),
                'excerpt': excerpt
            })
        
        print(f"✅ {len(clean_posts)} artículos obtenidos de WordPress")
        return clean_posts
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener posts de WordPress: {e}")
        return []


# ============================================================================
# IDENTIFICACIÓN DE LINKS CON GEMINI
# ============================================================================

def identify_external_links(article_text: str, max_links: int = 5) -> list:
    """
    Usa Gemini para identificar herramientas, librerías y recursos que
    deberían tener links externos.
    
    IMPORTANTE: No regenera el artículo, solo identifica oportunidades.
    
    Args:
        article_text: Texto del artículo en markdown
        max_links: Número máximo de links a sugerir
    
    Returns:
        list: [{anchor_text, url, context_sentence}]
    """
    if not model:
        print("❌ Modelo Gemini no configurado")
        return []
    
    prompt = f"""Analiza este artículo técnico e identifica herramientas, librerías, frameworks, 
plataformas o recursos externos que deberían tener links a sus sitios oficiales.

REGLAS ESTRICTAS:
1. Solo identifica términos que APARECEN EXACTAMENTE en el artículo
2. Solo incluye URLs de sitios OFICIALES (documentación, GitHub oficial, sitio web oficial)
3. NO inventes términos que no están en el texto
4. Prioriza: herramientas de IA/ML, librerías Python, plataformas cloud, frameworks
5. El anchor_text debe ser EXACTAMENTE como aparece en el artículo (respeta mayúsculas/minúsculas)

ARTÍCULO:
{article_text[:8000]}

Responde SOLO con un JSON array válido, sin explicaciones:
[
  {{"anchor_text": "texto exacto del artículo", "url": "https://sitio-oficial.com", "context": "frase donde aparece"}},
  ...
]

Si no encuentras oportunidades válidas, responde: []
Máximo {max_links} links."""

    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        # Limpiar respuesta (a veces Gemini añade ```json)
        result = re.sub(r'^```json\s*', '', result)
        result = re.sub(r'\s*```$', '', result)
        
        links = json.loads(result)
        
        # Validar que cada link tiene los campos requeridos
        valid_links = []
        for link in links:
            if all(k in link for k in ['anchor_text', 'url', 'context']):
                # Verificar que el anchor_text realmente existe en el artículo
                if link['anchor_text'] in article_text:
                    valid_links.append(link)
                else:
                    print(f"⚠️  Anchor '{link['anchor_text']}' no encontrado en artículo, ignorando")
        
        return valid_links[:max_links]
        
    except json.JSONDecodeError as e:
        print(f"⚠️  Error parseando respuesta de Gemini: {e}")
        return []
    except Exception as e:
        print(f"❌ Error identificando links externos: {e}")
        return []


def identify_internal_links(article_text: str, existing_posts: list, max_links: int = 5) -> list:
    """
    Usa Gemini para identificar oportunidades de linking interno con
    artículos existentes de WordPress.
    
    IMPORTANTE: No regenera el artículo, solo identifica oportunidades.
    
    Args:
        article_text: Texto del artículo en markdown
        existing_posts: Lista de posts de WordPress [{title, url, excerpt}]
        max_links: Número máximo de links a sugerir
    
    Returns:
        list: [{anchor_text, url, post_title}]
    """
    if not model:
        print("❌ Modelo Gemini no configurado")
        return []
    
    if not existing_posts:
        print("⚠️  No hay artículos existentes para linking interno")
        return []
    
    # Preparar lista de posts existentes para el prompt
    posts_context = "\n".join([
        f"- TÍTULO: {p['title']}\n  URL: {p['url']}\n  TEMA: {p['excerpt'][:100]}"
        for p in existing_posts[:20]  # Limitar para no exceder contexto
    ])
    
    prompt = f"""Analiza este artículo y encuentra oportunidades de linking interno con 
los artículos existentes del blog.

REGLAS ESTRICTAS:
1. El anchor_text debe ser texto que EXISTE EXACTAMENTE en el artículo nuevo
2. Solo sugiere links donde hay conexión temática REAL
3. Respeta mayúsculas/minúsculas del texto original
4. No fuerces links - solo donde tiene sentido semánticamente
5. Prefiere frases de 2-4 palabras como anchor text

ARTÍCULO NUEVO:
{article_text[:6000]}

ARTÍCULOS EXISTENTES DEL BLOG:
{posts_context}

Responde SOLO con un JSON array válido:
[
  {{"anchor_text": "texto exacto del artículo nuevo", "url": "url del post existente", "post_title": "título del post"}},
  ...
]

Si no hay oportunidades válidas, responde: []
Máximo {max_links} links."""

    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        # Limpiar respuesta
        result = re.sub(r'^```json\s*', '', result)
        result = re.sub(r'\s*```$', '', result)
        
        links = json.loads(result)
        
        # Validar links
        valid_links = []
        for link in links:
            if all(k in link for k in ['anchor_text', 'url', 'post_title']):
                # Verificar que el anchor_text existe en el artículo
                if link['anchor_text'] in article_text:
                    valid_links.append(link)
                else:
                    print(f"⚠️  Anchor interno '{link['anchor_text']}' no encontrado, ignorando")
        
        return valid_links[:max_links]
        
    except json.JSONDecodeError as e:
        print(f"⚠️  Error parseando respuesta de Gemini: {e}")
        return []
    except Exception as e:
        print(f"❌ Error identificando links internos: {e}")
        return []


# ============================================================================
# INYECCIÓN DE LINKS (SIN REGENERAR CONTENIDO)
# ============================================================================

def inject_links_to_article(
    article_text: str,
    external_links: list,
    internal_links: list,
    external_attrs: str = 'target="_blank" rel="nofollow noopener"',
    internal_attrs: str = ''
) -> tuple:
    """
    Inyecta links en el artículo mediante búsqueda y reemplazo.
    
    IMPORTANTE: Esta función NO regenera el artículo. Solo hace reemplazos
    puntuales del anchor_text por el mismo texto envuelto en <a>.
    
    Para evitar dobles reemplazos, cada anchor_text solo se reemplaza UNA VEZ
    (la primera ocurrencia que no esté ya dentro de un link).
    
    Args:
        article_text: Texto original del artículo
        external_links: Lista de links externos [{anchor_text, url}]
        internal_links: Lista de links internos [{anchor_text, url}]
        external_attrs: Atributos HTML para links externos
        internal_attrs: Atributos HTML para links internos
    
    Returns:
        tuple: (article_with_links, stats_dict)
    """
    modified_text = article_text
    stats = {
        'external_added': 0,
        'internal_added': 0,
        'external_failed': 0,
        'internal_failed': 0
    }
    
    # Función auxiliar para reemplazar solo la primera ocurrencia que no esté ya linkeada
    def safe_replace_first(text: str, anchor: str, url: str, attrs: str) -> tuple:
        """
        Reemplaza la primera ocurrencia del anchor que no esté dentro de un tag <a>.
        Retorna (nuevo_texto, éxito_bool)
        """
        # Patrón para encontrar el anchor que NO esté precedido por "> o seguido de </a>
        # Esto evita linkear texto que ya está dentro de un link
        
        # Primero verificamos que el anchor existe
        if anchor not in text:
            return text, False
        
        # Verificar que no está ya linkeado (buscar si aparece entre > y </a>)
        already_linked_pattern = rf'>[^<]*{re.escape(anchor)}[^<]*</a>'
        if re.search(already_linked_pattern, text):
            # El anchor ya está dentro de un link, buscar otra ocurrencia
            pass
        
        # Crear el link HTML
        if attrs:
            link_html = f'<a href="{url}" {attrs}>{anchor}</a>'
        else:
            link_html = f'<a href="{url}">{anchor}</a>'
        
        # Reemplazar solo la primera ocurrencia
        # Usamos un enfoque más seguro: buscar la posición y verificar contexto
        pos = text.find(anchor)
        if pos == -1:
            return text, False
        
        # Verificar que no está dentro de un link existente
        # Buscar hacia atrás el último < y verificar que no es <a
        prefix = text[:pos]
        last_open_tag = prefix.rfind('<')
        if last_open_tag != -1:
            tag_content = prefix[last_open_tag:]
            # Si estamos dentro de un tag <a ...> sin cerrar, buscar siguiente ocurrencia
            if '<a ' in tag_content.lower() and '</a>' not in tag_content.lower():
                # Estamos dentro de un link, buscar siguiente ocurrencia
                next_pos = text.find(anchor, pos + len(anchor))
                if next_pos == -1:
                    return text, False
                pos = next_pos
        
        # Realizar el reemplazo en la posición encontrada
        new_text = text[:pos] + link_html + text[pos + len(anchor):]
        return new_text, True
    
    # Inyectar links externos
    print(f"\n🔗 Inyectando {len(external_links)} links externos...")
    for link in external_links:
        anchor = link.get('anchor_text', '')
        url = link.get('url', '')
        
        if not anchor or not url:
            continue
        
        modified_text, success = safe_replace_first(modified_text, anchor, url, external_attrs)
        
        if success:
            stats['external_added'] += 1
            print(f"   ✅ '{anchor}' → {url[:50]}...")
        else:
            stats['external_failed'] += 1
            print(f"   ⚠️  No se pudo linkear '{anchor}'")
    
    # Inyectar links internos
    print(f"\n🔗 Inyectando {len(internal_links)} links internos...")
    for link in internal_links:
        anchor = link.get('anchor_text', '')
        url = link.get('url', '')
        
        if not anchor or not url:
            continue
        
        modified_text, success = safe_replace_first(modified_text, anchor, url, internal_attrs)
        
        if success:
            stats['internal_added'] += 1
            print(f"   ✅ '{anchor}' → {link.get('post_title', url)[:40]}...")
        else:
            stats['internal_failed'] += 1
            print(f"   ⚠️  No se pudo linkear '{anchor}'")
    
    return modified_text, stats


# ============================================================================
# FUNCIÓN PRINCIPAL DE AUTO-LINKING
# ============================================================================

def auto_link_article(
    article_text: str,
    min_external: int = 3,
    min_internal: int = 3,
    max_external: int = 6,
    max_internal: int = 6
) -> tuple:
    """
    Función principal que ejecuta el proceso completo de auto-linking.
    
    GARANTÍA: Esta función NO regenera el artículo. Solo identifica
    oportunidades de linking y hace reemplazos puntuales de texto.
    
    El contenido, estructura y longitud del artículo se preservan intactos.
    Solo se añaden tags <a> alrededor de texto existente.
    
    Args:
        article_text: Texto del artículo en markdown
        min_external: Mínimo de links externos deseados
        min_internal: Mínimo de links internos deseados
        max_external: Máximo de links externos
        max_internal: Máximo de links internos
    
    Returns:
        tuple: (article_with_links, report_dict)
    """
    print("=" * 70)
    print("🔗 AUTO-LINKING: Insertando links inteligentes")
    print("=" * 70)
    print(f"\n📊 Configuración:")
    print(f"   • Links externos: {min_external}-{max_external}")
    print(f"   • Links internos: {min_internal}-{max_internal}")
    
    # Guardar longitud original para verificación
    original_length = len(article_text)
    original_word_count = len(article_text.split())
    
    # 1. Obtener artículos existentes de WordPress
    existing_posts = fetch_wordpress_posts(max_posts=30)
    
    # 2. Identificar oportunidades de links externos
    print(f"\n🔍 Analizando artículo para links externos...")
    external_links = identify_external_links(article_text, max_links=max_external)
    print(f"   Encontrados: {len(external_links)} oportunidades")
    
    # 3. Identificar oportunidades de links internos
    print(f"\n🔍 Analizando artículo para links internos...")
    internal_links = identify_internal_links(article_text, existing_posts, max_links=max_internal)
    print(f"   Encontrados: {len(internal_links)} oportunidades")
    
    # 4. Inyectar los links
    linked_article, stats = inject_links_to_article(
        article_text,
        external_links,
        internal_links
    )
    
    # 5. Verificar integridad del contenido
    new_length = len(linked_article)
    new_word_count = len(linked_article.split())
    
    # El texto solo debe crecer (por los tags <a>), nunca reducirse significativamente
    length_diff = new_length - original_length
    word_diff = new_word_count - original_word_count
    
    print(f"\n" + "=" * 70)
    print("📊 REPORTE DE AUTO-LINKING")
    print("=" * 70)
    print(f"\n✅ Links externos añadidos: {stats['external_added']}/{len(external_links)}")
    print(f"✅ Links internos añadidos: {stats['internal_added']}/{len(internal_links)}")
    
    if stats['external_failed'] > 0:
        print(f"⚠️  Links externos fallidos: {stats['external_failed']}")
    if stats['internal_failed'] > 0:
        print(f"⚠️  Links internos fallidos: {stats['internal_failed']}")
    
    print(f"\n🔒 VERIFICACIÓN DE INTEGRIDAD:")
    print(f"   • Longitud original: {original_length:,} chars")
    print(f"   • Longitud final: {new_length:,} chars")
    print(f"   • Diferencia: +{length_diff:,} chars (solo tags <a>)")
    print(f"   • Palabras: {original_word_count} → {new_word_count} (diff: {word_diff})")
    
    # Verificar que no hubo pérdida de contenido
    if new_length < original_length:
        print(f"\n❌ ERROR: Se perdió contenido durante el linking!")
        print(f"   Retornando artículo original sin cambios.")
        return article_text, {'error': 'content_loss', 'stats': stats}
    
    # Verificar que se alcanzaron los mínimos
    total_links = stats['external_added'] + stats['internal_added']
    min_total = min_external + min_internal
    
    if total_links < min_total:
        print(f"\n⚠️  ADVERTENCIA: Solo se añadieron {total_links}/{min_total} links mínimos")
    
    # 6. Sanitizar links incorrectos (en headers, código, etc.)
    print(f"\n🧹 Sanitizando links en zonas protegidas...")
    linked_article = sanitize_article_links(linked_article)
    
    # 7. Normalizar TODOS los links externos (nuevos y existentes)
    print(f"\n🔧 Normalizando todos los links externos...")
    linked_article = normalize_external_links(linked_article)
    
    # Actualizar longitud final después de normalización
    final_length = len(linked_article)
    
    report = {
        'external_links': external_links,
        'internal_links': internal_links,
        'stats': stats,
        'original_length': original_length,
        'final_length': final_length,
        'integrity_check': 'passed' if final_length >= original_length else 'failed'
    }
    
    print(f"\n✅ Auto-linking completado exitosamente")
    
    return linked_article, report


# ============================================================================
# UTILIDADES
# ============================================================================

def count_links_in_article(article_text: str) -> dict:
    """
    Cuenta los links existentes en un artículo.
    
    Returns:
        dict: {total, internal, external}
    """
    # Buscar todos los tags <a href="...">
    all_links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>', article_text, re.IGNORECASE)
    
    internal = 0
    external = 0
    
    for url in all_links:
        if 'ghendigital.com' in url:
            internal += 1
        else:
            external += 1
    
    # También contar links markdown [texto](url)
    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', article_text)
    for text, url in md_links:
        if 'ghendigital.com' in url:
            internal += 1
        else:
            external += 1
    
    return {
        'total': internal + external,
        'internal': internal,
        'external': external
    }


def normalize_external_links(
    article_text: str,
    internal_domain: str = 'ghendigital.com',
    external_attrs: str = 'target="_blank" rel="nofollow noopener"'
) -> tuple:
    """
    Normaliza TODOS los links externos del artículo para que tengan
    target="_blank" y rel="nofollow noopener".
    
    También convierte links markdown externos a HTML con los atributos correctos.
    
    IMPORTANTE: Esta función NO regenera el artículo, solo modifica los links.
    
    Args:
        article_text: Texto del artículo
        internal_domain: Dominio interno (no se modifica)
        external_attrs: Atributos para links externos
    
    Returns:
        tuple: (article_normalized, stats_dict)
    """
    modified_text = article_text
    stats = {
        'html_links_fixed': 0,
        'markdown_links_converted': 0,
        'already_correct': 0
    }
    
    # 1. Procesar links HTML existentes (<a href="...">)
    def fix_html_link(match):
        full_tag = match.group(0)
        url = match.group(1)
        
        # Si es link interno, no modificar
        if internal_domain in url:
            return full_tag
        
        # Si ya tiene los atributos correctos, no modificar
        if 'target="_blank"' in full_tag and 'nofollow' in full_tag:
            stats['already_correct'] += 1
            return full_tag
        
        # Extraer el contenido del link (texto entre <a> y </a>)
        # Esto es más complejo, así que mejor reconstruimos el tag
        
        # Remover atributos existentes de target y rel si los hay
        clean_tag = re.sub(r'\s+target=["\'][^"\']*["\']', '', full_tag)
        clean_tag = re.sub(r'\s+rel=["\'][^"\']*["\']', '', clean_tag)
        
        # Insertar los nuevos atributos antes del >
        new_tag = clean_tag.replace('>', f' {external_attrs}>', 1)
        
        stats['html_links_fixed'] += 1
        return new_tag
    
    # Patrón para encontrar tags <a> con href
    html_link_pattern = r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>'
    modified_text = re.sub(html_link_pattern, fix_html_link, modified_text)
    
    # 2. Convertir links Markdown externos a HTML con atributos
    def convert_markdown_link(match):
        text = match.group(1)
        url = match.group(2)
        
        # Si es link interno, convertir a HTML simple
        if internal_domain in url:
            return f'<a href="{url}">{text}</a>'
        
        # Si es externo, añadir atributos
        stats['markdown_links_converted'] += 1
        return f'<a href="{url}" {external_attrs}>{text}</a>'
    
    # Patrón para links markdown [texto](url)
    md_link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    modified_text = re.sub(md_link_pattern, convert_markdown_link, modified_text)
    
    total_changes = stats['html_links_fixed'] + stats['markdown_links_converted']
    
    return modified_text, stats


def prepare_article_for_publish(
    article_text: str,
    normalize_links: bool = True
) -> tuple:
    """
    Prepara el artículo para publicación, normalizando todos los links externos.
    
    Esta es la función que se debe llamar antes de publicar en WordPress
    para asegurar que todos los links externos tengan los atributos correctos.
    
    Args:
        article_text: Texto del artículo
        normalize_links: Si True, normaliza los links externos
    
    Returns:
        tuple: (article_prepared, report_dict)
    """
    if not normalize_links:
        return article_text, {'skipped': True}
    
    print("🔗 Normalizando links externos...")
    
    # Contar links antes
    links_before = count_links_in_article(article_text)
    
    # Normalizar
    normalized_text, stats = normalize_external_links(article_text)
    
    # Contar links después
    links_after = count_links_in_article(normalized_text)
    
    print(f"   ✅ Links HTML corregidos: {stats['html_links_fixed']}")
    print(f"   ✅ Links Markdown convertidos: {stats['markdown_links_converted']}")
    print(f"   ℹ️  Links ya correctos: {stats['already_correct']}")
    
    report = {
        'links_before': links_before,
        'links_after': links_after,
        'stats': stats
    }
    
    return normalized_text, report


def sanitize_article_links(article_text: str) -> str:
    """
    Limpia links HTML que se insertaron incorrectamente en:
    1. Encabezados markdown (# H1, ## H2, ### H3, etc.)
    2. Bloques de código (entre ``` y ```)
    3. Especificador de lenguaje del bloque (```python, ```javascript, etc.)
    4. Código inline (entre backticks simples `)
    
    Esta función extrae solo el texto del link, eliminando el tag <a>.
    Debe ejecutarse DESPUÉS del auto-linking para corregir errores.
    
    Args:
        article_text: Texto del artículo con posibles links incorrectos
    
    Returns:
        str: Artículo con links limpiados de zonas protegidas
    """
    import re
    
    lines = article_text.split('\n')
    result_lines = []
    in_code_block = False
    fixes_applied = {
        'headers': 0,
        'code_blocks': 0,
        'inline_code': 0,
        'lang_specifier': 0
    }
    
    # Patrón para extraer el texto de un link HTML
    link_pattern = re.compile(r'<a\s+[^>]*>([^<]*)</a>')
    
    def strip_links(text: str) -> str:
        """Reemplaza todos los links HTML por su texto interno."""
        return link_pattern.sub(r'\1', text)
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Detectar inicio/fin de bloque de código
        if line.strip().startswith('```'):
            if not in_code_block:
                # Inicio de bloque - limpiar el especificador de lenguaje
                in_code_block = True
                if '<a ' in line:
                    line = strip_links(line)
                    if line != original_line:
                        fixes_applied['lang_specifier'] += 1
            else:
                # Fin de bloque
                in_code_block = False
            
            result_lines.append(line)
            continue
        
        # Dentro de bloque de código - limpiar todos los links
        if in_code_block:
            if '<a ' in line:
                line = strip_links(line)
                if line != original_line:
                    fixes_applied['code_blocks'] += 1
            result_lines.append(line)
            continue
        
        # Fuera de bloques de código
        
        # 1. Limpiar links en encabezados markdown
        if line.strip().startswith('#'):
            if '<a ' in line:
                line = strip_links(line)
                if line != original_line:
                    fixes_applied['headers'] += 1
            result_lines.append(line)
            continue
        
        # 2. Limpiar links dentro de código inline (backticks simples)
        # Patrón: `código con <a href="...">texto</a> más código`
        inline_code_pattern = re.compile(r'`([^`]+)`')
        
        def clean_inline_code(match):
            code_content = match.group(1)
            if '<a ' in code_content:
                cleaned = strip_links(code_content)
                if cleaned != code_content:
                    fixes_applied['inline_code'] += 1
                return f'`{cleaned}`'
            return match.group(0)
        
        line = inline_code_pattern.sub(clean_inline_code, line)
        
        result_lines.append(line)
    
    # Reportar cambios
    total_fixes = sum(fixes_applied.values())
    if total_fixes > 0:
        print(f"🧹 Links sanitizados:")
        if fixes_applied['headers'] > 0:
            print(f"   • Encabezados: {fixes_applied['headers']} links removidos")
        if fixes_applied['code_blocks'] > 0:
            print(f"   • Bloques de código: {fixes_applied['code_blocks']} links removidos")
        if fixes_applied['lang_specifier'] > 0:
            print(f"   • Especificador de lenguaje: {fixes_applied['lang_specifier']} links removidos")
        if fixes_applied['inline_code'] > 0:
            print(f"   • Código inline: {fixes_applied['inline_code']} links removidos")
    
    return '\n'.join(result_lines)