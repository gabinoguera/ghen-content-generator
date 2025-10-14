"""
Funciones de utilidad del módulo LongContent Generator
"""

import os
from .config import CONFIG


def show_generated_files():
    """Muestra resumen de archivos generados."""
    files_to_check = [
        CONFIG["output_analysis_csv"],
        CONFIG["output_outline_md"],
        CONFIG["output_article_md"],
        CONFIG["output_qa_report"],
        CONFIG["output_suggestions"]
    ]
    
    print("📁 Archivos generados:")
    print("="*70)
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({size:,} bytes)")
        else:
            print(f"❌ {file_path} (no existe)")
    
    print("="*70)


def preview_article(max_chars=2000):
    """Vista previa del artículo generado."""
    article_path = CONFIG["output_article_md"]
    
    if not os.path.exists(article_path):
        print(f"❌ Artículo no encontrado: {article_path}")
        return
    
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("📄 Vista previa del artículo:")
    print("="*70)
    print(content[:max_chars])
    
    if len(content) > max_chars:
        print(f"\n... ({len(content) - max_chars} caracteres más)")
    
    print("="*70)
    print(f"Total: {len(content):,} caracteres, {len(content.split()):,} palabras")


def preview_qa_report(max_chars=1500):
    """Vista previa del reporte QA."""
    qa_path = CONFIG["output_qa_report"]
    
    if not os.path.exists(qa_path):
        print(f"❌ Reporte QA no encontrado: {qa_path}")
        return
    
    with open(qa_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Vista previa del reporte QA:")
    print("="*70)
    print(content[:max_chars])
    
    if len(content) > max_chars:
        print(f"\n... ({len(content) - max_chars} caracteres más)")
    
    print("="*70)


def cleanup_temp_files():
    """Limpia archivos temporales generados durante el proceso"""
    temp_files = [
        'search_results.csv',
        'scraped_articles.csv',
        'keywords_scraped.csv',
        'test_seo_analysis.csv'
    ]
    
    cleaned = []
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
            cleaned.append(file)
    
    if cleaned:
        print(f"🧹 Archivos temporales eliminados: {', '.join(cleaned)}")
    else:
        print("🧹 No hay archivos temporales para limpiar")


def change_keyword(new_keyword):
    """Cambia la keyword principal y muestra las nuevas configuraciones"""
    print(f"🎯 Keyword cambiada a: {new_keyword}")
    print(f"💡 Ejecuta las celdas del pipeline desde el PASO 1 para generar nuevo contenido")
    return new_keyword

