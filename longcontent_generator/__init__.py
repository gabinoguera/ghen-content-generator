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
    generate_article_with_qa_feedback,  # 🆕 v2.5 - Regeneración con feedback QA
    load_seo_keywords_from_analysis,
    extract_keywords_from_seo_analysis,
    extract_questions_from_seo_analysis,
    extract_keywords_from_search_titles,
    extract_newsletter_from_gmail,
    list_gmail_newsletters,
    add_source_links_to_article,
    clean_article_metatext,
    normalize_code_blocks,  # 🆕 v2.6.1 - Normalización de bloques de código
    load_ghen_context,
    generate_featured_image_prompt
)

from .scraper import (
    GoogleKeywordScraper,
    scrape_google_keywords
)

from .wordpress import (
    publish_article_from_markdown_cleaned,
    upload_featured_image_to_wordpress
)

from .imagen import (
    generate_image_from_prompt,
    optimize_image_for_wordpress
)

from .social import (
    generate_all_social_posts,
    generate_twitter_thread,
    generate_linkedin_post,
    generate_reddit_post,
    generate_threads_post,
)

from .linking import (
    auto_link_article,
    fetch_wordpress_posts,
    identify_external_links,
    identify_internal_links,
    inject_links_to_article,
    count_links_in_article,
    normalize_external_links,
    sanitize_article_links,  # 🆕 v2.6.1 - Limpia links de headers y código
)

from .utils import (
    show_generated_files,
    preview_article,
    preview_qa_report,
    cleanup_temp_files
)

from .config import CONFIG, generation_config, model

__version__ = "2.6.0"
__author__ = "GHEN Digital"

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
    'generate_article_with_qa_feedback',  # 🆕 v2.5
    'load_seo_keywords_from_analysis',
    'extract_keywords_from_seo_analysis',
    'extract_questions_from_seo_analysis',
    'extract_keywords_from_search_titles',
    'extract_newsletter_from_gmail',
    'list_gmail_newsletters',
    'add_source_links_to_article',
    'clean_article_metatext',
    'load_ghen_context',
    'generate_featured_image_prompt',
    
    # Scraper
    'GoogleKeywordScraper',
    'scrape_google_keywords',
    
    # WordPress
    'publish_article_from_markdown_cleaned',
    'upload_featured_image_to_wordpress',
    
    # Imagen
    'generate_image_from_prompt',
    'optimize_image_for_wordpress',
    
    # Social Media Adapters
    'generate_all_social_posts',
    'generate_twitter_thread',
    'generate_linkedin_post',
    'generate_reddit_post',
    'generate_threads_post',
    
    # Auto-Linking
    'auto_link_article',
    'fetch_wordpress_posts',
    'identify_external_links',
    'identify_internal_links',
    'inject_links_to_article',
    'count_links_in_article',
    
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

print("✅ LongContent Generator v2.6.0 cargado correctamente")
print("📋 Funciones principales disponibles:")
print("   • google_custom_search() - Búsqueda en Google")
print("   • scrape_articles_batch() - Scraping de artículos")
print("   • analyze_articles_batch() - Análisis SEO con Gemini")
print("   • generate_article_from_outline() - Generación de contenido")
print("   • qa_article_coverage() - Análisis de calidad")
print("   • improve_article_based_on_qa() - Regeneración con feedback QA")
print("   • auto_link_article() - 🆕 v2.6 Auto-linking inteligente")
print("   • publish_article_from_markdown_cleaned() - Publicación WordPress")
print("   • extract_newsletter_from_gmail() - Leer newsletters desde Gmail")
print("   • generate_all_social_posts() - Generar posts para redes sociales")
print("   • load_ghen_context(level='base|full') - Sistema de personalidad")
