import json
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

USUARIO = "willsmith"
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

        # CAMBIO 2: Captura en carpeta exports
        png_path = f"exports/{USUARIO}_profile.png"
        driver.save_screenshot(png_path)

        nombre = driver.find_element(
            By.XPATH, '//h1[@data-e2e="user-title"]'
        ).text
        subnombre = driver.find_element(
            By.XPATH, '//h2[@data-e2e="user-subtitle"]'
        ).text
        siguiendo = driver.find_element(
            By.XPATH, '//strong[@data-e2e="following-count"]'
        ).text
        seguidores = driver.find_element(
            By.XPATH, '//strong[@data-e2e="followers-count"]'
        ).text
        likes = driver.find_element(
            By.XPATH, '//strong[@data-e2e="likes-count"]'
        ).text
        bio = driver.find_element(By.XPATH, '//h2[@data-e2e="user-bio"]').text

        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(3)

        videos_links = []
        elementos_video = driver.find_elements(By.TAG_NAME, "a")
        for elem in elementos_video:
            try:
                href = elem.get_attribute("href")
                if (
                    href
                    and f"/@{USUARIO}/video/" in href
                    and href not in videos_links
                ):
                    videos_links.append(href)
            except:
                continue

        datos_perfil = {
            "usuario": USUARIO,
            "nombre": nombre,
            "subnombre": subnombre,
            "siguiendo": siguiendo,
            "seguidores": seguidores,
            "likes_totales": likes,
            "biografia": bio,
            "url_perfil": URL,
            "videos_recientes": videos_links[:6],
        }

        json_path = f"exports/{USUARIO}_profile.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(datos_perfil, f, ensure_ascii=False, indent=4)

        csv_path = f"exports/{USUARIO}_profile.csv"
        df = pd.DataFrame([datos_perfil])
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")

        print("¡Proceso completado! Archivos guardados en 'exports/'.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    scraper_tiktok()