<?php
// views/comunicados.php - Módulo 11: Gestión de Comunicados DYL SCHOOL
$pageTitle = 'Comunicados Institucionales';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// Acción: Eliminar Comunicado
if (isset($_GET['action']) && $_GET['action'] === 'eliminar' && isset($_GET['id'])) {
    $cid = (int)$_GET['id'];
    $pdo->prepare("DELETE FROM comunicados WHERE id = ?")->execute([$cid]);
    set_flash('success', 'Aviso eliminado correctamente del historial.');
    header('Location: ' . url('views/comunicados.php'));
    exit;
}

// Acción: Publicar Comunicado
$error = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'publicar') {
    $titulo = trim($_POST['titulo'] ?? '');
    $fecha = trim($_POST['fecha'] ?? SYSTEM_DATE);
    $mensaje = trim($_POST['mensaje'] ?? '');
    $audiencia = $_POST['audiencia'] ?? 'Todos';
    $alumnoId = ($audiencia === 'Alumno') ? (int)($_POST['alumno_id'] ?? 0) : null;

    if (empty($titulo) || empty($mensaje)) {
        $error = 'Título y mensaje son obligatorios.';
    } else {
        $stmtIns = $pdo->prepare("INSERT INTO comunicados (titulo, mensaje, fecha, audiencia, alumno_id) VALUES (?, ?, ?, ?, ?)");
        $stmtIns->execute([$titulo, $mensaje, $fecha, $audiencia, $alumnoId]);
        set_flash('success', '¡Aviso institucional publicado con éxito!');
        header('Location: ' . url('views/comunicados.php'));
        exit;
    }
}

// Obtener Alumnos para selector específico
$alumnos = $pdo->query("SELECT id, nombres, apellidos, dni FROM alumnos WHERE estado = 'ACTIVO' ORDER BY apellidos ASC")->fetchAll();

