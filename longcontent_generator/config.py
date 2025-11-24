"""
Configuración del módulo LongContent Generator
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv, find_dotenv

# Load environment variables
_ = load_dotenv(find_dotenv())

# Configuration parameters
CONFIG = {
    # Gemini Configuration
    "gemini_model": "gemini-2.5-flash",
    # Optimizado para contenido de actualidad/newsletter:
    # - temperature más alta para mayor variedad léxica y creatividad
    # - top_p reducido para evitar repeticiones
    # - top_k aumentado para riqueza de vocabulario
    "temperature": 0.8,      # ↑ Mayor creatividad y variación
    "top_p": 0.85,           # ↓ Reduce repeticiones mantiene calidad
    "top_k": 50,             # ↑ Mayor diversidad léxica
    "max_output_tokens": 12000,
    
    # Search Configuration
    "default_country": "ES",
    "max_search_results": 10,
    
    # Output Configuration
    "output_language": "spanish",
    "output_encoding": "UTF-8",
    "output_dir": "outputs",
    
    # Files
    "output_analysis_csv": "outputs/SEO_Analysis_Results.csv",
    "output_outline_md": "outputs/esquema_articulo.md",
    "output_article_md": "outputs/articulo_ghen_generado.md",
    "output_qa_report": "outputs/qa_report.md",
    "output_suggestions": "outputs/articulos_sugeridos.md",
    
    # API delay
    "api_delay": 2
}

# Gemini generation config
generation_config = {
    "temperature": CONFIG["temperature"],
    "top_p": CONFIG["top_p"],
    "top_k": CONFIG["top_k"],
    "max_output_tokens": CONFIG["max_output_tokens"],
}

# Configure Gemini
try:
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    model = genai.GenerativeModel(CONFIG["gemini_model"], generation_config=generation_config)
    print("✅ Configuración Gemini cargada correctamente")
except KeyError:
    print("⚠️  GEMINI_API_KEY no encontrada en variables de entorno")
    model = None
except Exception as e:
    print(f"❌ Error configurando Gemini: {str(e)}")
    model = None

print(f"📊 Configuración cargada:")
print(f"   • Modelo: {CONFIG['gemini_model']}")
print(f"   • Temperatura: {CONFIG['temperature']}")
print(f"   • País por defecto: {CONFIG['default_country']}")
