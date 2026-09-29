<?php
/**
 * api/save.php -- guarda el progreso editorial del mapa (rutas dibujadas en
 * "Caminos", pintura de terreno, símbolos/números colocados con su ficha)
 * en data/state.json, del lado del servidor.
 *
 * Requiere la clave de administrador en el encabezado X-Admin-Token,
 * definida en api/config.php (que NO se sube a git -- ver
 * api/config.example.php). Sin esa clave, cualquiera podría reescribir el
 * mapa de todos los visitantes.
 */

header('Content-Type: application/json; charset=utf-8');

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

$raw = file_get_contents('php://input');
if ($raw === false || strlen($raw) === 0) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Sin datos en la petición']);
    exit;
}
if (strlen($raw) > 20 * 1024 * 1024) { // 20 MB -- las máscaras de pintura viajan como PNG en base64
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

foreach (['roadPaths', 'masks', 'objects'] as $key) {
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

$statePath = $dataDir . '/state.json';
$backupPath = $dataDir . '/state.backup.json';

// Respaldo de la versión anterior antes de sobrescribir -- permite volver
// atrás a mano (renombrando state.backup.json a state.json) si algo sale mal.
if (file_exists($statePath)) {
    @copy($statePath, $backupPath);
}

$data['version'] = 1;
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
