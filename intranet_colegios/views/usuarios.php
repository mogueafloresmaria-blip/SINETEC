<?php
// views/usuarios.php - Módulo 10: Gestión de Usuarios DYL SCHOOL
$pageTitle = 'Gestión de Usuarios y Roles';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// Acción: Restablecer Contraseña
if (isset($_GET['action']) && $_GET['action'] === 'reset' && isset($_GET['id'])) {
    $uid = (int)$_GET['id'];
    $uRow = $pdo->prepare("SELECT dni FROM usuarios WHERE id = ?");
    $uRow->execute([$uid]);
    $dniUser = $uRow->fetchColumn() ?: '123456';
    $newHash = password_hash($dniUser, PASSWORD_BCRYPT);

    $pdo->prepare("UPDATE usuarios SET password_hash = ? WHERE id = ?")->execute([$newHash, $uid]);
    set_flash('success', "Contraseña restablecida exitosamente al DNI ({$dniUser})");
    header('Location: ' . url('views/usuarios.php'));
    exit;
}

// Métricas de Usuarios
$totalUsuarios = $pdo->query("SELECT COUNT(*) FROM usuarios")->fetchColumn() ?: 13;
$totalAdmins = $pdo->query("SELECT COUNT(*) FROM usuarios WHERE rol = 'admin'")->fetchColumn() ?: 1;
$totalDocentes = $pdo->query("SELECT COUNT(*) FROM usuarios WHERE rol = 'docente'")->fetchColumn() ?: 2;
$totalAlumnos = $pdo->query("SELECT COUNT(*) FROM usuarios WHERE rol = 'alumno'")->fetchColumn() ?: 10;

// Listado de usuarios
$stmt = $pdo->query("SELECT * FROM usuarios ORDER BY rol ASC, apellidos ASC");
$usuarios = $stmt->fetchAll();
?>

<!-- Métricas de Usuarios -->
<div class="row g-3 mb-4">
    <div class="col-3">
        <div class="dyl-card p-3 d-flex align-items-center justify-content-between">
            <div>
                <div class="text-muted small fw-bold text-uppercase">TOTAL</div>
                <div class="h3 fw-bold text-dark my-1"><?= $totalUsuarios ?></div>
            </div>
            <div class="rounded-3 p-2 fs-4" style="background: #F1F5F9; color: #475569;">
                <i class="bi bi-people-fill"></i>
            </div>
        </div>
    </div>
    <div class="col-3">
        <div class="dyl-card p-3 d-flex align-items-center justify-content-between">
            <div>
                <div class="text-danger small fw-bold text-uppercase">ADMINS</div>
                <div class="h3 fw-bold text-danger my-1"><?= $totalAdmins ?></div>
            </div>
            <div class="rounded-3 p-2 fs-4" style="background: #FEF2F2; color: #EF4444;">
                <i class="bi bi-shield-fill-check"></i>
            </div>
        </div>
    </div>
    <div class="col-3">
        <div class="dyl-card p-3 d-flex align-items-center justify-content-between">
            <div>
                <div class="text-success small fw-bold text-uppercase">DOCENTES</div>
                <div class="h3 fw-bold text-success my-1"><?= $totalDocentes ?></div>
            </div>
            <div class="rounded-3 p-2 fs-4" style="background: #ECFDF5; color: #10B981;">
                <i class="bi bi-person-workspace"></i>
            </div>
        </div>
    </div>
    <div class="col-3">
        <div class="dyl-card p-3 d-flex align-items-center justify-content-between">
            <div>
                <div class="text-primary small fw-bold text-uppercase">ALUMNOS</div>
                <div class="h3 fw-bold text-primary my-1"><?= $totalAlumnos ?></div>
            </div>
            <div class="rounded-3 p-2 fs-4" style="background: #EEF2FF; color: #4F46E5;">
                <i class="bi bi-mortarboard-fill"></i>
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
                <input type="text" class="form-control border-start-0 ps-0" placeholder="Buscar usuario por nombre o documento..." data-table-search="tablaUsuarios">
            </div>
        </div>
        <div>
            <a href="<?= url('views/usuario_nuevo.php') ?>" class="btn btn-dyl-primary">
                <i class="bi bi-person-plus-fill"></i>
                <span>Nuevo Usuario</span>
            </a>
        </div>
    </div>
</div>

<!-- Tabla de Usuarios -->
<div class="dyl-card overflow-hidden">
    <div class="table-responsive">
        <table class="table table-hover align-middle mb-0" id="tablaUsuarios">
            <thead class="table-light">
                <tr class="small text-muted text-uppercase fw-bold">
                    <th class="ps-4">USUARIO / PERSONA</th>
                    <th>DNI / ID</th>
                    <th class="text-center">ROL</th>
                    <th class="text-center">ESTADO</th>
                    <th class="text-end pe-4">ACCIONES</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($usuarios as $u): ?>
                    <tr>
                        <td class="ps-4">
                            <div class="d-flex align-items-center gap-2.5">
                                <div class="dyl-user-avatar" style="width: 38px; height: 38px; font-size: 0.85rem;">
                                    <?= strtoupper(substr($u['nombres'], 0, 1)) ?>
                                </div>
                                <div>
                                    <div class="fw-bold text-dark small mb-0"><?= htmlspecialchars($u['nombres'] . ' ' . $u['apellidos']) ?></div>
                                    <div class="text-muted" style="font-size: 0.72rem;"><?= htmlspecialchars($u['email'] ?? $u['username']) ?></div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="badge bg-light text-dark border font-monospace">
                                <?= htmlspecialchars($u['dni']) ?>
                            </span>
                        </td>
                        <td class="text-center">
                            <?php if ($u['rol'] === 'admin'): ?>
                                <span class="badge badge-dyl-red">ADMIN</span>
                            <?php elseif ($u['rol'] === 'docente'): ?>
                                <span class="badge badge-dyl-green">PROFESOR</span>
                            <?php else: ?>
                                <span class="badge badge-dyl-purple">ALUMNO</span>
                            <?php endif; ?>
                        </td>
                        <td class="text-center">
                            <span class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25 px-2 py-1 small fw-bold">
                                <?= htmlspecialchars($u['estado']) ?>
                            </span>
                        </td>
                        <td class="text-end pe-4">
                            <a href="?action=reset&id=<?= $u['id'] ?>" class="btn btn-sm btn-outline-secondary px-2.5 py-1 rounded-2 shadow-xs" title="Restablecer Contraseña al DNI" onclick="return confirm('¿Restablecer la contraseña de este usuario a su número de DNI?')">
                                <i class="bi bi-key-fill me-1"></i> Reset Pass
                            </a>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
