<?php
// views/matricula_nueva.php - Módulo 3: Nueva Matrícula DYL SCHOOL
$pageTitle = 'Nueva Matrícula 2026';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();
$error = null;

// Obtener alumnos activos sin matrícula activa en 2026
$stmtAlumnos = $pdo->query("
    SELECT a.id, a.nombres, a.apellidos, a.dni
    FROM alumnos a
    WHERE a.estado = 'ACTIVO'
    AND a.id NOT IN (SELECT alumno_id FROM matriculas WHERE anio_lectivo = 2026)
    ORDER BY a.apellidos ASC
");
$alumnosDisponibles = $stmtAlumnos->fetchAll();

$grados = $pdo->query("SELECT * FROM grados ORDER BY orden ASC")->fetchAll();
$secciones = $pdo->query("SELECT * FROM secciones ORDER BY nombre ASC")->fetchAll();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $alumno_id = (int)($_POST['alumno_id'] ?? 0);
    $grado_id = (int)($_POST['grado_id'] ?? 0);
    $seccion_id = (int)($_POST['seccion_id'] ?? 0);

    if ($alumno_id <= 0 || $grado_id <= 0 || $seccion_id <= 0) {
        $error = 'Debe seleccionar el alumno, grado y sección.';
    } else {
        $stmtMat = $pdo->prepare("
            INSERT INTO matriculas (alumno_id, grado_id, seccion_id, anio_lectivo, estado_pension, fecha_matricula)
            VALUES (?, ?, ?, 2026, 'SIN_HISTORIAL', '2026-01-09')
        ");
        $stmtMat->execute([$alumno_id, $grado_id, $seccion_id]);
        $matricula_id = $pdo->lastInsertId();

        // Inicializar registro de notas para materias vinculadas al grado
        $stmtCursos = $pdo->prepare("SELECT curso_id FROM curso_grados WHERE grado_id = ?");
        $stmtCursos->execute([$grado_id]);
        $cursos = $stmtCursos->fetchAll();
        foreach ($cursos as $c) {
            $pdo->prepare("INSERT INTO notas (matricula_id, curso_id) VALUES (?, ?)")->execute([$matricula_id, $c['curso_id']]);
        }

        set_flash('success', '¡Matrícula registrada exitosamente para el periodo escolar 2026!');
        header('Location: ' . url('views/matriculas.php'));
        exit;
    }
}
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h3 class="h4 fw-bold text-dark mb-1">Nueva Matrícula Escolar 2026</h3>
        <p class="text-muted small mb-0">Asigne un estudiante a un grado y sección correspondiente.</p>
    </div>
    <a href="<?= url('views/matriculas.php') ?>" class="btn btn-outline-secondary btn-sm px-3 rounded-3">
        <i class="bi bi-arrow-left me-1"></i> Volver a Matrículas
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
                <!-- 1. Seleccione el Alumno -->
                <div class="mb-4">
                    <label class="form-label small fw-bold text-dark mb-1">1. Seleccione el Alumno <span class="text-danger">*</span></label>
                    <select name="alumno_id" class="form-select form-select-lg fs-6" required>
                        <option value="">-- Seleccionar Alumno No Matriculado --</option>
                        <?php foreach ($alumnosDisponibles as $al): ?>
                            <option value="<?= $al['id'] ?>">
                                <?= htmlspecialchars($al['apellidos'] . ', ' . $al['nombres'] . ' (DNI: ' . $al['dni'] . ')') ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                    <div class="form-text small">
                        <?php if (empty($alumnosDisponibles)): ?>
                            <span class="text-amber-600 fw-semibold"><i class="bi bi-info-circle me-1"></i> Todos los alumnos registrados ya cuentan con matrícula activa 2026.</span>
                            <a href="<?= url('views/alumno_nuevo.php') ?>" class="ms-2 fw-bold text-primary">Registrar nuevo alumno</a>
                        <?php else: ?>
                            Solo se muestran estudiantes activos sin matrícula vigente en 2026.
                        <?php endif; ?>
                    </div>
                </div>

                <!-- 2. Grado / Año -->
                <div class="mb-4">
                    <label class="form-label small fw-bold text-dark mb-1">2. Grado / Año Académico <span class="text-danger">*</span></label>
                    <select name="grado_id" class="form-select" required>
                        <option value="">-- Seleccionar Grado --</option>
                        <optgroup label="Nivel Primaria">
                            <?php foreach ($grados as $g): ?>
                                <?php if ($g['nivel'] === 'Primaria'): ?>
                                    <option value="<?= $g['id'] ?>"><?= htmlspecialchars($g['nombre']) ?></option>
                                <?php endif; ?>
                            <?php endforeach; ?>
                        </optgroup>
                        <optgroup label="Nivel Secundaria">
                            <?php foreach ($grados as $g): ?>
                                <?php if ($g['nivel'] === 'Secundaria'): ?>
                                    <option value="<?= $g['id'] ?>"><?= htmlspecialchars($g['nombre']) ?></option>
                                <?php endif; ?>
                            <?php endforeach; ?>
                        </optgroup>
                    </select>
                </div>

                <!-- 3. Sección -->
                <div class="mb-4">
                    <label class="form-label small fw-bold text-dark mb-1">3. Sección <span class="text-danger">*</span></label>
                    <div class="d-flex gap-3">
                        <?php foreach ($secciones as $s): ?>
                            <div class="form-check form-check-inline">
                                <input class="form-check-input" type="radio" name="seccion_id" id="sec_<?= $s['id'] ?>" value="<?= $s['id'] ?>" <?= $s['nombre'] === 'A' ? 'checked' : '' ?> required>
                                <label class="form-check-label fw-bold" for="sec_<?= $s['id'] ?>">Sección "<?= htmlspecialchars($s['nombre']) ?>"</label>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>

                <div class="d-flex justify-content-between align-items-center pt-3 border-top">
                    <a href="<?= url('views/matriculas.php') ?>" class="btn btn-light px-4">Cancelar</a>
                    <button type="submit" class="btn btn-dyl-primary px-4 py-2.5">
                        <i class="bi bi-check2-circle me-1"></i> Confirmar Matrícula
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
