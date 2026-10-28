# Guía para retomar Oruga Pose Studio

## Punto de partida y objetivo

Petición: crear y publicar una alternativa independiente a una galería de referencias de pose. El objetivo ampliado es **600 poses estándar distintas**, no 600 vistas de unas pocas poses. El usuario pidió explícitamente un **maniquí verde militar con líneas de guía**. Mantener ese diseño.

Este proyecto no redistribuye materiales del sitio de referencia. Todo modelo, pose, código y render incluido se genera aquí. La biblioteca es de maniquíes adultos estilizados **no explícitos**. No hay una colección adicional de 300 poses incluida ni terminada.

## Estado verificable — 28 de octubre de 2026

El estado de producción **no se deduce de este texto**: consultar `poses/render-status.json`, `poses/gallery-manifest.json` y los archivos reales. La web calcula su contador a partir de los renders completos, nunca del objetivo de 600.

### Implementado

- Geometría propia por lofts elípticos, superficies suaves y volúmenes de extremidades.
- Torso continuo con interpolación entre orientación de pelvis y tórax.
- IK de dos segmentos, longitudes fijas y aviso por recorte mayor de 5 mm.
- Cabeza neutral, manos con dedos, gestos básicos (`relaxed`, `open`, `fist`, `point`, `thumb_up`) y pies orientables.
- Color oliva mate y líneas de construcción proyectadas sobre la superficie evaluada.
- Cinco cámaras ortográficas con encuadre automático sin recortar el cuerpo.
- Catálogo inicial de 24 posturas, generador y empaquetador reproducibles.
- Galería estática, búsqueda, filtro, favoritos, visor, PNG/JSON y temporizador.
- Atlas de alta resolución **WebP sin pérdida**, 10 poses por hoja, 5 vistas por pose.

### Trabajo pendiente al punto de control inicial

1. Incorporar y revisar el catálogo ampliado de 600 coordenadas distintas.
2. Revisar visualmente posturas de suelo, reclinadas, escalada, deportes y contactos.
3. Renderizar las cinco vistas de cada pose aceptada; nunca anunciar poses sólo nombradas.
4. Volver a empaquetar, pasar pruebas y publicar el punto de control completo.
5. Verificar la galería desplegada y sus descargas, no sólo la existencia del repositorio.

## Flujo recomendado

```bash
# 1. Probar un grupo pequeño antes de renderizar cientos.
blender -b --python scripts/render.py -- --catalog poses/catalog.json \
  --ids ID_1,ID_2 --angles three-quarter,side \
  --output renders/qa --width 600 --height 750

# 2. Inspeccionar los PNG: alcance, apoyo, manos, pies, cruces y guías.
# 3. Cuando el catálogo esté revisado, render completo.
blender -b --python scripts/render.py -- --catalog poses/catalog.json \
  --output renders/full --width 600 --height 750

# 4. Publicar sólo las poses con las cinco vistas.
python scripts/pack_gallery.py --catalog poses/catalog.json \
  --renders renders/full --width 600 --height 750

# 5. Validación y prueba local.
python -m unittest discover -s tests -v
node --check app.js
python -m http.server 8000
```

Si un lote se interrumpe, los PNG completados permanecen. Para reanudar, pasar en `--ids` sólo los IDs pendientes; no ejecutar `seed_catalog.py` sobre un catálogo ampliado porque **sobrescribe `poses/catalog.json` con las 24 semillas**. El empaquetador informa poses incompletas en `render-status.json` y no las presenta como listas.

## Esquema de pose

```json
{
  "id": "stand-neutral",
  "name": "De pie · neutral",
  "name_en": "Neutral standing",
  "category": "standing",
  "tags": ["equilibrio", "relajado"],
  "root": [0, 0, 1],
  "pelvis_euler": [0, 0, 0],
  "torso_euler": [0, 0, 0],
  "head_euler": [0, 0, 0],
  "wrists": {"L": [-0.30, -0.03, 0.90], "R": [0.30, -0.03, 0.90]},
  "elbows": {"L": [-1, 0, 1.2], "R": [1, 0, 1.2]},
  "ankles": {"L": [-0.13, 0, 0.10], "R": [0.13, 0, 0.10]},
  "knees": {"L": [-0.2, -1, 0.5], "R": [0.2, -1, 0.5]},
  "hand_directions": {"L": [0, 0, -1], "R": [0, 0, -1]},
  "hand_pose": {"L": "relaxed", "R": "relaxed"},
  "foot_euler": {"L": [0, 0, -5], "R": [0, 0, 5]},
  "support": "none"
}
```

