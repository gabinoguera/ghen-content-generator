import os
import requests
import pandas as pd
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

#EXTRAE SOLO 10 RESULTADOS

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

#-------------------SCRAPING del texto de los articulos de las 10 primeras posiciones de Google SERP

#Extraer el texto de los articulos con la libreria newspapper y, en su defecto, con beautiful soup
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

import google.generativeai as genai
import time

# Configurar la API de Gemini (asumiendo que ya se ha configurado anteriormente)
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

# Cargar el modelo Gemini 1.5 Flash
model = genai.GenerativeModel("gemini-1.5-flash")

# Función para hacer la llamada a Gemini 1.5 Flash y obtener un resumen y análisis SEO
def gemini_summarize_and_analyze(text):
    try:
        prompt = f"""Eres un experto en optimización SEO semántica y estrategia de contenido.

        Resume el siguiente artículo y extrae los puntos más importantes relacionados con SEO, incluyendo las palabras clave, bigramas, trigramas, estructura, meta tags y estrategia de contenido utilizada. Enfócate en identificar fortalezas y debilidades en las prácticas de SEO para determinar qué hace que este artículo se posicione alto en los motores de búsqueda. Ten en cuenta que todo este análisis servirá como base para la creación de nuevo contenido que los superará en SEO.

        Artículo: {text}
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error al generar el análisis con Gemini 1.5 Flash: {str(e)}")
        return "Error al generar análisis con Gemini 1.5 Flash"

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

        # Llamada a Gemini 1.5 Flash para analizar cada artículo
        print(f"Procesando artículo {index + 1}/{len(df)}: {row['link']}")
        summary_and_seo_analysis = gemini_summarize_and_analyze(article_text)
        df.at[index, 'SEO Analysis'] = summary_and_seo_analysis
        time.sleep(2)  # Agrega un pequeño retraso para no sobrecargar la API

    # Guardar el DataFrame a CSV
    output_csv = "Gemini_SEO_Analysis_on_SERP_Links_Text.csv"
    df.to_csv(output_csv, index=False)
    print(f"Archivo CSV generado: {output_csv}")

    return df

# Llama a la función para procesar los artículos scrapeados y generar el CSV
df = process_scraped_articles(df)

def generar_guia_escritor_con_gemini(df):
    if 'SEO Analysis' not in df.columns:
        print("La columna 'SEO Analysis' no está presente en el DataFrame.")
        return

    # Concatenar todos los análisis SEO en un solo texto
    contexto_seo = "\n\n".join(df['SEO Analysis'].dropna().tolist())
    
    # Verificar el contenido de contexto_seo
    #print("Contenido de contexto_seo:", contexto_seo)  # Añadir esta línea para depuración

    # Prompt para Gemini
    prompt = f"""
    You are an expert at Semantic SEO. In particular, you are superhuman at taking the result of an SEO analysis of a search engine results page for a given keyword: {contexto_seo}.
    Using it to build a readout/guide that can be used to inform someone writing a long-form article about a given topic so that they can best fully cover the semantic SEO
    as shown in the SERP. The goal of this guide is to help the writer make sure that the content they are creating is as comprehensive to the semantic SEO
    expressed in the content that ranks on the first page of Google for the given {query}. With the following semantic data, please provide this readout/guide.
    This readout/guide should be useful to someone writing about the topic, and should not include instructions to add info to the article about the SERP itself.
    The SERP semantic SEO data is just to be used to help inform the guide/readout. Please provide the readout/guide in well organized and hierarchical markdown.
    Output Lenguage: spanish. Codification: UTF-8"
    """

    try:
        # Generar la guía con Gemini
        response = model.generate_content(prompt)
        guia_escritor = response.text

        print("Guía para el escritor generada con éxito.")
        return guia_escritor
    except Exception as e:
        print(f"Error al generar la guía con Gemini: {str(e)}")
        return "Error al generar la guía con Gemini"

# Llamar a la función para generar la guía
guia_para_escritor = generar_guia_escritor_con_gemini(df)

# Imprimir la guía generada
print("\nGuía para el escritor:")
print(guia_para_escritor)

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
        print("Esquema generado con éxito.")
        return outline
    except Exception as e:
        print(f"Error al generar el esquema con Gemini: {str(e)}")
        return "Error al generar el esquema con Gemini"
    return outline

# Llamar a la función para generar el esquema
esquema_articulo = generar_outline_con_gemini(guia_para_escritor, query)

# Imprimir el esquema generado
print("\nEsquema del artículo:")
print(esquema_articulo)


def generar_contenido_seccion(seccion, guia_para_escritor):
    prompt = f"""
    Basándote en la siguiente guía para el escritor: {guia_para_escritor}

    Genera contenido para la siguiente sección del artículo:

    {seccion}

    El contenido debe desarrollar únicamente lo que define la sección indicada, debe ser informativo y optimizado para SEO.
    Asegúrate de cubrir todos los puntos mencionados en la sección y expandir cada idea con ejemplos, datos y explicaciones detalladas.

    Adicionalemnte:
    1. No proporcionar información redundante
    2. No proporcionar información duplicada
    3. Reducir el formato de listas cuando no sean necesarias, prefiero parrafos.
    4. No proporcionar conclusiones

    Formato de salida: Markdown
    Idioma de salida: Español
    Codificación: UTF-8
    """

    try:
        response = model.generate_content(prompt)
        contenido_seccion = response.text
        print(f"Contenido generado con éxito para la sección: {seccion[:50]}...")
        return contenido_seccion
    except Exception as e:
        print(f"Error al generar contenido para la sección {seccion[:50]}...: {str(e)}")
        return f"Error al generar contenido para la sección: {seccion[:50]}..."

def procesar_esquema(esquema_articulo, guia_para_escritor):
    secciones = esquema_articulo.split('\n')
    contenido_mejorado = []

    for seccion in secciones:
        if seccion.strip() and not seccion.startswith('#'):
            contenido_seccion = generar_contenido_seccion(seccion, guia_para_escritor)
            contenido_mejorado.append(contenido_seccion)
            time.sleep(2)  # Pausa para evitar sobrecargar la API

    return contenido_mejorado

# Generar contenido para cada sección
contenido_mejorado = procesar_esquema(esquema_articulo, guia_para_escritor)

# Combinar las secciones mejoradas en un solo contenido
contenido_completo = "\n\n".join(contenido_mejorado)

print("\nContenido completo generado:")
print(contenido_completo[:500] + "...")  # Mostrar los primeros 500 caracteres como ejemplo

# Guardar el contenido completo en un archivo
with open("articulo_completo.md", "w", encoding="utf-8") as f:
    f.write(contenido_completo)

print("\nEl artículo completo ha sido guardado en 'articulo_completo.md'")


import base64
import requests
import os

def publicar_en_wordpress(titulo, contenido):
    # Obtener credenciales de WordPress desde variables de entorno
    login = os.getenv('WORDPRESS_LOGIN')
    password = os.getenv('WORDPRESS_PASSWORD')

    if not login or not password:
        print("Error: No se encontraron las credenciales de WordPress en las variables de entorno.")
        return

    # Configurar la URL de la API de WordPress y los encabezados de autorización
    url = 'https://archivofinal.com/wp-json/wp/v2/posts'
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(f"{login}:{password}".encode()).decode()
    }

    # Preparar el cuerpo de la solicitud
    data = {
        'title': titulo,
        'content': contenido,
        'status': 'draft'
    }

    # Realizar la solicitud POST
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print('Entrada creada correctamente en WordPress como borrador.')
    except requests.exceptions.RequestException as e:
        print(f'Error al crear la entrada en WordPress: {str(e)}')

# Combinar las secciones mejoradas en un solo contenido
contenido_completo = "\n\n".join(contenido_mejorado)

# Llamar a la función para publicar en WordPress
publicar_en_wordpress("Titulo", contenido_completo)

#----------------------------STREAMLIT: interfaz para controlar todo el proceso
import streamlit as st
import pandas as pd
# Importa las demás funciones necesarias

def main():
    st.title("Generador de Contenido SEO")

    # Configuración inicial
    query = st.text_input("Ingresa la palabra clave:")
    country = st.selectbox("Selecciona el país:", ["ES", "US", "MX"])  # Agrega más países si es necesario

    if st.button("Generar Guía"):
        # Generar DataFrame con resultados de búsqueda
        df = google_custom_search_df(query, country)
        
        # Generar guía
        guia_para_escritor = generar_guia_escritor_con_gemini(df)
        
        # Mostrar guía y permitir edición
        guia_editada = st.text_area("Edita la guía si es necesario:", value=guia_para_escritor, height=300)
        
        if st.button("Generar Esquema"):
            esquema_articulo = generar_outline_con_gemini(guia_editada, query)
            st.write("Esquema del artículo:")
            st.write(esquema_articulo)
            
            if st.button("Generar Contenido"):
                contenido_mejorado = procesar_esquema(esquema_articulo, guia_editada)
                contenido_completo = "\n\n".join(contenido_mejorado)
                
                # Mostrar contenido y permitir edición
                contenido_editado = st.text_area("Revisa y edita el contenido si es necesario:", value=contenido_completo, height=500)
                
                if st.button("Guardar y Publicar"):
                    # Guardar en archivo
                    with open("articulo_completo.md", "w", encoding="utf-8") as f:
                        f.write(contenido_editado)
                    st.success("Artículo guardado en 'articulo_completo.md'")
                    
                    # Opción para publicar en WordPress
                    if st.checkbox("Publicar en WordPress"):
                        titulo = st.text_input("Título del artículo:")
                        if st.button("Publicar"):
                            publicar_en_wordpress(titulo, contenido_editado)
                            st.success("Artículo publicado en WordPress como borrador")

if __name__ == "__main__":
    main()