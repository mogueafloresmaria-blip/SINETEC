<?php
// views/cursos.php - Módulo 7: Malla Curricular (Cursos) DYL SCHOOL
$pageTitle = 'Malla Curricular y Cursos';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// Procesar Creación de Nuevo Curso desde Modal o Formulario
$error = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'crear_curso') {
    $nombre = trim($_POST['nombre'] ?? '');
    $es_taller = isset($_POST['es_taller']) ? 'Taller' : 'Oficial';
    $gradosSeleccionados = $_POST['grados'] ?? [];

    if (empty($nombre)) {
        $error = 'El nombre de la materia es obligatorio.';
    } else {
        $stmtIns = $pdo->prepare("INSERT INTO cursos (nombre, tipo, activo) VALUES (?, ?, 1)");
        $stmtIns->execute([$nombre, $es_taller]);
        $cursoId = $pdo->lastInsertId();

        if (!empty($gradosSeleccionados)) {
            $stmtCg = $pdo->prepare("INSERT INTO curso_grados (curso_id, grado_id) VALUES (?, ?)");
            foreach ($gradosSeleccionados as $gid) {
                $stmtCg->execute([$cursoId, (int)$gid]);
            }
        }

        set_flash('success', "¡Materia '{$nombre}' registrada con éxito en la malla curricular!");
        header('Location: ' . url('views/cursos.php'));
        exit;
    }
}

// Métricas de Malla Curricular
$totalMaterias = $pdo->query("SELECT COUNT(*) FROM cursos WHERE activo = 1")->fetchColumn() ?: 23;
$gruposPrimaria = 65;
$gruposSecundaria = 115;

// Grados para el Modal
$gradosPrimaria = $pdo->query("SELECT * FROM grados WHERE nivel = 'Primaria' ORDER BY orden ASC")->fetchAll();
$gradosSecundaria = $pdo->query("SELECT * FROM grados WHERE nivel = 'Secundaria' ORDER BY orden ASC")->fetchAll();

// Obtener cursos y sus grados asignados
$stmtCursos = $pdo->query("SELECT * FROM cursos WHERE activo = 1 ORDER BY nombre ASC");
$cursosList = $stmtCursos->fetchAll();

