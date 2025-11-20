#!/bin/bash
# Script de prueba rápida para generación de imágenes con Imagen 3

echo "========================================="
echo "🎨 Test: Generación de Imagen con Imagen 3"
echo "========================================="

# Activar virtual environment
source .venv/bin/activate

# Test básico de Imagen 3
python3 << 'PYEOF'
import os
from dotenv import load_dotenv

load_dotenv()

print("\n1️⃣ Verificando configuración de Vertex AI...")

# Verificar variables de entorno
PROJECT_ID = os.getenv('PROJECT_ID')
LOCATION = os.getenv('LOCATION')
SERVICE_ACCOUNT_KEY = os.getenv('SERVICE_ACCOUNT_KEY')

if not all([PROJECT_ID, LOCATION, SERVICE_ACCOUNT_KEY]):
    print("❌ Faltan variables de entorno:")
    if not PROJECT_ID: print("   - PROJECT_ID")
    if not LOCATION: print("   - LOCATION")
    if not SERVICE_ACCOUNT_KEY: print("   - SERVICE_ACCOUNT_KEY")
    print("\nAgrega estas variables a tu archivo .env")
    exit(1)

print(f"✅ PROJECT_ID: {PROJECT_ID}")
print(f"✅ LOCATION: {LOCATION}")
print(f"✅ SERVICE_ACCOUNT_KEY: {SERVICE_ACCOUNT_KEY}")

# Verificar que existe el archivo de credenciales
if not os.path.exists(SERVICE_ACCOUNT_KEY):
    print(f"\n❌ No se encontró el archivo: {SERVICE_ACCOUNT_KEY}")
    print("   Descarga la clave JSON de tu Service Account desde Google Cloud")
    exit(1)

print(f"✅ Service Account JSON encontrado")

print("\n2️⃣ Probando importación del módulo imagen...")
try:
    from longcontent_generator.imagen import generate_image_from_prompt
    print("✅ Módulo imagen importado correctamente")
except ImportError as e:
    print(f"❌ Error al importar módulo: {e}")
    exit(1)

print("\n3️⃣ Generando imagen de prueba...")
test_prompt = """Modern tech illustration showing AI neural network concept with flowing data streams,
gradient colors from blue to purple, abstract geometric shapes, futuristic atmosphere,
professional and clean design, 16:9 horizontal format"""

try:
    image_path = generate_image_from_prompt(
        prompt=test_prompt,
        output_path="outputs/test_featured_image.png"
    )
    
    if image_path:
        print(f"\n✅ ¡Imagen generada exitosamente!")
        print(f"   📁 Ubicación: {image_path}")
        print(f"   💰 Costo: ~$0.04 USD")
        
        # Verificar tamaño del archivo
        file_size = os.path.getsize(image_path) / 1024  # KB
        print(f"   📊 Tamaño: {file_size:.2f} KB")
    else:
        print("\n❌ La generación de imagen falló (ver logs arriba)")
        
except Exception as e:
    print(f"\n❌ Error durante la generación: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 40)
print("✅ TEST COMPLETADO")
print("=" * 40)

PYEOF

echo ""
echo "Para usar en el pipeline completo:"
echo "  • Abre Pipeline_GHEN_Enhanced.ipynb"
echo "  • Configura GENERATE_IMAGE = True en el Paso 7"
echo "  • Ejecuta la celda de generación de imagen"
