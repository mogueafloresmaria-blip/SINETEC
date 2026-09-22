<?php
// views/transporte.php - Módulo 13: Transporte Escolar DYL SCHOOL
$pageTitle = 'Transporte Escolar';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// Métricas de Transporte
$totalRutas = $pdo->query("SELECT COUNT(*) FROM transporte WHERE estado = 'Activo'")->fetchColumn() ?: 0;
$totalAlumnosTransporte = 0;
$totalCapacidad = $pdo->query("SELECT SUM(capacidad) FROM transporte WHERE estado = 'Activo'")->fetchColumn() ?: 0;

$stmt = $pdo->query("SELECT * FROM transporte WHERE estado = 'Activo' ORDER BY id DESC");
$rutas = $stmt->fetchAll();
?>

<!-- Métricas de Transporte -->
<div class="row g-3 mb-4">
    <div class="col-4">
        <div class="dyl-card p-3 d-flex align-items-center justify-content-between">
            <div>
                <div class="text-muted small fw-bold text-uppercase">RUTAS</div>
                <div class="h3 fw-bold text-dark my-1"><?= $totalRutas ?></div>
            </div>
            <div class="rounded-3 p-2.5 fs-4" style="background: #EEF2FF; color: #4F46E5;">
                <i class="bi bi-bus-front-fill"></i>
            </div>
        </div>
    </div>
    <div class="col-4">
        <div class="dyl-card p-3 d-flex align-items-center justify-content-between">
            <div>
                <div class="text-muted small fw-bold text-uppercase">ACTIVOS</div>
                <div class="h3 fw-bold text-dark my-1"><?= $totalAlumnosTransporte ?></div>
            </div>
            <div class="rounded-3 p-2.5 fs-4" style="background: #ECFEFF; color: #06B6D4;">
                <i class="bi bi-people-fill"></i>
            </div>
        </div>
    </div>
    <div class="col-4">
        <div class="dyl-card p-3 d-flex align-items-center justify-content-between">
            <div>
                <div class="text-muted small fw-bold text-uppercase">CAPACIDAD</div>
                <div class="h3 fw-bold text-dark my-1"><?= $totalCapacidad ?></div>
            </div>
            <div class="rounded-3 p-2.5 fs-4" style="background: #FFFBEB; color: #F59E0B;">
                <i class="bi bi-speedometer2"></i>
            </div>
        </div>
    </div>
</div>

<!-- Barra de Control -->
<div class="dyl-card p-3 mb-4">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
        <div class="flex-grow-1" style="max-width: 420px;">
            <div class="input-group">
                <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                <input type="text" class="form-control border-start-0 ps-0" placeholder="Buscar ruta, conductor o placa..." data-table-search="tablaTransporte">
            </div>
        </div>
        <div>
            <a href="<?= url('views/transporte_nuevo.php') ?>" class="btn btn-dyl-primary">
                <i class="bi bi-plus-lg"></i>
                <span>+ Nueva Ruta</span>
            </a>
        </div>
    </div>
</div>

<!-- Contenedor Principal: Estado Vacío Ilustrado o Tabla -->
<div class="dyl-card p-4">
    <?php if (empty($rutas)): ?>
        <div class="text-center py-5">
            <!-- Ilustración de Autobús Escolar SVG -->
            <div class="mb-3 d-inline-block p-4 rounded-circle bg-light border">
                <svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M4 6v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2Z"></path>
                    <path d="M4 10h16"></path>
                    <path d="M7 18v2"></path>
                    <path d="M17 18v2"></path>
                    <circle cx="7.5" cy="14.5" r="1.5"></circle>
                    <circle cx="16.5" cy="14.5" r="1.5"></circle>
                </svg>
            </div>
            <h5 class="fw-bold text-dark mb-1">No hay rutas de transporte registradas</h5>
            <p class="text-muted small mb-3">Organice la flota institucional y asigne conductores a las rutas escolares.</p>
            <a href="<?= url('views/transporte_nuevo.php') ?>" class="btn btn-dyl-primary btn-sm px-3">
                <i class="bi bi-plus-circle me-1"></i> Registrar Primera Ruta
            </a>
        </div>
    <?php else: ?>
        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0" id="tablaTransporte">
                <thead class="table-light">
                    <tr class="small text-muted text-uppercase fw-bold">
                        <th class="ps-3">RUTA</th>
                        <th>CONDUCTOR</th>
                        <th>PLACA</th>
                        <th class="text-center">CAPACIDAD</th>
                        <th>COSTO MENSUAL</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($rutas as $r): ?>
                        <tr>
                            <td class="ps-3 fw-bold text-dark small"><?= htmlspecialchars($r['nombre_ruta']) ?></td>
                            <td class="small"><?= htmlspecialchars($r['conductor']) ?></td>
                            <td><span class="badge bg-light text-dark border font-monospace"><?= htmlspecialchars($r['placa']) ?></span></td>
                            <td class="text-center"><span class="badge badge-dyl-blue"><?= $r['capacidad'] ?> asientos</span></td>
                            <td class="fw-bold font-monospace"><?= money_format_pen((float)$r['costo_mensual']) ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    <?php endif; ?>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
