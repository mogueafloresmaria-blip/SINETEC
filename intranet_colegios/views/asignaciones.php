<?php
// views/asignaciones.php - Módulo 6: Carga Académica DYL SCHOOL
$pageTitle = 'Carga Académica';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// Acción: Eliminar asignación
if (isset($_GET['action']) && $_GET['action'] === 'eliminar' && isset($_GET['id'])) {
    $asigId = (int)$_GET['id'];
    $pdo->prepare("DELETE FROM asignaciones WHERE id = ?")->execute([$asigId]);
    set_flash('success', 'Asignación académica retirada correctamente.');
    header('Location: ' . url('views/asignaciones.php'));
    exit;
}

// Acción: Crear Asignación
$error = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'asignar') {
    $profesor_id = (int)($_POST['profesor_id'] ?? 0);
    $curso_id = (int)($_POST['curso_id'] ?? 0);
    $grado_id = (int)($_POST['grado_id'] ?? 0);
    $seccion_id = (int)($_POST['seccion_id'] ?? 0);

    if ($profesor_id <= 0 || $curso_id <= 0 || $grado_id <= 0 || $seccion_id <= 0) {
        $error = 'Todos los campos son obligatorios para asignar la carga académica.';
    } else {
        // Verificar si ya existe asignación exacta
        $stmtCheck = $pdo->prepare("SELECT id FROM asignaciones WHERE profesor_id = ? AND curso_id = ? AND grado_id = ? AND seccion_id = ? AND anio_lectivo = 2026");
        $stmtCheck->execute([$profesor_id, $curso_id, $grado_id, $seccion_id]);
        if ($stmtCheck->fetch()) {
            $error = 'Esta asignación ya se encuentra registrada para el periodo lectivo 2026.';
        } else {
            $stmtIns = $pdo->prepare("INSERT INTO asignaciones (profesor_id, curso_id, grado_id, seccion_id, anio_lectivo) VALUES (?, ?, ?, ?, 2026)");
            $stmtIns->execute([$profesor_id, $curso_id, $grado_id, $seccion_id]);
            set_flash('success', '¡Carga académica asignada exitosamente!');
            header('Location: ' . url('views/asignaciones.php'));
            exit;
        }
    }
}

// Datos para el formulario
$profesores = $pdo->query("SELECT id, nombres, apellidos, dni FROM profesores WHERE estado = 'ACTIVO' ORDER BY apellidos ASC, nombres ASC")->fetchAll();
$cursos = $pdo->query("SELECT id, nombre, tipo FROM cursos WHERE activo = 1 ORDER BY nombre ASC")->fetchAll();
$grados = $pdo->query("SELECT id, nombre, nivel, orden FROM grados ORDER BY orden ASC")->fetchAll();
$secciones = $pdo->query("SELECT id, nombre FROM secciones ORDER BY nombre ASC")->fetchAll();

