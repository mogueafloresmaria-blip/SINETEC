<?php
// views/calificar_alumno.php - Módulo 8: Registro de Notas por Alumno DYL SCHOOL
$pageTitle = 'Registro de Calificaciones';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

$alumnoId = (int)($_GET['id'] ?? 0);

// Si no viene ID, seleccionar el primer alumno matriculado activo
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

// Procesar Guardado de Notas POST (Soporta envío tradicional y AJAX)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'guardar_notas') {
    $notasData = $_POST['notas'] ?? [];
    foreach ($notasData as $cursoId => $valores) {
        $b1 = ($valores['b1'] !== '' && is_numeric($valores['b1'])) ? (float)$valores['b1'] : null;
        $b2 = ($valores['b2'] !== '' && is_numeric($valores['b2'])) ? (float)$valores['b2'] : null;
        $b3 = ($valores['b3'] !== '' && is_numeric($valores['b3'])) ? (float)$valores['b3'] : null;
        $b4 = ($valores['b4'] !== '' && is_numeric($valores['b4'])) ? (float)$valores['b4'] : null;

        // Calcular promedio bimestral
        $suma = 0;
        $count = 0;
        foreach ([$b1, $b2, $b3, $b4] as $v) {
            if ($v !== null) {
                $suma += $v;
                $count++;
            }
        }
        $promedio = ($count > 0) ? round($suma / $count, 1) : null;

        // Verificar si existe registro
        $stmtCheck = $pdo->prepare("SELECT id FROM notas WHERE matricula_id = ? AND curso_id = ?");
        $stmtCheck->execute([$alumno['matricula_id'], $cursoId]);
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
            $ins->execute([$alumno['matricula_id'], $cursoId, $b1, $b2, $b3, $b4, $promedio]);
        }
    }

    if (isset($_POST['is_ajax'])) {
        header('Content-Type: application/json');
        echo json_encode(['status' => 'success', 'message' => 'Guardado automático realizado']);
        exit;
    }

    set_flash('success', '¡Calificaciones actualizadas y promediadas exitosamente!');
    header("Location: " . url("views/calificar_alumno.php?id={$alumnoId}"));
    exit;
}

