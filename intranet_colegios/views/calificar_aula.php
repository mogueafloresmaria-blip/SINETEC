<?php
// views/calificar_aula.php - Módulo 8: Sábana de Notas por Aula y Curso DYL SCHOOL
$pageTitle = 'Acta de Calificaciones por Aula';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// Extraer parámetros de entrada
$aulaSeccion = $_GET['aula_seccion'] ?? '';
$parts = explode('_', $aulaSeccion);
$gradoId = (int)($parts[0] ?? 0);
$seccionId = (int)($parts[1] ?? 0);
$cursoId = (int)($_GET['curso_id'] ?? 0);

if ($gradoId <= 0 || $seccionId <= 0 || $cursoId <= 0) {
    // Si no vienen parámetros, seleccionar primer grado, sección y curso válidos
    $firstGrado = $pdo->query("SELECT id FROM grados ORDER BY orden ASC LIMIT 1")->fetchColumn() ?: 7;
    $gradoId = (int)$firstGrado;
    $seccionId = 1;
    $cursoId = 1;
}

// Obtener datos del Grado, Sección y Curso
$stmtG = $pdo->prepare("SELECT * FROM grados WHERE id = ?");
$stmtG->execute([$gradoId]);
$grado = $stmtG->fetch();

$stmtS = $pdo->prepare("SELECT * FROM secciones WHERE id = ?");
$stmtS->execute([$seccionId]);
$seccion = $stmtS->fetch();

$stmtC = $pdo->prepare("SELECT * FROM cursos WHERE id = ?");
$stmtC->execute([$cursoId]);
$curso = $stmtC->fetch();

