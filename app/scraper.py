import json
import os
import time
from dotenv import load_dotenv
from google import genai
import pandas as pd
from PIL import Image
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

# Cargar variables de entorno (.env)
load_dotenv()

# ---------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------
USUARIO = "mrbeast"
URL = f"https://www.tiktok.com/@{USUARIO}"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------------------------------------------------------


def analizar_big_five_multimodal(
    descripciones, rutas_imagenes, max_reintentos=5
):
    """Envía los textos y las imágenes de las portadas de los videos a Gemini (Multimodal) con reintentos."""
    print(
        "\nAnalizando personalidad Big Five con IA (Multimodal: Texto +"
        " Imágenes)..."
    )

    if not GEMINI_API_KEY:
        print(
            "Error: No se encontró GEMINI_API_KEY en las variables de entorno (.env)."
        )
        return {"Error": "API Key no configurada"}

    client = genai.Client(api_key=GEMINI_API_KEY)

    # Construir el contenido multimodal (Prompt + Textos + Imágenes)
    contenido_multimodal = [
        f"""
        Actúa como un psicólogo experto en análisis de personalidad y lingüística comportamental.
        Analiza las siguientes descripciones de publicaciones y las imágenes/portadas de los videos de TikTok pertenecientes al usuario @{USUARIO}:

        Textos de las publicaciones:
        {json.dumps(descripciones, ensure_ascii=False, indent=2)}

        Basándote en el contenido visual de las portadas (estética, expresiones, contexto visual, elementos gráficos) y en el tono y temática de los textos, estima el perfil psicológico del usuario utilizando el Modelo de los Cinco Grandes (Big Five):
        1. Openness (Apertura a la experiencia)
        2. Conscientiousness (Responsabilidad / Tesón)
        3. Extraversion (Extraversión)
        4. Agreeableness (Amabilidad)
        5. Neuroticismo (Neuroticismo / Inestabilidad emocional)

        Devuelve la respuesta estrictamente en formato JSON válido con la siguiente estructura:
        {{
          "Apertura": "X%",
          "Responsabilidad": "X%",
          "Extraversion": "X%",
          "Amabilidad": "X%",
          "Neuroticismo": "X%",
          "Justificacion": "Explicación cualitativa detallada basada tanto en los elementos visuales observados en las portadas de los videos como en los textos de las publicaciones."
        }}
        """
    ]

    # Adjuntar cada imagen descargada al prompt multimodal
    for ruta_img in rutas_imagenes:
        try:
            img = Image.open(ruta_img)
            contenido_multimodal.append(img)
        except Exception as e:
            print(f"Aviso: No se pudo adjuntar la imagen {ruta_img}: {e}")

    modelo = "gemini-3.8-flash"
    time.sleep(2)

    for intento in range(1, max_reintentos + 1):
        try:
            print(
                f"Enviando consulta multimodal a {modelo} (Intento {intento}/{max_reintentos})..."
            )
            response = client.models.generate_content(
                model=modelo,
                contents=contenido_multimodal,
            )

            texto_limpio = response.text.strip()
            if texto_limpio.startswith("```json"):
                texto_limpio = texto_limpio[7:]
            if texto_limpio.startswith("```"):
                texto_limpio = texto_limpio[3:]
            if texto_limpio.endswith("```"):
                texto_limpio = texto_limpio[:-3]

            return json.loads(texto_limpio.strip())

        except Exception as e:
            print(f"Aviso: Intento {intento} devolvió un inconveniente: {e}")
            if intento < max_reintentos:
                espera = intento * 6
                print(
                    f"Servidor saturado (503). Reintentando en {espera} segundos..."
                )
                time.sleep(espera)

    return {
        "Error": "No se pudo realizar el análisis de IA por alta demanda continua."
    }


