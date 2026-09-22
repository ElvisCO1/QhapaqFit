# QhapaqFit

Desktop exercise encyclopedia built with Python 3.12 and PySide6.
Enciclopedia de ejercicios de escritorio con Python 3.12 y PySide6.

## Run / Ejecutar

After setup, double-click `Run-QhapaqFit.cmd`.
Despues de instalar, haz doble clic en `Run-QhapaqFit.cmd`.

Initial setup from PowerShell in this directory:
Instalacion inicial desde PowerShell en esta carpeta:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

If the Python launcher cannot find your installation, replace `py -3.12`
with the full path to your Python 3.12 executable.
Si el lanzador no encuentra Python, sustituye `py -3.12` por la ruta
completa a tu ejecutable de Python 3.12.

## Content / Contenido

Fifteen exercises, search by Spanish/English name, muscles or equipment,
body-region and equipment filters, local favorites, optional images and MP4 playback with
pause, seek, loop, mute and volume controls.
Quince ejercicios, busqueda por nombre en espanol/ingles, musculos
o equipamiento, filtros de zona y equipamiento, favoritos locales, imagenes opcionales y reproduccion
MP4 con pausa, avance, bucle, silencio y control de volumen.

The initial interface is Spanish. Exercise guidance is draft catalog content
to review before public distribution. No routines, tracking or computer vision yet.
La interfaz inicial esta en espanol. Las indicaciones son contenido inicial
pendiente de revision antes de distribuir publicamente. Todavia no incluye
rutinas, seguimiento ni vision por computadora.

Catalog: `data/exercises.json`. Keep exercise identifiers stable.
Catalogo: `data/exercises.json`. Conserva estables los identificadores.

| Exercise / Ejercicio | Video | Image / Imagen |
| --- | --- | --- |
| Sentadilla | `sentadilla.mp4` | `sentadilla.jpg` |
| Zancada | `zancada.mp4` | `zancada.jpg` |
| Peso muerto rumano | `peso_muerto_rumano.mp4` | `peso_muerto_rumano.jpg` |
| Elevacion de pantorrillas | `elevacion_pantorrillas.mp4` | `elevacion_pantorrillas.jpg` |
| Step-up | `step_up.mp4` | `step_up.jpg` |
| Plancha normal (flexiones) | `plancha_normal.mp4` | `plancha_normal.jpg` |
| Plancha abierta (flexiones) | `plancha_abierta.mp4` | `plancha_abierta.jpg` |
| Plancha diamante (flexiones) | `plancha_diamante.mp4` | `plancha_diamante.jpg` |
| Plancha pica (flexiones) | `plancha_pica.mp4` | `plancha_pica.jpg` |
| Plancha Mike Tyson (flexiones) | `plancha_mike_tyson.mp4` | `plancha_mike_tyson.jpg` |
| Plancha arquero (flexiones) | `plancha_arquero.mp4` | `plancha_arquero.jpg` |
| Plancha espartana (flexiones) | `plancha_espartana.mp4` | `plancha_espartana.jpg` |
| Plancha inclinada (flexiones) | `plancha_inclinada.mp4` | `plancha_inclinada.jpg` |
| Plancha declinada (flexiones) | `plancha_declinada.mp4` | `plancha_declinada.jpg` |
| Plancha con rodillas apoyadas (flexiones) | `plancha_rodillas.mp4` | `plancha_rodillas.jpg` |

Videos go in `assets/videos/`; images in `assets/images/exercises/`.
PNG exercise images are also accepted. Optional muscle images go in
`assets/images/muscles/<exercise_id>.png`. Reopen an exercise or press
the refresh icon after adding files. Missing files never block the catalog.
Videos en `assets/videos/`; imagenes en `assets/images/exercises/`.
Tambien se admite PNG. Ilustraciones musculares opcionales en
`assets/images/muscles/<exercise_id>.png`. Reabre el ejercicio o pulsa
el icono de actualizar despues de agregar archivos.

Favorites are stored in Qt's local application data directory, outside the
repository. Media files are ignored by Git by default. No sample media is included.
Los favoritos se guardan en el directorio local de datos de Qt, fuera del
repositorio. Git ignora multimedia por defecto. No se incluyen videos ni fotos de ejemplo.

## Verification / Verificacion

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Packaging with PyInstaller is a later step; this version runs from source.
El empaquetado con PyInstaller queda para una fase posterior; esta version se ejecuta desde el codigo.