// Carga asignada organizada por nivel
$stmtAsigPrimaria = $pdo->query("
    SELECT asig.id, p.nombres as prof_nombres, p.apellidos as prof_apellidos, p.dni as prof_dni,
           c.nombre as curso_nombre, c.tipo as curso_tipo, g.nombre as grado_nombre, s.nombre as seccion_nombre
    FROM asignaciones asig
    JOIN profesores p ON asig.profesor_id = p.id
    JOIN cursos c ON asig.curso_id = c.id
    JOIN grados g ON asig.grado_id = g.id
    JOIN secciones s ON asig.seccion_id = s.id
    WHERE g.nivel = 'Primaria' AND asig.anio_lectivo = 2026
    ORDER BY g.orden ASC, c.nombre ASC
");
$asigPrimaria = $stmtAsigPrimaria->fetchAll();

$stmtAsigSecundaria = $pdo->query("
    SELECT asig.id, p.nombres as prof_nombres, p.apellidos as prof_apellidos, p.dni as prof_dni,
           c.nombre as curso_nombre, c.tipo as curso_tipo, g.nombre as grado_nombre, s.nombre as seccion_nombre
    FROM asignaciones asig
    JOIN profesores p ON asig.profesor_id = p.id
    JOIN cursos c ON asig.curso_id = c.id
    JOIN grados g ON asig.grado_id = g.id
    JOIN secciones s ON asig.seccion_id = s.id
    WHERE g.nivel = 'Secundaria' AND asig.anio_lectivo = 2026
    ORDER BY g.orden ASC, c.nombre ASC
");
$asigSecundaria = $stmtAsigSecundaria->fetchAll();
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h3 class="h4 fw-bold text-dark mb-1">Carga Académica (Asignación Docente)</h3>
        <p class="text-muted small mb-0">Distribución y asignación de profesores a materias, grados y secciones lectivas 2026.</p>
    </div>
</div>

<?php if ($error): ?>
    <div class="alert alert-danger rounded-3 py-2 px-3 small mb-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i><?= htmlspecialchars($error) ?>
    </div>
<?php endif; ?>

<div class="row g-4">
    <!-- COLUMNA IZQUIERDA: Nueva Asignación (Tarjeta blanca) -->
    <div class="col-lg-4">
        <div class="dyl-card p-4">
            <h5 class="fw-bold text-dark mb-3 d-flex align-items-center gap-2">
                <i class="bi bi-person-plus-fill text-primary"></i>
                Nueva Asignación
            </h5>

            <form method="POST" action="">
                <input type="hidden" name="action" value="asignar">

                <!-- Paso 1: 1. BUSCAR DOCENTE -->
                <div class="mb-3">
                    <label class="form-label small fw-bold text-dark mb-1">1. BUSCAR DOCENTE <span class="text-danger">*</span></label>
                    <select name="profesor_id" class="form-select" required>
                        <option value="">-- Seleccionar Profesor --</option>
                        <?php foreach ($profesores as $p): ?>
                            <option value="<?= $p['id'] ?>">
                                <?= htmlspecialchars($p['nombres'] . ' ' . $p['apellidos'] . ' - ' . $p['dni']) ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>

                <!-- Paso 2: 2. FILTRAR POR NIVEL -->
                <div class="mb-3">
                    <label class="form-label small fw-bold text-dark mb-1">2. FILTRAR POR NIVEL <span class="text-danger">*</span></label>
                    <select id="filtroNivelAsig" class="form-select" onchange="filtrarGradosPorNivel(this.value)">
                        <option value="Todos">-- Seleccionar Nivel --</option>
                        <option value="Primaria">Primaria</option>
                        <option value="Secundaria">Secundaria</option>
                        <option value="Inicial">Inicial</option>
                    </select>
                </div>

                <!-- Paso 3: 3. SELECCIONAR GRADO -->
                <div class="mb-3">
                    <label class="form-label small fw-bold text-dark mb-1">3. SELECCIONAR GRADO <span class="text-danger">*</span></label>
                    <select name="grado_id" id="selectGradoAsig" class="form-select" required>
                        <option value="">-- Seleccionar Grado --</option>
                        <optgroup label="Primaria" data-nivel="Primaria">
                            <?php foreach ($grados as $g): ?>
                                <?php if ($g['nivel'] === 'Primaria'): ?>
                                    <option value="<?= $g['id'] ?>" data-nivel="Primaria"><?= htmlspecialchars($g['nombre']) ?></option>
                                <?php endif; ?>
                            <?php endforeach; ?>
                        </optgroup>
                        <optgroup label="Secundaria" data-nivel="Secundaria">
                            <?php foreach ($grados as $g): ?>
                                <?php if ($g['nivel'] === 'Secundaria'): ?>
                                    <option value="<?= $g['id'] ?>" data-nivel="Secundaria"><?= htmlspecialchars($g['nombre']) ?></option>
                                <?php endif; ?>
                            <?php endforeach; ?>
                        </optgroup>
                        <optgroup label="Inicial" data-nivel="Inicial">
                            <?php foreach ($grados as $g): ?>
                                <?php if ($g['nivel'] === 'Inicial'): ?>
                                    <option value="<?= $g['id'] ?>" data-nivel="Inicial"><?= htmlspecialchars($g['nombre']) ?></option>
                                <?php endif; ?>
                            <?php endforeach; ?>
                        </optgroup>
                    </select>
                </div>

                <!-- Paso 4: 4. SELECCIONAR CURSO -->
                <div class="mb-3">
                    <label class="form-label small fw-bold text-dark mb-1">4. SELECCIONAR CURSO <span class="text-danger">*</span></label>
                    <select name="curso_id" class="form-select" required>
                        <option value="">-- Seleccionar Curso --</option>
                        <?php foreach ($cursos as $c): ?>
                            <option value="<?= $c['id'] ?>"><?= htmlspecialchars($c['nombre']) ?> (<?= $c['tipo'] ?>)</option>
                        <?php endforeach; ?>
                    </select>
                </div>

                <!-- Paso 5: 5. ASIGNAR SECCIÓN -->
                <div class="mb-4">
                    <label class="form-label small fw-bold text-dark mb-1">5. ASIGNAR SECCIÓN <span class="text-danger">*</span></label>
                    <select name="seccion_id" class="form-select" required>
                        <option value="">-- Seleccionar Sección --</option>
                        <?php foreach ($secciones as $s): ?>
                            <option value="<?= $s['id'] ?>">Sección "<?= htmlspecialchars($s['nombre']) ?>"</option>
                        <?php endforeach; ?>
                    </select>
                </div>

                <!-- Botón al pie: Asignar Carga en color morado -->
                <button type="submit" class="btn btn-dyl-primary w-100 py-2.5 fw-semibold shadow-sm">
                    <i class="bi bi-check-circle me-1"></i> Asignar Carga
                </button>
            </form>
        </div>
    </div>

    <!-- COLUMNA DERECHA: Carga Actual Asignada (Visualizador en 2 secciones) -->
    <div class="col-lg-8">
        <div class="dyl-card p-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold text-dark mb-0">Carga Actual Asignada</h5>
            </div>

            <!-- Pestañas Primaria / Secundaria -->
            <ul class="nav nav-pills mb-3 gap-2" id="pills-tab-carga" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active rounded-pill px-4 py-2 fw-bold" id="pills-primaria-tab" data-bs-toggle="pill" data-bs-target="#pills-primaria" type="button" role="tab" aria-selected="true">
                        NIVEL PRIMARIA (<?= count($asigPrimaria) ?>)
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link rounded-pill px-4 py-2 fw-bold" id="pills-secundaria-tab" data-bs-toggle="pill" data-bs-target="#pills-secundaria" type="button" role="tab" aria-selected="false">
                        NIVEL SECUNDARIA (<?= count($asigSecundaria) ?>)
                    </button>
                </li>
            </ul>

            <div class="tab-content" id="pills-cargaContent">
                <!-- Pestaña 1: NIVEL PRIMARIA -->
                <div class="tab-pane fade show active" id="pills-primaria" role="tabpanel" aria-labelledby="pills-primaria-tab">
                    <?php if (empty($asigPrimaria)): ?>
                        <div class="text-center py-5 text-muted small">
                            <i class="bi bi-info-circle fs-3 d-block mb-2 text-slate-300"></i>
                            No hay asignaciones registradas para el Nivel Primaria.
                        </div>
                    <?php else: ?>
                        <div class="row g-3">
                            <?php foreach ($asigPrimaria as $as): ?>
                                <div class="col-md-6">
                                    <div class="dyl-card p-3 border shadow-xs dyl-card-hover h-100 position-relative d-flex flex-column justify-content-between">
                                        <div>
                                            <div class="d-flex justify-content-between align-items-start mb-2">
                                                <h4 class="fw-bold text-dark h5 mb-0"><?= htmlspecialchars($as['curso_nombre']) ?></h4>
                                                <a href="?action=eliminar&id=<?= $as['id'] ?>" class="btn btn-outline-danger btn-sm p-1 rounded-circle lh-1" title="Quitar carga" onclick="return confirm('¿Retirar esta asignación académica?')">
                                                    <i class="bi bi-trash-fill" style="font-size: 0.75rem;"></i>
                                                </a>
                                            </div>
                                            <p class="text-muted small mb-2 d-flex align-items-center gap-1.5">
                                                <i class="bi bi-person-fill text-indigo-600"></i>
                                                <span>Prof. <?= htmlspecialchars($as['prof_nombres'] . ' ' . $as['prof_apellidos']) ?></span>
                                            </p>
                                        </div>
                                        <div class="pt-2 border-top d-flex justify-content-between align-items-center">
                                            <span class="badge badge-dyl-purple fw-bold" style="font-size: 0.75rem;">
                                                <?= htmlspecialchars($as['grado_nombre'] . ' - Sec. ' . $as['seccion_nombre']) ?>
                                            </span>
                                            <span class="badge bg-light text-muted border" style="font-size: 0.68rem;"><?= htmlspecialchars($as['curso_tipo']) ?></span>
                                        </div>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    <?php endif; ?>
                </div>

                <!-- Pestaña 2: NIVEL SECUNDARIA -->
                <div class="tab-pane fade" id="pills-secundaria" role="tabpanel" aria-labelledby="pills-secundaria-tab">
                    <?php if (empty($asigSecundaria)): ?>
                        <div class="text-center py-5 text-muted small">
                            <i class="bi bi-info-circle fs-3 d-block mb-2 text-slate-300"></i>
                            No hay asignaciones registradas para el Nivel Secundaria.
                        </div>
                    <?php else: ?>
                        <div class="row g-3">
                            <?php foreach ($asigSecundaria as $as): ?>
                                <div class="col-md-6">
                                    <div class="dyl-card p-3 border shadow-xs dyl-card-hover h-100 position-relative d-flex flex-column justify-content-between">
                                        <div>
                                            <div class="d-flex justify-content-between align-items-start mb-2">
                                                <h4 class="fw-bold text-dark h5 mb-0"><?= htmlspecialchars($as['curso_nombre']) ?></h4>
                                                <a href="?action=eliminar&id=<?= $as['id'] ?>" class="btn btn-outline-danger btn-sm p-1 rounded-circle lh-1" title="Quitar carga" onclick="return confirm('¿Retirar esta asignación académica?')">
                                                    <i class="bi bi-trash-fill" style="font-size: 0.75rem;"></i>
                                                </a>
                                            </div>
                                            <p class="text-muted small mb-2 d-flex align-items-center gap-1.5">
                                                <i class="bi bi-person-fill text-indigo-600"></i>
                                                <span>Prof. <?= htmlspecialchars($as['prof_nombres'] . ' ' . $as['prof_apellidos']) ?></span>
                                            </p>
                                        </div>
                                        <div class="pt-2 border-top d-flex justify-content-between align-items-center">
                                            <span class="badge badge-dyl-blue fw-bold" style="font-size: 0.75rem;">
                                                <?= htmlspecialchars($as['grado_nombre'] . ' - Sec. ' . $as['seccion_nombre']) ?>
                                            </span>
                                            <span class="badge bg-light text-muted border" style="font-size: 0.68rem;"><?= htmlspecialchars($as['curso_tipo']) ?></span>
                                        </div>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function filtrarGradosPorNivel(nivel) {
    const select = document.getElementById('selectGradoAsig');
    if (!select) return;
    const optgroups = select.querySelectorAll('optgroup');
    optgroups.forEach(group => {
        if (nivel === 'Todos' || group.getAttribute('data-nivel') === nivel) {
            group.style.display = '';
        } else {
            group.style.display = 'none';
        }
    });
    select.value = '';
}
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
