# 🎯 Propuesta de Mejora de Calidad de Contenido

**Fecha:** 21 de noviembre de 2025  
**Versión del sistema:** 2.3.0  
**Problemas identificados:**
1. Contenido repetitivo que pierde valor
2. Abuso de listas, falta de narrativa fluida con párrafos
3. Tono distante y frío

---

## 📊 Análisis de la Situación Actual

### Configuración Actual de Gemini

```python
# config.py - Configuración actual
CONFIG = {
    "gemini_model": "gemini-2.5-flash",
    "temperature": 0.7,      # ← MODERADA (creatividad media)
    "top_p": 0.95,           # ← ALTA (permite diversidad alta)
    "top_k": 40,             # ← ESTÁNDAR
    "max_output_tokens": 12000,
}
```

**Diagnóstico:**
- ✅ `temperature: 0.7` es razonable para contenido técnico
- ⚠️ `top_p: 0.95` es MUY ALTO → genera contenido predecible y repetitivo
- ⚠️ `top_k: 40` es ESTÁNDAR pero puede combinarse mal con top_p alto
- ❌ NO hay variación de parámetros según tipo de contenido

### Sistema QA Existente (NO UTILIZADO)

**Funciones implementadas pero NO integradas:**

1. **`qa_article_coverage()`** (línea 744 de core.py)
   - ✅ Evalúa cobertura de keywords
   - ✅ Verifica respuestas a preguntas
   - ✅ Analiza completitud semántica
   - ✅ Evalúa calidad del contenido (coherencia, profundidad, estructura)
   - ✅ Genera puntuaciones sobre 10
   - ✅ Proporciona recomendaciones específicas
   - ❌ **NO se llama desde el notebook principal**

2. **`improve_article_based_on_qa()`** (línea 933 de core.py)
   - ✅ Mejora artículo basándose en reporte QA
   - ✅ Hace correcciones quirúrgicas
   - ❌ **NO se llama desde el notebook principal**

3. **`suggest_related_articles()`** (línea 851 de core.py)
   - ✅ Sugiere artículos complementarios
   - ✅ Construye content clusters
   - ❌ **NO se utiliza actualmente**

**Problema crítico:** Tenemos un sistema QA completo implementado que NO estamos usando.

### Problemas en los Prompts Actuales

**Análisis de los prompts de generación:**

```python
# Problemas detectados en prompts:
# 1. DEMASIADAS INSTRUCCIONES EN LISTA
"**El artículo debe:**
- Sintetizar las tendencias...
- Analizar implicaciones...
- Tener entre 1500-2000 palabras...
- Incluir un título atractivo..."
```

**Por qué esto causa listas excesivas:**
- El modelo IMITA el formato de las instrucciones
- Si le damos listas, genera listas
- Falta guía sobre CÓMO narrar (tono, voz, estilo)

**Tono actual en prompts:**
- ❌ "Escribe desde la perspectiva de un consultor técnico experimentado" (demasiado formal)
- ❌ No hay indicaciones sobre CALOR humano
- ❌ No hay ejemplos de tono conversacional técnico

---

## 💡 Propuesta Integral de Mejora

### FASE 1: Ajuste de Parámetros de Generación

#### 1.1. Configuración Dinámica por Tipo de Contenido

**Crear perfiles de generación:**

```python
# config.py - NUEVA CONFIGURACIÓN
GENERATION_PROFILES = {
    "actualidad": {
        "temperature": 0.8,   # ↑ Más creativo para análisis
        "top_p": 0.85,        # ↓ Reduce repetición
        "top_k": 50,          # ↑ Aumenta variedad léxica
        "max_output_tokens": 12000,
    },
    "tutorial": {
        "temperature": 0.7,   # = Balance creatividad/precisión
        "top_p": 0.80,        # ↓ Más enfocado en técnica
        "top_k": 45,          # = Moderado
        "max_output_tokens": 12000,
    },
    "comparativa": {
        "temperature": 0.6,   # ↓ Más objetivo
        "top_p": 0.75,        # ↓ Más determinista
        "top_k": 35,          # ↓ Menos variación
        "max_output_tokens": 12000,
    },
    "case_study": {
        "temperature": 0.85,  # ↑↑ Más narrativo
        "top_p": 0.88,        # = Balance
        "top_k": 55,          # ↑ Mayor riqueza léxica
        "max_output_tokens": 12000,
    }
}
```

