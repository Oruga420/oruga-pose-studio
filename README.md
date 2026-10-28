# Oruga Pose Studio

**Referencias de pose originales y reproducibles.** Un maniquí adulto estilizado de color verde militar, con líneas de construcción, una galería buscable y cinco cámaras por postura.

> Proyecto independiente. No contiene imágenes, modelos, texturas ni código extraídos de AI Pose Gallery ni de otra biblioteca. Se reproduce el concepto general de una herramienta de referencias, no sus materiales protegidos.

## Qué hay realmente

La galería muestra **únicamente poses que tienen las cinco vistas renderizadas**. El número exacto está en [`poses/render-status.json`](poses/render-status.json); un concepto o un ángulo adicional no cuenta como otra pose. El primer punto de control contiene 24 poses semilla. La ampliación a 600 posturas estándar se está preparando y se incorpora sólo después del render y la comprobación.

- Cinco vistas ortográficas: frente, tres cuartos, perfil, espalda y picado.
- Geometría propia: torso continuo, pelvis, cabeza, extremidades con volúmenes y manos con dedos.
- Guías de eje de cabeza, ojos, tórax, cintura, pelvis, brazos y muslos.
- Búsqueda, categorías, favoritos locales, pose aleatoria y temporizador de dibujo.
- Descarga PNG de cada vista y JSON con la definición de cada pose.
- Generador Blender sin modelos externos ni servicios de pago.

## Abrir la galería

```bash
python -m http.server 8000
# Abrir http://localhost:8000
```

No requiere npm, CDN, cuenta, base de datos ni una clave API. Los favoritos se guardan sólo en `localStorage` del navegador. La descarga PNG usa un recorte del atlas WebP **sin pérdida**; no aumenta la resolución ni sintetiza detalle. Abrir `index.html` directamente puede impedir la descarga por las restricciones de archivos locales del navegador: usa el servidor anterior.

## Reproducir los renders

Requisitos: **Blender 4.3+**, Python 3.10+ y Pillow para empaquetar. Verificado inicialmente con Blender 4.3.2.

```bash
python -m pip install -r requirements.txt

# Las 24 poses semilla, con las cinco vistas (600 × 750 px por vista):
blender -b --python scripts/render.py -- \
  --catalog poses/seed-24.json --output renders/seed-24 \
  --width 600 --height 750

# Una pose y dos cámaras, útil para iterar:
blender -b --python scripts/render.py -- \
  --catalog poses/seed-24.json --ids stand-neutral \
  --angles front,three-quarter --output renders/test

# Empaquetar sólo las poses completas:
python scripts/pack_gallery.py --catalog poses/seed-24.json \
  --renders renders/seed-24 --width 600 --height 750

# Pruebas sin lanzar Blender:
python -m unittest discover -s tests -v
node --check app.js
```

El motor predeterminado es **Workbench**: sombreado de estudio mate, guías visibles, sin ruido de Monte Carlo. También se aceptan `--engine CYCLES` y `--engine BLENDER_EEVEE_NEXT`, pero su iluminación y rendimiento difieren. En la instalación inicial no había OpenImageDenoise; por ello el denoiser no es una dependencia. `--save-blend` conserva una escena editable por pose.

### Estructura

| Ruta | Contenido |
|---|---|
| `scripts/render.py` | Geometría, IK analítica, cámaras y render |
| `scripts/seed_catalog.py` | Autoría reproducible de las 24 poses iniciales |
| `scripts/pack_gallery.py` | Atlas WebP sin pérdida, miniaturas e índice web |
| `poses/seed-24.json` | Definiciones completas de las poses iniciales |
| `poses/catalog.json` | Catálogo de trabajo activo |
| `poses/gallery-manifest.json` | Poses realmente publicadas y ubicación en atlas |
| `site-assets/plates/` | 10 poses × 5 vistas por hoja de alta resolución |
| `site-assets/thumbs/` | Miniaturas de navegación; no son los archivos de descarga |
| `renders/` | PNG y metadatos locales, excluidos de Git para evitar duplicación |
| `HANDOFF.md` | Estado, decisiones, esquema y guía para retomar |

## Editar una postura

Cada pose usa coordenadas **en metros**: `x` horizontal, `y` negativo hacia el frente y `z` hacia arriba. `L` es el lado de coordenada `x` negativa; `R`, positiva. `wrists` y `ankles` son objetivos de IK; **`elbows` y `knees` son polos de flexión, no posiciones exactas de articulación**. Ver el esquema detallado en [HANDOFF.md](HANDOFF.md).

La IK mantiene longitudes constantes. Si un objetivo queda fuera de alcance, se ajusta al límite y se registra una advertencia. Esto no sustituye la revisión visual: una pose puede tener longitudes válidas y aun así presentar contactos poco convincentes o intersecciones.

## Licencias y procedencia

- **Código:** [MIT](LICENSE).
- **Geometría procedural, coordenadas originales y renders de este proyecto:** [CC0 1.0](ASSET-LICENSE.md).
- No se concede ninguna licencia sobre marcas o materiales de terceros.
- Son referencias de dibujo estilizadas, **no anatomía clínica ni captura de movimiento de personas reales**. El maniquí es adulto, neutral y no explícito.

Ver [PROVENANCE.md](PROVENANCE.md) para la declaración de creación independiente y [HANDOFF.md](HANDOFF.md) para límites conocidos.
