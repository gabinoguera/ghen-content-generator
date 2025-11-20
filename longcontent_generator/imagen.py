"""
Módulo de generación de imágenes destacadas usando Vertex AI Imagen 3
"""

import os
import io
from google import genai
from google.genai.types import GenerateImagesConfig
from PIL import Image as PILImage
from dotenv import load_dotenv

load_dotenv()

# Configuración de Vertex AI
PROJECT_ID = os.getenv('PROJECT_ID')
LOCATION = os.getenv('LOCATION')
SERVICE_ACCOUNT_KEY = os.getenv('SERVICE_ACCOUNT_KEY')

# Validar configuración
if not all([PROJECT_ID, LOCATION, SERVICE_ACCOUNT_KEY]):
    raise ValueError("❌ Faltan variables de entorno para Vertex AI: PROJECT_ID, LOCATION o SERVICE_ACCOUNT_KEY")

# Configurar credenciales
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 
    SERVICE_ACCOUNT_KEY
)

# Inicializar cliente de Vertex AI
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# Modelo de generación de imágenes
IMAGEN_MODEL = "imagen-3.0-generate-001"


def generate_image_from_prompt(prompt, output_path="outputs/featured_image.png"):
    """
    Genera una imagen usando Vertex AI Imagen 3 basándose en un prompt.
    
    Args:
        prompt (str): Descripción de la imagen a generar
        output_path (str): Ruta donde guardar la imagen generada
    
    Returns:
        str: Ruta del archivo de imagen generado, o None si falla
    """
    try:
        print(f"🎨 Generando imagen con Imagen 3...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # Generar imagen con Imagen 3
        response = client.models.generate_images(
            model=IMAGEN_MODEL,
            prompt=prompt,
            config=GenerateImagesConfig(
                number_of_images=1,
                safety_filter_level="BLOCK_MEDIUM_AND_ABOVE",
                person_generation="ALLOW_ADULT",
                aspect_ratio="16:9",  # Formato ideal para imágenes destacadas de WordPress
            ),
        )
        
        # Guardar la imagen generada
        generated_image = response.generated_images[0]
        generated_image.image.save(output_path)
        
        print(f"✅ Imagen generada y guardada en: {output_path}")
        print(f"💰 Costo estimado: $0.04 USD")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error al generar imagen: {str(e)}")
        return None


def get_image_bytes(image_path):
    """
    Lee una imagen y devuelve sus bytes.
    
    Args:
        image_path (str): Ruta de la imagen
    
    Returns:
        bytes: Contenido de la imagen en bytes
    """
    try:
        with open(image_path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error al leer imagen: {str(e)}")
        return None


def optimize_image_for_wordpress(image_path, max_width=1920, quality=85):
    """
    Optimiza una imagen para WordPress (resize y compresión).
    
    Args:
        image_path (str): Ruta de la imagen a optimizar
        max_width (int): Ancho máximo en píxeles
        quality (int): Calidad JPEG (0-100)
    
    Returns:
        str: Ruta de la imagen optimizada (sobrescribe la original)
    """
    try:
        img = PILImage.open(image_path)
        
        # Resize si es necesario
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), PILImage.Resampling.LANCZOS)
        
        # Convertir a RGB si es necesario (para JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = PILImage.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # Guardar optimizada
        img.save(image_path, format='JPEG', quality=quality, optimize=True)
        print(f"✅ Imagen optimizada para WordPress")
        
        return image_path
        
    except Exception as e:
        print(f"❌ Error al optimizar imagen: {str(e)}")
        return image_path
