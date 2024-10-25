import os
import requests
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup
from newspaper import Article
import google.generativeai as genai
import streamlit as st
import time
import base64

# Cargar las variables de entorno
_ = load_dotenv(find_dotenv())

# Configurar la API de Gemini
genai.configure(api_key=os.environ['GEMINI_API_KEY'])
model = genai.GenerativeModel("gemini-1.5-flash")

# Funciones necesarias
def google_custom_search_df(query, country):
    API_KEY = os.getenv('API_KEY')
    API_CUSTOM_SEARCH_ID = os.getenv('API_CUSTOM_SEARCH_ID')
    
    if not API_KEY or not API_CUSTOM_SEARCH_ID:
        st.error("Error: API Key o ID de búsqueda no están cargados correctamente")
        return pd.DataFrame()

    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={API_CUSTOM_SEARCH_ID}&q={query}&start=1&gl={country}"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"Error en la petición: {response.status_code}")
        return pd.DataFrame()

    items = response.json().get("items", [])
    return pd.DataFrame(items, columns=['title', 'link']) if items else pd.DataFrame()

def scrape_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text or ' '.join([p.get_text() for p in BeautifulSoup(requests.get(url).content, 'html.parser').find_all(['p', 'div'])])
    except Exception as e:
        st.error(f"Error al scrapear el artículo: {str(e)}")
        return ""

def scrape_articles_in_dataframe(df):
    df['scraped_text'] = [scrape_article(url) for url in df['link']]
    return df

def gemini_summarize_and_analyze(text):
    prompt = f"""Eres un experto en optimización SEO semántica y estrategia de contenido...
    Artículo: {text}"""
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        st.error(f"Error al generar análisis con Gemini: {str(e)}")
        return ""

def process_scraped_articles(df):
    if df.empty:
        st.warning("El DataFrame está vacío.")
        return df
    for i, text in enumerate(df['scraped_text']):
        st.write(f"Procesando artículo {i + 1}/{len(df)}")
        df.at[i, 'SEO Analysis'] = gemini_summarize_and_analyze(text)
        time.sleep(2)
    return df

def generar_guia_escritor_con_gemini(df):
    contexto_seo = "\n\n".join(df['SEO Analysis'].dropna().tolist())
    prompt = f"Using this SEO analysis: {contexto_seo}..."
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        st.error(f"Error al generar la guía con Gemini: {str(e)}")
        return ""
    
def generar_outline_con_gemini(guia_para_escritor, query):
    prompt = f"""
    Use the following writer's guide: {guia_para_escritor} and generate an incredibly thorough article outline.
    Consider all possible angles and be as thorough as possible. Do not add or modify the indications of the guide, 
    just develop each of the sections for our outline. Please provide the readout/guide in well organized and hierarchical markdown.
    Output Lenguage: spanish. Codification: UTF-8
    """

    try:
        response = model.generate_content(prompt)
        outline = response.text
        st.success("Esquema generado con éxito.")
        return outline
    except Exception as e:
        st.error(f"Error al generar el esquema con Gemini: {str(e)}")
        return "Error al generar el esquema con Gemini"

def generar_contenido_seccion(seccion, guia_para_escritor):
    prompt = f"Using the following guide: {guia_para_escritor}..."
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        st.error(f"Error en la sección {seccion[:50]}: {str(e)}")
        return ""

def publicar_en_wordpress(titulo, contenido):
    login, password = os.getenv('WORDPRESS_LOGIN'), os.getenv('WORDPRESS_PASSWORD')
    if not login or not password:
        st.error("Error: credenciales de WordPress no encontradas.")
        return
    url = 'https://archivofinal.com/wp-json/wp/v2/posts'
    headers = {'Authorization': 'Basic ' + base64.b64encode(f"{login}:{password}".encode()).decode()}
    data = {'title': titulo, 'content': contenido, 'status': 'draft'}
    try:
        requests.post(url, headers=headers, json=data).raise_for_status()
        st.success("Publicado en WordPress como borrador.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error al publicar en WordPress: {str(e)}")

# Interfaz de Streamlit
st.title("Generador de Contenido SEO")
query = st.text_input("Palabra clave:")
country = st.selectbox("País:", ["ES", "US", "MX"])

if st.button("Generar Guía"):
    df = process_scraped_articles(scrape_articles_in_dataframe(google_custom_search_df(query, country)))
    guia_para_escritor = generar_guia_escritor_con_gemini(df)
    guia_editada = st.text_area("Edita la guía:", value=guia_para_escritor, height=300)

    if st.button("Generar Esquema"):
        esquema_articulo = generar_outline_con_gemini(guia_editada, query)
        st.write("Esquema del artículo:")
        st.write(esquema_articulo)

        if st.button("Generar Contenido"):
            contenido_mejorado = [generar_contenido_seccion(seccion, guia_editada) for seccion in esquema_articulo.split('\n') if seccion.strip()]
            contenido_completo = "\n\n".join(contenido_mejorado)
            contenido_editado = st.text_area("Revisa el contenido:", value=contenido_completo, height=500)

            if st.button("Guardar y Publicar"):
                with open("articulo_completo.md", "w", encoding="utf-8") as f:
                    f.write(contenido_editado)
                st.success("Artículo guardado en 'articulo_completo.md'")
                if st.checkbox("Publicar en WordPress"):
                    titulo = st.text_input("Título del artículo:")
                    if st.button("Publicar"):
                        publicar_en_wordpress(titulo, contenido_editado)