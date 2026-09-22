<?php
// includes/header.php - Encabezado y Navbar compartido para DYL SCHOOL
require_once __DIR__ . '/../config/app.php';
require_login();

$user = current_user();
$pageTitle = $pageTitle ?? 'Panel';
$flash = get_flash();
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($pageTitle) ?> · DYL SCHOOL</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
    <!-- Estilos DYL SCHOOL -->
    <link rel="stylesheet" href="<?= asset('css/dyl_school.css') ?>?v=<?= time() ?>">
    
    <!-- Estilos Críticos Garantizados para la Estructura de Dos Columnas (Sidebar Fijo 260px) -->
    <style>
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            min-height: 100vh;
            background-color: #F8FAFC;
        }
        .dyl-wrapper {
            display: flex !important;
            min-height: 100vh !important;
            width: 100% !important;
            position: relative !important;
        }
        .dyl-sidebar {
            width: 260px !important;
            min-width: 260px !important;
            max-width: 260px !important;
            height: 100vh !important;
            position: fixed !important;
            top: 0 !important;
            bottom: 0 !important;
            left: 0 !important;
            background-color: #0F172A !important;
            color: #F8FAFC !important;
            z-index: 1050 !important;
            display: flex !important;
            flex-direction: column !important;
            overflow-y: auto !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
            box-shadow: 2px 0 12px rgba(0, 0, 0, 0.25) !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        .dyl-main {
            margin-left: 260px !important;
            width: calc(100% - 260px) !important;
            min-width: 0 !important;
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
            min-height: 100vh !important;
            background-color: #F8FAFC !important;
        }
        .dyl-menu-link {
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
            padding: 9px 14px !important;
            color: #CBD5E1 !important;
            text-decoration: none !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            transition: all 0.15s ease-in-out !important;
        }
        .dyl-menu-link i {
            font-size: 1.1rem !important;
            width: 22px !important;
            text-align: center !important;
            color: #94A3B8 !important;
            transition: color 0.15s ease-in-out !important;
        }
        .dyl-menu-link:hover {
            background-color: #334155 !important;
            color: #FFFFFF !important;
        }
        .dyl-menu-link:hover i {
            color: #FFFFFF !important;
        }
        .dyl-menu-link.active {
            background-color: #4F46E5 !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35) !important;
        }
        .dyl-menu-link.active i {
            color: #FFFFFF !important;
        }
    </style>
</head>
<body>

<div class="dyl-wrapper" style="display: flex !important; min-height: 100vh !important; width: 100% !important;">
    <!-- Sidebar Compartido Fijo a la Izquierda (260px) -->
    <?php require_once __DIR__ . '/sidebar.php'; ?>

    <!-- Área de Contenido Principal a la Derecha -->
    <div class="dyl-main" style="margin-left: 260px !important; width: calc(100% - 260px) !important; min-width: 0 !important; flex: 1 !important; display: flex !important; flex-direction: column !important; min-height: 100vh !important; background-color: #F8FAFC !important;">
        <!-- Navbar Superior Compartido -->
        <header class="dyl-header">
            <div class="dyl-header-left">
                <h2 class="dyl-header-title"><?= htmlspecialchars($pageTitle) ?></h2>
            </div>
            <div class="dyl-header-right">
                <!-- Píldora con Fecha del Sistema -->
                <div class="dyl-date-pill">
                    <i class="bi bi-calendar-event-fill text-indigo-500"></i>
                    <span><?= SYSTEM_DATE ?></span>
                </div>

                <!-- Usuario y Avatar -->
                <div class="dyl-user-chip">
                    <div class="dyl-user-avatar">
                        <?= strtoupper(substr($user['nombres'] ?? 'J', 0, 1)) ?>
                    </div>
                    <div class="dyl-user-info">
                        <span class="dyl-user-name">¡Hola, <?= htmlspecialchars($user['nombres'] ?? 'Joseph') ?>!</span>
                        <span class="dyl-user-role"><?= htmlspecialchars(ucfirst($user['rol'] ?? 'Admin')) ?></span>
                    </div>
                </div>
            </div>
        </header>

        <!-- Mensajes Flash de Notificación -->
        <?php if ($flash): ?>
            <div class="px-4 pt-3">
                <div class="alert alert-<?= $flash['type'] === 'error' ? 'danger' : ($flash['type'] === 'success' ? 'success' : 'info') ?> alert-dismissible fade show rounded-3 shadow-sm border-0 d-flex align-items-center gap-2 mb-0" role="alert">
                    <i class="bi bi-<?= $flash['type'] === 'error' ? 'exclamation-circle-fill' : 'check-circle-fill' ?> fs-5"></i>
                    <div><?= htmlspecialchars($flash['message']) ?></div>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            </div>
        <?php endif; ?>

        <!-- Contenedor de la Vista -->
        <main class="dyl-content">
