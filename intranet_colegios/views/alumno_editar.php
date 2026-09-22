<?php
// views/alumno_editar.php - Módulo 2: Edición de Alumno DYL SCHOOL
$pageTitle = 'Editar Alumno';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();
$id = (int)($_GET['id'] ?? 0);

$stmt = $pdo->prepare("
    SELECT a.*, u.username, u.email as user_email
    FROM alumnos a
    LEFT JOIN usuarios u ON a.usuario_id = u.id
    WHERE a.id = ?
");
$stmt->execute([$id]);
$alumno = $stmt->fetch();

if (!$alumno) {
    set_flash('error', 'El alumno solicitado no existe.');
    header('Location: ' . url('views/alumnos.php'));
    exit;
}

$error = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $nombres = trim($_POST['nombres'] ?? '');
    $apellidos = trim($_POST['apellidos'] ?? '');
    $dni = trim($_POST['dni'] ?? '');
    $genero = $_POST['genero'] ?? 'Masculino';
    $correo = trim($_POST['correo'] ?? '');
    $apoderado_nombre = trim($_POST['apoderado_nombre'] ?? '');
    $telefono = trim($_POST['telefono'] ?? '');
    $direccion = trim($_POST['direccion'] ?? '');
    $estado = $_POST['estado'] ?? 'ACTIVO';

    if (empty($nombres) || empty($apellidos) || empty($dni)) {
        $error = 'Nombres, Apellidos y DNI son campos obligatorios.';
    } else {
        // Actualizar tabla alumnos
        $updAlum = $pdo->prepare("
            UPDATE alumnos 
            SET nombres = ?, apellidos = ?, dni = ?, genero = ?, correo = ?, apoderado_nombre = ?, telefono_apoderado = ?, direccion = ?, estado = ?
            WHERE id = ?
        ");
        $updAlum->execute([$nombres, $apellidos, $dni, $genero, $correo, $apoderado_nombre, $telefono, $direccion, $estado, $id]);

        // Actualizar usuario vinculado si existe
        if (!empty($alumno['usuario_id'])) {
            $updUser = $pdo->prepare("
                UPDATE usuarios 
                SET nombres = ?, apellidos = ?, dni = ?, username = ?, email = ?, telefono = ?, estado = ?
                WHERE id = ?
            ");
            $userEstado = ($estado === 'ACTIVO') ? 'Activo' : 'Inactivo';
            $updUser->execute([$nombres, $apellidos, $dni, $dni, $correo, $telefono, $userEstado, $alumno['usuario_id']]);
        }


        set_flash('success', "Datos de {$nombres} {$apellidos} actualizados correctamente.");
        header('Location: ' . url('views/alumnos.php'));
        exit;
    }
}
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h3 class="h4 fw-bold text-dark mb-1">Editar Expediente de Alumno</h3>
        <p class="text-muted small mb-0">ID #<?= $alumno['id'] ?> · <?= htmlspecialchars($alumno['nombres'] . ' ' . $alumno['apellidos']) ?></p>
    </div>
    <a href="<?= url('views/alumnos.php') ?>" class="btn btn-outline-danger btn-sm px-3 rounded-3">
        <i class="bi bi-x-lg me-1"></i> Cancelar
    </a>
</div>

<?php if ($error): ?>
    <div class="alert alert-danger rounded-3 py-2 px-3 small mb-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i><?= htmlspecialchars($error) ?>
    </div>
<?php endif; ?>

<div class="dyl-card p-4">
    <form method="POST" action="">
        <!-- Avatar y Datos de Cabecera -->
        <div class="d-flex align-items-center gap-4 mb-4 pb-4 border-bottom">
            <div class="dyl-user-avatar" style="width: 76px; height: 76px; font-size: 1.8rem;">
                <?= strtoupper(substr($alumno['nombres'], 0, 1)) ?>
            </div>
            <div>
                <h5 class="fw-bold text-dark mb-1"><?= htmlspecialchars($alumno['nombres'] . ' ' . $alumno['apellidos']) ?></h5>
                <span class="badge bg-light text-dark border font-monospace me-2">DNI: <?= htmlspecialchars($alumno['dni']) ?></span>
                <span class="badge <?= $alumno['estado'] === 'ACTIVO' ? 'badge-dyl-green' : 'badge-dyl-red' ?>">
                    <?= $alumno['estado'] ?>
                </span>
            </div>
        </div>

        <div class="row g-3 mb-4">
            <div class="col-md-6">
                <label class="form-label small fw-bold text-dark">Nombres</label>
                <input type="text" name="nombres" class="form-control" value="<?= htmlspecialchars($alumno['nombres']) ?>" required>
            </div>
            <div class="col-md-6">
                <label class="form-label small fw-bold text-dark">Apellidos</label>
                <input type="text" name="apellidos" class="form-control" value="<?= htmlspecialchars($alumno['apellidos']) ?>" required>
            </div>
            <div class="col-md-4">
                <label class="form-label small fw-bold text-dark">DNI / Usuario</label>
                <input type="text" name="dni" class="form-control" value="<?= htmlspecialchars($alumno['dni']) ?>" required>
            </div>
            <div class="col-md-4">
                <label class="form-label small fw-bold text-dark">Género</label>
                <select name="genero" class="form-select">
                    <option value="Masculino" <?= $alumno['genero'] === 'Masculino' ? 'selected' : '' ?>>Masculino</option>
                    <option value="Femenino" <?= $alumno['genero'] === 'Femenino' ? 'selected' : '' ?>>Femenino</option>
                </select>
            </div>
            <div class="col-md-4">
                <label class="form-label small fw-bold text-dark">Estado del Alumno</label>
                <select name="estado" class="form-select fw-bold <?= $alumno['estado'] === 'ACTIVO' ? 'text-success' : 'text-danger' ?>">
                    <option value="ACTIVO" <?= $alumno['estado'] === 'ACTIVO' ? 'selected' : '' ?>>ACTIVO (Habilitado)</option>
                    <option value="BAJA" <?= $alumno['estado'] === 'BAJA' ? 'selected' : '' ?>>BAJA (Retirado)</option>
                </select>
            </div>
            <div class="col-md-6">
                <label class="form-label small fw-bold text-dark">Padre / Madre / Tutor Legal</label>
                <input type="text" name="apoderado_nombre" class="form-control" value="<?= htmlspecialchars($alumno['apoderado_nombre'] ?? '') ?>" placeholder="Nombre del apoderado">
            </div>
            <div class="col-md-6">
                <label class="form-label small fw-bold text-dark">Teléfono / Celular (Apoderado)</label>
                <input type="text" name="telefono" class="form-control" value="<?= htmlspecialchars($alumno['telefono_apoderado'] ?? '') ?>">
            </div>
            <div class="col-md-6">
                <label class="form-label small fw-bold text-dark">Correo Electrónico</label>
                <input type="email" name="correo" class="form-control" value="<?= htmlspecialchars($alumno['correo'] ?? '') ?>">
            </div>
            <div class="col-md-6">
                <label class="form-label small fw-bold text-dark">Dirección de Domicilio</label>
                <input type="text" name="direccion" class="form-control" value="<?= htmlspecialchars($alumno['direccion'] ?? '') ?>" placeholder="Dirección del domicilio">
            </div>
        </div>

        <div class="text-end">
            <a href="<?= url('views/alumnos.php') ?>" class="btn btn-light px-4 me-2">Cancelar</a>
            <button type="submit" class="btn btn-dyl-primary px-4 py-2">
                <i class="bi bi-floppy-fill me-1"></i> Guardar Cambios
            </button>
        </div>

    </form>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
