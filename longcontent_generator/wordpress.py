"""
Módulo de publicación en WordPress
"""

import os
import requests
import base64
import markdown
import re


def publish_article_from_markdown_cleaned(article_title, markdown_file_path="articulo_completo.md", status='draft'):
    """
    Publica artículo desde archivo Markdown a WordPress con limpieza automática del formato.
    
    Args:
        article_title: Título del artículo
        markdown_file_path: Ruta al archivo markdown (default: articulo_completo.md)
        status: Estado del post - 'draft' o 'publish' (default: 'draft')
    
    Returns:
        bool: True si exitoso, False en caso contrario
    """
    # Credenciales de WordPress
    login = os.getenv('WORDPRESS_LOGIN_AF')
    password = os.getenv('WORDPRESS_PASSWORD_AF')
    
    if not login or not password:
        print("❌ Error: Credenciales de WordPress no encontradas en .env")
        print("   Asegúrate de tener WORDPRESS_LOGIN_AF y WORDPRESS_PASSWORD_AF configuradas")
        return False
    
    # WordPress API endpoint
    url = 'https://ghendigital.com/wp-json/wp/v2/posts'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{login}:{password}".encode()).decode(),
        'Content-Type': 'application/json'
    }
    
    # Leer contenido Markdown
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        print(f"✅ Archivo Markdown leído: {markdown_file_path}")
    except FileNotFoundError:
        print(f"❌ Error: Archivo {markdown_file_path} no encontrado")
        return False
    except IOError as e:
        print(f"❌ Error al leer archivo: {str(e)}")
        return False
    
    # LIMPIAR Y CORREGIR EL MARKDOWN
    try:
        # 1. Remover texto inicial innecesario
        lines = markdown_content.split('\n')
        cleaned_lines = []
        start_processing = False
        
        for line in lines:
            # Buscar el inicio del artículo real (primera línea con #)
            if line.strip().startswith('#') and not start_processing:
                start_processing = True
            
            if start_processing:
                cleaned_lines.append(line)
        
        # Unir las líneas limpias
        cleaned_markdown = '\n'.join(cleaned_lines)
        
        # 2. Corregir formato de títulos
        # Asegurar que los títulos principales usen # y subtítulos ##
        cleaned_markdown = re.sub(r'^### ([^#])', r'## \1', cleaned_markdown, flags=re.MULTILINE)
        cleaned_markdown = re.sub(r'^#### ([^#])', r'### \1', cleaned_markdown, flags=re.MULTILINE)
        
        # 3. Limpiar líneas vacías excesivas
        cleaned_markdown = re.sub(r'\n\n\n+', '\n\n', cleaned_markdown)
        
        # 4. Corregir formato de texto en negrita
        cleaned_markdown = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', cleaned_markdown)
        
        # 5. Limpiar backticks innecesarios
        cleaned_markdown = re.sub(r'`([^`]+)`', r'**\1**', cleaned_markdown)
        
        print("✅ Markdown limpiado y corregido automáticamente")
        
    except Exception as e:
        print(f"⚠️  Error al limpiar Markdown, usando contenido original: {str(e)}")
        cleaned_markdown = markdown_content
    
    # Convertir Markdown a HTML
    try:
        html_content = markdown.markdown(
            cleaned_markdown,
            extensions=['extra', 'nl2br', 'sane_lists', 'codehilite', 'toc']
        )
        
        # Mejorar el HTML generado
        # Asegurar que los párrafos estén bien formateados
        html_content = re.sub(r'<p>\s*</p>', '', html_content)  # Remover párrafos vacíos
        html_content = re.sub(r'\n\s*\n', '\n', html_content)  # Limpiar espacios
        
        print("✅ Markdown convertido a HTML correctamente")
    except Exception as e:
        print(f"❌ Error al convertir Markdown: {str(e)}")
        return False
    
    # Preparar datos para WordPress
    data = {
        'title': article_title,
        'content': html_content,
        'status': status,
        'format': 'standard'
    }
    
    # Enviar a WordPress
    try:
        print(f"🔄 Publicando en WordPress (status: {status})...")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        post_data = response.json()
        post_id = post_data.get('id')
        post_url = post_data.get('link')
        
        print(f"✅ Artículo publicado correctamente")
        print(f"   📝 ID del post: {post_id}")
        print(f"   🔗 URL: {post_url}")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al publicar en WordPress: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Código de error: {e.response.status_code}")
            print(f"   Respuesta: {e.response.text}")
        return False


def publicar_articulo_completo_limpio():
    """Función de conveniencia para publicar el artículo completo con formato corregido"""
    return publish_article_from_markdown_cleaned(
        article_title="aprender a escribir",
        markdown_file_path="articulo_completo.md",
        status='draft'  # Cambiar a 'publish' cuando estés listo
    )

