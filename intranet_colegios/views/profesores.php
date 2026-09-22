<?php
// views/profesores.php - Módulo 5: Directorio de Profesores DYL SCHOOL
$pageTitle = 'Plana Docente';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// Acción: Cambiar estado a BAJA
if (isset($_GET['action']) && $_GET['action'] === 'baja' && isset($_GET['id'])) {
    $pid = (int)$_GET['id'];
    $pdo->prepare("UPDATE profesores SET estado = 'BAJA' WHERE id = ?")->execute([$pid]);
    set_flash('success', 'Docente dado de baja correctamente.');
    header('Location: ' . url('views/profesores.php'));
    exit;
}

// Métricas
$totalDocentes = $pdo->query("SELECT COUNT(*) FROM profesores")->fetchColumn() ?: 2;
$totalActivos = $pdo->query("SELECT COUNT(*) FROM profesores WHERE estado = 'ACTIVO'")->fetchColumn() ?: 2;
$totalBaja = $pdo->query("SELECT COUNT(*) FROM profesores WHERE estado = 'BAJA'")->fetchColumn() ?: 0;

$stmt = $pdo->query("SELECT * FROM profesores ORDER BY apellidos ASC");
$profesores = $stmt->fetchAll();
?>

<!-- Métricas de Plana Docente -->
<div class="row g-3 mb-4">
    <div class="col-4">
        <div class="dyl-card p-3 d-flex align-items-center justify-content-between">
            <div>
                <div class="text-muted small fw-bold text-uppercase">TOTAL DOCENTES</div>
                <div class="h3 fw-bold text-dark my-1"><?= $totalDocentes ?></div>
            </div>
            <div class="rounded-3 p-2.5 fs-4" style="background: #EEF2FF; color: #4F46E5;">
                <i class="bi bi-person-workspace"></i>
            </div>
        </div>
    </div>
    <div class="col-4">
        <div class="dyl-card p-3 d-flex align-items-center justify-content-between">
            <div>
                <div class="text-success small fw-bold text-uppercase">ACTIVOS</div>
                <div class="h3 fw-bold text-success my-1"><?= $totalActivos ?></div>
            </div>
            <div class="rounded-3 p-2.5 fs-4" style="background: #ECFDF5; color: #10B981;">
                <i class="bi bi-check-circle-fill"></i>
            </div>
        </div>
    </div>
    <div class="col-4">
        <div class="dyl-card p-3 d-flex align-items-center justify-content-between">
            <div>
                <div class="text-danger small fw-bold text-uppercase">DE BAJA</div>
                <div class="h3 fw-bold text-danger my-1"><?= $totalBaja ?></div>
            </div>
            <div class="rounded-3 p-2.5 fs-4" style="background: #FEF2F2; color: #EF4444;">
                <i class="bi bi-x-circle-fill"></i>
            </div>
        </div>
    </div>
</div>

<!-- Barra de Acción: Buscador y Botón Contratar Docente -->
<div class="dyl-card p-3 mb-4">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
        <div class="flex-grow-1" style="max-width: 420px;">
            <div class="input-group">
                <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                <input type="text" class="form-control border-start-0 ps-0" placeholder="Buscar profesor por nombre o DNI..." data-table-search="tablaProfesores">
            </div>
        </div>
        <div>
            <a href="<?= url('views/profesor_nuevo.php') ?>" class="btn btn-dyl-primary">
                <i class="bi bi-person-plus-fill"></i>
                <span>+ Contratar Docente</span>
            </a>
        </div>
    </div>
</div>

<!-- Tabla de Docentes -->
<div class="dyl-card overflow-hidden">
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0" id="tablaProfesores">
            <thead class="table-light">
                <tr class="small text-muted text-uppercase fw-bold">
                    <th class="ps-4">DOCENTE</th>
                    <th>IDENTIFICACIÓN</th>
                    <th>CONTACTO</th>
                    <th class="text-center">ESTADO</th>
                    <th class="text-end pe-4">ACCIONES</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($profesores as $p): ?>
                    <tr>
                        <td class="ps-4">
                            <div class="d-flex align-items-center gap-2.5">
                                <div class="dyl-user-avatar" style="width: 38px; height: 38px; font-size: 0.85rem; background: linear-gradient(135deg, #10B981, #059669);">
                                    <?= strtoupper(substr($p['nombres'], 0, 1)) ?>
                                </div>
                                <div>
                                    <div class="fw-bold text-dark small mb-0"><?= htmlspecialchars($p['nombres'] . ' ' . $p['apellidos']) ?></div>
                                    <div class="text-muted" style="font-size: 0.72rem;">Docente Titular · <?= htmlspecialchars($p['genero']) ?></div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="badge bg-light text-dark border px-2.5 py-1.5 fw-semibold font-monospace">
                                DNI: <?= htmlspecialchars($p['dni']) ?>
                            </span>
                        </td>
                        <td>
                            <div class="small fw-semibold text-dark"><i class="bi bi-envelope me-1 text-muted"></i><?= htmlspecialchars($p['correo'] ?? 'Sin correo') ?></div>
                            <div class="text-muted" style="font-size: 0.74rem;"><i class="bi bi-telephone me-1 text-muted"></i><?= htmlspecialchars($p['telefono'] ?? 'Sin teléfono') ?></div>
                        </td>
                        <td class="text-center">
                            <?php if ($p['estado'] === 'ACTIVO'): ?>
                                <span class="badge badge-dyl-green">ACTIVO</span>
                            <?php else: ?>
                                <span class="badge badge-dyl-red">DE BAJA</span>
                            <?php endif; ?>
                        </td>
                        <td class="text-end pe-4">
                            <div class="d-inline-flex gap-1">
                                <a href="?action=baja&id=<?= $p['id'] ?>" class="btn btn-sm btn-outline-danger px-2 py-1 rounded-2 shadow-xs" title="Dar de Baja" onclick="return confirm('¿Confirma dar de baja a este docente?')">
                                    <i class="bi bi-person-x-fill"></i> Baja
                                </a>
                            </div>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