// Procesar Guardado Masivo de Notas POST
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'guardar_acta') {
    $actaData = $_POST['alumnos_notas'] ?? [];
    foreach ($actaData as $matriculaId => $valores) {
        $matId = (int)$matriculaId;
        $b1 = ($valores['b1'] !== '' && is_numeric($valores['b1'])) ? (float)$valores['b1'] : null;
        $b2 = ($valores['b2'] !== '' && is_numeric($valores['b2'])) ? (float)$valores['b2'] : null;
        $b3 = ($valores['b3'] !== '' && is_numeric($valores['b3'])) ? (float)$valores['b3'] : null;
        $b4 = ($valores['b4'] !== '' && is_numeric($valores['b4'])) ? (float)$valores['b4'] : null;

        $suma = 0;
        $count = 0;
        foreach ([$b1, $b2, $b3, $b4] as $v) {
            if ($v !== null) {
                $suma += $v;
                $count++;
            }
        }
        $promedio = ($count > 0) ? round($suma / $count, 1) : null;

        $stmtCheck = $pdo->prepare("SELECT id FROM notas WHERE matricula_id = ? AND curso_id = ?");
        $stmtCheck->execute([$matId, $cursoId]);
        $notaExistente = $stmtCheck->fetch();

        if ($notaExistente) {
            $upd = $pdo->prepare("
                UPDATE notas 
                SET bimestre_1 = ?, bimestre_2 = ?, bimestre_3 = ?, bimestre_4 = ?, promedio_final = ?
                WHERE id = ?
            ");
            $upd->execute([$b1, $b2, $b3, $b4, $promedio, $notaExistente['id']]);
        } else {
            $ins = $pdo->prepare("
                INSERT INTO notas (matricula_id, curso_id, bimestre_1, bimestre_2, bimestre_3, bimestre_4, promedio_final)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ");
            $ins->execute([$matId, $cursoId, $b1, $b2, $b3, $b4, $promedio]);
        }
    }

    if (isset($_POST['is_ajax'])) {
        header('Content-Type: application/json');
        echo json_encode(['status' => 'success', 'message' => 'Acta guardada']);
        exit;
    }

    set_flash('success', '¡Acta de calificaciones actualizada exitosamente!');
    header("Location: " . url("views/calificar_aula.php?aula_seccion={$gradoId}_{$seccionId}&curso_id={$cursoId}"));
    exit;
}

// Obtener alumnos matriculados en esta aula y sus notas en el curso
$stmtAlumnosAula = $pdo->prepare("
    SELECT a.id as alumno_id, a.nombres, a.apellidos, a.dni, a.foto,
           m.id as matricula_id,
           n.bimestre_1, n.bimestre_2, n.bimestre_3, n.bimestre_4, n.promedio_final
    FROM matriculas m
    JOIN alumnos a ON m.alumno_id = a.id
    LEFT JOIN notas n ON n.matricula_id = m.id AND n.curso_id = ?
    WHERE m.grado_id = ? AND m.seccion_id = ? AND m.anio_lectivo = 2026
    ORDER BY a.apellidos ASC, a.nombres ASC
");
$stmtAlumnosAula->execute([$cursoId, $gradoId, $seccionId]);
$alumnosAula = $stmtAlumnosAula->fetchAll();
?>

<!-- Encabezado del Acta de Aula -->
<div class="dyl-card p-4 mb-4 border shadow-xs">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
        <div>
            <div class="d-flex align-items-center gap-2 mb-1">
                <span class="badge badge-dyl-blue fw-bold fs-6">
                    <?= htmlspecialchars($grado['nombre'] ?? 'Aula') ?> - Sección "<?= htmlspecialchars($seccion['nombre'] ?? 'A') ?>"
                </span>
                <span class="badge bg-light text-dark border font-monospace">NIVEL <?= strtoupper($grado['nivel'] ?? 'SECUNDARIA') ?></span>
                <span class="badge badge-dyl-purple"><?= htmlspecialchars($curso['tipo'] ?? 'Oficial') ?></span>
            </div>
            <h4 class="h5 fw-bold text-dark mb-0">
                Materia: <?= htmlspecialchars($curso['nombre'] ?? 'Curso') ?>
            </h4>
        </div>
        <div class="d-flex gap-2">
            <a href="<?= url('views/notas.php') ?>" class="btn btn-outline-secondary shadow-xs">
                <i class="bi bi-arrow-left me-1"></i> Volver a Métodos
            </a>
        </div>
    </div>
</div>

<!-- Sábana Completa de Notas de Todos los Alumnos del Salón -->
<div class="dyl-card p-4 border shadow-xs">
    <form id="formActaAula" method="POST" action="">
        <input type="hidden" name="action" value="guardar_acta">

        <div class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-2 mb-3">
            <div>
                <h5 class="fw-bold text-dark mb-0">Sábana Oficial de Notas (<?= count($alumnosAula) ?> Estudiantes)</h5>
                <span class="text-muted small">Cálculo de promedio bimestral en tiempo real.</span>
            </div>
            <div class="d-flex align-items-center gap-2">
                <span id="autoSaveIndicatorAula" class="small text-muted" style="display: none;">
                    <i class="bi bi-check2-all text-success"></i> Guardado
                </span>
                <button type="submit" class="btn btn-dyl-green px-4 py-2 shadow-sm fw-semibold">
                    <i class="bi bi-floppy-fill me-1"></i> Guardar Acta Completa
                </button>
            </div>
        </div>

        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0" id="tablaActaNotas">
                <thead class="table-light">
                    <tr class="small text-muted text-uppercase fw-bold text-center">
                        <th style="width: 50px;">#</th>
                        <th class="text-start ps-3" style="min-width: 240px;">ALUMNO / ESTUDIANTE</th>
                        <th style="width: 120px;">DNI</th>
                        <th style="width: 110px;">I BIM</th>
                        <th style="width: 110px;">II BIM</th>
                        <th style="width: 110px;">III BIM</th>
                        <th style="width: 110px;">IV BIM</th>
                        <th style="width: 130px;">PROM. FINAL</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($alumnosAula)): ?>
                        <tr>
                            <td colspan="8" class="text-center py-5 text-muted small">
                                <i class="bi bi-person-x fs-3 d-block mb-2 text-slate-300"></i>
                                No hay alumnos matriculados en esta aula para el periodo 2026.
                            </td>
                        </tr>
                    <?php else: ?>
                        <?php foreach ($alumnosAula as $idx => $al): ?>
                            <?php $mId = $al['matricula_id']; ?>
                            <tr class="fila-acta" data-matricula-id="<?= $mId ?>">
                                <td class="text-center font-monospace text-muted small"><?= $idx + 1 ?></td>
                                <td class="ps-3">
                                    <div class="d-flex align-items-center gap-2">
                                        <div class="dyl-user-avatar" style="width: 32px; height: 32px; font-size: 0.78rem;">
                                            <?= strtoupper(substr($al['nombres'], 0, 1)) ?>
                                        </div>
                                        <div>
                                            <div class="fw-bold text-dark small mb-0"><?= htmlspecialchars($al['apellidos'] . ', ' . $al['nombres']) ?></div>
                                        </div>
                                    </div>
                                </td>
                                <td class="text-center font-monospace small text-muted"><?= htmlspecialchars($al['dni']) ?></td>
                                <td>
                                    <input type="number" step="0.5" min="0" max="20" 
                                           name="alumnos_notas[<?= $mId ?>][b1]" 
                                           value="<?= $al['bimestre_1'] !== null ? htmlspecialchars($al['bimestre_1']) : '' ?>" 
                                           class="form-control form-control-sm text-center fw-bold shadow-none input-bimestre-aula" 
                                           placeholder="--">
                                </td>
                                <td>
                                    <input type="number" step="0.5" min="0" max="20" 
                                           name="alumnos_notas[<?= $mId ?>][b2]" 
                                           value="<?= $al['bimestre_2'] !== null ? htmlspecialchars($al['bimestre_2']) : '' ?>" 
                                           class="form-control form-control-sm text-center fw-bold shadow-none input-bimestre-aula" 
                                           placeholder="--">
                                </td>
                                <td>
                                    <input type="number" step="0.5" min="0" max="20" 
                                           name="alumnos_notas[<?= $mId ?>][b3]" 
                                           value="<?= $al['bimestre_3'] !== null ? htmlspecialchars($al['bimestre_3']) : '' ?>" 
                                           class="form-control form-control-sm text-center fw-bold shadow-none input-bimestre-aula" 
                                           placeholder="--">
                                </td>
                                <td>
                                    <input type="number" step="0.5" min="0" max="20" 
                                           name="alumnos_notas[<?= $mId ?>][b4]" 
                                           value="<?= $al['bimestre_4'] !== null ? htmlspecialchars($al['bimestre_4']) : '' ?>" 
                                           class="form-control form-control-sm text-center fw-bold shadow-none input-bimestre-aula" 
                                           placeholder="--">
                                </td>
                                <td class="text-center">
                                    <?php 
                                        $pf = $al['promedio_final']; 
                                        $badgeClass = '';
                                        if ($pf !== null) {
                                            $badgeClass = ($pf > 11) ? 'bg-primary' : 'bg-danger';
                                        }
                                    ?>
                                    <span class="badge <?= $badgeClass ?> px-3 py-1.5 fw-bold font-monospace prom-final-acta" style="font-size: 0.88rem;">
                                        <?= $pf !== null ? number_format($pf, 1) : '--' ?>
                                    </span>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>

        <div class="d-flex justify-content-between align-items-center pt-3 mt-3 border-top">
            <div class="small text-muted">
                <span class="badge bg-primary me-1 px-2 py-1">Mayor a 11: Aprobado (Azul)</span>
                <span class="badge bg-danger px-2 py-1">Menor o igual a 10: En Inicio (Rojo)</span>
            </div>
            <button type="submit" class="btn btn-dyl-green px-4 py-2.5 shadow-sm fw-semibold">
                <i class="bi bi-floppy-fill me-1"></i> Guardar Acta Completa
            </button>
        </div>
    </form>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const filas = document.querySelectorAll('.fila-acta');

    function recalcularFila(fila) {
        const inputs = fila.querySelectorAll('.input-bimestre-aula');
        let suma = 0;
        let count = 0;

        inputs.forEach(input => {
            const val = parseFloat(input.value);
            if (!isNaN(val) && val >= 0 && val <= 20) {
                suma += val;
                count++;
            }
        });

        const badge = fila.querySelector('.prom-final-acta');
        if (count > 0) {
            const prom = (suma / count).toFixed(1);
            badge.textContent = prom;
            badge.classList.remove('bg-primary', 'bg-danger');
            if (parseFloat(prom) > 11) {
                badge.classList.add('bg-primary');
            } else {
                badge.classList.add('bg-danger');
            }
        } else {
            badge.textContent = '--';
            badge.className = 'badge px-3 py-1.5 fw-bold font-monospace prom-final-acta';
        }
    }

    filas.forEach(fila => {
        const inputs = fila.querySelectorAll('.input-bimestre-aula');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                let val = parseFloat(this.value);
                if (val > 20) this.value = 20;
                if (val < 0) this.value = 0;
                recalcularFila(fila);
            });
        });
    });
});
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
