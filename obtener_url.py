from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

BASE_URL = "https://www.frecuento.com/categorias/"

def get_categories_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Para correr sin abrir ventana
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(BASE_URL)
    time.sleep(5)  # Esperar carga JS (ajustar tiempo o usar esperas explícitas)

    # Las categorías parecen estar en enlaces dentro de elementos con clase 'category-link' o similar
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/categorias/']")

    categories = {}
    for link in links:
        text = link.text.strip()
        href = link.get_attribute("href")
        if text and href and href not in categories.values():
            categories[text] = href

    driver.quit()
    return categories

if __name__ == "__main__":
    cat = get_categories_selenium()
    print("Categorías encontradas:")
    for name, url in cat.items():
        print(f"{name}: {url}")