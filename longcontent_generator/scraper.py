"""
Módulo de scraping de keywords desde Google SERP
"""

import requests
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from collections import Counter
import random
from typing import List, Dict


class GoogleKeywordScraper:
    """Scraper simplificado de Google SERP para extraer keywords."""
    
    def __init__(self, keyword: str, language: str = 'es', country: str = 'es', 
                 scrape_levels: int = 2, headless: bool = True):
        self.keyword = keyword
        self.language = language
        self.country = country
        self.scrape_levels = scrape_levels
        self.headless = headless
        
        self.scrapeado = []
        self.contador_busquedas = []
        self.contador_suggest = []
        self.google_has_hunted_us = False
        
        self.url_inicial = (
            f"https://www.google.com/search?"
            f"hl={language}&gl={country}&q={keyword}&oq={keyword}"
        )
    
    def _setup_driver(self):
        """Configura Chrome con opciones optimizadas."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def _get_google_suggest(self, query: str):
        """Obtiene sugerencias de Google Suggest API."""
        try:
            url = (
                f'http://suggestqueries.google.com/complete/search?'
                f'output=toolbar&hl={self.language}&gl={self.country}&q={query}'
            )
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.content, 'lxml-xml')
            suggestions = [sugg['data'] for sugg in soup.find_all('suggestion')]
            return suggestions
        except:
            return []
    
    def _scroll_to_bottom(self):
        """Scroll para cargar Related Searches."""
        try:
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(0.3)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
        except:
            pass
    
    def _scrape_serp(self, busqueda, url, level):
        """Scrapea una SERP individual."""
        if busqueda.lower() in self.scrapeado or self.google_has_hunted_us:
            return []
        
        print(f"   🔍 [{level}] Scrapeando: {busqueda[:50]}...")
        
        busquedas_relacionadas = []
        
        try:
            self.driver.get(url)
            time.sleep(random.uniform(1.0, 2.0))
            
            # Check CAPTCHA
            page_source = self.driver.page_source.lower()
            if "captcha" in page_source or "unusual traffic" in page_source:
                self.google_has_hunted_us = True
                print("   ⚠️  Google bloqueó el scraping")
                return []
            
            # Aceptar cookies (solo primer nivel)
            if level == 1:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[id*='accept']")
                    if buttons:
                        buttons[0].click()
                        time.sleep(0.5)
                except:
                    pass
            
            # Scroll para cargar Related Searches
            self._scroll_to_bottom()
            
            # Extraer Related Searches
            try:
                selectors = ["a.k8XOCe", "a[href*='/search?q=']"]
                related_elements = []
                
                for selector in selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    valid = []
                    for elem in elements:
                        try:
                            text = elem.text.strip()
                            href = elem.get_attribute('href')
                            if text and len(text) > 2 and href and '/search?q=' in href:
                                # Filtrar enlaces de navegación
                                if text.lower() not in ['siguiente', 'anterior', 'next', 'previous']:
                                    valid.append(elem)
                        except:
                            continue
                    if valid:
                        related_elements = valid
                        break
                
                for element in related_elements[:10]:
                    try:
                        text = element.text.strip()
                        href = element.get_attribute('href')
                        if text and href:
                            self.contador_busquedas.append(text.lower())
                            busquedas_relacionadas.append([text, href])
                    except:
                        continue
                
                if related_elements:
                    print(f"   ✅ {len(related_elements)} Related Searches encontradas")
            except Exception as e:
                print(f"   ⚠️  Error en Related Searches: {str(e)}")
            
            # Extraer Google Suggest
            try:
                sugerencias = self._get_google_suggest(busqueda)
                sugerencias = [s for s in sugerencias if s != busqueda and s.lower() != busqueda.lower()]
                
                for sug in sugerencias[:10]:
                    self.contador_suggest.append(sug.lower())
                
                if sugerencias:
                    print(f"   ✅ {len(sugerencias[:10])} Google Suggest encontradas")
            except:
                pass
            
            self.scrapeado.append(busqueda.lower())
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        return busquedas_relacionadas
    
    def _scrape_recursive(self, busquedas, level):
        """Función recursiva para múltiples niveles."""
        if self.google_has_hunted_us or level > self.scrape_levels:
            return
        
        print(f"\n{'='*60}")
        print(f"🔄 NIVEL {level} - {len(busquedas)} búsquedas")
        print(f"{'='*60}")
        
        sub_busquedas = []
        for busqueda_data in busquedas:
            busqueda, url = busqueda_data
            resultados = self._scrape_serp(busqueda, url, level)
            sub_busquedas.extend(resultados)
        
        if level < self.scrape_levels and sub_busquedas:
            self._scrape_recursive(sub_busquedas, level + 1)
    
    def scrape(self):
        """Ejecuta el scraping completo."""
        print(f"\n{'='*60}")
        print(f"🚀 SCRAPING KEYWORDS: {self.keyword}")
        print(f"{'='*60}")
        
        self._setup_driver()
        
        try:
            self._scrape_recursive([[self.keyword, self.url_inicial]], 1)
        finally:
            if self.driver:
                self.driver.quit()
        
        # Procesar resultados
        keywords_count = Counter(self.contador_busquedas + self.contador_suggest)
        df_keywords = pd.DataFrame(
            keywords_count.most_common(),
            columns=['keyword', 'frequency']
        )
        
        print(f"\n{'='*60}")
        print(f"📊 RESULTADOS")
        print(f"{'='*60}")
        print(f"✅ Keywords únicas: {len(df_keywords)}")
        print(f"   - Related Searches: {len(self.contador_busquedas)}")
        print(f"   - Google Suggest: {len(self.contador_suggest)}")
        print(f"✅ SERPs scrapeadas: {len(self.scrapeado)}")
        
        return df_keywords


def scrape_google_keywords(keyword, language='es', country='es', 
                           scrape_levels=2, output_csv=None):
    """Función wrapper para scraping de keywords."""
    scraper = GoogleKeywordScraper(
        keyword=keyword,
        language=language,
        country=country,
        scrape_levels=scrape_levels,
        headless=True
    )
    
    df = scraper.scrape()
    
    if output_csv and not df.empty:
        df.to_csv(output_csv, index=False, encoding='utf-8')
        print(f"\n💾 Keywords guardadas en: {output_csv}")
    
    return df
