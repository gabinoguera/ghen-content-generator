# Directorio de Outputs

Este directorio contiene todos los archivos generados por el sistema de generación de contenido LEO.

## Archivos Generados

### Artículos
- `articulo_completo.md` - Artículo final generado
- `articulo_leo_generado.md` - Artículo generado con personalidad LEO
- `articulo_mejorado_qa.md` - Artículo mejorado después del análisis QA
- `test_articulo.md` - Artículo de prueba

### Análisis y Reportes
- `esquema_articulo.md` - Esquema/outline del artículo
- `qa_report.md` - Reporte de análisis de calidad
- `articulos_sugeridos.md` - Sugerencias de artículos relacionados
- `analisis_newsletter.md` - Análisis de newsletter (método 3)

### Datos de Investigación (CSV)
- `keywords_scraped.csv` - Keywords scrapeadas de Google SERP
- `search_results.csv` - Resultados de búsqueda de Google Custom Search
- `scraped_articles.csv` - Contenido scrapeado de artículos
- `SEO_Analysis_Results.csv` - Análisis SEO de artículos competencia

## Configuración

Todos los paths de output están configurados en `longcontent_generator/config.py`:

```python
CONFIG = {
    "output_dir": "outputs",
    "output_analysis_csv": "outputs/SEO_Analysis_Results.csv",
    "output_outline_md": "outputs/esquema_articulo.md",
    "output_article_md": "outputs/articulo_completo.md",
    "output_qa_report": "outputs/qa_report.md",
    "output_suggestions": "outputs/articulos_sugeridos.md",
}
```

## Limpieza

Para limpiar todos los outputs generados:

```bash
rm outputs/*.md outputs/*.csv
```

**Nota:** El archivo `.gitkeep` debe permanecer para mantener el directorio en git.
