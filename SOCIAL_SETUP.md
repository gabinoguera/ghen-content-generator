# 📱 Social Media Setup Guide

Guía para configurar las APIs de redes sociales para publicación automática.

---

## 🐦 Twitter/X

### Estado actual: ✅ Solo generación (sin API por ahora)

Twitter/X cambió sus políticas de API en 2023. El tier gratuito es muy limitado.

### Opciones de publicación:

**Opción A: Manual (Recomendado inicialmente)**
1. El sistema genera el thread en `outputs/social/twitter_*.md`
2. Copias cada tweet manualmente o usas Typefully/Buffer

**Opción B: API Directa (Futuro)**
- Requiere: Twitter Developer Account ($100/mes para Basic tier)
- Pasos:
  1. Ir a https://developer.twitter.com/
  2. Crear proyecto y app
  3. Generar OAuth 2.0 credentials
  4. Añadir a `.env`:
     ```
     TWITTER_API_KEY=xxx
     TWITTER_API_SECRET=xxx
     TWITTER_ACCESS_TOKEN=xxx
     TWITTER_ACCESS_SECRET=xxx
     ```

### Límites:
- 280 caracteres por tweet
- Threads ilimitados
- Rate limit: 50 tweets/24h (Basic tier)

---

## 💼 LinkedIn

### Estado actual: 🔄 Pendiente implementación API

LinkedIn tiene una API robusta pero requiere aprobación.

### Setup:

1. **Crear LinkedIn App:**
   - Ir a https://www.linkedin.com/developers/
   - Create App → Completar información
   - Asociar a tu LinkedIn Page (necesitas una Company Page)

2. **Solicitar permisos:**
   - Products → Request Access to:
     - Share on LinkedIn (`w_member_social`)
     - Sign In with LinkedIn (para OAuth)
   - ⚠️ Puede tardar 1-2 semanas en aprobarse

3. **Configurar OAuth:**
   - Auth → Añadir redirect URL: `http://localhost:8080/callback`
   - Guardar Client ID y Client Secret

4. **Añadir a `.env`:**
   ```
   LINKEDIN_CLIENT_ID=xxx
   LINKEDIN_CLIENT_SECRET=xxx
   LINKEDIN_ACCESS_TOKEN=xxx  # Se genera después del OAuth flow
   ```

### Límites:
- 3000 caracteres por post
- Imágenes: hasta 9 por post
- Rate limit: ~100 posts/día

---

## 🔴 Reddit

### Estado actual: ⚠️ Recomendado manual

Reddit es muy sensible al spam. Publicación automática puede resultar en ban.

### Recomendación:
1. El sistema genera el post en `outputs/social/reddit_*.md`
2. Publicar **manualmente** en subreddits relevantes
3. Esperar engagement antes de postear el siguiente

### Si decides automatizar (bajo tu riesgo):

1. **Crear Reddit App:**
   - Ir a https://www.reddit.com/prefs/apps
   - Create App → Script
   - Guardar `client_id` y `client_secret`

2. **Añadir a `.env`:**
   ```
   REDDIT_CLIENT_ID=xxx
   REDDIT_CLIENT_SECRET=xxx
   REDDIT_USERNAME=xxx
   REDDIT_PASSWORD=xxx
   ```

### Subreddits sugeridos para contenido tech:
- r/MachineLearning (research-focused, 3M+ members)
- r/artificial (news, 1M+ members)
- r/LocalLLaMA (LLMs locales, muy técnico)
- r/Python (si hay código Python)
- r/programming (general)

### ⚠️ Reglas críticas de Reddit:
- NO más de 1 post/semana por subreddit
- El contenido debe aportar valor SIN el link
- Participa en comentarios, no solo postees
- Cada subreddit tiene reglas propias - léelas primero

---

## 🧵 Threads (Meta)

### Estado actual: ⏳ API recién lanzada (Junio 2024)

Meta lanzó la API de Threads recientemente.

### Setup:

1. **Requisitos previos:**
   - Cuenta de Threads vinculada a Instagram
   - Instagram Business/Creator account
   - Meta Developer account

2. **Crear Meta App:**
   - Ir a https://developers.facebook.com/
   - Create App → Business type
   - Añadir producto: Threads API

3. **Permisos necesarios:**
   - `threads_basic`
   - `threads_content_publish`

4. **Añadir a `.env`:**
   ```
   THREADS_ACCESS_TOKEN=xxx
   ```

### Límites:
- 500 caracteres por post
- 10 imágenes/carrusel
- 250 posts/24h

---

## 🚀 Próximos pasos recomendados

### Fase 1 (Ahora - Sin APIs)
```
[Artículo WordPress] → [Generar posts] → [Copiar manualmente]
```
- ✅ Twitter: Copiar thread a Typefully o publicar manual
- ✅ LinkedIn: Copiar post y publicar
- ✅ Reddit: Publicar manualmente (RECOMENDADO siempre)
- ✅ Threads: Copiar y publicar

### Fase 2 (Cuando tengas APIs aprobadas)
```
[Artículo WordPress] → [Generar posts] → [Publicar con API]
```
- Implementar `longcontent_generator/social/publishers/`
- Cada plataforma tendrá su módulo de publicación

### Fase 3 (Integración completa)
```
[Publicar WordPress] → [Trigger automático] → [Posts en todas las redes]
```
- Webhook desde WordPress
- Scheduling opcional

---

## 📋 Checklist de configuración

| Plataforma | App creada | Permisos | .env | Listo |
|------------|------------|----------|------|-------|
| Twitter/X | ⬜ | ⬜ | ⬜ | ⬜ |
| LinkedIn | ⬜ | ⬜ | ⬜ | ⬜ |
| Reddit | ⬜ | ⬜ | ⬜ | ⬜ |
| Threads | ⬜ | ⬜ | ⬜ | ⬜ |

---

## 🔐 Seguridad

Todos los tokens van en `.env` (ya está en `.gitignore`):

```bash
# Social Media APIs
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=

LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_ACCESS_TOKEN=

REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USERNAME=
REDDIT_PASSWORD=

THREADS_ACCESS_TOKEN=
```

**NUNCA** commitear estos valores al repositorio.
