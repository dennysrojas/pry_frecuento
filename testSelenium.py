from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import csv

BASE_URL = "https://www.frecuento.com"

def extract_product_basic_info(div):
    try:
        title_el = div.find_element(By.CSS_SELECTOR, "div.title a")
        name = title_el.text.strip()
        url = title_el.get_attribute("href")

        try:
            img_el = div.find_element(By.CSS_SELECTOR, "div.ps-product-media a img")
            img_url = img_el.get_attribute("src")
        except NoSuchElementException:
            img_url = ""

        try:
            price_curr = div.find_element(By.CSS_SELECTOR, "div.price h4:nth-of-type(2)").text.strip()
        except NoSuchElementException:
            price_curr = ""

        try:
            price_old = div.find_element(By.CSS_SELECTOR, "del.ml-4.h9").text.strip()
        except NoSuchElementException:
            price_old = ""

        return {
            "name": name,
            "url": url,
            "image": img_url,
            "price_current": price_curr,
            "price_old": price_old
        }
    except Exception as e:
        print(f"Error extrayendo info básica: {e}")
        return None

def scrape_products_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.item-container-product"))
        )
    except:
        print("No se cargaron productos.")
        driver.quit()
        return []

    product_divs = driver.find_elements(By.CSS_SELECTOR, "div.item-container-product")
    results = []

    for div in product_divs:
        prod_info = extract_product_basic_info(div)
        if prod_info:
            results.append(prod_info)

    driver.quit()
    return results

if __name__ == "__main__":
    url = "https://www.frecuento.com/categorias/leches/15108/productos/"
    productos = scrape_products_selenium(url)

    # Guardar resultados en CSV
    if productos:
        keys = productos[0].keys()
        with open("productos_leches.csv", "w", newline="", encoding="utf-8") as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(productos)
        print(f"Scraping completado. Total productos extraídos: {len(productos)}")
    else:
        print("No se extrajeron productos.")