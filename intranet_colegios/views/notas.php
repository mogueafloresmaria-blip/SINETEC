<?php
// views/notas.php - Módulo 8: Calificaciones y Evaluación Académica DYL SCHOOL
$pageTitle = 'Registro de Calificaciones';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// Datos para el Método 1: Aulas y Cursos
$grados = $pdo->query("SELECT * FROM grados ORDER BY orden ASC")->fetchAll();
$secciones = $pdo->query("SELECT * FROM secciones ORDER BY nombre ASC")->fetchAll();
$cursos = $pdo->query("SELECT * FROM cursos WHERE activo = 1 ORDER BY nombre ASC")->fetchAll();

// Datos para el Método 2: Alumnos Matriculados 2026
$stmtAlumnos = $pdo->query("
    SELECT a.id, a.nombres, a.apellidos, a.dni, a.foto, g.nombre as grado_nombre, g.nivel as grado_nivel, s.nombre as seccion_nombre, m.id as matricula_id
    FROM matriculas m
    JOIN alumnos a ON m.alumno_id = a.id
    JOIN grados g ON m.grado_id = g.id
    JOIN secciones s ON m.seccion_id = s.id
    WHERE m.anio_lectivo = 2026
    ORDER BY a.apellidos ASC, a.nombres ASC
");
$alumnos = $stmtAlumnos->fetchAll();
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h3 class="h4 fw-bold text-dark mb-1">Calificaciones y Evaluación Académica</h3>
        <p class="text-muted small mb-0">Seleccione el método de registro de notas: por aula o individual por estudiante.</p>
    </div>
</div>

<div class="row g-4">
    <!-- MÉTODO 1: "Ingreso por Aula" (Actas por Sección y Curso) -->
    <div class="col-lg-5">
        <div class="dyl-card p-4 h-100 border shadow-xs d-flex flex-column justify-content-between">
            <div>
                <div class="d-flex align-items-center gap-3 mb-3">
                    <div class="rounded-3 p-2.5" style="background: #EEF2FF; color: #4F46E5;">
                        <i class="bi bi-card-checklist fs-4"></i>
                    </div>
                    <div>
                        <h5 class="fw-bold text-dark mb-0">Ingreso por Aula</h5>
                        <span class="text-muted small">Actas por Sección y Curso</span>
                    </div>
                </div>

                <form method="GET" action="<?= url('views/calificar_aula.php') ?>">
                    <!-- Selector: AULA / SECCIÓN -->
                    <div class="mb-3">
                        <label class="form-label small fw-bold text-dark mb-1">AULA / SECCIÓN <span class="text-danger">*</span></label>
                        <select name="aula_seccion" class="form-select" required>
                            <option value="">-- Seleccionar Aula --</option>
                            <optgroup label="Nivel Primaria">
                                <?php foreach ($grados as $g): ?>
                                    <?php if ($g['nivel'] === 'Primaria'): ?>
                                        <?php foreach ($secciones as $s): ?>
                                            <option value="<?= $g['id'] ?>_<?= $s['id'] ?>">
                                                <?= htmlspecialchars($g['nombre'] . ' "' . $s['nombre'] . '" - Primaria') ?>
                                            </option>
                                        <?php endforeach; ?>
                                    <?php endif; ?>
                                <?php endforeach; ?>
                            </optgroup>
                            <optgroup label="Nivel Secundaria">
                                <?php foreach ($grados as $g): ?>
                                    <?php if ($g['nivel'] === 'Secundaria'): ?>
                                        <?php foreach ($secciones as $s): ?>
                                            <option value="<?= $g['id'] ?>_<?= $s['id'] ?>">
                                                <?= htmlspecialchars($g['nombre'] . ' "' . $s['nombre'] . '" - Secundaria') ?>
                                            </option>
                                        <?php endforeach; ?>
                                    <?php endif; ?>
                                <?php endforeach; ?>
                            </optgroup>
                        </select>
                    </div>

                    <!-- Selector: CURSO FILTRADO -->
                    <div class="mb-4">
                        <label class="form-label small fw-bold text-dark mb-1">CURSO FILTRADO <span class="text-danger">*</span></label>
                        <select name="curso_id" class="form-select" required>
                            <option value="">-- Seleccionar Curso --</option>
                            <?php foreach ($cursos as $c): ?>
                                <option value="<?= $c['id'] ?>"><?= htmlspecialchars($c['nombre']) ?> (<?= $c['tipo'] ?>)</option>
                            <?php endforeach; ?>
                        </select>
                    </div>

                    <!-- Botón destacado: Ir al Registro -> -->
                    <button type="submit" class="btn btn-dyl-primary w-100 py-2.5 fw-semibold shadow-sm d-flex align-items-center justify-content-center gap-2">
                        <span>Ir al Registro</span>
                        <i class="bi bi-arrow-right"></i>
                    </button>
                </form>
            </div>

            <div class="pt-3 mt-4 border-top">
                <div class="d-flex align-items-center gap-2 text-muted small" style="font-size: 0.76rem;">
                    <i class="bi bi-info-circle-fill text-indigo-600"></i>
                    <span>Permite llenar las calificaciones masivas de todos los alumnos de un aula simultáneamente.</span>
                </div>
            </div>
        </div>
    </div>

    <!-- MÉTODO 2: "Gestión por Alumno" (Búsqueda Individual) -->
    <div class="col-lg-7">
        <div class="dyl-card p-4 border shadow-xs">
            <div class="d-flex align-items-center gap-3 mb-3">
                <div class="rounded-3 p-2.5" style="background: #ECFEFF; color: #06B6D4;">
                    <i class="bi bi-person-badge-fill fs-4"></i>
                </div>
                <div>
                    <h5 class="fw-bold text-dark mb-0">Gestión por Alumno</h5>
                    <span class="text-muted small">Búsqueda Individual de Estudiantes</span>
                </div>
            </div>

            <!-- Buscador: "Buscar por Nombre o DNI del estudiante..." -->
            <div class="mb-3">
                <div class="input-group">
                    <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                    <input type="text" class="form-control border-start-0 ps-0" placeholder="Buscar por Nombre o DNI del estudiante..." data-table-search="tablaNotasAlumnos">
                </div>
            </div>

            <!-- Lista de Resultados con Foto, Nombre del Alumno y Grado + Botones Libreta / Calificar -->
            <div class="table-responsive" style="max-height: 420px; overflow-y: auto;">
                <table class="table table-hover align-middle mb-0" id="tablaNotasAlumnos">
                    <thead class="table-light sticky-top">
                        <tr class="small text-muted text-uppercase fw-bold">
                            <th class="ps-3">ALUMNO</th>
                            <th>GRADO</th>
                            <th class="text-end pe-3">ACCIONES</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php if (empty($alumnos)): ?>
                            <tr>
                                <td colspan="3" class="text-center py-4 text-muted small">No hay alumnos matriculados registrados.</td>
                            </tr>
                        <?php else: ?>
                            <?php foreach ($alumnos as $a): ?>
                                <tr>
                                    <td class="ps-3">
                                        <div class="d-flex align-items-center gap-2.5">
                                            <div class="dyl-user-avatar" style="width: 36px; height: 36px; font-size: 0.82rem; flex-shrink: 0;">
                                                <?= strtoupper(substr($a['nombres'], 0, 1)) ?>
                                            </div>
                                            <div>
                                                <div class="fw-bold text-dark small mb-0"><?= htmlspecialchars($a['apellidos'] . ', ' . $a['nombres']) ?></div>
                                                <div class="text-muted" style="font-size: 0.72rem;">DNI: <?= htmlspecialchars($a['dni']) ?></div>
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <span class="badge badge-dyl-blue" style="font-size: 0.72rem;">
                                            <?= htmlspecialchars($a['grado_nombre'] . ' "' . $a['seccion_nombre'] . '"') ?>
                                        </span>
                                    </td>
                                    <td class="text-end pe-3">
                                        <div class="d-inline-flex gap-1.5">
                                            <!-- Botón azul: Libreta -->
                                            <a href="<?= url('views/ver_libreta.php?id=' . $a['id']) ?>" class="btn btn-sm btn-dyl-cyan px-2.5 py-1 text-white text-decoration-none shadow-xs fw-semibold" title="Ver e imprimir Libreta Oficial">
                                                <i class="bi bi-file-earmark-bar-graph me-1"></i> Libreta
                                            </a>
                                            <!-- Botón verde: Calificar -->
                                            <a href="<?= url('views/calificar_alumno.php?id=' . $a['id']) ?>" class="btn btn-sm btn-dyl-green px-2.5 py-1 text-white text-decoration-none shadow-xs fw-semibold" title="Calificar materias">
                                                <i class="bi bi-pencil-square me-1"></i> Calificar
                                            </a>
                                        </div>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        <?php endif; ?>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