// Obtener todas las materias y las notas registradas del alumno
$stmtNotas = $pdo->prepare("
    SELECT c.id as curso_id, c.nombre as curso_nombre, c.tipo as curso_tipo,
           n.bimestre_1, n.bimestre_2, n.bimestre_3, n.bimestre_4, n.promedio_final
    FROM cursos c
    LEFT JOIN notas n ON c.id = n.curso_id AND n.matricula_id = ?
    WHERE c.activo = 1
    ORDER BY c.nombre ASC
");
$stmtNotas->execute([$alumno['matricula_id']]);
$materiasNotas = $stmtNotas->fetchAll();
?>

<!-- ENCABEZADO: Foto, Nombre del Estudiante, Grado/Nivel y estado "EN PROCESO" -->
<div class="dyl-card p-4 mb-4 border shadow-xs">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
        <div class="d-flex align-items-center gap-3">
            <div class="dyl-user-avatar" style="width: 60px; height: 60px; font-size: 1.5rem; flex-shrink: 0;">
                <?= strtoupper(substr($alumno['nombres'], 0, 1)) ?>
            </div>
            <div>
                <h4 class="h5 fw-bold text-dark mb-1">
                    <?= htmlspecialchars($alumno['apellidos'] . ', ' . $alumno['nombres']) ?>
                </h4>
                <div class="d-flex align-items-center gap-2 flex-wrap">
                    <span class="badge bg-light text-dark border">DNI: <?= htmlspecialchars($alumno['dni']) ?></span>
                    <span class="badge badge-dyl-blue"><?= htmlspecialchars($alumno['grado_nombre'] . ' - Sec. ' . $alumno['seccion_nombre'] . ' (' . $alumno['grado_nivel'] . ')') ?></span>
                    <span class="badge badge-dyl-amber fw-semibold">EN PROCESO</span>
                </div>
            </div>
        </div>
        <div class="d-flex gap-2">
            <a href="<?= url('views/ver_libreta.php?id=' . $alumnoId) ?>" class="btn btn-dyl-cyan shadow-xs fw-semibold">
                <i class="bi bi-file-earmark-bar-graph me-1"></i> Libreta Oficial
            </a>
            <a href="<?= url('views/notas.php') ?>" class="btn btn-outline-secondary shadow-xs">
                <i class="bi bi-arrow-left me-1"></i> Volver a Notas
            </a>
        </div>
    </div>
</div>

<!-- TABLA DE NOTAS CON CÁLCULO EN TIEMPO REAL Y AUTOGUARDADO -->
<div class="dyl-card p-4 border shadow-xs">
    <form id="formNotasAlumno" method="POST" action="">
        <input type="hidden" name="action" value="guardar_notas">

        <div class="d-flex flex-column flex-sm-row justify-content-between align-items-sm-center gap-2 mb-3">
            <h5 class="fw-bold text-dark mb-0 d-flex align-items-center gap-2">
                <i class="bi bi-card-checklist text-primary"></i>
                Registro Bimestral de Calificaciones (Escala 00 a 20)
            </h5>
            <div class="d-flex align-items-center gap-2">
                <span id="autoSaveIndicator" class="small text-muted" style="display: none;">
                    <i class="bi bi-check2-all text-success"></i> Guardado automático
                </span>
                <button type="submit" class="btn btn-dyl-green px-4 py-2 shadow-sm fw-semibold">
                    <i class="bi bi-floppy-fill me-1"></i> Guardar Calificaciones
                </button>
            </div>
        </div>

        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0" id="tablaNotasInputs">
                <thead class="table-light">
                    <tr class="small text-muted text-uppercase fw-bold text-center">
                        <th class="text-start ps-3" style="min-width: 220px;">CURSO</th>
                        <th style="width: 120px;">I BIM</th>
                        <th style="width: 120px;">II BIM</th>
                        <th style="width: 120px;">III BIM</th>
                        <th style="width: 120px;">IV BIM</th>
                        <th style="width: 140px;">PROM. FINAL</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($materiasNotas as $mn): ?>
                        <?php $cid = $mn['curso_id']; ?>
                        <tr class="fila-nota" data-curso-id="<?= $cid ?>">
                            <td class="ps-3">
                                <span class="fw-bold text-dark small"><?= htmlspecialchars($mn['curso_nombre']) ?></span>
                                <?php if ($mn['curso_tipo'] === 'Oficial'): ?>
                                    <span class="badge badge-dyl-blue ms-1" style="font-size: 0.65rem;">Oficial</span>
                                <?php else: ?>
                                    <span class="badge badge-dyl-purple ms-1" style="font-size: 0.65rem;">Taller</span>
                                <?php endif; ?>
                            </td>
                            <td>
                                <input type="number" step="0.5" min="0" max="20" 
                                       name="notas[<?= $cid ?>][b1]" 
                                       value="<?= $mn['bimestre_1'] !== null ? htmlspecialchars($mn['bimestre_1']) : '' ?>" 
                                       class="form-control form-control-sm text-center fw-bold shadow-none input-bimestre b1-input" 
                                       placeholder="--">
                            </td>
                            <td>
                                <input type="number" step="0.5" min="0" max="20" 
                                       name="notas[<?= $cid ?>][b2]" 
                                       value="<?= $mn['bimestre_2'] !== null ? htmlspecialchars($mn['bimestre_2']) : '' ?>" 
                                       class="form-control form-control-sm text-center fw-bold shadow-none input-bimestre b2-input" 
                                       placeholder="--">
                            </td>
                            <td>
                                <input type="number" step="0.5" min="0" max="20" 
                                       name="notas[<?= $cid ?>][b3]" 
                                       value="<?= $mn['bimestre_3'] !== null ? htmlspecialchars($mn['bimestre_3']) : '' ?>" 
                                       class="form-control form-control-sm text-center fw-bold shadow-none input-bimestre b3-input" 
                                       placeholder="--">
                            </td>
                            <td>
                                <input type="number" step="0.5" min="0" max="20" 
                                       name="notas[<?= $cid ?>][b4]" 
                                       value="<?= $mn['bimestre_4'] !== null ? htmlspecialchars($mn['bimestre_4']) : '' ?>" 
                                       class="form-control form-control-sm text-center fw-bold shadow-none input-bimestre b4-input" 
                                       placeholder="--">
                            </td>
                            <td class="text-center">
                                <?php 
                                    $pf = $mn['promedio_final']; 
                                    $badgeClass = '';
                                    if ($pf !== null) {
                                        $badgeClass = ($pf > 11) ? 'bg-primary' : 'bg-danger';
                                    }
                                ?>
                                <span class="badge <?= $badgeClass ?> px-3 py-1.5 fw-bold font-monospace prom-final-badge" style="font-size: 0.88rem;">
                                    <?= $pf !== null ? number_format($pf, 1) : '--' ?>
                                </span>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>

        <div class="d-flex justify-content-between align-items-center pt-3 mt-3 border-top">
            <div class="small text-muted">
                <span class="badge bg-primary me-1 px-2 py-1">Mayor a 11: Aprobado (Azul)</span>
                <span class="badge bg-danger px-2 py-1">Menor o igual a 10: En Inicio (Rojo)</span>
            </div>
            <button type="submit" class="btn btn-dyl-green px-4 py-2.5 shadow-sm fw-semibold">
                <i class="bi bi-floppy-fill me-1"></i> Guardar Calificaciones
            </button>
        </div>
    </form>
</div>

<!-- SCRIPT DE CÁLCULO EN TIEMPO REAL Y AUTOGUARDADO -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    const filas = document.querySelectorAll('.fila-nota');
    const autoSaveIndicator = document.getElementById('autoSaveIndicator');
    let autoSaveTimeout = null;

    function recalcularFila(fila) {
        const inputs = fila.querySelectorAll('.input-bimestre');
        let suma = 0;
        let count = 0;

        inputs.forEach(input => {
            const val = parseFloat(input.value);
            if (!isNaN(val) && val >= 0 && val <= 20) {
                suma += val;
                count++;
            }
        });

        const badge = fila.querySelector('.prom-final-badge');
        if (count > 0) {
            const prom = (suma / count).toFixed(1);
            badge.textContent = prom;
            badge.classList.remove('bg-primary', 'bg-danger', 'bg-light', 'text-muted');
            if (parseFloat(prom) > 11) {
                badge.classList.add('bg-primary');
            } else {
                badge.classList.add('bg-danger');
            }
        } else {
            badge.textContent = '--';
            badge.className = 'badge px-3 py-1.5 fw-bold font-monospace prom-final-badge';
        }
    }

    filas.forEach(fila => {
        const inputs = fila.querySelectorAll('.input-bimestre');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                // Limit to 0-20
                let val = parseFloat(this.value);
                if (val > 20) this.value = 20;
                if (val < 0) this.value = 0;

                recalcularFila(fila);

                // Debounce auto-save
                clearTimeout(autoSaveTimeout);
                if (autoSaveIndicator) {
                    autoSaveIndicator.style.display = 'inline';
                    autoSaveIndicator.innerHTML = '<span class="spinner-border spinner-border-sm text-primary"></span> Guardando...';
                }
                autoSaveTimeout = setTimeout(guardarAutomatico, 1200);
            });
        });
    });

    function guardarAutomatico() {
        const form = document.getElementById('formNotasAlumno');
        if (!form) return;

        const formData = new FormData(form);
        formData.append('is_ajax', '1');

        fetch(window.location.href, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (autoSaveIndicator) {
                autoSaveIndicator.innerHTML = '<i class="bi bi-check2-all text-success"></i> Guardado automáticamente';
                setTimeout(() => {
                    autoSaveIndicator.style.display = 'none';
                }, 2500);
            }
        })
        .catch(error => {
            if (autoSaveIndicator) {
                autoSaveIndicator.innerHTML = '<i class="bi bi-cloud-check text-muted"></i> Cambios en memoria';
            }
        });
    }
});
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