**Beneficios:**
- ✅ Actualidad: Más creativo y variado (evita repetición)
- ✅ Tutorial: Balance entre claridad y fluidez
- ✅ Comparativa: Más objetivo y estructurado
- ✅ Case study: Más narrativo y humano

#### 1.2. Función de Selección Automática

```python
def get_generation_config(content_type="actualidad"):
    """Retorna configuración de generación según tipo de contenido"""
    profile = GENERATION_PROFILES.get(content_type, GENERATION_PROFILES["actualidad"])
    return {
        "temperature": profile["temperature"],
        "top_p": profile["top_p"],
        "top_k": profile["top_k"],
        "max_output_tokens": profile["max_output_tokens"],
    }
```

---

### FASE 2: Mejora de Prompts (Anti-Lista, Pro-Narrativa)

#### 2.1. Nuevo Sistema de Instrucciones Narrativas

**ANTES (causa listas):**
```markdown
**El artículo debe:**
- Sintetizar las tendencias...
- Analizar implicaciones...
- Tener entre 1500-2000 palabras...
```

**DESPUÉS (favorece párrafos):**
```markdown
# Guía de Estilo y Tono

Escribe con la voz de un consultor técnico senior que comparte insights en una 
conversación con colegas desarrolladores. Imagina que estás explicando estos 
conceptos en un café técnico después de una conferencia: accesible pero profundo, 
conversacional pero preciso.

## Narrativa vs. Listas

PREFIERE párrafos que fluyan naturalmente. Las listas solo cuando sean 
ESTRICTAMENTE necesarias (opciones de configuración, pasos secuenciales, 
comparaciones directas). El 70% del contenido debe ser narrativo en párrafos.

EJEMPLO CORRECTO:
"La arquitectura de agentes ReAct ha revolucionado cómo pensamos sobre sistemas 
autónomos. A diferencia de los enfoques tradicionales que separaban razonamiento 
y acción, ReAct los entrelaza en un ciclo continuo donde cada decisión se 
fundamenta en observaciones del entorno. En mi experiencia implementando estos 
sistemas, he visto cómo esta integración reduce errores de contexto en un 40% 
comparado con pipelines lineales."

EJEMPLO INCORRECTO (demasiadas listas):
"Ventajas de ReAct:
- Integra razonamiento y acción
- Reduce errores de contexto
- Mejora la autonomía
..."

## Tono: Técnico pero Humano

- USA primera persona cuando compartes experiencia: "Durante el proyecto X, 
  descubrimos que..."
- CONECTA conceptos con experiencias: "Esto me recuerda a cuando..."
- ADMITE complejidad: "No es trivial, pero vale la pena porque..."
- AÑADE matices: "Depende del contexto, en producción suele ser mejor X, 
  pero en prototipado Y tiene sentido"
```

#### 2.2. Ejemplos de Buena Escritura en el Prompt

**Incluir fragmento de referencia:**

```markdown
## Ejemplo de Tono y Estilo Deseado

"La elección entre LangGraph y CrewAI no es blanco o negro. En proyectos donde 
necesitas debugging visual y workflows complejos con bifurcaciones condicionales, 
LangGraph brilla. Su arquitectura basada en grafos te permite ver exactamente 
dónde falla un agente, algo invaluable cuando estás depurando a las 3 AM con un 
cliente en espera. Por otro lado, CrewAI simplifica dramáticamente la coordinación 
de múltiples agentes con roles específicos. Si tu caso de uso es un equipo de 
agentes especializados colaborando, CrewAI reduce tu código a la mitad.

La clave está en entender tus restricciones reales. ¿Tienes un equipo pequeño 
que necesita iterar rápido? CrewAI. ¿Tienes casos edge complejos y necesitas 
control granular? LangGraph. En mi experiencia, he usado ambos en producción y 
cada uno tiene su momento."

NOTA: Observa cómo se usan párrafos fluidos, primera persona cuando es relevante, 
matices ("no es blanco o negro"), y se conectan decisiones técnicas con contexto 
real ("depurando a las 3 AM").
```

---

### FASE 3: Integración del Sistema QA (CRÍTICO)

#### 3.1. Agregar Paso QA en el Notebook

**Nueva celda después de generación del artículo:**

