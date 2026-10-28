# Creación independiente

Oruga Pose Studio fue escrito para generar sus propias referencias mediante programación. El proyecto utiliza formas matemáticas (lofts de anillos elípticos, elipsoides y curvas), una solución analítica de cinemática inversa y objetivos de articulaciones authored para este catálogo.

No se descargaron ni incorporaron imágenes, modelos, texturas, rigs, hojas de estilo o código fuente de `ai-pose-gallery.pages.dev`. Ese sitio sólo motivó la idea general de una galería de referencia multiángulo. Una postura humana general o una función de búsqueda no se presenta aquí como propiedad de ese sitio; tampoco se afirma una reconstrucción idéntica de su contenido.

Las imágenes publicadas provienen del script `scripts/render.py`. Los atlas sólo reorganizan esos renders. Blender es la herramienta de creación, no una fuente de personajes prediseñados. No se usan generadores de pago, modelos externos ni proveedores de imagen.

Para auditar: regenerar una pose desde su JSON, inspeccionar su geometría con `--save-blend` y comparar las vistas. Los metadatos registran las articulaciones resueltas y avisos de alcance; la galería lista únicamente poses con cinco renders terminados.
