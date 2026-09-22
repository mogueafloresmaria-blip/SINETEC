<?php
// views/matriculas.php - Módulo 3: Matrículas y Control de Vencimientos DYL SCHOOL
$pageTitle = 'Matrículas y Control de Pensiones';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// Métricas de Matrículas
$totalMatriculados = $pdo->query("SELECT COUNT(*) FROM matriculas WHERE anio_lectivo = 2026")->fetchColumn() ?: 8;
$totalPrimaria = $pdo->query("SELECT COUNT(*) FROM matriculas m JOIN grados g ON m.grado_id = g.id WHERE g.nivel = 'Primaria' AND m.anio_lectivo = 2026")->fetchColumn() ?: 0;
$totalSecundaria = $pdo->query("SELECT COUNT(*) FROM matriculas m JOIN grados g ON m.grado_id = g.id WHERE g.nivel = 'Secundaria' AND m.anio_lectivo = 2026")->fetchColumn() ?: 8;

// Listado de Grados para filtros
$grados = $pdo->query("SELECT * FROM grados ORDER BY orden ASC")->fetchAll();
$secciones = $pdo->query("SELECT * FROM secciones ORDER BY nombre ASC")->fetchAll();

// Filtros GET
$filtroGrado = (int)($_GET['grado_id'] ?? 0);
$filtroSeccion = (int)($_GET['seccion_id'] ?? 0);
$filtroQuery = trim($_GET['q'] ?? '');

$sql = "
    SELECT m.*, a.nombres, a.apellidos, a.dni, a.telefono_apoderado, g.nombre as grado_nombre, g.nivel as grado_nivel, s.nombre as seccion_nombre
    FROM matriculas m
    JOIN alumnos a ON m.alumno_id = a.id
    JOIN grados g ON m.grado_id = g.id
    JOIN secciones s ON m.seccion_id = s.id
    WHERE m.anio_lectivo = 2026
";
$params = [];

if ($filtroGrado > 0) {
    $sql .= " AND m.grado_id = ?";
    $params[] = $filtroGrado;
}
if ($filtroSeccion > 0) {
    $sql .= " AND m.seccion_id = ?";
    $params[] = $filtroSeccion;
}
if ($filtroQuery !== '') {
    $sql .= " AND (a.nombres LIKE ? OR a.apellidos LIKE ? OR a.dni LIKE ?)";
    $term = "%{$filtroQuery}%";
    $params[] = $term;
    $params[] = $term;
    $params[] = $term;
}

$sql .= " ORDER BY g.orden ASC, s.nombre ASC, a.apellidos ASC";
$stmt = $pdo->prepare($sql);
$stmt->execute($params);
$matriculas = $stmt->fetchAll();

// Agrupar por "Grado - Nivel - Sección"
$grupos = [];
foreach ($matriculas as $m) {
    $key = strtoupper($m['grado_nombre']) . ' - ' . strtoupper($m['grado_nivel']) . ' (SECCIÓN ' . $m['seccion_nombre'] . ')';
    $grupos[$key][] = $m;
}
?>

<!-- Métricas Principales -->
<div class="row g-3 mb-4">
    <div class="col-4">
        <div class="dyl-card p-3 d-flex align-items-center justify-content-between">
            <div>
                <div class="text-muted small fw-bold text-uppercase">TOTAL ALUMNOS</div>
                <div class="h3 fw-bold text-dark my-1"><?= $totalMatriculados ?></div>
            </div>
            <div class="rounded-3 p-2.5 fs-4" style="background: #EEF2FF; color: #4F46E5;">
                <i class="bi bi-mortarboard-fill"></i>
            </div>
        </div>
    </div>
    <div class="col-4">
        <div class="dyl-card p-3 d-flex align-items-center justify-content-between">
            <div>
                <div class="text-muted small fw-bold text-uppercase">PRIMARIA</div>
                <div class="h3 fw-bold text-dark my-1"><?= $totalPrimaria ?></div>
            </div>
            <div class="rounded-3 p-2.5 fs-4" style="background: #F1F5F9; color: #64748B;">
                <i class="bi bi-backpack-fill"></i>
            </div>
        </div>
    </div>
    <div class="col-4">
        <div class="dyl-card p-3 d-flex align-items-center justify-content-between">
            <div>
                <div class="text-primary small fw-bold text-uppercase">SECUNDARIA</div>
                <div class="h3 fw-bold text-primary my-1"><?= $totalSecundaria ?></div>
            </div>
            <div class="rounded-3 p-2.5 fs-4" style="background: #EFF6FF; color: #2563EB;">
                <i class="bi bi-mortarboard-fill"></i>
            </div>
        </div>
    </div>
</div>

<!-- Barra de Filtros en Línea -->
<div class="dyl-card p-3 mb-4">
    <form method="GET" action="" class="row g-2 align-items-center">
        <!-- Buscador -->
        <div class="col-md-4">
            <div class="input-group">
                <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                <input type="text" name="q" class="form-control border-start-0 ps-0" placeholder="Buscar por alumno o DNI..." value="<?= htmlspecialchars($filtroQuery) ?>">
            </div>
        </div>

        <!-- Selector Grados -->
        <div class="col-md-3">
            <select name="grado_id" class="form-select">
                <option value="0">Todos los Grados</option>
                <?php foreach ($grados as $g): ?>
                    <option value="<?= $g['id'] ?>" <?= $filtroGrado === (int)$g['id'] ? 'selected' : '' ?>>
                        <?= htmlspecialchars($g['nombre'] . ' (' . $g['nivel'] . ')') ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </div>

        <!-- Selector Secciones -->
        <div class="col-md-2">
            <select name="seccion_id" class="form-select">
                <option value="0">Todas las Secciones</option>
                <?php foreach ($secciones as $s): ?>
                    <option value="<?= $s['id'] ?>" <?= $filtroSeccion === (int)$s['id'] ? 'selected' : '' ?>>
                        Sec. <?= htmlspecialchars($s['nombre']) ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </div>

        <div class="col-md-1">
            <button type="submit" class="btn btn-dark w-100"><i class="bi bi-funnel"></i></button>
        </div>

        <!-- Botón Nueva Matrícula -->
        <div class="col-md-2 text-end">
            <a href="<?= url('views/matricula_nueva.php') ?>" class="btn btn-dyl-primary w-100">
                <i class="bi bi-plus-lg"></i>
                <span>Nueva Matrícula</span>
            </a>
        </div>
    </form>
