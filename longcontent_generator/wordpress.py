"""
Módulo de publicación en WordPress
"""

import os
import requests
import base64
import markdown
import re


def upload_featured_image_to_wordpress(image_path, login=None, password=None):
    """
    Sube una imagen a WordPress Media Library y retorna su ID.
    
    Args:
        image_path (str): Ruta del archivo de imagen
        login (str): Usuario de WordPress (opcional, usa .env si no se provee)
        password (str): Password de WordPress (opcional, usa .env si no se provee)
    
    Returns:
        int: ID de la imagen en WordPress, o None si falla
    """
    # Credenciales
    login = login or os.getenv('WORDPRESS_LOGIN_GHEN')
    password = password or os.getenv('WORDPRESS_PASSWORD_GHEN')
    
    if not login or not password:
        print("❌ Error: Credenciales de WordPress no encontradas")
        return None
    
    # WordPress Media API endpoint
    url = 'https://ghendigital.com/wp-json/wp/v2/media'
    
    try:
        # Leer el archivo de imagen
        with open(image_path, 'rb') as img_file:
            image_data = img_file.read()
        
        filename = os.path.basename(image_path)
        
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(f"{login}:{password}".encode()).decode(),
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'image/jpeg'
        }
        
        print(f"📤 Subiendo imagen a WordPress: {filename}")
        response = requests.post(url, headers=headers, data=image_data)
        response.raise_for_status()
        
        media_data = response.json()
        media_id = media_data.get('id')
        media_url = media_data.get('source_url')
        
        print(f"✅ Imagen subida correctamente")
        print(f"   🆔 Media ID: {media_id}")
        print(f"   🔗 URL: {media_url}")
        
        return media_id
        
    except FileNotFoundError:
        print(f"❌ Error: Archivo de imagen no encontrado: {image_path}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al subir imagen a WordPress: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Código de error: {e.response.status_code}")
            print(f"   Respuesta: {e.response.text}")
        return None


def publish_article_from_markdown_cleaned(article_title, markdown_file_path="outputs/articulo_ghen_generado.md", 
                                          status='draft', featured_image_path=None):
    """
    Publica artículo desde archivo Markdown a WordPress con limpieza automática del formato.
    
    Args:
        article_title: Título del artículo
        markdown_file_path: Ruta al archivo markdown (default: outputs/articulo_ghen_generado.md)
        status: Estado del post - 'draft' o 'publish' (default: 'draft')
        featured_image_path: Ruta a la imagen destacada (opcional)
    
    Returns:
        dict: {'success': bool, 'post_id': int, 'post_url': str} o None si falla
    """
    # Credenciales de WordPress
    login = os.getenv('WORDPRESS_LOGIN_GHEN')
    password = os.getenv('WORDPRESS_PASSWORD_GHEN')
    
    if not login or not password:
        print("❌ Error: Credenciales de WordPress no encontradas en .env")
        print("   Asegúrate de tener WORDPRESS_LOGIN_GHEN y WORDPRESS_PASSWORD_GHEN configuradas")
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
    
    # Subir imagen destacada si se proporcionó
    featured_media_id = None
    if featured_image_path and os.path.exists(featured_image_path):
        print("🖼️  Procesando imagen destacada...")
        featured_media_id = upload_featured_image_to_wordpress(featured_image_path, login, password)
        if featured_media_id:
            data['featured_media'] = featured_media_id
    
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
        if featured_media_id:
            print(f"   🖼️  Imagen destacada asignada (ID: {featured_media_id})")
        
        return {
            'success': True,
            'post_id': post_id,
            'post_url': post_url,
            'featured_media_id': featured_media_id
        }
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al publicar en WordPress: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Código de error: {e.response.status_code}")
            print(f"   Respuesta: {e.response.text}")
        return None


def publicar_articulo_completo_limpio(featured_image_path=None):
    """
    Función de conveniencia para publicar el artículo completo con formato corregido.
    
    Args:
        featured_image_path (str): Ruta opcional a imagen destacada
    
    Returns:
        dict: Resultado de la publicación
    """
    return publish_article_from_markdown_cleaned(
        article_title="aprender a escribir",
        markdown_file_path="outputs/articulo_ghen_generado.md",
        status='draft',  # Cambiar a 'publish' cuando estés listo
        featured_image_path=featured_image_path
    )


