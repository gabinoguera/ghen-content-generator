# 📋 Sistema Híbrido de Personalidad de Contenido GHEN

## Descripción General

El sistema de personalidad de GHEN Digital cuenta con **dos niveles** que permiten generar contenido adaptado al contexto y objetivo de cada artículo.

---

## 🎯 Los Dos Niveles

### Nivel BASE (`personalidad_base.md`)

**Objetivo:** Contenido técnico neutral, objetivo y stack-agnostic

**Características:**
- ✅ Voz del "experto técnico neutral"
- ✅ Sin referencias a proyectos personales (Cofares, hackathons, clientes)
- ✅ Comparaciones objetivas con múltiples opciones tecnológicas
- ✅ Basado en evidencia pública (benchmarks, papers, documentación oficial)
- ✅ Stack-agnostic: presenta alternativas equivalentes

**Exclusiones:**
- ❌ Primera persona singular ("En mi experiencia...", "Durante mi trabajo...")
- ❌ Stack tecnológico presentado como preferencia personal
- ❌ Anécdotas de proyectos privados
- ❌ Código que asume configuración específica de un proyecto personal

**Ideal para:**
- Artículos de actualidad y noticias técnicas
- Comparativas de herramientas y frameworks
- Análisis de benchmarks
- Explicaciones de conceptos técnicos (RAG, fine-tuning, agents)
- Contenido SEO donde la credibilidad neutral es clave

**Ejemplo de título:**
> "Arquitectura de agentes IA: patrones ReAct con implementaciones en LangGraph y CrewAI"

---

### Nivel FULL (`personalidad_completa.md`)

**Objetivo:** Contenido con experiencia personal, voice marca GHEN

**Características:**
- ✅ Voz del "consultor técnico senior con experiencia real"
- ✅ Referencias a proyectos específicos (Cofares, microservicios, consultoría)
- ✅ Stack tecnológico definido (FastAPI, LangChain, Gemini, ChromaDB)
- ✅ Primera persona en retrospectivas ("En mi experiencia con...")
- ✅ Lecciones aprendidas de proyectos en producción

**Incluye:**
- ✅ Anécdotas de hackathons y proyectos reales
- ✅ Preferencias técnicas justificadas con experiencia
- ✅ Código basado en implementaciones probadas
- ✅ Recomendaciones desde la experiencia práctica

**Ideal para:**
- Tutoriales paso a paso con stack específico
- Case studies y retrospectivas de proyectos
- Lecciones aprendidas de implementaciones reales
- Artículos de opinión técnica fundamentada
- Contenido que busca diferenciación de marca personal

**Ejemplo de título:**
> "Lecciones aprendidas en la creación de un microservicio de mapeo automático (Parte I)"

---

## 🔧 Uso en Código

### Cargar contexto en nivel específico

```python
from longcontent_generator import core

# Nivel BASE (neutral)
ghen_context_base = core.load_ghen_context(level="base")

# Nivel FULL (con experiencias)
ghen_context_full = core.load_ghen_context(level="full")

# Default es FULL si no se especifica
ghen_context = core.load_ghen_context()  # → level="full"
```

### Generar artículo con nivel específico

```python
# Artículo neutral para actualidad
ghen_context = core.load_ghen_context(level="base")
article = core.generate_article_with_context(
    keyword="Grok 4.1 vs Gemini 3: análisis comparativo",
    context_sources=newsletter_content,
    leo_context=ghen_context
)

# Artículo con experiencia personal para tutorial
ghen_context = core.load_ghen_context(level="full")
article = core.generate_article_with_context(
    keyword="Cómo implementé un sistema RAG con LangChain",
    context_sources=research_content,
    leo_context=ghen_context
)
```

---

## 📊 Guía de Decisión: ¿Qué Nivel Usar?

| Tipo de Contenido | Nivel Recomendado | Razón |
|-------------------|-------------------|-------|
| **Newsletter analysis / Actualidad** | `base` | Maximiza credibilidad, evita sesgo personal |
| **Comparativa de herramientas** | `base` | Necesita objetividad, múltiples opciones |
| **Explicación de conceptos** | `base` | Universal, stack-agnostic |
| **Tutorial con stack específico** | `full` | Justifica elecciones con experiencia |
| **Case study / Retrospectiva** | `full` | Valor en la experiencia personal |
| **Lecciones aprendidas** | `full` | Autenticidad de la experiencia |
| **Opinión técnica fundamentada** | `full` | Voz personal con autoridad |