def scraper_tiktok():
    print(f"Iniciando extracción multimodal y stealth para @{USUARIO}...")

    os.makedirs("exports", exist_ok=True)
    thumb_dir = "exports/thumbnails"
    os.makedirs(thumb_dir, exist_ok=True)

    # Configuración de Chrome con Selenium Stealth
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation", "enable-logging"]
    )
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    stealth(
        driver,
        languages=["es-ES", "es", "en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    try:
        driver.get(URL)
        time.sleep(7)

        # 1. Captura de pantalla general del perfil
        png_path = f"exports/{USUARIO}_profile.png"
        driver.save_screenshot(png_path)
        print(f"Captura de pantalla guardada en: {png_path}")

        # 2. Extraer datos del perfil
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

        # 3. Scroll paulatino para cargar las publicaciones y miniaturas
        print("Cargando publicaciones y portadas de los videos...")
        for _ in range(4):
            driver.execute_script("window.scrollBy(0, 700);")
            time.sleep(2)

        posteos_textos = []
        rutas_imagenes_descargadas = []

        # Buscar las imágenes (miniatura de los videos) y sus atributos alt/src
        elementos_imagenes = driver.find_elements(
            By.XPATH,
            '//div[@data-e2e="user-post-item"]//img | //a[contains(@href, "/video/")]//img',
        )

        contador = 0
        for elem in elementos_imagenes:
            texto = elem.get_attribute("alt") or elem.get_attribute("title") or ""
            img_url = elem.get_attribute("src")
            texto = texto.strip()

            # Filtrar avatares o textos basura
            if (
                texto
                and "Captcha" not in texto
                and "Avatar for" not in texto
                and "avatar" not in texto.lower()
                and texto not in posteos_textos
                and len(texto) > 4
            ):
                posteos_textos.append(texto)

                # Descargar la imagen de la portada si tiene URL válida
                if img_url and img_url.startswith("http"):
                    try:
                        contador += 1
                        img_resp = requests.get(img_url, timeout=10)
                        if img_resp.status_code == 200:
                            img_path = os.path.join(
                                thumb_dir, f"post_{contador}.jpg"
                            )
                            with open(img_path, "wb") as f:
                                f.write(img_resp.content)
                            rutas_imagenes_descargadas.append(img_path)
                    except Exception as img_err:
                        print(
                            f"Aviso: No se pudo descargar imagen {contador}: {img_err}"
                        )

            if len(posteos_textos) >= 10:
                break

        if not posteos_textos:
            posteos_textos.append(f"Biografía del usuario: {bio}")
        else:
            posteos_textos.insert(0, f"Biografía del usuario: {bio}")

        print(
            f"Se capturaron {len(posteos_textos)} textos y {len(rutas_imagenes_descargadas)} portadas de video."
        )

        # 4. Procesar análisis Big Five Multimodal con Gemini
        analisis_big_five = analizar_big_five_multimodal(
            posteos_textos, rutas_imagenes_descargadas
        )

        # 5. Estructurar el diccionario completo
        datos_perfil = {
            "usuario": USUARIO,
            "nombre": nombre,
            "subnombre": subnombre,
            "siguiendo": siguiendo,
            "seguidores": seguidores,
            "likes_totales": likes,
            "biografia": bio,
            "url_perfil": URL,
            "cantidad_posteos_analizados": len(posteos_textos),
            "titulos_y_descripciones_posteos": posteos_textos,
            "imagenes_portadas_guardadas": rutas_imagenes_descargadas,
            "analisis_psicologico_big_five": analisis_big_five,
        }

        # 6. Guardar en JSON
        json_path = f"exports/{USUARIO}_profile.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(datos_perfil, f, ensure_ascii=False, indent=4)
        print(f"Archivo JSON guardado en: {json_path}")

        # 7. Guardar en CSV
        csv_path = f"exports/{USUARIO}_profile.csv"
        datos_csv = {
            "usuario": USUARIO,
            "nombre": nombre,
            "seguidores": seguidores,
            "likes_totales": likes,
            "descripciones_posteos_analizados": " | ".join(posteos_textos),
            "Apertura": analisis_big_five.get("Apertura", "N/A"),
            "Responsabilidad": analisis_big_five.get("Responsabilidad", "N/A"),
            "Extraversion": analisis_big_five.get("Extraversion", "N/A"),
            "Amabilidad": analisis_big_five.get("Amabilidad", "N/A"),
            "Neuroticismo": analisis_big_five.get("Neuroticismo", "N/A"),
            "Justificacion_IA": analisis_big_five.get("Justificacion", "N/A"),
        }
        df = pd.DataFrame([datos_csv])
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"Archivo CSV guardado en: {csv_path}")

        print(
            "\n¡Proceso de Scraping + Análisis Multimodal Big Five completado!"
        )

    except Exception as e:
        print(f"Error durante la ejecución: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    scraper_tiktok()