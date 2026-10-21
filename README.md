# TikTok Profile Scraper (Selenium & Python)

Este proyecto es un scraper automatizado desarrollado en Python utilizando Selenium para extraer métricas, datos públicos y capturas de pantalla de cuentas de TikTok sin la necesidad de APIs de terceros.

# Tecnologías Utilizadas

- **Python 3.x**: Lenguaje principal de desarrollo.
- **Selenium**: Automatización e interacción con el navegador Chrome.
- **Pandas**: Generación y exportación de archivos CSV.
- **JSON / CSV**: Formatos de exportación de los datos extraídos.

# Estructura del Proyecto

MiScraperTikTok/
│
├── data/                    # Archivos generados (.json, .csv y .png)
│   ├── mrbeast_profile.csv
│   ├── mrbeast_profile.json
│   └── mrbeast_profile.png
│
├── src/                     # Código fuente principal
│   └── scraper.py
│
├── .gitignore               # Archivos excluidos del repositorio
├── README.md                # Documentación del proyecto
└── requirements.txt         # Dependencias del proyecto

## Instalación y Uso


Clonar el repositorio:

```bash

git clone [https://github.com/TU_USUARIO/MiScraperTikTok.git](https://github.com/TU_USUARIO/MiScraperTikTok.git)
cd MiScraperTikTok
Instalar dependencias:

Bash
pip install -r requirements.txt
Ejecutar el scraper:

Bash
python src/scraper.py
bash
```
---

### Paso 4: Instalar `pandas` y probar la ejecución

En la terminal de VS Code, instala `pandas`:

```bash
pip install pandas
Ejecuta el script ajustado a la nueva estructura:

Bash
python src/scraper.py
Al finalizar la ejecución, abre la carpeta data/ en la barra lateral de VS Code y verás:

mrbeast_profile.png (La captura de pantalla del perfil).

mrbeast_profile.json (Los datos estructurados en formato JSON).

mrbeast_profile.csv (Los datos organizados en tabla CSV).
```