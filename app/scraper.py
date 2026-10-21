import json
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

USUARIO = "zachking"
URL = f"https://www.tiktok.com/@{USUARIO}"


def scraper_tiktok():
    print(f"Iniciando extracción para @{USUARIO}...")

    os.makedirs("exports", exist_ok=True)

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    try:
        driver.get(URL)
        time.sleep(6)  

        png_path = f"exports/{USUARIO}_profile.png"
        driver.save_screenshot(png_path)
        print(f"Captura guardada en: {png_path}")

        try:
            nombre = driver.find_element(
                By.XPATH, '//h1[@data-e2e="user-title"]'
            ).text
        except:
            nombre = "No detectado"

        try:
            subnombre = driver.find_element(
                By.XPATH, '//h2[@data-e2e="user-subtitle"]'
            ).text
        except:
            subnombre = "No detectado"

        try:
            siguiendo = driver.find_element(
                By.XPATH, '//strong[@data-e2e="following-count"]'
            ).text
        except:
            siguiendo = "No detectado"

        try:
            seguidores = driver.find_element(
                By.XPATH, '//strong[@data-e2e="followers-count"]'
            ).text
        except:
            seguidores = "No detectado"

        try:
            likes = driver.find_element(
                By.XPATH, '//strong[@data-e2e="likes-count"]'
            ).text
        except:
            likes = "No detectado"

        try:
            bio = driver.find_element(
                By.XPATH, '//h2[@data-e2e="user-bio"]'
            ).text
        except:
            bio = "Sin biografía"

        datos_perfil = {
            "usuario": USUARIO,
            "nombre": nombre,
            "subnombre": subnombre,
            "siguiendo": siguiendo,
            "seguidores": seguidores,
            "likes_totales": likes,
            "biografia": bio,
            "url_perfil": URL,
        }

        json_path = f"exports/{USUARIO}_profile.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(datos_perfil, f, ensure_ascii=False, indent=4)
        print(f"Archivo JSON guardado en: {json_path}")

        csv_path = f"exports/{USUARIO}_profile.csv"
        df = pd.DataFrame([datos_perfil])
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"Archivo CSV guardado en: {csv_path}")

        print("\n¡Proceso completado con éxito!")

    except Exception as e:
        print(f"Ocurrió un error durante el scraping: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    scraper_tiktok()