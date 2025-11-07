#!/usr/bin/env python3
"""
Script para probar la nueva funcionalidad de mejora automática basada en QA
"""

# Recargar el módulo con la nueva funcionalidad
import importlib
import sys

if 'longcontent_generator.core' in sys.modules:
    importlib.reload(sys.modules['longcontent_generator.core'])

from longcontent_generator.core import improve_article_based_on_qa

def test_qa_improvement():
    """Prueba la funcionalidad de mejora automática basada en QA"""
    
    print("🧪 PRUEBA DE MEJORA AUTOMÁTICA BASADA EN QA")
    print("="*60)
    
    # Cargar el artículo actual
    try:
        with open("articulo_completo.md", "r", encoding="utf-8") as f:
            article_content = f.read()
        print("✅ Artículo cargado correctamente")
    except FileNotFoundError:
        print("❌ No se encontró articulo_completo.md")
        return
    
    # Cargar el reporte QA
    try:
        with open("qa_report.md", "r", encoding="utf-8") as f:
            qa_report = f.read()
        print("✅ Reporte QA cargado correctamente")
    except FileNotFoundError:
        print("❌ No se encontró qa_report.md")
        return
    
    print(f"\n📊 Estadísticas:")
    print(f"   • Artículo: {len(article_content)} caracteres")
    print(f"   • QA Report: {len(qa_report)} caracteres")
    
    # Aplicar mejoras
    print(f"\n🔧 Aplicando mejoras basadas en QA...")
    improved_article = improve_article_based_on_qa(article_content, qa_report)
    
    print(f"\n✅ Proceso completado")
    print(f"   • Artículo mejorado: {len(improved_article)} caracteres")
    print(f"   • Diferencia: {len(improved_article) - len(article_content)} caracteres")

if __name__ == "__main__":
    test_qa_improvement()
