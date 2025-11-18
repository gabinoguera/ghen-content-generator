#!/bin/bash

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 INSTALACIÓN DE DEPENDENCIAS GMAIL API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Script para instalar las nuevas dependencias de Gmail API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e  # Exit on error

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 INSTALADOR DE DEPENDENCIAS - GMAIL API INTEGRATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Entorno virtual NO activado"
    echo "🔧 Activando .venv..."
    
    if [[ -d ".venv" ]]; then
        source .venv/bin/activate
        echo "✅ Entorno virtual activado"
    else
        echo "❌ Error: No se encontró .venv/"
        echo "💡 Crea el entorno primero: python3 -m venv .venv"
        exit 1
    fi
else
    echo "✅ Entorno virtual activo: $VIRTUAL_ENV"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📥 Instalando dependencias desde requirements.txt..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Verificando instalación de paquetes Gmail..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 -c "import google.auth; print('✅ google-auth instalado')" || echo "❌ google-auth faltante"
python3 -c "import google_auth_oauthlib; print('✅ google-auth-oauthlib instalado')" || echo "❌ google-auth-oauthlib faltante"
python3 -c "import googleapiclient; print('✅ google-api-python-client instalado')" || echo "❌ google-api-python-client faltante"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ INSTALACIÓN COMPLETADA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo ""
echo "1️⃣  Configurar Google Cloud OAuth (sigue GMAIL_SETUP.md)"
echo "2️⃣  Descargar credentials.json → raíz del proyecto"
echo "3️⃣  Ejecutar Pipeline_GHEN_Enhanced.ipynb (Método 3)"
echo "4️⃣  Autorizar acceso en navegador (primera vez)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