- Unidades: metros; `x` derecha en la imagen frontal, `y` negativo al frente, `z` arriba.
- `L` / `R` nombran el lado por signo de `x`, **no la izquierda/derecha médica del sujeto**.
- `root` es el origen de pelvis/tórax. Caderas: `root + pelvis_rotation × [±0.115, 0, -0.04]`.
- Hombros: `root + torso_rotation × [±0.198, 0, 0.415]`.
- Euler XYZ en grados: X positivo inclina el cuerpo al frente; Y inclina a la derecha; Z gira sobre vertical. `torso_euler` y `pelvis_euler` son absolutos. `head_euler` se aplica respecto al tórax.
- Brazo: 0.29 m; antebrazo: 0.26 m. Muslo: 0.45 m; pantorrilla: 0.43 m.
- `wrists`/`ankles`: objetivos absolutos. El solver recorta los inalcanzables sin estirar.
- `elbows`/`knees`: puntos-polo absolutos que eligen el plano y sentido de flexión. No son los joints finales.
- `hand_directions`: vector absoluto que apunta de la muñeca hacia los dedos. Si falta, continúa el antebrazo; sobre `stool`, apunta hacia delante para descansar sobre muslos.
- `hand_pose`: gestos geométricos aproximados; no una mano anatómica completa ni un rig de todos los dedos.
- `foot_euler`: orientación absoluta del pie. Si falta, acepta `foot_yaw` por lado.
- `support`: `none` o `stool`. No se inventan objetos para otros apoyos: describirlos honestamente y añadir geometría si se necesita una mesa, muro o escalera.

## Archivos y decisiones importantes

- `scripts/render.py`: fuente de verdad de proporciones, materiales y cámaras. Cualquier cambio de geometría debe verificarse con standing/seated/dynamic y una pose reclinada antes del lote completo.
- `scripts/seed_catalog.py`: autoría de semillas; usar sólo si se quiere regenerar ese catálogo.
- `scripts/pack_gallery.py`: recorta/combina PNG ya generados; no genera poses ni completa renders faltantes.
- `gallery-data.js`: índice embebido para no necesitar API. Se genera, no se mantiene a mano.
- `poses/gallery-manifest.json`: mismo catálogo publicado, legible para otras herramientas.
- `site-assets/plates/NNN.webp`: fila = pose (`spriteRow`), columna = ángulo. Resolución por vista en `width`/`height`; la descarga recorta exactamente ese rectángulo y lo codifica PNG.
- `assets/` y `renders/`: pruebas locales/PNG; no deben subir automáticamente a Git por duplicación y tamaño.

## Calidad: comprobar antes de darlo por terminado

- [ ] 600 IDs y 600 configuraciones mayores de cuerpo distintas; no contar nombres distintos sobre una misma postura.
- [ ] Coincidencia razonable entre nombre, categoría y forma visual.
- [ ] Cinco imágenes completas por pose y cero archivos faltantes.
- [ ] Advertencias IK revisadas; ninguna extremidad estirada arbitrariamente.
- [ ] Pies/manos apoyan donde corresponde y no atraviesan torso o suelo.
- [ ] Poses reclinadas realmente orientadas y apoyadas; cámara no genera una silueta imposible.
- [ ] Guías sobre la superficie, sin aros flotantes o líneas ocultas accidentalmente.
- [ ] Atlas de alta resolución sin pérdida y descarga PNG correcta en los cinco ángulos.
- [ ] Búsqueda, categorías, teclado, móvil, favoritos y temporizador comprobados.
- [ ] Repositorio público, enlace real y estado de despliegue revisados.

### Límites conocidos

No hay detección automática robusta de autocolisiones, simulación física ni anatomía médica. La IK válida no garantiza una pose físicamente realizable. La mano es simplificada; algunos gestos de dedos son aproximados. Las mallas pueden intersectar ligeramente cerca de articulaciones por diseño del maniquí. Workbench no es un render fotorrealista y las proporciones son una estilización adulta. No presentar esas limitaciones como captura anatómica o como copia exacta de las poses del sitio original.

## Procedencia y autorización

Código MIT; geometría, coordenadas originales y renders CC0. No importar assets protegidos del sitio de referencia para aumentar el conteo. No añadir proveedores de pago, suscripciones ni nuevos costes sin autorización. Mantener el alcance de estudio de figura no explícito. Una guía de continuidad no cambia esos límites.
