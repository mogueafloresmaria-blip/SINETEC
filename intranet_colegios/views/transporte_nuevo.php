<?php
// views/transporte_nuevo.php - Módulo 13: Registrar Ruta de Transporte DYL SCHOOL
$pageTitle = 'Nueva Ruta de Transporte';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();
$error = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $nombre_ruta = trim($_POST['nombre_ruta'] ?? '');
    $conductor = trim($_POST['conductor'] ?? '');
    $placa = trim($_POST['placa'] ?? '');
    $capacidad = (int)($_POST['capacidad'] ?? 15);
    $costo_mensual = (float)($_POST['costo_mensual'] ?? 0.00);

    if (empty($nombre_ruta) || empty($conductor) || empty($placa)) {
        $error = 'Nombre de ruta, conductor y placa son obligatorios.';
    } else {
        $stmtIns = $pdo->prepare("
            INSERT INTO transporte (nombre_ruta, conductor, placa, capacidad, costo_mensual, estado)
            VALUES (?, ?, ?, ?, ?, 'Activo')
        ");
        $stmtIns->execute([$nombre_ruta, $conductor, $placa, $capacidad, $costo_mensual]);

        set_flash('success', "¡Ruta de transporte '{$nombre_ruta}' creada exitosamente!");
        header('Location: ' . url('views/transporte.php'));
        exit;
    }
}
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h3 class="h4 fw-bold text-dark mb-1">Registrar Nueva Ruta Escolar</h3>
        <p class="text-muted small mb-0">Asigne vehículos y conductores autorizados para el transporte de estudiantes.</p>
    </div>
    <a href="<?= url('views/transporte.php') ?>" class="btn btn-outline-secondary btn-sm px-3 rounded-3">
        &larr; Volver a Lista
    </a>
</div>

<?php if ($error): ?>
    <div class="alert alert-danger rounded-3 py-2 px-3 small mb-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i><?= htmlspecialchars($error) ?>
    </div>
<?php endif; ?>

<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="dyl-card p-4">
            <form method="POST" action="">
                <!-- 1. Información de la Ruta -->
                <div class="border-bottom pb-4 mb-4">
                    <h5 class="fw-bold text-primary mb-3 d-flex align-items-center gap-2">
                        <i class="bi bi-map-fill"></i> 1. INFORMACIÓN DE LA RUTA
                    </h5>
                    <div class="row g-3">
                        <div class="col-md-6">
                            <label class="form-label small fw-bold text-dark mb-1">Nombre de la Ruta <span class="text-danger">*</span></label>
                            <input type="text" name="nombre_ruta" class="form-control" placeholder="Ej. Ruta Norte - Los Olivos" required value="<?= htmlspecialchars($_POST['nombre_ruta'] ?? '') ?>">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label small fw-bold text-dark mb-1">Conductor Asignado <span class="text-danger">*</span></label>
                            <input type="text" name="conductor" class="form-control" placeholder="Ej. Mario Casas Pérez" required value="<?= htmlspecialchars($_POST['conductor'] ?? '') ?>">
                        </div>
                    </div>
                </div>

                <!-- 2. Datos del Vehículo -->
                <div class="border-bottom pb-4 mb-4">
                    <h5 class="fw-bold text-primary mb-3 d-flex align-items-center gap-2">
                        <i class="bi bi-bus-front-fill"></i> 2. DATOS DEL VEHÍCULO
                    </h5>
                    <div class="row g-3">
                        <div class="col-md-4">
                            <label class="form-label small fw-bold text-dark mb-1">Placa del Vehículo <span class="text-danger">*</span></label>
                            <input type="text" name="placa" class="form-control font-monospace" placeholder="Ej. ABC-123" required value="<?= htmlspecialchars($_POST['placa'] ?? '') ?>">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label small fw-bold text-dark mb-1">Capacidad (Asientos) <span class="text-danger">*</span></label>
                            <input type="number" min="5" max="60" name="capacidad" class="form-control" placeholder="18" value="<?= htmlspecialchars($_POST['capacidad'] ?? '18') ?>" required>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label small fw-bold text-dark mb-1">Costo Mensual (S/)</label>
                            <input type="number" step="0.50" name="costo_mensual" class="form-control" placeholder="0.00" value="<?= htmlspecialchars($_POST['costo_mensual'] ?? '150.00') ?>">
                        </div>
                    </div>
                </div>

                <div class="d-flex justify-content-between align-items-center pt-3">
                    <a href="<?= url('views/transporte.php') ?>" class="btn btn-light px-4">Cancelar</a>
                    <button type="submit" class="btn btn-dyl-primary px-4 py-2.5">
                        <i class="bi bi-check-circle me-1"></i> Guardar Ruta
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
