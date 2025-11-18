# 📧 Gmail API Setup Guide

## 🎯 Objetivo
Configurar la autenticación OAuth 2.0 de Gmail API para leer newsletters desde tu bandeja de entrada.

---

## ⚙️ CONFIGURACIÓN PASO A PASO

### 1️⃣ Crear Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Haz clic en el selector de proyectos (arriba a la izquierda)
3. Clic en **"Nuevo Proyecto"**
4. Nombre: `GHEN Content Generator` (o el que prefieras)
5. Clic en **"Crear"**

---

### 2️⃣ Habilitar Gmail API

1. En el panel lateral izquierdo: **APIs y servicios → Biblioteca**
2. Busca: `Gmail API`
3. Clic en **Gmail API** (de Google)
4. Clic en **"Habilitar"**

> ✅ Deberías ver "API habilitada" en verde

---

### 3️⃣ Configurar Pantalla de Consentimiento OAuth

1. **APIs y servicios → Pantalla de consentimiento de OAuth**
2. Tipo de usuario: **Externo** (para uso personal)
3. Clic en **"Crear"**

#### Configuración de la aplicación:
- **Nombre de la aplicación**: `GHEN Content Generator`
- **Correo de asistencia**: tu email
- **Logotipo**: (opcional, puedes dejarlo vacío)
- **Dominios autorizados**: (déjalo vacío)
- **Información de contacto del desarrollador**: tu email

4. Clic en **"Guardar y continuar"**

#### Ámbitos (Scopes):
5. Clic en **"Agregar o quitar ámbitos"**
6. Busca y selecciona:
   ```
   https://www.googleapis.com/auth/gmail.readonly
   ```
   (Gmail API → "Ver tu correo electrónico" - Solo lectura)
7. Clic en **"Actualizar"**
8. Clic en **"Guardar y continuar"**

#### Usuarios de prueba:
9. Clic en **"Agregar usuarios"**
10. Agrega tu dirección de Gmail (la que usarás para leer newsletters)
11. Clic en **"Agregar"**
12. Clic en **"Guardar y continuar"**

13. Revisa el resumen y clic en **"Volver al panel"**

---

### 4️⃣ Crear Credenciales OAuth 2.0

1. **APIs y servicios → Credenciales**
2. Clic en **"+ Crear credenciales"** (arriba)
3. Selecciona: **"ID de cliente de OAuth"**

#### Configuración:
- **Tipo de aplicación**: **Aplicación de escritorio**
- **Nombre**: `GHEN Desktop Client` (o el que prefieras)

4. Clic en **"Crear"**

#### Descargar credenciales:
5. Aparecerá un modal con tu Client ID y Client Secret
6. Clic en **"Descargar JSON"**
7. Guarda el archivo como: `credentials.json`

---

### 5️⃣ Instalar credentials.json en el Proyecto

```bash
# Mueve el archivo descargado a la raíz del proyecto
mv ~/Downloads/client_secret_*.json /Users/gabrielnoguera/Documents/ghen/LongContent_Generator_Script/credentials.json
```

**Estructura esperada:**
```
LongContent_Generator_Script/
├── credentials.json  ← NUEVO (OAuth credentials)
├── .env              ← Ya existente (Gemini API key)
├── longcontent_generator/
│   ├── gmail.py      ← Módulo de Gmail
│   └── ...
└── Pipeline_GHEN_Enhanced.ipynb
```

---

## 🔐 PRIMERA AUTENTICACIÓN

### Ejecutar el script de prueba:

```bash
# Activar entorno
source .venv/bin/activate

# Test de autenticación
python3 -c "from longcontent_generator import core; core.list_gmail_newsletters(max_results=5)"
```

### ¿Qué sucederá?

1. **Primera vez**:
   - Se abrirá tu navegador
   - Verás pantalla de Google OAuth
   - Mensaje: "Esta app no está verificada" → **Clic en "Avanzado"**
   - Clic en **"Ir a GHEN Content Generator (no seguro)"**
   - Revisa permisos (solo lectura de Gmail)
   - Clic en **"Continuar"**

2. **Token guardado**:
   - Se creará `token.pickle` en la raíz del proyecto
   - **Próximas ejecuciones no pedirán autorización** (token válido 7 días)

3. **Salida esperada**:
   ```
   📧 Listando newsletters de Gmail...
   ✅ Conectado a Gmail API

   📬 NEWSLETTERS DISPONIBLES:
   1. 📨 [Newsletter Title 1]
      De: sender@example.com
      Fecha: 2025-01-15
      ID: 1849085179733622850
   ...
   ```

---

## 📋 CHECKLIST DE VERIFICACIÓN

- [ ] Proyecto creado en Google Cloud Console
- [ ] Gmail API habilitada
- [ ] Pantalla de consentimiento OAuth configurada (tipo: Externo)
- [ ] Scope agregado: `gmail.readonly`
- [ ] Tu email agregado como usuario de prueba
- [ ] Credenciales OAuth creadas (tipo: Aplicación de escritorio)
- [ ] `credentials.json` descargado y colocado en raíz del proyecto
- [ ] Script de prueba ejecutado exitosamente
- [ ] `token.pickle` generado (después de autorizar)

---

## 🔧 TROUBLESHOOTING

### Error: "Archivo credentials.json no encontrado"
- Verifica que `credentials.json` esté en la raíz del proyecto
- Verifica que no se llame `client_secret_*.json` (debe ser renombrado)

### Error: "Redirect URI mismatch"
- Asegúrate de crear **Aplicación de escritorio** (no Web)
- El módulo Gmail usa `redirect_uri=localhost` automáticamente

### Error: "This app isn't verified"
- Normal para apps en desarrollo
- Clic en "Avanzado" → "Ir a [nombre app] (no seguro)"
- Solo tú usarás esta app, es seguro continuar

### Error: "Access blocked: Authorization Error"
- Verifica que tu email esté en "Usuarios de prueba"
- Verifica que el scope `gmail.readonly` esté agregado

### Token expirado (después de 7 días)
- Elimina `token.pickle`
- Ejecuta el script de prueba de nuevo → re-autoriza en navegador

---

## 🚀 USO EN EL NOTEBOOK

Una vez autenticado, en `Pipeline_GHEN_Enhanced.ipynb`:

```python
# Método 3: Newsletter
metodo_seleccionado = "newsletter"
usar_gmail = True  # ← TRUE para usar Gmail API

# Opción A: Pegar URL directa
gmail_url = "https://mail.google.com/mail/u/0/#inbox/1849085179733622850"

# Opción B: Listar newsletters disponibles
newsletters = core.list_gmail_newsletters(
    sender_filter="newsletter@substack.com",  # Filtro opcional
    max_results=10
)
# → Copia el URL del newsletter que quieras analizar
```

---

## 🔒 SEGURIDAD

- **credentials.json**: Contiene client ID/secret (NO COMMITEAR)
- **token.pickle**: Token de acceso personal (NO COMMITEAR)
- Ambos están en `.gitignore` automáticamente
- Scope mínimo: `gmail.readonly` (solo lectura)
- Token expira cada 7 días, se renueva automáticamente

---

## 📚 RECURSOS ADICIONALES

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)

---

## ✅ LISTO PARA USAR

Si completaste todos los pasos y el script de prueba funcionó:

🎉 **¡Gmail API está configurado correctamente!**

Ahora puedes:
- Leer newsletters desde Gmail
- Analizar contenido con Gemini
- Generar artículos basados en newsletters privados
