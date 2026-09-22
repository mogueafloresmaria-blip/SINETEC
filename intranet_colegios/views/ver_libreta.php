<?php
// views/ver_libreta.php - Módulo 8: Libreta Oficial de Calificaciones DYL SCHOOL
$pageTitle = 'Libreta de Calificaciones';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

$alumnoId = (int)($_GET['id'] ?? 0);
if ($alumnoId <= 0) {
    $first = $pdo->query("SELECT a.id FROM alumnos a JOIN matriculas m ON a.id = m.alumno_id WHERE a.estado = 'ACTIVO' AND m.anio_lectivo = 2026 LIMIT 1")->fetchColumn();
    $alumnoId = (int)$first;
}

$stmtAlumno = $pdo->prepare("
    SELECT a.*, m.id as matricula_id, g.nombre as grado_nombre, g.nivel as grado_nivel, s.nombre as seccion_nombre
    FROM alumnos a
    JOIN matriculas m ON a.id = m.alumno_id
    JOIN grados g ON m.grado_id = g.id
    JOIN secciones s ON m.seccion_id = s.id
    WHERE a.id = ? AND m.anio_lectivo = 2026
");
$stmtAlumno->execute([$alumnoId]);
$alumno = $stmtAlumno->fetch();

if (!$alumno) {
    set_flash('error', 'El alumno seleccionado no cuenta con matrícula activa para el periodo 2026.');
    header('Location: ' . url('views/notas.php'));
    exit;
}

$stmtNotas = $pdo->prepare("
    SELECT c.nombre as curso_nombre, c.tipo as curso_tipo,
           n.bimestre_1, n.bimestre_2, n.bimestre_3, n.bimestre_4, n.promedio_final
    FROM cursos c
    LEFT JOIN notas n ON c.id = n.curso_id AND n.matricula_id = ?
    WHERE c.activo = 1
    ORDER BY c.nombre ASC
");
$stmtNotas->execute([$alumno['matricula_id']]);
$notas = $stmtNotas->fetchAll();

// Promedio general de todas las materias
$sumaPromedios = 0;
$totalMateriasEvaluadas = 0;
foreach ($notas as $n) {
    if ($n['promedio_final'] !== null) {
        $sumaPromedios += (float)$n['promedio_final'];
        $totalMateriasEvaluadas++;
    }
}
$promedioGeneral = ($totalMateriasEvaluadas > 0) ? round($sumaPromedios / $totalMateriasEvaluadas, 2) : 0;
?>

<!-- Barra de Acción Superior (No Imprimible) -->
<div class="d-flex justify-content-between align-items-center mb-4 no-print">
    <div>
        <h3 class="h4 fw-bold text-dark mb-1">Libreta Oficial de Información Académica</h3>
        <p class="text-muted small mb-0">Periodo Lectivo <?= SYSTEM_YEAR ?> · Sede Central DYL SCHOOL</p>
    </div>
    <div class="d-flex gap-2">
        <a href="<?= url('views/calificar_alumno.php?id=' . $alumnoId) ?>" class="btn btn-outline-primary shadow-xs">
            <i class="bi bi-pencil-square me-1"></i> Calificar
        </a>
        <button onclick="window.print()" class="btn btn-dyl-primary shadow-xs">
            <i class="bi bi-printer-fill me-1"></i> Imprimir Libreta
        </button>
        <a href="<?= url('views/notas.php') ?>" class="btn btn-outline-secondary shadow-xs">
            <i class="bi bi-arrow-left me-1"></i> Volver
        </a>
    </div>
</div>

<!-- Contenedor Oficial de Libreta para Visualización e Impresión -->
<div class="dyl-card p-0 overflow-hidden shadow-sm border" style="max-width: 920px; margin: 0 auto; background: #FFFFFF;">
    <!-- Membrete con Degradado Morado / Azul -->
    <div class="p-4 text-white position-relative" style="background: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);">
        <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center gap-3">
                <div class="rounded-3 p-2.5 bg-white text-indigo-700 shadow-sm" style="font-size: 28px; width: 56px; height: 56px; display: flex; align-items: center; justify-content: center;">
                    <i class="bi bi-mortarboard-fill"></i>
                </div>
                <div>
                    <h2 class="h4 fw-bold mb-0 text-white" style="letter-spacing: 0.5px;">DYL SCHOOL</h2>
                    <span class="text-white text-opacity-80 small">Colegio de Educación Primaria y Secundaria de Excelencia</span>
                </div>
            </div>
            <div class="text-end">
                <span class="badge bg-white bg-opacity-20 text-white border border-white border-opacity-25 px-3 py-1.5 fw-bold font-monospace fs-6">
                    AÑO ESCOLAR 2026
                </span>
            </div>
        </div>
    </div>

    <!-- Ficha del Estudiante -->
    <div class="p-4 bg-light border-bottom">
        <div class="row g-3">
            <div class="col-md-5">
                <span class="small text-muted fw-bold text-uppercase d-block" style="font-size: 0.72rem;">ESTUDIANTE</span>
                <div class="fw-bold text-dark fs-5"><?= htmlspecialchars($alumno['apellidos'] . ', ' . $alumno['nombres']) ?></div>
            </div>
            <div class="col-md-3">
                <span class="small text-muted fw-bold text-uppercase d-block" style="font-size: 0.72rem;">DNI / CÓDIGO</span>
                <div class="fw-bold text-dark font-monospace fs-6"><?= htmlspecialchars($alumno['dni']) ?></div>
            </div>
            <div class="col-md-4">
                <span class="small text-muted fw-bold text-uppercase d-block" style="font-size: 0.72rem;">GRADO, SECCIÓN Y NIVEL</span>
                <div class="fw-bold text-dark fs-6"><?= htmlspecialchars($alumno['grado_nombre'] . ' "' . $alumno['seccion_nombre'] . '" (' . $alumno['grado_nivel'] . ')') ?></div>
            </div>
        </div>
    </div>

    <!-- Tabla Limpia Consolidada de Notas -->
    <div class="p-4">
        <div class="table-responsive">
            <table class="table table-bordered align-middle text-center mb-0">
                <thead class="table-light">
                    <tr class="small text-uppercase text-dark fw-bold">
                        <th class="text-start ps-3" style="width: 40%;">ÁREA / CURSO CURRICULAR</th>
                        <th style="width: 12%;">I BIM</th>
                        <th style="width: 12%;">II BIM</th>
                        <th style="width: 12%;">III BIM</th>
                        <th style="width: 12%;">IV BIM</th>
                        <th style="width: 12%; background: #EEF2FF; color: #4338CA;">PROM. FINAL</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($notas as $n): ?>
                        <tr>
                            <td class="text-start ps-3">
                                <span class="fw-semibold text-dark small"><?= htmlspecialchars($n['curso_nombre']) ?></span>
                                <span class="text-muted small ms-1">(<?= $n['curso_tipo'] ?>)</span>
                            </td>
                            <td class="font-monospace <?= ($n['bimestre_1'] !== null && $n['bimestre_1'] <= 10) ? 'text-danger fw-bold' : 'text-dark' ?>">
                                <?= $n['bimestre_1'] !== null ? number_format($n['bimestre_1'], 0) : '-' ?>
                            </td>
                            <td class="font-monospace <?= ($n['bimestre_2'] !== null && $n['bimestre_2'] <= 10) ? 'text-danger fw-bold' : 'text-dark' ?>">
                                <?= $n['bimestre_2'] !== null ? number_format($n['bimestre_2'], 0) : '-' ?>
                            </td>
                            <td class="font-monospace <?= ($n['bimestre_3'] !== null && $n['bimestre_3'] <= 10) ? 'text-danger fw-bold' : 'text-dark' ?>">
                                <?= $n['bimestre_3'] !== null ? number_format($n['bimestre_3'], 0) : '-' ?>
                            </td>
                            <td class="font-monospace <?= ($n['bimestre_4'] !== null && $n['bimestre_4'] <= 10) ? 'text-danger fw-bold' : 'text-dark' ?>">
                                <?= $n['bimestre_4'] !== null ? number_format($n['bimestre_4'], 0) : '-' ?>
                            </td>
                            <td style="background: #F8FAFC;">
                                <?php if ($n['promedio_final'] !== null): ?>
                                    <span class="fw-bold font-monospace <?= $n['promedio_final'] > 11 ? 'text-primary' : 'text-danger' ?>">
                                        <?= number_format($n['promedio_final'], 1) ?>
                                    </span>
                                <?php else: ?>
                                    <span class="text-muted small">-</span>
                                <?php endif; ?>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
                <tfoot class="table-light">
                    <tr class="fw-bold">
                        <td class="text-end pe-3 text-uppercase">PROMEDIO PONDERADO GENERAL:</td>
                        <td colspan="4"></td>
                        <td class="fs-6 font-monospace <?= $promedioGeneral > 11 ? 'text-primary' : 'text-danger' ?>">
                            <?= number_format($promedioGeneral, 2) ?>
                        </td>
                    </tr>
                </tfoot>
            </table>
        </div>

        <!-- Escala e Interpretación -->
        <div class="row g-3 mt-4 pt-3 border-top">
            <div class="col-md-6">
                <span class="small fw-bold text-muted text-uppercase d-block mb-1">ESCALA VIGENTE</span>
                <span class="badge badge-dyl-green me-1">18 - 20 Destacado</span>
                <span class="badge badge-dyl-blue me-1">14 - 17 Logrado</span>
                <span class="badge badge-dyl-amber me-1">11 - 13 Proceso</span>
                <span class="badge badge-dyl-red">00 - 10 En Inicio</span>
            </div>
            <div class="col-md-6 text-md-end text-muted small">
                <p class="mb-0">Expedido por Dirección Académica · DYL SCHOOL</p>
                <p class="mb-0">Fecha de emisión: <?= SYSTEM_DATE ?></p>
            </div>
        </div>
    </div>
</div>

<!-- BOTÓN FLOTANTE: "Imprimir Libreta" -->
<button onclick="window.print()" class="btn btn-dyl-primary btn-lg rounded-pill shadow-lg no-print d-flex align-items-center gap-2" 
        style="position: fixed; bottom: 28px; right: 28px; z-index: 1050; padding: 12px 24px; box-shadow: 0 8px 24px rgba(79, 70, 229, 0.45) !important;">
    <i class="bi bi-printer-fill fs-5"></i>
    <span class="fw-bold">Imprimir Libreta</span>
</button>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