// Historial de Comunicados
$stmtHistorial = $pdo->query("
    SELECT c.*, a.nombres as alum_nombres, a.apellidos as alum_apellidos
    FROM comunicados c
    LEFT JOIN alumnos a ON c.alumno_id = a.id
    ORDER BY c.id DESC
");
$comunicados = $stmtHistorial->fetchAll();
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h3 class="h4 fw-bold text-dark mb-1">Muro de Comunicados Escolares</h3>
        <p class="text-muted small mb-0">Emisión de avisos, circulares institucionales y notificaciones a padres de familia.</p>
    </div>
</div>

<?php if ($error): ?>
    <div class="alert alert-danger rounded-3 py-2 px-3 small mb-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i><?= htmlspecialchars($error) ?>
    </div>
<?php endif; ?>

<div class="row g-4">
    <!-- Panel Izquierdo: Redactor de Aviso -->
    <div class="col-lg-5">
        <div class="dyl-card p-4">
            <h5 class="fw-bold text-dark mb-3 d-flex align-items-center gap-2">
                <i class="bi bi-pencil-square text-primary"></i>
                Redactor de Aviso
            </h5>

            <form method="POST" action="">
                <input type="hidden" name="action" value="publicar">

                <!-- Selección de Audiencia -->
                <div class="mb-3">
                    <label class="form-label small fw-bold text-dark mb-2">Destinatarios</label>
                    <div class="btn-group w-100" role="group">
                        <input type="radio" class="btn-check" name="audiencia" id="aud_todos" value="Todos" checked onchange="toggleAlumnoSelector(false)">
                        <label class="btn btn-outline-primary small fw-bold" for="aud_todos">
                            <i class="bi bi-people-fill me-1"></i> A Todos
                        </label>

                        <input type="radio" class="btn-check" name="audiencia" id="aud_alumno" value="Alumno" onchange="toggleAlumnoSelector(true)">
                        <label class="btn btn-outline-primary small fw-bold" for="aud_alumno">
                            <i class="bi bi-person-fill me-1"></i> Alumno Específico
                        </label>
                    </div>
                </div>

                <!-- Selector Alumno Específico (condicional) -->
                <div class="mb-3" id="wrapperAlumnoSelector" style="display: none;">
                    <label class="form-label small fw-bold text-dark mb-1">Seleccionar Estudiante</label>
                    <select name="alumno_id" class="form-select">
                        <option value="">-- Buscar Alumno --</option>
                        <?php foreach ($alumnos as $al): ?>
                            <option value="<?= $al['id'] ?>">
                                <?= htmlspecialchars($al['apellidos'] . ', ' . $al['nombres'] . ' (DNI: ' . $al['dni'] . ')') ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>

                <!-- Título -->
                <div class="mb-3">
                    <label class="form-label small fw-bold text-dark mb-1">Título del Aviso <span class="text-danger">*</span></label>
                    <input type="text" name="titulo" class="form-control" placeholder="Ej. Suspensión de actividades por feriado" required>
                </div>

                <!-- Fecha -->
                <div class="mb-3">
                    <label class="form-label small fw-bold text-dark mb-1">Fecha de Publicación</label>
                    <input type="date" name="fecha" class="form-control" value="2026-01-09">
                </div>

                <!-- Mensaje -->
                <div class="mb-4">
                    <label class="form-label small fw-bold text-dark mb-1">Mensaje <span class="text-danger">*</span></label>
                    <textarea name="mensaje" rows="4" class="form-control" placeholder="Escriba el contenido del comunicado aquí..." required></textarea>
                </div>

                <button type="submit" class="btn btn-dyl-primary w-100 py-2.5">
                    <i class="bi bi-send-fill me-1"></i> Publicar
                </button>
            </form>
        </div>
    </div>

    <!-- Panel Derecho: Historial de Avisos -->
    <div class="col-lg-7">
        <div class="dyl-card p-4">
            <h5 class="fw-bold text-dark mb-3 d-flex align-items-center gap-2">
                <i class="bi bi-clock-history text-secondary"></i>
                Historial de Avisos Publicados
            </h5>

            <?php if (empty($comunicados)): ?>
                <div class="text-center py-5 text-muted small">No hay avisos registrados en el sistema.</div>
            <?php else: ?>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr class="small text-muted text-uppercase fw-bold">
                                <th style="width: 110px;">FECHA</th>
                                <th>DETALLE DEL AVISO</th>
                                <th style="width: 140px;">DESTINATARIO</th>
                                <th class="text-end" style="width: 50px;"></th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($comunicados as $c): ?>
                                <tr>
                                    <td class="small text-muted font-monospace">
                                        <?= date('d/m/Y', strtotime($c['fecha'])) ?>
                                    </td>
                                    <td>
                                        <div class="fw-bold text-dark small mb-1"><?= htmlspecialchars($c['titulo']) ?></div>
                                        <div class="text-muted small text-truncate" style="max-width: 280px; font-size: 0.74rem;">
                                            <?= htmlspecialchars($c['mensaje']) ?>
                                        </div>
                                    </td>
                                    <td>
                                        <?php if ($c['audiencia'] === 'Todos'): ?>
                                            <span class="badge badge-dyl-purple">Todos</span>
                                        <?php else: ?>
                                            <span class="badge badge-dyl-blue text-truncate" style="max-width: 130px;">
                                                <?= htmlspecialchars($c['alum_nombres'] . ' ' . $c['alum_apellidos']) ?>
                                            </span>
                                        <?php endif; ?>
                                    </td>
                                    <td class="text-end">
                                        <a href="?action=eliminar&id=<?= $c['id'] ?>" class="btn btn-sm btn-outline-danger p-1 rounded-2 shadow-xs" title="Borrar comunicado" onclick="return confirm('¿Borrar este comunicado?')">
                                            <i class="bi bi-x-lg"></i>
                                        </a>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>

                    </table>
                </div>
            <?php endif; ?>
        </div>
    </div>
</div>

<script>
function toggleAlumnoSelector(show) {
    document.getElementById('wrapperAlumnoSelector').style.display = show ? 'block' : 'none';
}
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
