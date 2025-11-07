#!/usr/bin/env python3
"""
Script de prueba para las nuevas funcionalidades de LEO
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar módulos
from longcontent_generator import core

def test_load_context():
    """Prueba la carga de contexto de LEO"""
    print("\n" + "="*70)
    print("TEST 1: Cargar Contexto de LEO")
    print("="*70)
    
    leo_context = core.load_leo_context()
    
    print(f"\n✓ Personalidad cargada: {len(leo_context['personality'])} caracteres")
    print(f"✓ Proyecto cargado: {len(leo_context['project'])} caracteres")
    print(f"✓ Audiencia cargada: {len(leo_context['audience'])} caracteres")
    
    return leo_context


def test_system_prompt(leo_context):
    """Prueba la construcción del system prompt"""
    print("\n" + "="*70)
    print("TEST 2: Construir System Prompt")
    print("="*70)
    
    system_prompt = core.build_system_prompt(leo_context)
    
    print(f"\n✓ System prompt generado: {len(system_prompt)} caracteres")
    print("\nPrimeras líneas del system prompt:")
    print("-" * 70)
    print(system_prompt[:500] + "...")
    print("-" * 70)
    
    return system_prompt


def test_suggest_keyword(leo_context):
    """Prueba la sugerencia de keyword desde un tópico"""
    print("\n" + "="*70)
    print("TEST 3: Sugerir Keyword desde Tópico")
    print("="*70)
    
    topico = "Inteligencia Artificial aplicada a la escritura creativa"
    print(f"\nTópico de prueba: '{topico}'")
    
    keyword = core.suggest_keyword_from_topic(topico, leo_context)
    
    if keyword:
        print(f"\n✓ Keyword sugerida: '{keyword}'")
        return keyword
    else:
        print("\n✗ No se pudo sugerir keyword")
        return None


def test_extract_url(leo_context):
    """Prueba la extracción y análisis de URL"""
    print("\n" + "="*70)
    print("TEST 4: Extraer y Analizar URL")
    print("="*70)
    
    # URL de prueba (puedes cambiarla)
    test_url = "https://www.prodigiosovolcan.com/"
    print(f"\nURL de prueba: {test_url}")
    
    analysis = core.extract_and_summarize_url(test_url, leo_context)
    
    if analysis:
        print(f"\n✓ Análisis completado")
        print(f"✓ Análisis: {len(analysis['raw_analysis'])} caracteres")
        print("\nPrimeras líneas del análisis:")
        print("-" * 70)
        print(analysis['raw_analysis'][:500] + "...")
        print("-" * 70)
        return analysis
    else:
        print("\n✗ No se pudo analizar la URL")
        return None


def test_generate_article(leo_context):
    """Prueba la generación de artículo con contexto"""
    print("\n" + "="*70)
    print("TEST 5: Generar Artículo con Contexto")
    print("="*70)
    
    keyword = "mejores prácticas para escritores noveles"
    context_sources = [
        "La escritura requiere disciplina y práctica constante.",
        "Es importante leer mucho para mejorar como escritor.",
        "Los escritores deben encontrar su propia voz única."
    ]
    
    print(f"\nKeyword: '{keyword}'")
    print(f"Fuentes de contexto: {len(context_sources)}")
    
    article = core.generate_article_with_context(keyword, context_sources, leo_context)
    
    if article:
        print(f"\n✓ Artículo generado: {len(article)} caracteres")
        print(f"✓ Palabras aproximadas: {len(article.split())}")
        print("\nPrimeras líneas del artículo:")
        print("-" * 70)
        print(article[:500] + "...")
        print("-" * 70)
        
        # Guardar artículo de prueba
        with open('outputs/test_articulo.md', 'w', encoding='utf-8') as f:
            f.write(article)
        print("\n✓ Artículo guardado en 'outputs/test_articulo.md'")
        
        return article
    else:
        print("\n✗ No se pudo generar el artículo")
        return None


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*70)
    print("🧪 INICIANDO PRUEBAS DE LEO ENHANCED")
    print("="*70)
    
    # Crear directorio outputs si no existe
    os.makedirs('outputs', exist_ok=True)
    
    try:
        # Test 1: Cargar contexto
        leo_context = test_load_context()
        
        # Test 2: System prompt
        system_prompt = test_system_prompt(leo_context)
        
        # Test 3: Sugerir keyword (requiere API de Gemini)
        if os.getenv('GEMINI_API_KEY'):
            print("\n🔑 API Key de Gemini encontrada. Ejecutando tests con API...")
            
            keyword = test_suggest_keyword(leo_context)
            
            # Test 4: Extraer URL (opcional, puede fallar si la URL no es accesible)
            # analysis = test_extract_url(leo_context)
            
            # Test 5: Generar artículo
            article = test_generate_article(leo_context)
        else:
            print("\n⚠️  GEMINI_API_KEY no encontrada. Saltando tests que requieren API.")
        
        print("\n" + "="*70)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("="*70)
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ ERROR EN LAS PRUEBAS")
        print("="*70)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