</div>

<!-- Listado Agrupado por Grado y Sección -->
<?php if (empty($grupos)): ?>
    <div class="dyl-card p-5 text-center text-muted">
        <i class="bi bi-inbox fs-1 d-block mb-2 text-slate-300"></i>
        <h5 class="fw-bold text-dark">No se encontraron matrículas</h5>
        <p class="small mb-3">Intenta cambiar los filtros o registra una nueva matrícula en el sistema.</p>
        <a href="<?= url('views/matricula_nueva.php') ?>" class="btn btn-dyl-primary btn-sm px-3">Registrar Matrícula</a>
    </div>
<?php else: ?>
    <?php foreach ($grupos as $nombreGrupo => $alumnosGrupo): ?>
        <div class="dyl-card mb-4 overflow-hidden">
            <div class="p-3 bg-white border-bottom d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded-2 fw-bold" style="background: #EEF2FF; color: #4F46E5;">
                        <i class="bi bi-collection-fill me-1"></i> AULA
                    </span>
                    <h4 class="h6 fw-bold text-dark mb-0"><?= htmlspecialchars($nombreGrupo) ?></h4>
                </div>
                <span class="badge bg-light text-dark border px-2.5 py-1">
                    <?= count($alumnosGrupo) ?> Estudiantes
                </span>
            </div>

            <div class="table-responsive">
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr class="small text-muted text-uppercase fw-bold">
                            <th class="ps-4">ALUMNO</th>
                            <th>UBICACIÓN</th>
                            <th>ESTADO DE PENSIÓN</th>
                            <th class="text-end pe-4">ACCIONES</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($alumnosGrupo as $m): ?>
                            <?php
                                $telefonoClean = preg_replace('/[^0-9]/', '', $m['telefono_apoderado'] ?? '51987111222');
                                $fechaCob = $m['pagado_hasta'] ?? 'Marzo 2026';
                                $alumnoNombre = $m['nombres'] . ' ' . $m['apellidos'];
                                $gradoNombre = $m['grado_nombre'];
                                $msjWhatsapp = urlencode("¡Gracias por su pago adelantado! Estimado apoderado de {$alumnoNombre} ({$gradoNombre}), confirmamos que sus pensiones están cubiertas hasta el {$fechaCob}. Atte: DYL SCHOOL");
                                $whatsappUrl = "https://api.whatsapp.com/send?phone={$telefonoClean}&text={$msjWhatsapp}";
                            ?>
                            <tr>
                                <td class="ps-4">
                                    <div class="d-flex align-items-center gap-2.5">
                                        <div class="dyl-user-avatar" style="width: 36px; height: 36px; font-size: 0.8rem;">
                                            <?= strtoupper(substr($m['nombres'], 0, 1)) ?>
                                        </div>
                                        <div>
                                            <div class="fw-bold text-dark small mb-0"><?= htmlspecialchars($alumnoNombre) ?></div>
                                            <div class="text-muted" style="font-size: 0.72rem;">DNI: <?= htmlspecialchars($m['dni']) ?></div>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <span class="small fw-semibold text-secondary">
                                        <?= htmlspecialchars($m['grado_nombre'] . ' - Sec. ' . $m['seccion_nombre'] . ' (' . $m['grado_nivel'] . ')') ?>
                                    </span>
                                </td>
                                <td>
                                    <?php if ($m['estado_pension'] === 'ADELANTADO'): ?>
                                        <span class="badge badge-dyl-blue d-inline-flex align-items-center gap-1">
                                            <i class="bi bi-shield-check"></i> ADELANTADO
                                        </span>
                                        <span class="small text-muted ms-1" style="font-size: 0.74rem;">Hasta <?= htmlspecialchars($m['pagado_hasta'] ?? 'Mar 2026') ?></span>
                                    <?php else: ?>
                                        <span class="badge badge-dyl-gray d-inline-flex align-items-center gap-1">
                                            <i class="bi bi-exclamation-circle"></i> SIN HISTORIAL
                                        </span>
                                        <span class="small text-danger fw-semibold ms-1" style="font-size: 0.74rem;">Requiere Pago</span>
                                    <?php endif; ?>
                                </td>
                                <td class="text-end pe-4">
                                    <div class="d-inline-flex gap-1">
                                        <!-- Botón WhatsApp Interactivo -->
                                        <a href="<?= $whatsappUrl ?>" target="_blank" class="btn btn-sm btn-outline-success px-2.5 py-1 rounded-2 shadow-xs" title="Enviar Notificación por WhatsApp">
                                            <i class="bi bi-whatsapp"></i> WhatsApp
                                        </a>
                                        <!-- Editar Matrícula (naranja) -->
                                        <a href="<?= url('views/alumno_editar.php?id=' . $m['alumno_id']) ?>" class="btn btn-sm btn-outline-warning text-dark px-2 py-1 rounded-2 shadow-xs" title="Editar">
                                            <i class="bi bi-pencil-fill text-amber-600"></i>
                                        </a>
                                    </div>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </div>
    <?php endforeach; ?>
<?php endif; ?>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
