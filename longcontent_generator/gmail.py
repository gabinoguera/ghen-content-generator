"""
Módulo de integración con Gmail para leer newsletters
"""

import os
import pickle
import base64
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# Scopes necesarios para leer emails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authenticate_gmail():
    """
    Autentica con Gmail API usando OAuth 2.0
    
    La primera vez abrirá el navegador para autorizar.
    Después guarda las credenciales en token.pickle.
    
    Returns:
        Resource: Servicio de Gmail API
    """
    creds = None
    
    # Cargar credenciales guardadas si existen
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Si no hay credenciales válidas, obtener nuevas
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Buscar archivo de credenciales (soporta ambos nombres)
            credentials_file = None
            if os.path.exists('credentials.json'):
                credentials_file = 'credentials.json'
            else:
                # Buscar archivo client_secret_*.json
                for file in os.listdir('.'):
                    if file.startswith('client_secret_') and file.endswith('.json'):
                        credentials_file = file
                        break
            
            if not credentials_file:
                print("❌ Error: No se encontró archivo de credenciales OAuth")
                print("   Descarga las credenciales desde Google Cloud Console")
                print("   y guárdalas como 'credentials.json' (o usa el nombre original)")
                return None
            
            print(f"🔑 Usando archivo de credenciales: {credentials_file}")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar credenciales para próximas ejecuciones
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('gmail', 'v1', credentials=creds)
    print("✅ Autenticación exitosa con Gmail API")
    return service


def get_newsletter_by_message_id(service, message_id):
    """
    Obtiene el contenido completo de un newsletter por su ID
    
    Args:
        service: Servicio de Gmail API
        message_id: ID del mensaje (número, e.g., '1849085179733622850')
    
    Returns:
        dict: {'subject': str, 'from': str, 'body': str, 'html': str, 'url': str}
    """
    try:
        # Obtener el mensaje completo
        message = service.users().messages().get(
            userId='me', 
            id=message_id,
            format='full'
        ).execute()
        
        # Extraer headers
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'Sin asunto')
        from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Desconocido')
        
        # Extraer cuerpo (texto plano y HTML)
        body_text = ''
        body_html = ''
        
        def get_body_from_part(part):
            """Extrae texto de una parte del mensaje recursivamente"""
            nonlocal body_text, body_html
            
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body_text = base64.urlsafe_b64decode(
                    part['body']['data']
                ).decode('utf-8', errors='ignore')
            elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                body_html = base64.urlsafe_b64decode(
                    part['body']['data']
                ).decode('utf-8', errors='ignore')
            
            # Recursión para partes anidadas
            if 'parts' in part:
                for subpart in part['parts']:
                    get_body_from_part(subpart)
        
        # Procesar el payload
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                get_body_from_part(part)
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            data = message['payload']['body']['data']
            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            
            # Intentar determinar si es HTML o texto
            if '<html' in decoded.lower() or '<body' in decoded.lower():
                body_html = decoded
            else:
                body_text = decoded
        
        # Si tenemos HTML, extraer texto limpio también
        if body_html and not body_text:
            soup = BeautifulSoup(body_html, 'html.parser')
            # Remover scripts y estilos
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            body_text = soup.get_text(separator='\n', strip=True)
        
        # Construir URL del mensaje
        gmail_url = f"https://mail.google.com/mail/u/0/#inbox/{message_id}"
        
        print(f"✅ Newsletter obtenido: '{subject[:60]}...'")
        print(f"   De: {from_email}")
        print(f"   Contenido: {len(body_text)} caracteres (texto), {len(body_html)} caracteres (HTML)")
        
        return {
            'subject': subject,
            'from': from_email,
            'body': body_text,
            'html': body_html,
            'message_id': message_id,
            'url': gmail_url
        }
    
    except Exception as e:
        print(f"❌ Error al obtener mensaje {message_id}: {str(e)}")
        return None


def list_newsletters(service, sender_filter=None, subject_filter=None, max_results=10):
    """
    Lista newsletters recientes (opcionalmente filtrados)
    
    Args:
        service: Servicio de Gmail API
        sender_filter: Email del remitente para filtrar (e.g., 'newsletter@substack.com')
        subject_filter: Texto que debe aparecer en el asunto
        max_results: Número máximo de resultados (default: 10)
    
    Returns:
        list: Lista de dicts con info básica de newsletters
    """
    try:
        # Construir query de búsqueda
        query_parts = []
        
        if sender_filter:
            query_parts.append(f'from:{sender_filter}')
        
        if subject_filter:
            query_parts.append(f'subject:{subject_filter}')
        
        # Si no hay filtros, buscar en categorías típicas de newsletters
        if not query_parts:
            query_parts.append('(category:updates OR category:promotions OR label:newsletters)')
        
        query = ' '.join(query_parts)
        
        print(f"🔍 Buscando newsletters con query: {query}")
        
        # Buscar mensajes
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("⚠️  No se encontraron newsletters con esos criterios")
            return []
        
        print(f"📧 Encontrados {len(messages)} newsletters")
        
        # Obtener detalles básicos de cada mensaje
        newsletters = []
        for msg in messages:
            # Solo obtener headers para listado rápido
            msg_detail = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['Subject', 'From', 'Date']
            ).execute()
            
            headers = msg_detail['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sin asunto')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Desconocido')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            newsletters.append({
                'id': msg['id'],
                'subject': subject,
                'from': from_email,
                'date': date
            })
        
        return newsletters
    
    except Exception as e:
        print(f"❌ Error al listar newsletters: {str(e)}")
        return []


def extract_message_id_from_url(gmail_url):
    """
    Extrae el message ID de una URL de Gmail.
    Convierte IDs decimales (permmsgid) a hexadecimal requeridos por la API.
    
    Args:
        gmail_url: URL como https://mail.google.com/mail/u/0/?ui=2&ik=...&permmsgid=msg-f:1849085179733622850
                   o https://mail.google.com/mail/u/0/#inbox/1849085179733622850
    
    Returns:
        str: Message ID hexadecimal o None si no se encuentra
    """
    # Patrón 1: permmsgid=msg-f:ID o msg-a:ID (Decimal)
    match = re.search(r'msg-[fa]:(\d+)', gmail_url)
    if match:
        try:
            # Convertir decimal a hex para la API (quitando '0x')
            return hex(int(match.group(1)))[2:]
        except ValueError:
            pass
    
    # Patrón 2: #inbox/ID (Hexadecimal)
    match = re.search(r'#inbox/([a-fA-F0-9]+)', gmail_url)
    if match:
        return match.group(1)
    
    # Patrón 3: Solo el ID numérico largo (asumimos decimal si > 16 dígitos)
    match = re.search(r'(\d{18,})', gmail_url)
    if match:
        try:
            return hex(int(match.group(1)))[2:]
        except ValueError:
            pass

    # Patrón 4: ID Hexadecimal directo (fallback)
    match = re.search(r'([a-fA-F0-9]{16})', gmail_url)
    if match:
        return match.group(1)
    
    return None
