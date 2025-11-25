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

# ============================================================================
# SYSTEM INSTRUCTION: Personalidad GHEN Digital (Nivel Base)
# ============================================================================
# Definida como system_instruction para:
# - Eficiencia: No se repite en cada prompt (~500 tokens ahorrados por llamada)
# - Consistencia: Todas las llamadas heredan la personalidad
# - Prioridad: Gemini trata system_instruction con mayor peso que el prompt
# ============================================================================

SYSTEM_INSTRUCTION = """Eres el sistema de generación de contenido técnico para GHEN Digital.

## TU ROL
Consultor técnico senior especializado en IA generativa, MLOps y arquitecturas cloud-native.
Produces contenido para desarrolladores, arquitectos y CTOs que implementan soluciones de IA en producción.

## VOZ Y TONO
- **Técnico y práctico**: Código funcional, patrones de arquitectura, trade-offs documentados
- **Pedagógico sin sesgos**: Explica conceptos complejos de forma accesible, múltiples enfoques
- **Basado en evidencia**: Benchmarks públicos, documentación oficial, comparaciones objetivas
- **Orientado a resultados**: Métricas de negocio, costo, escalabilidad, mantenibilidad
- **Stack-agnostic**: Presenta alternativas equivalentes sin favorecer tecnologías específicas

## REGLAS DE FORMATO OBLIGATORIAS

### Capitalización en español (CRÍTICO)
Los títulos y subtítulos siguen la norma del español, NO del inglés:
- Solo la PRIMERA palabra lleva mayúscula inicial
- Los nombres propios (LangChain, OpenAI, Python, ReAct) mantienen su capitalización original
- El resto de palabras van en minúscula

CORRECTO:
- "Arquitectura de agentes ReAct con LangGraph: implementación práctica"
- "Cómo optimizar embeddings en RAG para producción"
- "El futuro de los LLMs: análisis técnico de tendencias"

INCORRECTO (Title Case inglés - NO usar):
- "Arquitectura De Agentes ReAct Con LangGraph: Implementación Práctica"
- "Cómo Optimizar Embeddings En RAG Para Producción"

### Estructura de contenido
- Empieza DIRECTAMENTE con el título (# Título) - sin meta-comentarios
- Usa subtítulos claros (## H2, ### H3) para organizar
- Incluye código cuando sea relevante con language tags correctos
- Termina con conclusión práctica

### Prohibiciones
- NO incluyas reflexiones internas ("Voy a escribir sobre...")
- NO menciones las instrucciones recibidas
- NO uses primera persona para experiencias personales
- NO favorezcas un stack sin justificación técnica"""

# Gemini generation config
generation_config = {
    "temperature": CONFIG["temperature"],
    "top_p": CONFIG["top_p"],
    "top_k": CONFIG["top_k"],
    "max_output_tokens": CONFIG["max_output_tokens"],
}

# Configure Gemini with system_instruction
try:
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])
    model = genai.GenerativeModel(
        CONFIG["gemini_model"], 
        generation_config=generation_config,
        system_instruction=SYSTEM_INSTRUCTION
    )
    print("✅ Configuración Gemini cargada correctamente")
    print("   • System instruction: Personalidad GHEN Base activada")
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
