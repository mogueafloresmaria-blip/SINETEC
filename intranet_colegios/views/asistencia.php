<?php
// views/asistencia.php - Módulo 12: Control de Asistencia DYL SCHOOL
$pageTitle = 'Control Diario de Asistencia';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// Filtros
$filtroFecha = $_GET['fecha'] ?? '2026-01-09';
$filtroNivel = $_GET['nivel'] ?? 'Secundaria';
$filtroGrado = (int)($_GET['grado_id'] ?? 0);
$filtroSeccion = (int)($_GET['seccion_id'] ?? 0);

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

// Procesar Guardado de Asistencia
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'guardar_asistencia') {
    $fechaPost = $_POST['fecha_asist'] ?? $filtroFecha;
    $asistencias = $_POST['asistencia'] ?? [];

    foreach ($asistencias as $matId => $estado) {
        $stmtCheck = $pdo->prepare("SELECT id FROM asistencia WHERE matricula_id = ? AND fecha = ?");
        $stmtCheck->execute([$matId, $fechaPost]);
        $row = $stmtCheck->fetch();

        if ($row) {
            $pdo->prepare("UPDATE asistencia SET estado = ? WHERE id = ?")->execute([$estado, $row['id']]);
        } else {
            $pdo->prepare("INSERT INTO asistencia (matricula_id, fecha, estado) VALUES (?, ?, ?)")->execute([$matId, $fechaPost, $estado]);
        }
    }

    set_flash('success', '¡Asistencia escolar guardada y consolidada exitosamente!');
    header("Location: " . url("views/asistencia.php?fecha={$fechaPost}&nivel={$filtroNivel}&grado_id={$filtroGrado}&seccion_id={$filtroSeccion}"));
    exit;
}

