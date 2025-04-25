from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import csv

BASE_URL = "https://www.frecuento.com"

def extract_brand_from_detail(detail_driver, product_url):
    """
    Extrae la marca desde la página detalle de un producto usando driver independiente.
    """
    detail_driver.get(product_url)
    try:
        WebDriverWait(detail_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ps-product__meta"))
        )
        brand_elem = detail_driver.find_element(By.CSS_SELECTOR, "p.ml-2.text-capitalize.brand__title")
        brand = brand_elem.text.strip()
        return brand
    except Exception as e:
        print(f"No se pudo obtener la marca en detalle para {product_url}: {e}")
        return ""

def extract_product_basic_info(listing_driver, detail_driver, product_div):
    """
    Extrae info básica de producto en la página listado y llama a driver detalle para extraer marca.
    """
    try:
        title_el = product_div.find_element(By.CSS_SELECTOR, "div.title a")
        name = title_el.text.strip()
        url = title_el.get_attribute("href")

        try:
            img_el = product_div.find_element(By.CSS_SELECTOR, "div.ps-product-media a img")
            img_url = img_el.get_attribute("src")
        except NoSuchElementException:
            img_url = ""

        try:
            price_curr = product_div.find_element(By.CSS_SELECTOR, "div.price h4:nth-of-type(2)").text.strip()
        except NoSuchElementException:
            price_curr = ""

        try:
            price_old = product_div.find_element(By.CSS_SELECTOR, "del.ml-4.h9").text.strip()
        except NoSuchElementException:
            price_old = ""

        brand = extract_brand_from_detail(detail_driver, url)

        return {
            "name": name,
            "url": url,
            "image": img_url,
            "price_current": price_curr,
            "price_old": price_old,
            "brand": brand
        }
    except Exception as e:
        print(f"Error extrayendo info básica: {e}")
        return None

def scrape_products_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    # Driver para la página listado
    listing_driver = webdriver.Chrome(options=options)
    listing_driver.get(url)

    try:
        WebDriverWait(listing_driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.item-container-product"))
        )
    except:
        print("No se cargaron productos.")
        listing_driver.quit()
        return []

    product_divs = listing_driver.find_elements(By.CSS_SELECTOR, "div.item-container-product")
    print(f"Productos encontrados en la página: {len(product_divs)}")

    # Driver separado para detalle producto
    detail_driver = webdriver.Chrome(options=options)

    results = []
    for idx, div in enumerate(product_divs, 1):
        print(f"Extrayendo producto {idx}/{len(product_divs)}")
        prod_info = extract_product_basic_info(listing_driver, detail_driver, div)
        if prod_info:
            results.append(prod_info)
        time.sleep(1)  # opcional pausa para no saturar servidor

    listing_driver.quit()
    detail_driver.quit()

    return results

if __name__ == "__main__":
    url = "https://www.frecuento.com/categorias/leches/15108/productos/"
    start_time = time.time()
    productos = scrape_products_selenium(url)
   

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nScraping completado en {elapsed_time:.2f} segundos.")

    if productos:
        keys = productos[0].keys()
        with open("productos_leches_con_marca.csv", "w", newline="", encoding="utf-8") as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(productos)
        print(f"Scraping completado. Total productos extraídos: {len(productos)}")
    else:
        print("No se extrajeron productos.")