import os
import requests
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from bs4 import BeautifulSoup
from newspaper import Article
from openai import OpenAI
import time
import re

# Cargar las variables de entorno
_ = load_dotenv(find_dotenv())

# API setup
API_KEY = os.getenv('API_KEY')
API_CUSTOM_SEARCH_ID = os.getenv('API_CUSTOM_SEARCH_ID')

if not API_KEY or not API_CUSTOM_SEARCH_ID:
    raise ValueError("API Key o ID de búsqueda no están cargados correctamente")

# Función para obtener resultados de Google Custom Search
def google_custom_search_df(query, country):
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={API_CUSTOM_SEARCH_ID}&q={query}&start=1&gl={country}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error en la petición: {response.status_code}")
        return pd.DataFrame()

    data = response.json()
    items = data.get("items", [])

    if not items:
        print("No se encontraron resultados")
        return pd.DataFrame()

    df = pd.DataFrame(items, columns=['title', 'link'])
    return df

# Scraping de artículos
def scrape_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        if not article.text:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            article_text = ' '.join([p.get_text() for p in soup.find_all(['p', 'div'])])
            return article_text
        return article.text
    except Exception as e:
        print(f"Error al scrapear el artículo: {str(e)}")
        return ""

def scrape_articles_in_dataframe(df):
    df['scraped_text'] = df['link'].apply(scrape_article)
    return df

# Llamada a GPT-4 para resumir y analizar SEO
client = OpenAI()

def gpt4_summarize_and_analyze(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in semantic SEO optimization and content strategy."},
                {"role": "user", "content": f"Summarize the following article and extract the most important points related to SEO, including the keywords, biagrams, triagrams, structure, meta tags, and content strategy used. Focus on identifying strengths and weaknesses in SEO practices to determine what makes this article rank highly in search engines: {text}. Output: Spanish."}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error al generar el análisis con GPT-4: {str(e)}")
        return "Error al generar análisis con GPT-4"

# Procesar artículos scrapeados
def process_scraped_articles(df):
    if df.empty:
        print("El DataFrame está vacío, no hay datos para procesar.")
        return df

    for index, row in df.iterrows():
        article_text = row['scraped_text']

        if not article_text.strip():
            print(f"Artículo vacío para la URL: {row['link']}, omitiendo análisis.")
            df.at[index, 'SEO Analysis'] = "No se pudo scrapear el texto del artículo"
            continue

        print(f"Procesando artículo {index + 1}/{len(df)}: {row['link']}")
        summary_and_seo_analysis = gpt4_summarize_and_analyze(article_text)
        df.at[index, 'SEO Analysis'] = summary_and_seo_analysis
        time.sleep(2)

    output_csv = "GPT4_SEO_Analysis_on_SERP_Links_Text.csv"
    df.to_csv(output_csv, index=False)
    print(f"Archivo CSV generado: {output_csv}")

    return df

import pandas as pd
from openai import OpenAI
import os

client = OpenAI()

# Generar contenido a partir del análisis SEO
def generar_guia_inicial(output_csv):
    try:
        # Verificar si el archivo existe
        if not os.path.exists(output_csv):
            raise FileNotFoundError(f"El archivo {output_csv} no existe.")

        # Leer el archivo CSV
        df = pd.read_csv(output_csv)
        
        # Verificar si la columna 'SEO Analysis' existe
        if 'SEO Analysis' not in df.columns:
            raise ValueError("La columna 'SEO Analysis' no está presente en el archivo CSV.")
        
        # Extraer los análisis SEO
        analisis_seo = df['SEO Analysis'].tolist()
        
        # Combinar todos los análisis en un solo texto
        texto_completo = ' '.join(analisis_seo)
        
        # Llamada a GPT-4 para generar la guía inicial
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un experto en SEO y creación de contenido. Tu tarea es crear una guía inicial basada en el análisis SEO proporcionado."},
                {"role": "user", "content": f"Basándote en el siguiente análisis SEO, genera una guía inicial que cubra los temas clave y las mejores prácticas de SEO. La guía debe ser estructurada y fácil de seguir para que otro agente la utilice como base para crear contenido más detallado: {texto_completo}"}
            ]
        )
        
        guia_inicial = response.choices[0].message.content
        
        # Guardar la guía inicial en un archivo markdown
        with open('initial_guide.md', 'w', encoding='utf-8') as f:
            f.write(guia_inicial)
        
        print("Guía inicial generada y guardada en 'initial_guide.md'")
        return guia_inicial
    
    except Exception as e:
        print(f"Error al generar la guía inicial: {str(e)}")
        return None

# Llamar a la función para generar la guía inicial
guia_inicial = generar_guia_inicial("GPT4_SEO_Analysis_on_SERP_Links_Text.csv")
