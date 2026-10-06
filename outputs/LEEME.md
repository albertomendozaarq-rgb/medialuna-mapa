# Rancho Media Luna — versión 1

Abre **ver-rancho-3d.html** en tu navegador. Arrastra para girar y utiliza la rueda para acercarte. Funciona sin conexión y muestra la misma geometría exportada al GLB.

## Archivo para el mapa

**rancho-medialuna-v1.glb** es un modelo glTF 2.0 con geometría y colores integrados. No necesita imágenes ni texturas externas. Incluye el conjunto arquitectónico, terraza, mobiliario, tejas en relieve, jardineras, portal y torre de agua.

- Unidades: metros. Dimensiones aproximadas: 18.61 × 24.58 m de planta; 11.50 m de altura.
- Eje vertical: Y. Base: Y = 0. Origen centrado horizontalmente.
- 49,860 triángulos; un material con colores por vértice. Tamaño: 5.14 MiB.
- Colócalo sobre una plataforma nivelada: el conjunto tiene base plana y no se adapta automáticamente a pendientes.
- Es una interpretación conceptual de una imagen, con fachadas no visibles y medidas estimadas. No es un levantamiento arquitectónico ni reproduce el acabado ilustrado de la referencia.
- Las pequeñas luces son geometría coloreada; no incorporan fuentes de iluminación.
- No está instalado en el mapa. La importación depende de que su editor admita GLB o de añadir un cargador al proyecto.

## Ejemplo para el desarrollador del mapa (Three.js)

Usar el GLTFLoader correspondiente a la versión de Three.js del proyecto:

```js
loader.load('assets/rancho-medialuna-v1.glb', ({ scene: rancho }) => {
  rancho.name = 'Rancho Media Luna';
  rancho.position.set(x, alturaDePlataforma, z);
  rancho.scale.setScalar(1); // 1 unidad = 1 metro
  rancho.rotation.y = orientacionEnRadianes;
  rancho.traverse(obj => {
    if (obj.isMesh) {
      obj.castShadow = true;
      obj.receiveShadow = true;
    }
  });
  scene.add(rancho);
});
```

Para persistir la colocación, guardar la ruta del modelo, posición, rotación y escala en el sistema de guardado del mapa.

## Archivos

- `rancho-medialuna-v1.glb`: modelo para importar.
- `ver-rancho-3d.html`: visor autónomo.
- `rancho-v1-vista.png`: vista de la geometría.
- `modelo-datos.json`: dimensiones y conteos.
- `generar-rancho.py`: fuente editable de generación (Python, NumPy y Pillow; fuentes de Windows).

Verificación: estructura binaria, rangos de buffers, atributos finitos, normales y dimensiones; inspección visual de la geometría y carga del visor WebGL local. Pendiente: probar la importación dentro del mapa real.