```python
# ============================================
# PASO 4.5 (NUEVO): Quality Assurance
# ============================================

print("=" * 70)
print("🔍 FASE QA: Evaluación de Calidad del Artículo")
print("=" * 70)

# Preparar contexto para QA
related_keywords_context = {
    'keywords': [],  # Se puede extraer del análisis o contexto
    'questions': []  # Preguntas implícitas del tema
}

# Si tenemos análisis de newsletter, extraer keywords
if metodo_seleccionado == "newsletter" and newsletter_analysis:
    # Extraer keywords del análisis
    analysis_text = newsletter_analysis['raw_analysis']
    # Simplificado: palabras clave del título
    related_keywords_context['keywords'] = keyword_principal.split()

# Ejecutar QA
qa_report = core.qa_article_coverage(
    article_content=articulo,
    related_keywords_context=related_keywords_context,
    main_query=keyword_principal
)

print("\n📊 REPORTE QA GENERADO")
print("=" * 70)
print(qa_report[:1000] + "\n...\n")
print("=" * 70)
print(f"\n💾 Reporte completo en: outputs/qa_report.md")

# Opción de mejora automática
APPLY_QA_IMPROVEMENTS = True  # Cambiar a False para desactivar

if APPLY_QA_IMPROVEMENTS:
    print("\n🔧 Aplicando mejoras basadas en QA...")
    
    articulo_mejorado = core.improve_article_based_on_qa(
        article_content=articulo,
        qa_report=qa_report
    )
    
    if articulo_mejorado and articulo_mejorado != articulo:
        # Guardar versión mejorada
        with open('outputs/articulo_ghen_mejorado_qa.md', 'w', encoding='utf-8') as f:
            f.write(articulo_mejorado)
        
        articulo = articulo_mejorado  # Usar versión mejorada
        print("✅ Artículo mejorado con recomendaciones QA")
        print(f"📊 Longitud mejorada: {len(articulo)} caracteres")
    else:
        print("ℹ️  No se aplicaron mejoras (artículo ya óptimo)")
```

#### 3.2. Mejorar Función QA para Detectar Problemas Específicos

**Actualizar prompt de QA:**

```python
# Agregar sección en qa_article_coverage()
prompt = f"""...

### 6. ANÁLISIS DE ESTILO Y NARRATIVA (NUEVO)
- **Uso de listas vs. párrafos:** ¿Se abusa de listas? Ratio listas/párrafos
- **Fluidez narrativa:** ¿El texto fluye naturalmente o es mecánico?
- **Tono:** ¿Es demasiado frío/distante? ¿Falta voz humana?
- **Repeticiones:** ¿Hay frases o estructuras que se repiten demasiado?
- **Valor agregado:** ¿Cada párrafo aporta algo nuevo o repite información?
- Puntuación: X/10

### 7. RECOMENDACIONES DE ESTILO
- Secciones que necesitan convertirse de listas a párrafos
- Frases repetitivas a variar
- Lugares donde añadir voz/experiencia personal
- Transiciones a mejorar para fluidez

...
"""
```

---

### FASE 4: Post-Procesamiento Anti-Repetición

#### 4.1. Nueva Función de Detección de Repeticiones

```python
def detect_repetitions(text):
    """
    Detecta frases y estructuras repetitivas en el artículo.
    
    Returns:
        dict: {'repetitive_phrases': [...], 'repetitive_structures': [...]}
    """
    import re
    from collections import Counter
    
    # Detectar frases de 5+ palabras que se repiten
    sentences = re.split(r'[.!?]\s+', text)
    sentence_ngrams = []
    
    for sent in sentences:
        words = sent.lower().split()
        if len(words) >= 5:
            # Crear n-gramas de 5 palabras
            for i in range(len(words) - 4):
                ngram = ' '.join(words[i:i+5])
                sentence_ngrams.append(ngram)
    
    # Contar repeticiones
    ngram_counts = Counter(sentence_ngrams)
    repetitive = [ng for ng, count in ngram_counts.items() if count >= 2]
    
    # Detectar estructuras repetitivas (mismo inicio de frase)
    sentence_starts = [s.strip()[:30] for s in sentences if len(s.strip()) > 30]
    start_counts = Counter(sentence_starts)
    repetitive_structures = [start for start, count in start_counts.items() if count >= 3]
    
    return {
        'repetitive_phrases': repetitive[:10],  # Top 10
        'repetitive_structures': repetitive_structures[:5]
    }
```

