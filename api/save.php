<?php
/**
 * api/save.php -- guarda el progreso editorial del mapa (rutas dibujadas en
 * "Caminos", pintura de terreno, símbolos/números colocados con su ficha)
 * del editor WebGL en data/project-state.json, del lado del servidor.
 *
 * Requiere la clave de administrador en el encabezado X-Admin-Token,
 * definida en api/config.php (que NO se sube a git -- ver
 * api/config.example.php). Sin esa clave, cualquiera podría reescribir el
 * mapa de todos los visitantes.
 */

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (isset($_GET['modules'])) {
        $manifestPath = __DIR__ . '/../data/modules.json';
        header('Cache-Control: no-store, max-age=0');
        if (!file_exists($manifestPath)) { echo json_encode(['version' => 1, 'modules' => []]); exit; }
        readfile($manifestPath);
        exit;
    }
    if (isset($_GET['module'])) {
        $id = (string)$_GET['module'];
        if (!preg_match('/^mod:[a-z0-9_-]{1,80}$/', $id)) { http_response_code(400); echo json_encode(['ok' => false, 'error' => 'Identificador de módulo inválido']); exit; }
        $file = __DIR__ . '/../data/modules/' . substr($id, 4) . '.glb';
        if (!file_exists($file)) { http_response_code(404); echo json_encode(['ok' => false, 'error' => 'Módulo no encontrado']); exit; }
        header('Content-Type: model/gltf-binary');
        header('Content-Length: ' . filesize($file));
        header('Cache-Control: no-cache, must-revalidate');
        readfile($file);
        exit;
    }
    $state = __DIR__ . '/../data/project-state.json';
    $seed = __DIR__ . '/../data/project-seed.json';
    $source = file_exists($state) ? $state : $seed;
    if (!file_exists($source)) { http_response_code(404); echo json_encode(['ok' => false, 'error' => 'Todavía no hay un avance publicado']); exit; }
    header('Cache-Control: no-store, max-age=0');
    header('Vary: Accept-Encoding');
    $raw = file_get_contents($source);
    $acceptsGzip = strpos($_SERVER['HTTP_ACCEPT_ENCODING'] ?? '', 'gzip') !== false;
    if ($raw !== false && $acceptsGzip && function_exists('gzencode')) {
        $compressed = gzencode($raw, 6);
        if ($compressed !== false) {
            header('Content-Encoding: gzip');
            header('Content-Length: ' . strlen($compressed));
            echo $compressed;
            exit;
        }
    }
    if ($raw !== false) echo $raw; else readfile($source);
    exit;
}
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'Método no permitido']);
    exit;
}

$configPath = __DIR__ . '/config.php';
if (!file_exists($configPath)) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'Falta configurar api/config.php en el servidor']);
    exit;
}
$config = require $configPath;

$sentToken = $_SERVER['HTTP_X_ADMIN_TOKEN'] ?? '';
$realToken = (string)($config['admin_token'] ?? '');
if ($realToken === '' || $realToken === 'CAMBIA-ESTA-CLAVE-POR-UNA-LARGA-Y-UNICA' || !hash_equals($realToken, (string)$sentToken)) {
    http_response_code(401);
    echo json_encode(['ok' => false, 'error' => 'Clave de administrador incorrecta o no configurada']);
    exit;
}

if (isset($_GET['auth'])) {
    echo json_encode(['ok' => true]);
    exit;
}

