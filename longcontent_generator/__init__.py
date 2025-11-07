"""
LongContent Generator - Módulo para generación de contenido long-form

Módulo profesional para generar contenido long-form con análisis SEO,
scraping de competencia y publicación automática en WordPress.
"""

from .core import (
    google_custom_search,
    scrape_articles_batch,
    analyze_articles_batch,
    analyze_combined_context,
    create_intelligent_content_plan,
    generate_article_outline,
    generate_article_from_outline,
    qa_article_coverage,
    suggest_related_articles,
    improve_article_based_on_qa,
    load_seo_keywords_from_analysis,
    extract_keywords_from_seo_analysis,
    extract_questions_from_seo_analysis,
    extract_keywords_from_search_titles
)

from .scraper import (
    GoogleKeywordScraper,
    scrape_google_keywords
)

from .wordpress import (
    publish_article_from_markdown_cleaned
)

from .utils import (
    show_generated_files,
    preview_article,
    preview_qa_report,
    cleanup_temp_files
)

from .config import CONFIG, generation_config, model

__version__ = "1.0.0"
__author__ = "LongContent Generator Team"

__all__ = [
    # Core functions
    'google_custom_search',
    'scrape_articles_batch', 
    'analyze_articles_batch',
    'analyze_combined_context',
    'create_intelligent_content_plan',
    'generate_article_outline',
    'generate_article_from_outline',
    'qa_article_coverage',
    'suggest_related_articles',
    'improve_article_based_on_qa',
    'load_seo_keywords_from_analysis',
    'extract_keywords_from_seo_analysis',
    'extract_questions_from_seo_analysis',
    'extract_keywords_from_search_titles',
    
    # Scraper
    'GoogleKeywordScraper',
    'scrape_google_keywords',
    
    # WordPress
    'publish_article_from_markdown_cleaned',
    
    # Utils
    'show_generated_files',
    'preview_article', 
    'preview_qa_report',
    'cleanup_temp_files',
    
    # Config
    'CONFIG',
    'generation_config',
    'model'
]

print("✅ LongContent Generator v1.0.0 cargado correctamente")
print("📋 Funciones principales disponibles:")
print("   • google_custom_search() - Búsqueda en Google")
print("   • scrape_articles_batch() - Scraping de artículos")
print("   • analyze_articles_batch() - Análisis SEO con Gemini")
print("   • generate_article_from_outline() - Generación de contenido")
print("   • qa_article_coverage() - Análisis de calidad")
print("   • publish_article_from_markdown_cleaned() - Publicación WordPress")