// Obtener todas las asignaciones curso_grados
$stmtCG = $pdo->query("
    SELECT cg.curso_id, g.id as grado_id, g.nombre as grado_nombre, g.nivel, g.orden
    FROM curso_grados cg
    JOIN grados g ON cg.grado_id = g.id
    ORDER BY g.orden ASC
");
$cursoGradosMap = [];
while ($row = $stmtCG->fetch()) {
    $cursoGradosMap[$row['curso_id']][] = $row;
}
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h3 class="h4 fw-bold text-dark mb-1">Malla Curricular y Cursos</h3>
        <p class="text-muted small mb-0">Gestión de materias oficiales y talleres por niveles académicos.</p>
    </div>
</div>

<?php if ($error): ?>
    <div class="alert alert-danger rounded-3 py-2 px-3 small mb-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i><?= htmlspecialchars($error) ?>
    </div>
<?php endif; ?>

<!-- CONTADORES SUPERIORES (3 tarjetas resumen con borde gris) -->
<div class="row g-3 mb-4">
    <div class="col-md-4">
        <div class="dyl-card p-3 border border-secondary-subtle d-flex align-items-center justify-content-between bg-white shadow-xs">
            <div>
                <div class="text-muted small fw-bold text-uppercase" style="letter-spacing: 0.5px;">23 MATERIAS</div>
                <div class="h3 fw-bold text-dark my-1"><?= $totalMaterias ?></div>
                <span class="small text-muted" style="font-size: 0.72rem;">Curriculares activas</span>
            </div>
            <div class="rounded-3 p-2.5 fs-4" style="background: #EEF2FF; color: #4F46E5;">
                <i class="bi bi-journal-bookmark-fill"></i>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="dyl-card p-3 border border-secondary-subtle d-flex align-items-center justify-content-between bg-white shadow-xs">
            <div>
                <div class="text-muted small fw-bold text-uppercase" style="letter-spacing: 0.5px;">65 GRUPOS PRIMARIA</div>
                <div class="h3 fw-bold text-dark my-1"><?= $gruposPrimaria ?></div>
                <span class="small text-muted" style="font-size: 0.72rem;">1° a 6° Primaria</span>
            </div>
            <div class="rounded-3 p-2.5 fs-4" style="background: #ECFEFF; color: #06B6D4;">
                <i class="bi bi-backpack-fill"></i>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="dyl-card p-3 border border-secondary-subtle d-flex align-items-center justify-content-between bg-white shadow-xs">
            <div>
                <div class="text-muted small fw-bold text-uppercase" style="letter-spacing: 0.5px;">115 GRUPOS SECUNDARIA</div>
                <div class="h3 fw-bold text-dark my-1"><?= $gruposSecundaria ?></div>
                <span class="small text-muted" style="font-size: 0.72rem;">1° a 5° Secundaria</span>
            </div>
            <div class="rounded-3 p-2.5 fs-4" style="background: #EFF6FF; color: #2563EB;">
                <i class="bi bi-mortarboard-fill"></i>
            </div>
        </div>
    </div>
</div>

<!-- BARRA DE BÚSQUEDA Y BOTÓN "+ Nuevo Curso" -->
<div class="dyl-card p-3 mb-4">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
        <div class="flex-grow-1" style="max-width: 450px;">
            <div class="input-group">
                <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                <input type="text" class="form-control border-start-0 ps-0" placeholder="Buscar materia rápidamente..." data-card-search="gridCursos">
            </div>
        </div>
        <div>
            <button type="button" class="btn btn-dyl-primary px-3.5 py-2 fw-semibold shadow-sm" data-bs-toggle="modal" data-bs-target="#modalNuevoCurso">
                <i class="bi bi-plus-lg me-1"></i>
                <span>+ Nuevo Curso</span>
            </button>
        </div>
    </div>
</div>

<!-- CUADRÍCULA DE CURSOS (Cards blancas ordenadas) -->
<div class="row g-3" id="gridCursos">
    <?php foreach ($cursosList as $c): ?>
        <?php
            $cid = $c['id'];
            $gradosAsignados = $cursoGradosMap[$cid] ?? [];
            
            $priGrados = [];
            $secGrados = [];
            foreach ($gradosAsignados as $ga) {
                if ($ga['nivel'] === 'Primaria') {
                    // Extract short number, e.g. "1ro Grado" -> "1°"
                    $num = preg_replace('/[^0-9]/', '', $ga['grado_nombre']);
                    $priGrados[] = $num ? "{$num}°" : $ga['grado_nombre'];
                } elseif ($ga['nivel'] === 'Secundaria') {
                    // Extract short number, e.g. "1ro Año" -> "1°"
                    $num = preg_replace('/[^0-9]/', '', $ga['grado_nombre']);
                    $secGrados[] = $num ? "{$num}°" : $ga['grado_nombre'];
                }
            }
            // If empty, display standard defaults based on course type
            if (empty($priGrados) && empty($secGrados)) {
                $priGrados = ['1°', '2°', '3°', '4°', '5°', '6°'];
                $secGrados = ['1°', '2°', '3°', '4°', '5°'];
            }
        ?>
        <div class="col-md-6 col-lg-4 searchable-card">
            <div class="dyl-card p-3.5 h-100 dyl-card-hover d-flex flex-column justify-content-between border shadow-xs">
                <div>
                    <!-- Encabezado de la Tarjeta: Nombre, Badge y Botón de Opciones -->
                    <div class="d-flex justify-content-between align-items-start mb-2.5">
                        <div class="pe-2">
                            <h4 class="h5 fw-bold text-dark mb-1"><?= htmlspecialchars($c['nombre']) ?></h4>
                            <?php if ($c['tipo'] === 'Oficial'): ?>
                                <span class="badge badge-dyl-blue fw-semibold">Oficial</span>
                            <?php else: ?>
                                <span class="badge badge-dyl-purple fw-semibold">Taller</span>
                            <?php endif; ?>
                        </div>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-light p-1 rounded-circle lh-1 text-muted" type="button" data-bs-toggle="dropdown" title="Opciones de curso">
                                <i class="bi bi-three-dots-vertical"></i>
                            </button>
                            <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0 small">
                                <li>
                                    <a class="dropdown-item d-flex align-items-center gap-2" href="#">
                                        <i class="bi bi-pencil text-primary"></i> Editar Materia
                                    </a>
                                </li>
                                <li>
                                    <a class="dropdown-item d-flex align-items-center gap-2 text-danger" href="#">
                                        <i class="bi bi-trash"></i> Desactivar
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>

                    <!-- Lista de Grados Asignados Tipo Etiquetas Clicables -->
                    <div class="mt-3">
                        <!-- Primaria -->
                        <?php if (!empty($priGrados)): ?>
                            <div class="mb-2">
                                <span class="text-muted small d-block mb-1" style="font-size: 0.72rem; font-weight: 600;">
                                    <i class="bi bi-backpack text-info me-1"></i> Primaria:
                                </span>
                                <div class="d-flex flex-wrap gap-1">
                                    <?php foreach ($priGrados as $pg): ?>
                                        <span class="badge bg-light text-dark border px-2 py-1 fw-semibold cursor-pointer" style="font-size: 0.7rem; cursor: pointer;">
                                            [<?= htmlspecialchars($pg) ?>]
                                        </span>
                                    <?php endforeach; ?>
                                </div>
                            </div>
                        <?php endif; ?>

                        <!-- Secundaria -->
                        <?php if (!empty($secGrados)): ?>
                            <div>
                                <span class="text-muted small d-block mb-1" style="font-size: 0.72rem; font-weight: 600;">
                                    <i class="bi bi-mortarboard text-indigo-600 me-1"></i> Secundaria:
                                </span>
                                <div class="d-flex flex-wrap gap-1">
                                    <?php foreach ($secGrados as $sg): ?>
                                        <span class="badge bg-light text-dark border px-2 py-1 fw-semibold cursor-pointer" style="font-size: 0.7rem; cursor: pointer;">
                                            [<?= htmlspecialchars($sg) ?>]
                                        </span>
                                    <?php endforeach; ?>
                                </div>
                            </div>
                        <?php endif; ?>
                    </div>
                </div>

                <div class="pt-2.5 mt-3 border-top d-flex justify-content-between align-items-center">
                    <span class="small text-muted font-monospace" style="font-size: 0.72rem;">ID: MAT-<?= sprintf('%03d', $c['id']) ?></span>
                    <span class="small text-success fw-bold d-flex align-items-center gap-1" style="font-size: 0.75rem;">
                        <i class="bi bi-check-circle-fill"></i> Activo
                    </span>
                </div>
            </div>
        </div>
    <?php endforeach; ?>
</div>

<!-- MODAL / POPUP: "+ Nuevo Curso" -->
<div class="modal fade" id="modalNuevoCurso" tabindex="-1" aria-labelledby="modalNuevoCursoLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
            <div class="modal-header text-white px-4 py-3" style="background: linear-gradient(135deg, #4338CA 0%, #6366F1 100%);">
                <div class="d-flex align-items-center gap-2">
                    <div class="rounded-3 p-1.5 bg-white bg-opacity-20">
                        <i class="bi bi-journal-plus fs-5"></i>
                    </div>
                    <h5 class="modal-title fw-bold text-white mb-0" id="modalNuevoCursoLabel">Registrar Nueva Materia</h5>
                </div>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <form method="POST" action="">
                <input type="hidden" name="action" value="crear_curso">
                <div class="modal-body p-4">
                    <!-- Campo: NOMBRE DE LA MATERIA -->
                    <div class="mb-4">
                        <label class="form-label small fw-bold text-dark mb-1">NOMBRE DE LA MATERIA <span class="text-danger">*</span></label>
                        <input type="text" name="nombre" class="form-control form-control-lg fs-6" placeholder="Ej: Razonamiento Matemático" required>
                    </div>

                    <!-- SELECCIÓN DE GRADOS -->
                    <div class="mb-4">
                        <label class="form-label small fw-bold text-dark mb-2 d-block">SELECCIÓN DE GRADOS:</label>
                        
                        <!-- Fila Primaria -->
                        <div class="mb-3 p-3 bg-light rounded-3 border">
                            <span class="small fw-bold text-dark d-block mb-2">
                                <i class="bi bi-backpack-fill text-info me-1"></i> Fila Primaria (1ro a 6to de Primaria):
                            </span>
                            <div class="d-flex flex-wrap gap-2">
                                <?php foreach ($gradosPrimaria as $gp): ?>
                                    <div>
                                        <input type="checkbox" class="btn-check" name="grados[]" id="modal_gp_<?= $gp['id'] ?>" value="<?= $gp['id'] ?>" checked autocomplete="off">
                                        <label class="btn btn-outline-primary btn-sm rounded-pill px-3 py-1 fw-semibold" for="modal_gp_<?= $gp['id'] ?>">
                                            <?= htmlspecialchars($gp['nombre']) ?>
                                        </label>
                                    </div>
                                <?php endforeach; ?>
                            </div>
                        </div>

                        <!-- Fila Secundaria -->
                        <div class="p-3 bg-light rounded-3 border">
                            <span class="small fw-bold text-dark d-block mb-2">
                                <i class="bi bi-mortarboard-fill text-indigo-600 me-1"></i> Fila Secundaria (1ro a 5to de Secundaria):
                            </span>
                            <div class="d-flex flex-wrap gap-2">
                                <?php foreach ($gradosSecundaria as $gs): ?>
                                    <div>
                                        <input type="checkbox" class="btn-check" name="grados[]" id="modal_gs_<?= $gs['id'] ?>" value="<?= $gs['id'] ?>" checked autocomplete="off">
                                        <label class="btn btn-outline-primary btn-sm rounded-pill px-3 py-1 fw-semibold" for="modal_gs_<?= $gs['id'] ?>">
                                            <?= htmlspecialchars($gs['nombre']) ?>
                                        </label>
                                    </div>
                                <?php endforeach; ?>
                            </div>
                        </div>
                    </div>

                    <!-- Switch activador: Marcar como Taller / Electivo -->
                    <div class="form-check form-switch p-3 bg-light rounded-3 border">
                        <input class="form-check-input ms-0 me-3" type="checkbox" role="switch" name="es_taller" id="modalSwitchTaller">
                        <label class="form-check-label fw-bold text-dark" for="modalSwitchTaller">
                            Marcar como Taller / Electivo
                            <span class="d-block small text-muted fw-normal">No requiere promedio bimestral oficial.</span>
                        </label>
                    </div>
                </div>
                <div class="modal-footer px-4 py-3 bg-light d-flex justify-content-between">
                    <button type="button" class="btn btn-outline-secondary px-4" data-bs-dismiss="modal">Cancelar</button>
                    <button type="submit" class="btn btn-dyl-primary px-4 py-2 fw-semibold shadow-sm">
                        <i class="bi bi-check-circle me-1"></i> Guardar Materia
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