#### 4.2. Función de Limpieza Post-Generación

```python
def clean_repetitions(article_text):
    """
    Limpia repeticiones obvias del artículo usando Gemini.
    """
    repetitions = detect_repetitions(article_text)
    
    if not repetitions['repetitive_phrases'] and not repetitions['repetitive_structures']:
        return article_text
    
    prompt = f"""Eres un editor técnico. Revisa este artículo y SOLO corrige repeticiones 
obvias manteniendo el contenido técnico intacto.

REPETICIONES DETECTADAS:
Frases: {', '.join(repetitions['repetitive_phrases'][:5])}
Estructuras: {', '.join(repetitions['repetitive_structures'][:3])}

ARTÍCULO:
{article_text}

INSTRUCCIONES:
- Varía las frases repetitivas manteniendo el significado técnico
- Cambia estructuras de oración repetitivas
- NO modifiques contenido técnico preciso
- NO añadas ni quites información
- Mantén el formato markdown

ARTÍCULO MEJORADO:"""
    
    response = model.generate_content(prompt)
    return response.text
```

---

## 📋 Plan de Implementación Recomendado

### Prioridad 1 (Impacto Alto, Esfuerzo Bajo)

✅ **Ajustar parámetros de generación** (30 min)
- Modificar `config.py` con perfiles dinámicos
- Probar con temperature=0.8, top_p=0.85

✅ **Integrar sistema QA en notebook** (45 min)
- Agregar celda de QA después de generación
- Activar mejora automática basada en QA

### Prioridad 2 (Impacto Alto, Esfuerzo Medio)

🔄 **Reescribir prompts de generación** (1-2 horas)
- Implementar sistema de instrucciones narrativas
- Agregar ejemplos de buen estilo
- Enfatizar párrafos sobre listas

### Prioridad 3 (Impacto Medio, Esfuerzo Medio)

🔄 **Mejorar función QA** (1 hora)
- Agregar sección de análisis de estilo
- Detectar repeticiones
- Recomendar mejoras de narrativa

### Prioridad 4 (Impacto Medio, Esfuerzo Bajo)

⏸️ **Post-procesamiento anti-repetición** (30-45 min)
- Implementar `detect_repetitions()`
- Implementar `clean_repetitions()`
- Integrar en notebook (opcional)

---

## 🎯 Métricas de Éxito

**Antes de implementar, medir:**
- Ratio listas/párrafos → Target: <30% del contenido en listas
- Repeticiones detectadas → Target: <3 frases repetitivas
- Puntuación QA de fluidez → Target: >8/10
- Puntuación QA de tono → Target: >7/10

**Después de implementar, validar:**
- ¿El contenido es más variado y menos repetitivo?
- ¿Hay más párrafos narrativos que listas?
- ¿El tono es más cálido y conversacional?
- ¿El sistema QA detecta y corrige problemas automáticamente?

---

## 🚀 Próximos Pasos Recomendados

### Implementación Inmediata (Esta Sesión)

1. **Modificar `config.py`** con perfiles de generación
2. **Agregar celda QA** en notebook
3. **Probar generación** con nuevos parámetros
4. **Comparar resultados** con versión anterior

### Implementación Próxima Sesión

5. **Reescribir prompts** con enfoque narrativo
6. **Mejorar función QA** con análisis de estilo
7. **Implementar detección de repeticiones**
8. **Documentar mejores prácticas** de generación

---

## ❓ Preguntas para Decisión

1. **¿Quieres que implemente AHORA las Prioridades 1 y 2?**
   - Ajuste de parámetros (30 min)
   - Integración QA (45 min)
   - Reescritura de prompts (1-2 horas)

2. **¿Prefieres un enfoque incremental?**
   - Primero solo parámetros y QA (hoy)
   - Luego prompts (próxima sesión)

3. **¿Algún tipo de contenido es más prioritario?**
   - ¿Empezamos optimizando "actualidad" (newsletters)?
   - ¿O prefieres optimizar "tutoriales"?

**Recomendación:** Empezar con Prioridad 1 (parámetros + QA) AHORA, probar resultados, 
y si mejora significativamente, seguir con Prioridad 2 (prompts) en la misma sesión.