// Publica un GLB de forma independiente al JSON del mapa. Así una copia del
// objeto sólo guarda su id y cualquier dispositivo puede descargar la malla.
if (isset($_GET['module'])) {
    if (!isset($_FILES['glb'], $_FILES['meta'])) {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'Faltan el GLB o su ficha']);
        exit;
    }
    if ($_FILES['glb']['error'] !== UPLOAD_ERR_OK || $_FILES['meta']['error'] !== UPLOAD_ERR_OK) {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'El servidor rechazó la carga; revisa upload_max_filesize y post_max_size']);
        exit;
    }
    $size = (int)$_FILES['glb']['size'];
    if ($size < 20 || $size > 80 * 1024 * 1024) {
        http_response_code(413);
        echo json_encode(['ok' => false, 'error' => 'El GLB debe pesar entre 20 bytes y 80 MB']);
        exit;
    }
    $meta = json_decode((string)file_get_contents($_FILES['meta']['tmp_name']), true);
    $categories = ['decor', 'buildings', 'animals', 'people', 'vehicles', 'ranch', 'plants'];
    if (!is_array($meta) || !preg_match('/^mod:[a-z0-9_-]{1,80}$/', (string)($meta['id'] ?? '')) ||
        !is_string($meta['name'] ?? null) || trim($meta['name']) === '' || strlen($meta['name']) > 80 ||
        !in_array($meta['category'] ?? '', $categories, true) || !is_numeric($meta['height'] ?? null) ||
        $meta['height'] < .05 || $meta['height'] > 100 || !is_numeric($meta['yaw'] ?? 0)) {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'Ficha de módulo inválida']);
        exit;
    }
    $tmp = $_FILES['glb']['tmp_name'];
    $header = file_get_contents($tmp, false, null, 0, 12);
    if ($header === false || strlen($header) !== 12 || substr($header, 0, 4) !== "glTF" || unpack('V', substr($header, 4, 4))[1] !== 2 || unpack('V', substr($header, 8, 4))[1] !== $size) {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'El archivo no es un GLB 2 válido']);
        exit;
    }
    $hash = hash_file('sha256', $tmp);
    $expectedId = 'mod:' . substr($hash, 0, 24);
    if (!hash_equals($expectedId, $meta['id'])) {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'El identificador no coincide con el contenido del GLB']);
        exit;
    }
    $dataDir = realpath(__DIR__ . '/../data');
    if ($dataDir === false) { http_response_code(500); echo json_encode(['ok' => false, 'error' => 'No existe la carpeta data/']); exit; }
    $moduleDir = $dataDir . '/modules';
    if (!is_dir($moduleDir) && !mkdir($moduleDir, 0755, true)) { http_response_code(500); echo json_encode(['ok' => false, 'error' => 'No se pudo crear la biblioteca de módulos']); exit; }
    $target = $moduleDir . '/' . substr($meta['id'], 4) . '.glb';
    if (!file_exists($target) && !move_uploaded_file($tmp, $target)) { http_response_code(500); echo json_encode(['ok' => false, 'error' => 'No se pudo guardar el GLB en el servidor']); exit; }
    $manifestPath = $dataDir . '/modules.json';
    $manifest = ['version' => 1, 'modules' => []];
    if (file_exists($manifestPath)) {
        $existing = json_decode((string)file_get_contents($manifestPath), true);
        if (is_array($existing) && isset($existing['modules']) && is_array($existing['modules'])) $manifest = $existing;
    }
    $record = ['id' => $meta['id'], 'name' => trim($meta['name']), 'category' => $meta['category'], 'height' => (float)$meta['height'], 'yaw' => (float)($meta['yaw'] ?? 0)];
    $updated = false;
    foreach ($manifest['modules'] as $i => $module) if (($module['id'] ?? '') === $record['id']) { $manifest['modules'][$i] = $record; $updated = true; break; }
    if (!$updated) $manifest['modules'][] = $record;
    $manifestTmp = $manifestPath . '.tmp';
    if (file_put_contents($manifestTmp, json_encode($manifest, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)) === false || !rename($manifestTmp, $manifestPath)) {
        http_response_code(500);
        echo json_encode(['ok' => false, 'error' => 'El GLB llegó, pero no se pudo actualizar su catálogo']);
        exit;
    }
    echo json_encode(['ok' => true, 'id' => $record['id'], 'bytes' => $size, 'updatedAt' => date('c')]);
    exit;
}

// El cuerpo viaja como multipart/form-data (campo "payload", un Blob JSON)
// en vez de JSON crudo en el body: el firewall del hosting (ModSecurity)
// aplica un límite muy bajo (~1 MB, SecRequestBodyNoFilesLimit) a peticiones
// sin archivos, pero las máscaras pintadas ya superan eso con facilidad.
// Empaquetar el JSON como un archivo adjunto evita ese límite porque entra
// por la regla de peticiones CON archivos, mucho más permisiva.
// Se mantiene el fallback a php://input por compatibilidad con llamadas
// directas (pruebas, scripts) que sí manden el JSON crudo.
if (isset($_FILES['payload']) && is_uploaded_file($_FILES['payload']['tmp_name'])) {
    $raw = file_get_contents($_FILES['payload']['tmp_name']);
} else {
    $raw = file_get_contents('php://input');
}
if ($raw === false || strlen($raw) === 0) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Sin datos en la petición']);
    exit;
}
if (strlen($raw) > 30 * 1024 * 1024) {
    http_response_code(413);
    echo json_encode(['ok' => false, 'error' => 'Los datos enviados son demasiado grandes']);
    exit;
}

$data = json_decode($raw, true);
if (!is_array($data)) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'JSON inválido']);
    exit;
}

foreach (['version', 'a', 'b', 'c', 'objects', 'camera', 'target', 'nextId'] as $key) {
    if (!array_key_exists($key, $data)) {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => "Falta el campo '$key'"]);
        exit;
    }
}

$dataDir = realpath(__DIR__ . '/../data');
if ($dataDir === false) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'No existe la carpeta data/ en el servidor']);
    exit;
}

$statePath = $dataDir . '/project-state.json';
$backupPath = $dataDir . '/project-state.backup.json';

// Respaldo de la versión anterior antes de sobrescribir -- permite volver
// atrás a mano (renombrando state.backup.json a state.json) si algo sale mal.
if (file_exists($statePath)) {
    @copy($statePath, $backupPath);
}

$data['updatedAt'] = date('c');

$tmpPath = $statePath . '.tmp';
$written = file_put_contents($tmpPath, json_encode($data, JSON_UNESCAPED_UNICODE));
if ($written === false) {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'No se pudo escribir en el servidor (revisa permisos de data/)']);
    exit;
}
rename($tmpPath, $statePath); // escritura atómica -- nunca deja el archivo a medio escribir

echo json_encode(['ok' => true, 'updatedAt' => $data['updatedAt']]);
