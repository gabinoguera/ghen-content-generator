# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [2.0.0] - 2025-11-07

### 🎯 Añadido

#### Sistema de Personalidad LEO
- **LEO/personalidad.md**: Definición completa de 5 pilares de personalidad
  - Objetivo y Analítico
  - Empático y Respetuoso
  - Visionario y Estratégico
  - Narrador de Datos (inspirado en Prodigioso Volcán)
  - Curador de Conocimiento (inspirado en newsletter Proyecto451)

#### Tres Métodos de Generación de Contenido
- **Método 1 - Tópico**: Define tema amplio → LEO sugiere keyword → Pipeline completo
- **Método 2 - Keyword**: Keyword específica → Investigación → Generación
- **Método 3 - Newsletter**: Analiza newsletter → Extrae insights → Genera artículos

#### Nuevas Funciones en core.py (+509 líneas)
- `load_leo_context()`: Carga personalidad, proyecto y audiencia desde archivos markdown
- `build_system_prompt(leo_context)`: Construye system prompt con contexto completo de LEO
- `suggest_keyword_from_topic(topic, leo_context)`: Genera keyword SEO óptima desde tópico amplio
- `extract_and_summarize_url(url, leo_context)`: Analiza newsletters/artículos y genera resumen
- `generate_article_with_context(keyword, context_sources, leo_context)`: Genera artículos con personalidad LEO
- `improve_article_based_on_qa(article_content, qa_report)`: Mejora artículos basándose en análisis QA
- Funciones auxiliares: `extract_qa_improvements()`, `apply_qa_improvements()`, `integrate_missing_keyword()`, etc.

#### Documentación Completa
- **.github/copilot-instructions.md**: Guía completa para AI coding agents
- **.github/IMPLEMENTATION_SUMMARY.md**: Guía detallada de implementación y uso
- **.github/project-definitions.md**: Contexto del proyecto Archivo Final
- **.github/perfilado_cliente.md**: Perfil detallado de audiencia objetivo (escritores/autores)

#### Workflows y Testing
- **Pipeline_LEO_Enhanced.ipynb**: Notebook principal con selector de métodos y pipeline completo
- **test_leo_enhanced.py**: Suite de tests automatizados para validar todas las funciones
- **test_qa_improvement.py**: Test específico para mejoras post-QA

### 🔧 Modificado

#### Módulos Principales
- **longcontent_generator/core.py**: Añadidas 6 funciones principales + 6 auxiliares
- **longcontent_generator/__init__.py**: Exporta `improve_article_based_on_qa` en `__all__`

#### Configuración
- **.gitignore**: Actualizado para excluir archivos temporales y outputs generados
  - Excluye: archivos .md generados, CSVs de output, __pycache__, .DS_Store
  - Incluye: Documentación importante de .github/

### ✅ Testing

- Todos los tests pasan correctamente
- Artículo de prueba generado: 17,768 caracteres
- Personalidad LEO validada en outputs (tono empático, profesional, estratégico)
- Context injection funcional (personalidad: 4,731 chars, proyecto: 4,598 chars, audiencia: 2,491 chars)
- System prompt completo: 12,547 caracteres

### 🔑 Requisitos

- **Variables de entorno** (en `.env`):
  - `GEMINI_API_KEY`: API key de Google Gemini
  - `API_KEY`: Google Custom Search API key
  - `API_CUSTOM_SEARCH_ID`: ID de motor de búsqueda personalizado
  - `WORDPRESS_LOGIN_AF`: Usuario WordPress (opcional, para publicación)
  - `WORDPRESS_PASSWORD_AF`: App password WordPress (opcional)

### 📊 Estadísticas del Commit

- **Archivos nuevos**: 11
- **Líneas añadidas**: 1,797
- **Funciones nuevas**: 12 (6 principales + 6 auxiliares)
- **Archivos de documentación**: 5
- **Scripts de testing**: 2

### 🎨 Características Destacadas

1. **Context Injection**: Toda interacción con Gemini incluye personalidad, proyecto y audiencia
2. **Modularidad**: Funciones independientes y reutilizables
3. **Flexibilidad**: 3 flujos de trabajo diferentes según necesidades
4. **Testing**: Suite completa de tests automatizados
5. **Documentación**: Guías detalladas para desarrolladores y AI agents

---

## [1.0.0] - Versión Anterior

### Funcionalidades Base
- Pipeline de generación de contenido basado en keywords
- Scraping de Google SERP para investigación de keywords
- Análisis SEO con Gemini API
- Generación de artículos long-form
- QA y mejora de artículos
- Publicación en WordPress

---

## Próximas Versiones (Roadmap)

### [2.1.0] - Próxima Release
- [ ] Pipeline de descubrimiento de tendencias (pytrends)
- [ ] Integración con Google Trends
- [ ] Sugerencias automáticas de temas trending

### [2.2.0] - Futuro
- [ ] GUI para usuarios no técnicos
- [ ] Dashboard de métricas
- [ ] Automatización de workflows periódicos
- [ ] Integración con más fuentes de newsletters
