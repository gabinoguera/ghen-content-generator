import os
import requests
import pandas as pd
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# EXTRAE SOLO 10 RESULTADOS
query = "autopublicar"
country = "ES"

def google_custom_search_df(query, country):
    API_KEY = os.getenv('API_KEY')
    API_CUSTOM_SEARCH_ID = os.getenv('API_CUSTOM_SEARCH_ID')

    if not API_KEY or not API_CUSTOM_SEARCH_ID:
        print("Error: API Key o ID de búsqueda no están cargados correctamente")
        return pd.DataFrame()

    # URL request para obtener solo los primeros 10 resultados
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={API_CUSTOM_SEARCH_ID}&q={query}&start=1&gl={country}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error en la petición: {response.status_code}")
        return pd.DataFrame()

    data = response.json()

    # Extraer los primeros 10 resultados
    items = data.get("items", [])

    if not items:
        print("No se encontraron resultados")
        return pd.DataFrame()

    # Crear un DataFrame con los resultados de la búsqueda
    df = pd.DataFrame(items, columns=['title', 'link'])

    return df

# Llamada a la función para obtener solo los primeros 10 resultados
df = google_custom_search_df(query, country)
print(df)


# -------------------SCRAPING del texto de los artículos de las 10 primeras posiciones de Google SERP

# Extraer el texto de los artículos con la librería newspapper y, en su defecto, con beautiful soup
from bs4 import BeautifulSoup
from newspaper import Article

def scrape_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        if not article.text:
            # Si Newspaper no pudo obtener el texto, intenta con BeautifulSoup
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            # Busca contenido en etiquetas <p> o <div>
            article_text = ' '.join([p.get_text() for p in soup.find_all(['p', 'div'])])

            return article_text
        return article.text
    except Exception as e:
        print(f"Error al scrapear el artículo: {str(e)}")
        return ""

def scrape_articles_in_dataframe(df):
    scraped_texts = []  # Aquí almacenaremos el texto de los artículos

    for url in df['link']:
        scraped_text = scrape_article(url)
        scraped_texts.append(scraped_text)

    # Agregamos los textos como una nueva columna en el DataFrame
    df['scraped_text'] = scraped_texts

    return df

# Llama a la función scraping de los artículos
df = scrape_articles_in_dataframe(df)

from openai import OpenAI

client = OpenAI()
import time

# Función para hacer la llamada a GPT-4 y obtener un resumen y análisis SEO
def gpt4_summarize_and_analyze(text):
    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[
        {"role": "system", "content": "You are an expert in semantic SEO optimization and content strategy."},
        {"role": "user", "content": f"Summarize the following article and extract the most important points related to SEO, including the keywords, biagrams, triagrams, structure, meta tags, and content strategy used. Focus on identifying strengths and weaknesses in SEO practices to determine what makes this article rank highly in search engines: {text}. Keep in mind that all this analysis will serve as a basis for the creation of new content that will outperform them in SEO. Output: Spanish."}
])
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error al generar el análisis con GPT-4: {str(e)}")
        return "Error al generar análisis con GPT-4"

# Función principal para procesar los artículos scrapeados
def process_scraped_articles(df):
    if df.empty:
        print("El DataFrame está vacío, no hay datos para procesar.")
        return df

    for index, row in df.iterrows():
        article_text = row['scraped_text']

        if not article_text.strip():  # Verifica si el texto está vacío
            print(f"Artículo vacío para la URL: {row['link']}, omitiendo análisis.")
            df.at[index, 'SEO Analysis'] = "No se pudo scrapear el texto del artículo"
            continue

        # Llamada a GPT-4 para analizar cada artículo
        print(f"Procesando artículo {index + 1}/{len(df)}: {row['link']}")
        summary_and_seo_analysis = gpt4_summarize_and_analyze(article_text)
        df.at[index, 'SEO Analysis'] = summary_and_seo_analysis
        time.sleep(2)  # Agrega un pequeño retraso para no sobrecargar la API

    # Guardar el DataFrame a CSV
    output_csv = "GPT4_SEO_Analysis_on_SERP_Links_Text.csv"
    df.to_csv(output_csv, index=False)
    print(f"Archivo CSV generado: {output_csv}")

    return df

# Llama a la función para procesar los artículos scrapeados y generar el CSV
df = process_scraped_articles(df)


