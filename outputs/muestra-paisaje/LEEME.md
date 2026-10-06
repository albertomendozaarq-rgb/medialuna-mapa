# Media Luna — primera muestra de paisaje

## Abrir la muestra

Abre `MediaLuna-muestra-paisaje.html` (el archivo autónomo entregado junto al ZIP) en Chrome o Edge. Incluye las bibliotecas y los materiales y funciona sin descargar recursos. Necesita WebGL. El guardado local depende de los permisos del navegador; **Exportar avance** conserva una copia trasladable.

Para trabajar sobre el código del ZIP, sirve esta carpeta con un servidor local y abre `index.html`.

## Qué incluye

- Maguey con hojas afiladas y curvadas; majagua de hoja ancha; vid baja y lobulada; eucalipto alto de hoja alargada; jacaranda con flores violetas; eucalipto dólar con hojas redondas verde plata.
- Hojas individuales agrupadas en copas, ramas y troncos, sombras y colores diferentes por especie. Son aproximaciones visuales, no modelos botánicos exactos.
- Tres tamaños de piedra, además de escala ajustable entre 0,2 y 3 veces.
- Seis suelos procedurales: pradera, pasto seco, tierra, grava, suelo pedregoso y bosque. No son fotografías PBR; esta muestra explora una apariencia más natural con variaciones de color, hierbas, grano y piedras pequeñas.
- Radio de pincel de 0,10 a 6 metros. El radio de 0,10 m corresponde a un ancho nominal de 0,20 m. La visibilidad a distancia depende de la resolución de pintura y de la cámara.
- Mezcla de borde ajustable, máscaras normalizadas y cobertura máxima por trazo, para evitar que los bordes se vuelvan sólidos con los eventos repetidos del puntero.
- Panel fijo de posición X/Y/Z, rotación X/Y/Z, escala, apoyo sobre terreno, duplicar y eliminar. Mover permite arrastrar sobre X/Z; la altura Y se modifica numéricamente.
- Guardado automático y explícito en IndexedDB, exportación/importación JSON y 10 pasos de deshacer. El historial de deshacer no se conserva al cerrar.

## Uso

1. **Explorar:** arrastra para girar, rueda para acercar, botón derecho para desplazar.
2. **Vegetación / Piedras:** elige una ficha y pulsa el suelo para colocar.
3. **Seleccionar:** pulsa el objeto o su nombre en la lista derecha.
4. **Mover:** arrastra el objeto. Usa los campos X/Y/Z para posición precisa.
5. **Suelos:** elige material, radio y mezcla; arrastra sobre el terreno.
6. **Guardar avance:** conserva objetos, transformaciones, pintura, radio, mezcla y cámara en este navegador. **Exportar avance** crea un JSON que puedes importar en otra copia de esta muestra.

## Alcance

Es un editor de prueba independiente, sobre un terreno sintético de 48 × 36 m. No usa ni modifica el LiDAR, los avances existentes o la web publicada. La carpeta local del repositorio indicada anteriormente estaba vacía; por eso aún no se migraron los materiales del mapa real.

Las seis especies y las rocas están generadas por código; esta entrega no contiene un GLB individual por especie. Se pueden integrar directamente en un proyecto Three.js usando `createPlant(tipo, semilla)`.

## Integración

- `flora.js`: catálogo `SPECIES`, construcción reproducible `createPlant`, limpieza `disposePlant`.
- `terrain.js`: texturas, mezcla y pincel. Para el mapa real, adaptar el mapeo mundo/máscara a los límites y resolución de su terreno; no sustituir la geometría LiDAR por el plano de esta muestra.
- `app.js`: selección, controles, guardado y catálogo.
- `style.css`: paneles fijos y distribución.
- `three.module.js`, `OrbitControls.js`: Three.js r170, licencia MIT. En producción usar una única versión de Three.js compatible con el mapa.

Resolución de máscaras: 1024 × 1024 para esta parcela. Ocho samplers de terreno (seis superficies y dos mapas de pesos), más sombras del motor. Para terrenos grandes, dividir las máscaras en parcelas o aumentar su resolución antes de ofrecer trazos de 20 cm.

Límite de la muestra: 200 objetos. Las hojas usan instancias para reducir llamadas de dibujo; no se implementó todavía LOD ni vegetación masiva. Revisar rendimiento en móviles antes de integrar.

## Verificación

Se comprobó en navegador la carga sin errores, el desplazamiento vertical y su persistencia, giro, duplicación, eliminación, deshacer/rehacer, un trazo fino, superposición de bosque sobre sendero y recuperación de la pintura al recargar. Los archivos JavaScript pasan la comprobación de sintaxis de Node.js.


## Actualización 02 — habitantes del rancho

- Catálogos separados: Animales, Personas, Autos, Corrales y Agua.
- Gavilán con plumas por capas; chiva enana; caballo y yegua; burrita mamá con flor discreta inspirada en el video; burrito con proporciones propias; gallina, gallo y pollito. Se conservan vaca y oveja como opciones adicionales.
- Personas caminando y con sombrero; pickup y vehículo familiar; caballeriza de tres puestos, corral, cerca y bebedero.
- Arroyo y estanque con transparencia y ondas animadas. Son piezas decorativas: no excavan ni calculan el cauce sobre el terreno. Ajustar altura Y según el relieve.
- Son modelos 3D estilizados de primera muestra, creados con geometría y materiales procedurales. No reproducen el detalle de las ilustraciones ni incluyen animaciones de los animales. No se generaron GLB individuales.
- En celular: un dedo gira en Explorar o edita en la herramienta elegida; dos dedos desplazan y pellizcan para zoom. Al detectar el segundo dedo se revierte el trazo o movimiento pendiente y se bloquea la edición hasta levantar ambos dedos. Colocar ocurre al soltar un toque, nunca al iniciar una navegación.
- Catálogo y Objeto se abren como paneles inferiores para dejar el mapa a todo el ancho. El botón Ver objeto de cerca centra la cámara; si hay otro árbol delante, gira la vista.

### Conservar el avance

Continuar en la MISMA dirección y navegador: http://127.0.0.1:8767/MediaLuna-muestra-paisaje.html . Cambiar de puerto, navegador o abrir como archivo utiliza otro almacenamiento. En ese caso Exportar avance e Importar permiten trasladarlo.

La actualización mantiene la base IndexedDB y el formato v1. Antes de restaurar un guardado compatible crea una copia única bajo backup-before-update-02. Recuperar respaldo restaura esa copia y permite Deshacer. No se insertan animales automáticamente en los mapas existentes.

Si el guardado es incompatible o no puede leerse, se bloquean las escrituras para no sobrescribirlo. La copia de la interfaz v1 está en la carpeta hermana respaldo-interfaz-01; esa carpeta contiene el programa anterior, no los datos del navegador.

### Verificación de esta actualización

Pruebas automatizadas: gestos con segundo dedo y cancelación; geometría finita y dimensiones conservadas al guardar de 21 objetos nuevos; compatibilidad con esquema v1; mezcla normalizada, borrado y sendero de radio 0,10 m.

Pruebas visuales en navegador: catálogo, selección, posición, acercamiento al objeto, persistencia al recargar, agua y distribución a 390 × 844. Los gestos se verificaron por su lógica de eventos; queda por comprobar la sensación táctil en un teléfono físico.

Módulos nuevos: fauna.js (animales y caballeriza), props.js (catálogo y objetos), gestures.js (gestos).
