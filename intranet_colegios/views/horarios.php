<?php
// views/horarios.php - Módulo 4: Horarios Escolares DYL SCHOOL
$pageTitle = 'Horarios Escolares';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// Filtros
$filtroNivel = $_GET['nivel'] ?? 'Secundaria';
$filtroGrado = (int)($_GET['grado_id'] ?? 0);
$filtroSeccion = (int)($_GET['seccion_id'] ?? 0);
$filtroDia = $_GET['dia'] ?? 'Lunes';

// Grados según nivel
$grados = $pdo->prepare("SELECT * FROM grados WHERE nivel = ? ORDER BY orden ASC");
$grados->execute([$filtroNivel]);
$gradosList = $grados->fetchAll();

if ($filtroGrado <= 0 && !empty($gradosList)) {
    $filtroGrado = (int)$gradosList[0]['id'];
}

$secciones = $pdo->query("SELECT * FROM secciones ORDER BY nombre ASC")->fetchAll();
if ($filtroSeccion <= 0 && !empty($secciones)) {
    $filtroSeccion = (int)$secciones[0]['id'];
}

$cursos = $pdo->query("SELECT * FROM cursos WHERE activo = 1 ORDER BY nombre ASC")->fetchAll();

// Acción: Eliminar Bloque
if (isset($_GET['action']) && $_GET['action'] === 'eliminar' && isset($_GET['horario_id'])) {
    $hid = (int)$_GET['horario_id'];
    $pdo->prepare("DELETE FROM horarios WHERE id = ?")->execute([$hid]);
    set_flash('success', 'Bloque de horario eliminado correctamente.');
    header("Location: " . url("views/horarios.php?nivel={$filtroNivel}&grado_id={$filtroGrado}&seccion_id={$filtroSeccion}&dia={$filtroDia}"));
    exit;
}