// Consultar Alumnos matriculados en esa aula
$stmtAlumnos = $pdo->prepare("
    SELECT m.id as matricula_id, a.id as alumno_id, a.nombres, a.apellidos, a.dni,
           asi.estado as asistencia_estado
    FROM matriculas m
    JOIN alumnos a ON m.alumno_id = a.id
    LEFT JOIN asistencia asi ON m.id = asi.matricula_id AND asi.fecha = ?
    WHERE m.grado_id = ? AND m.seccion_id = ? AND m.anio_lectivo = 2026
    ORDER BY a.apellidos ASC
");
$stmtAlumnos->execute([$filtroFecha, $filtroGrado, $filtroSeccion]);
$alumnosAula = $stmtAlumnos->fetchAll();
?>

<!-- Barra de Filtros Superior -->
<div class="dyl-card p-3 mb-4">
    <form method="GET" action="" class="row g-2 align-items-center">
        <!-- 1. Selector de Fecha -->
        <div class="col-md-3">
            <label class="small text-muted fw-bold d-block mb-1">Fecha de Registro</label>
            <input type="date" name="fecha" class="form-control fw-bold text-dark" value="<?= htmlspecialchars($filtroFecha) ?>" onchange="this.form.submit()">
        </div>

        <!-- 2. Nivel Académico -->
        <div class="col-md-3">
            <label class="small text-muted fw-bold d-block mb-1">Nivel Académico</label>
            <select name="nivel" class="form-select" onchange="this.form.submit()">
                <option value="Inicial" <?= $filtroNivel === 'Inicial' ? 'selected' : '' ?>>Inicial</option>
                <option value="Primaria" <?= $filtroNivel === 'Primaria' ? 'selected' : '' ?>>Primaria</option>
                <option value="Secundaria" <?= $filtroNivel === 'Secundaria' ? 'selected' : '' ?>>Secundaria</option>
            </select>

        </div>

        <!-- 3. Grado -->
        <div class="col-md-3">
            <label class="small text-muted fw-bold d-block mb-1">Grado</label>
            <select name="grado_id" class="form-select" onchange="this.form.submit()">
                <?php foreach ($gradosList as $g): ?>
                    <option value="<?= $g['id'] ?>" <?= $filtroGrado === (int)$g['id'] ? 'selected' : '' ?>>
                        <?= htmlspecialchars($g['nombre']) ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </div>

        <!-- 4. Sección -->
        <div class="col-md-2">
            <label class="small text-muted fw-bold d-block mb-1">Sección</label>
            <select name="seccion_id" class="form-select" onchange="this.form.submit()">
                <?php foreach ($secciones as $s): ?>
                    <option value="<?= $s['id'] ?>" <?= $filtroSeccion === (int)$s['id'] ? 'selected' : '' ?>>
                        Sección "<?= htmlspecialchars($s['nombre']) ?>"
                    </option>
                <?php endforeach; ?>
            </select>
        </div>

        <div class="col-md-1 d-flex align-items-end">
            <button type="submit" class="btn btn-dark w-100" title="Buscar"><i class="bi bi-search"></i></button>
        </div>
    </form>
</div>

<!-- Listado de Asistencia Cargado Dinámicamente -->
<div class="dyl-card p-4">
    <form method="POST" action="">
        <input type="hidden" name="action" value="guardar_asistencia">
        <input type="hidden" name="fecha_asist" value="<?= htmlspecialchars($filtroFecha) ?>">

        <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4 pb-3 border-bottom">
            <div>
                <h5 class="fw-bold text-dark mb-1 d-flex align-items-center gap-2">
                    <i class="bi bi-calendar-check-fill text-primary"></i>
                    Lista de Control: <?= count($alumnosAula) ?> Estudiantes Encontrados
                </h5>
                <span class="text-muted small">Fecha: <strong><?= date('d/m/Y', strtotime($filtroFecha)) ?></strong></span>
            </div>
            <div>
                <!-- Botón Todos Presentes -->
                <button type="button" class="btn btn-outline-success btn-sm px-3 rounded-pill fw-bold" onclick="marcarTodosPresentes()">
                    <i class="bi bi-check2-all me-1"></i> Todos Presentes
                </button>
            </div>
        </div>

        <?php if (empty($alumnosAula)): ?>
            <div class="text-center py-5 text-muted">
                <i class="bi bi-people fs-1 text-slate-300 d-block mb-2"></i>
                <p class="small mb-0">No se encontraron estudiantes matriculados en esta sección para el periodo 2026.</p>
            </div>
        <?php else: ?>
            <div class="table-responsive mb-4">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr class="small text-muted text-uppercase fw-bold">
                            <th class="ps-3" style="width: 50px;">#</th>
                            <th>ESTUDIANTE</th>
                            <th>DNI</th>
                            <th class="text-center" style="width: 320px;">ESTADO DE ASISTENCIA</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($alumnosAula as $idx => $al): ?>
                            <?php $estadoActual = $al['asistencia_estado'] ?? 'Presente'; ?>
                            <tr>
                                <td class="ps-3 text-muted small fw-bold"><?= $idx + 1 ?></td>
                                <td>
                                    <div class="d-flex align-items-center gap-2.5">
                                        <div class="dyl-user-avatar" style="width: 36px; height: 36px; font-size: 0.8rem;">
                                            <?= strtoupper(substr($al['nombres'], 0, 1)) ?>
                                        </div>
                                        <div>
                                            <div class="fw-bold text-dark small mb-0"><?= htmlspecialchars($al['apellidos'] . ', ' . $al['nombres']) ?></div>
                                            <div class="text-muted" style="font-size: 0.72rem;">Matrícula #<?= $al['matricula_id'] ?></div>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <span class="badge bg-light text-dark border font-monospace">
                                        <?= htmlspecialchars($al['dni']) ?>
                                    </span>
                                </td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm rounded-pill p-1 border bg-light shadow-xs" role="group">
                                        <!-- Presente (Verde) -->
                                        <input type="radio" class="btn-check" name="asistencia[<?= $al['matricula_id'] ?>]" id="pres_<?= $al['matricula_id'] ?>" value="Presente" <?= $estadoActual === 'Presente' ? 'checked' : '' ?>>
                                        <label class="btn btn-sm rounded-pill px-3 py-1 fw-bold btn-outline-success" for="pres_<?= $al['matricula_id'] ?>">
                                            <i class="bi bi-check-lg"></i> Presente
                                        </label>

                                        <!-- Tarde (Ámbar) -->
                                        <input type="radio" class="btn-check" name="asistencia[<?= $al['matricula_id'] ?>]" id="tarde_<?= $al['matricula_id'] ?>" value="Tarde" <?= $estadoActual === 'Tarde' ? 'checked' : '' ?>>
                                        <label class="btn btn-sm rounded-pill px-3 py-1 fw-bold btn-outline-warning text-dark" for="tarde_<?= $al['matricula_id'] ?>">
                                            <i class="bi bi-clock"></i> Tarde
                                        </label>

                                        <!-- Falta (Rojo) -->
                                        <input type="radio" class="btn-check" name="asistencia[<?= $al['matricula_id'] ?>]" id="falta_<?= $al['matricula_id'] ?>" value="Falta" <?= $estadoActual === 'Falta' ? 'checked' : '' ?>>
                                        <label class="btn btn-sm rounded-pill px-3 py-1 fw-bold btn-outline-danger" for="falta_<?= $al['matricula_id'] ?>">
                                            <i class="bi bi-x-lg"></i> Falta
                                        </label>
                                    </div>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>

            <div class="text-end pt-3 border-top">
                <button type="submit" class="btn btn-dyl-primary px-5 py-2.5 fw-bold shadow-sm">
                    <i class="bi bi-check2-circle me-1"></i> Guardar Asistencia
                </button>
            </div>
        <?php endif; ?>
    </form>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
