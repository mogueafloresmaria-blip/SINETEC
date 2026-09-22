<?php
// config/app.php - Configuración General, Sesión y Helpers para DYL SCHOOL

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

require_once __DIR__ . '/db.php';

// Constantes institucionales
define('APP_NAME', 'DYL SCHOOL');
define('APP_SUBTITLE', 'Plataforma de Gestión Académica');
define('SYSTEM_DATE', '09/01/2026');
define('SYSTEM_YEAR', 2026);

// Detección dinámica de BASE_URL para funcionar tanto con 'php -S' en la raíz como en subcarpetas
function get_base_url(): string {
    $scriptDir = str_replace('\\', '/', dirname($_SERVER['SCRIPT_NAME'] ?? ''));
    
    // Si estamos dentro de /views o /config, subir un nivel
    if (str_ends_with($scriptDir, '/views') || str_ends_with($scriptDir, '/config')) {
        $scriptDir = dirname($scriptDir);
    }
    
    $base = rtrim($scriptDir, '/');
    return $base === '' ? '' : $base;
}

define('BASE_URL', get_base_url());

function url(string $path = ''): string {
    $cleanPath = '/' . ltrim($path, '/');
    return BASE_URL . $cleanPath;
}

function asset(string $path = ''): string {
    return url('assets/' . ltrim($path, '/'));
}

function money_format_pen(float $amount): string {
    return 'S/ ' . number_format($amount, 2, '.', ',');
}

// Helpers de autenticación
function is_logged_in(): bool {
    return isset($_SESSION['user']) && !empty($_SESSION['user']['id']);
}

function current_user(): ?array {
    return $_SESSION['user'] ?? null;
}

function require_login(): void {
    if (!is_logged_in()) {
        header('Location: ' . url('index.php'));
        exit;
    }
}

// Mensajes Flash
function set_flash(string $type, string $message): void {
    $_SESSION['flash'] = ['type' => $type, 'message' => $message];
}

function get_flash(): ?array {
    if (isset($_SESSION['flash'])) {
        $flash = $_SESSION['flash'];
        unset($_SESSION['flash']);
        return $flash;
    }
    return null;
}
