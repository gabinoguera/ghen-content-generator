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
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 12000,
    
    # Search Configuration
    "default_country": "ES",
    "max_search_results": 10,
    
    # Output Configuration
    "output_language": "spanish",
    "output_encoding": "UTF-8",
    
    # Files
    "output_analysis_csv": "SEO_Analysis_Results.csv",
    "output_outline_md": "esquema_articulo.md",
    "output_article_md": "articulo_completo.md",
    "output_qa_report": "qa_report.md",
    "output_suggestions": "articulos_sugeridos.md",
    
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