---

## 🔄 Flujo de Trabajo Recomendado

### Para artículos de actualidad (Método Newsletter):

1. Analizar newsletter técnico
2. **Usar `level="base"`** para el artículo
3. Resultado: Análisis objetivo sin sesgos de stack personal

```python
# En Pipeline_GHEN_Enhanced.ipynb
ghen_context = core.load_ghen_context(level="base")  # ← Cambiar aquí
```

### Para tutoriales con código:

1. Investigar tema técnico
2. **Usar `level="full"`** para el artículo
3. Resultado: Tutorial con stack probado y experiencia personal

```python
# En Pipeline_GHEN_Enhanced.ipynb
ghen_context = core.load_ghen_context(level="full")  # ← Cambiar aquí
```

---

## 📝 Ejemplos de Output

### Ejemplo NIVEL BASE (neutral):

```markdown
# Grok 4.1 en la carrera de los LLMs: análisis técnico de rendimiento y posicionamiento

El ecosistema de Large Language Models continúa su rápida evolución. 
El lanzamiento de xAI Grok 4.1 introduce mejoras significativas...

## Evaluación de rendimiento con benchmarks públicos

Según el Text LMArena, Grok 4.1 alcanza un Elo de 1483, posicionándose
como #1 en el ranking. Este benchmark, mantenido por la comunidad...

Comparación con competidores:
- **Grok 4.1**: Elo 1483, mejora 65% vs Grok 4
- **Gemini 2.5**: Elo estimado 1450
- **GPT-4 Turbo**: Elo 1470

*Nota: Benchmarks de LMArena al 2025-01-20*
```

### Ejemplo NIVEL FULL (con experiencia):

```markdown
# Implementando RAG con LangChain: lecciones desde la trinchera

Durante el hackathon de Cofares, mi equipo enfrentó el desafío de construir
un chatbot con RAG para consultas farmacéuticas en tiempo real...

## Por qué elegimos ChromaDB sobre Pinecone

En mi experiencia con bases de vectores en producción, la decisión entre
ChromaDB y Pinecone se reduce a tres factores clave...

```python
# Configuración que usamos en Cofares
from langchain.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="embedding-001")
vectorstore = Chroma(persist_directory="./chroma_db", 
                     embedding_function=embeddings)
```

Esta configuración nos permitió procesar 10k documentos farmacéuticos
con latencias <200ms en el p95...
```

---

## 🎨 Consistencia Visual

Ambos niveles mantienen:
- ✅ Capitalización correcta en español (solo primera palabra + nombres propios)
- ✅ Estructura clara con H2/H3
- ✅ Código ejecutable y comentado
- ✅ Referencias y fuentes al final
- ✅ Tono técnico profesional

La diferencia está en:
- 🔀 Voz narrativa (3ª persona vs 1ª persona)
- 🔀 Referencias (públicas vs experiencias personales)
- 🔀 Stack (múltiples opciones vs stack preferido justificado)

---

## 🚀 Migración de Contenido Existente

Si tienes contenido generado antes del sistema híbrido:

1. **Artículos de actualidad/comparativas** → Regenerar con `level="base"`
2. **Tutoriales con experiencias** → Mantener con `level="full"`
3. **Dudas** → Probar ambos niveles y comparar credibilidad/autenticidad

---

## 📚 Archivos del Sistema

```
GHEN/
├── README_PERSONALIDAD.md      ← Este archivo (guía de uso)
├── personalidad_base.md         ← Nivel BASE (neutral)
├── personalidad_completa.md     ← Nivel FULL (experiencias)
└── personalidad.md              ← Alias de personalidad_completa.md
```

---

## 🔗 Referencias

- Implementación en `longcontent_generator/core.py` → función `load_ghen_context(level)`
- Uso en notebook: `Pipeline_GHEN_Enhanced.ipynb` → Paso 1 (configuración)
- Documentación completa: `.github/copilot-instructions.md`

---

**Última actualización:** 2025-01-20  
**Versión del sistema:** 2.3.0 (Sistema Híbrido)