// Acción: Guardar Nueva Clase
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'nueva_clase') {
    $curso_id = !empty($_POST['curso_id']) ? (int)$_POST['curso_id'] : null;
    $hora_inicio = trim($_POST['hora_inicio'] ?? '08:00 AM');
    $hora_fin = trim($_POST['hora_fin'] ?? '09:30 AM');
    $es_recreo = isset($_POST['es_recreo']) ? 1 : 0;

    $stmtIns = $pdo->prepare("
        INSERT INTO horarios (curso_id, grado_id, seccion_id, dia, hora_inicio, hora_fin, modalidad, es_recreo)
        VALUES (?, ?, ?, ?, ?, ?, 'Presencial', ?)
    ");
    $stmtIns->execute([$curso_id, $filtroGrado, $filtroSeccion, $filtroDia, $hora_inicio, $hora_fin, $es_recreo]);

    set_flash('success', '¡Clase agregada exitosamente al horario escolar!');
    header("Location: " . url("views/horarios.php?nivel={$filtroNivel}&grado_id={$filtroGrado}&seccion_id={$filtroSeccion}&dia={$filtroDia}"));
    exit;
}

// Consultar Bloques del Día
$stmtHorarios = $pdo->prepare("
    SELECT h.*, c.nombre as curso_nombre, c.tipo as curso_tipo
    FROM horarios h
    LEFT JOIN cursos c ON h.curso_id = c.id
    WHERE h.grado_id = ? AND h.seccion_id = ? AND h.dia = ?
    ORDER BY h.hora_inicio ASC
");
$stmtHorarios->execute([$filtroGrado, $filtroSeccion, $filtroDia]);
$bloques = $stmtHorarios->fetchAll();
?>

<!-- Filtros Superiores en Barra -->
<div class="dyl-card p-3 mb-4">
    <form method="GET" action="" class="row g-2 align-items-center">
        <!-- 1. Nivel Académico -->
        <div class="col-md-3">
            <label class="small text-muted fw-bold d-block mb-1">Nivel Académico</label>
            <select name="nivel" class="form-select" onchange="this.form.submit()">
                <option value="Inicial" <?= $filtroNivel === 'Inicial' ? 'selected' : '' ?>>Inicial</option>
                <option value="Primaria" <?= $filtroNivel === 'Primaria' ? 'selected' : '' ?>>Primaria</option>
                <option value="Secundaria" <?= $filtroNivel === 'Secundaria' ? 'selected' : '' ?>>Secundaria</option>
            </select>
        </div>

        <!-- 2. Grado -->
        <div class="col-md-3">
            <label class="small text-muted fw-bold d-block mb-1">Grado / Año</label>
            <select name="grado_id" class="form-select" onchange="this.form.submit()">
                <?php foreach ($gradosList as $g): ?>
                    <option value="<?= $g['id'] ?>" <?= $filtroGrado === (int)$g['id'] ? 'selected' : '' ?>>
                        <?= htmlspecialchars($g['nombre']) ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </div>

        <!-- 3. Sección -->
        <div class="col-md-2">
            <label class="small text-muted fw-bold d-block mb-1">Sección</label>
            <select name="seccion_id" class="form-select" onchange="this.form.submit()">
                <?php foreach ($secciones as $s): ?>
                    <option value="<?= $s['id'] ?>" <?= $filtroSeccion === (int)$s['id'] ? 'selected' : '' ?>>
                        Sección <?= htmlspecialchars($s['nombre']) ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </div>

        <!-- 4. Día -->
        <div class="col-md-3">
            <label class="small text-muted fw-bold d-block mb-1">Día de la Semana</label>
            <select name="dia" class="form-select fw-bold text-indigo-700" onchange="this.form.submit()">
                <?php foreach (['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'] as $d): ?>
                    <option value="<?= $d ?>" <?= $filtroDia === $d ? 'selected' : '' ?>><?= $d ?></option>
                <?php endforeach; ?>
            </select>
        </div>

        <div class="col-md-1 d-flex align-items-end">
            <button type="submit" class="btn btn-dark w-100" title="Actualizar"><i class="bi bi-arrow-repeat"></i></button>
        </div>
    </form>
</div>

<!-- Layout de Horarios: Izquierda Formulario Nueva Clase, Derecha Tarjetas del Día -->
<div class="row g-4">
    <!-- Panel Izquierdo: Formulario "Nueva Clase" -->
    <div class="col-lg-4">
        <div class="dyl-card p-4">
            <h5 class="fw-bold text-dark mb-3 d-flex align-items-center gap-2">
                <i class="bi bi-calendar-plus-fill text-primary"></i>
                Nueva Clase
            </h5>
            <form method="POST" action="">
                <input type="hidden" name="action" value="nueva_clase">

                <div class="mb-3">
                    <label class="form-label small fw-bold text-dark mb-1">MATERIA / CURSO</label>
                    <select name="curso_id" class="form-select">
                        <option value="">-- Seleccionar Materia --</option>
                        <?php foreach ($cursos as $c): ?>
                            <option value="<?= $c['id'] ?>"><?= htmlspecialchars($c['nombre']) ?> (<?= $c['tipo'] ?>)</option>
                        <?php endforeach; ?>
                    </select>
                </div>

                <div class="row g-2 mb-3">
                    <div class="col-6">
                        <label class="form-label small fw-bold text-dark mb-1">HORA DE INICIO</label>
                        <div class="input-group">
                            <input type="text" name="hora_inicio" id="hora_inicio" class="form-control" placeholder="08:00 AM" value="08:00 AM" required>
                            <button class="btn btn-outline-secondary btn-sm px-2 fw-bold" type="button" onclick="toggleAmPm('hora_inicio')">AM/PM</button>
                        </div>
                    </div>
                    <div class="col-6">
                        <label class="form-label small fw-bold text-dark mb-1">HORA DE FIN</label>
                        <div class="input-group">
                            <input type="text" name="hora_fin" id="hora_fin" class="form-control" placeholder="09:30 AM" value="09:30 AM" required>
                            <button class="btn btn-outline-secondary btn-sm px-2 fw-bold" type="button" onclick="toggleAmPm('hora_fin')">AM/PM</button>
                        </div>
                    </div>
                </div>

                <div class="form-check mb-4">
                    <input class="form-check-input" type="checkbox" name="es_recreo" id="es_recreo">
                    <label class="form-check-label small text-dark fw-semibold" for="es_recreo">
                        Marcar como bloque de Recreo / Almuerzo
                    </label>
                </div>

                <button type="submit" class="btn btn-dyl-primary w-100 py-2.5">
                    <i class="bi bi-plus-circle me-1"></i> Guardar en Horario
                </button>
            </form>
        </div>
    </div>

    <!-- Panel Derecho: Horario del Día -->
    <div class="col-lg-8">
        <div class="dyl-card p-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4 class="h6 fw-bold text-dark mb-0 d-flex align-items-center gap-2">
                    <i class="bi bi-calendar3 text-indigo-600"></i>
                    Horario de <?= htmlspecialchars($filtroDia) ?>
                </h4>
                <span class="badge badge-dyl-blue px-3 py-1.5">
                    <?= count($bloques) ?> Bloques Programados
                </span>
            </div>

            <?php if (empty($bloques)): ?>
                <div class="text-center py-5 text-muted">
                    <i class="bi bi-calendar-x fs-1 text-slate-300 d-block mb-2"></i>
                    <p class="small mb-0">No hay clases programadas para este día.</p>
                </div>
            <?php else: ?>
                <div class="d-flex flex-column gap-3">
                    <?php foreach ($bloques as $b): ?>
                        <?php if ($b['es_recreo']): ?>
                            <!-- Bloque de Receso destacado en Amarillo -->
                            <div class="p-3 rounded-3 d-flex justify-content-between align-items-center shadow-xs" 
                                 style="background: #FFFBEB; border: 1.5px dashed #F59E0B;">
                                <div class="d-flex align-items-center gap-3">
                                    <span class="badge bg-warning text-dark px-2.5 py-1.5 fw-bold font-monospace">
                                        <?= htmlspecialchars($b['hora_inicio'] . ' - ' . $b['hora_fin']) ?>
                                    </span>
                                    <div>
                                        <div class="fw-bold text-dark small mb-0">
                                            <i class="bi bi-cup-hot-fill text-warning me-1"></i> RECREO / ALMUERZO (Tiempo Libre)
                                        </div>
                                        <div class="text-muted" style="font-size: 0.72rem;">Receso escolar institucional</div>
                                    </div>
                                </div>
                                <a href="?nivel=<?= $filtroNivel ?>&grado_id=<?= $filtroGrado ?>&seccion_id=<?= $filtroSeccion ?>&dia=<?= $filtroDia ?>&action=eliminar&horario_id=<?= $b['id'] ?>" 
                                   class="btn btn-sm btn-outline-danger px-2 py-1 rounded-2 shadow-xs" 
                                   title="Eliminar bloque"
                                   onclick="return confirm('¿Desea retirar este bloque?')">
                                    <i class="bi bi-x-lg"></i>
                                </a>
                            </div>
                        <?php else: ?>
                            <!-- Bloque de Clase Normal -->
                            <div class="p-3 rounded-3 d-flex justify-content-between align-items-center bg-white border shadow-xs dyl-card-hover">
                                <div class="d-flex align-items-center gap-3">
                                    <span class="badge bg-light text-dark border px-2.5 py-1.5 fw-bold font-monospace">
                                        <?= htmlspecialchars($b['hora_inicio'] . ' - ' . $b['hora_fin']) ?>
                                    </span>
                                    <div>
                                        <div class="fw-bold text-dark small mb-0 d-flex align-items-center gap-2">
                                            <span><?= htmlspecialchars($b['curso_nombre'] ?? 'Materia') ?></span>
                                            <span class="badge badge-dyl-purple" style="font-size: 0.65rem;"><?= htmlspecialchars($b['curso_tipo'] ?? 'Oficial') ?></span>
                                        </div>
                                        <div class="text-muted" style="font-size: 0.72rem;">
                                            <i class="bi bi-geo-alt me-1"></i> Modalidad <?= htmlspecialchars($b['modalidad'] ?? 'Presencial') ?>
                                        </div>
                                    </div>
                                </div>
                                <a href="?nivel=<?= $filtroNivel ?>&grado_id=<?= $filtroGrado ?>&seccion_id=<?= $filtroSeccion ?>&dia=<?= $filtroDia ?>&action=eliminar&horario_id=<?= $b['id'] ?>" 
                                   class="btn btn-sm btn-outline-danger px-2 py-1 rounded-2 shadow-xs" 
                                   title="Eliminar bloque"
                                   onclick="return confirm('¿Desea retirar esta clase del horario?')">
                                    <i class="bi bi-x-lg"></i>
                                </a>
                            </div>
                        <?php endif; ?>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
