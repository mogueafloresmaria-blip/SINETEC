<?php
// views/curso_nuevo.php - Módulo 7: Nueva Materia / Curso DYL SCHOOL
$pageTitle = 'Nuevo Curso';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();
$error = null;

$gradosPrimaria = $pdo->query("SELECT * FROM grados WHERE nivel = 'Primaria' ORDER BY orden ASC")->fetchAll();
$gradosSecundaria = $pdo->query("SELECT * FROM grados WHERE nivel = 'Secundaria' ORDER BY orden ASC")->fetchAll();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
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
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h3 class="h4 fw-bold text-dark mb-1">Registrar Nueva Materia</h3>
        <p class="text-muted small mb-0">Incorpore una nueva asignatura o taller a los grados correspondientes.</p>
    </div>
    <a href="<?= url('views/cursos.php') ?>" class="btn btn-outline-secondary btn-sm px-3 rounded-3">
        <i class="bi bi-arrow-left me-1"></i> Volver a Cursos
    </a>
</div>

<?php if ($error): ?>
    <div class="alert alert-danger rounded-3 py-2 px-3 small mb-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i><?= htmlspecialchars($error) ?>
    </div>
<?php endif; ?>

<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="dyl-card p-4 border shadow-xs">
            <form method="POST" action="">
                <!-- Campo: NOMBRE DE LA MATERIA -->
                <div class="mb-4">
                    <label class="form-label small fw-bold text-dark mb-1">NOMBRE DE LA MATERIA <span class="text-danger">*</span></label>
                    <input type="text" name="nombre" class="form-control form-control-lg fs-6" placeholder="Ej: Razonamiento Matemático" required value="<?= htmlspecialchars($_POST['nombre'] ?? '') ?>">
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
                                    <input type="checkbox" class="btn-check" name="grados[]" id="pg_<?= $gp['id'] ?>" value="<?= $gp['id'] ?>" checked autocomplete="off">
                                    <label class="btn btn-outline-primary btn-sm rounded-pill px-3 py-1 fw-semibold" for="pg_<?= $gp['id'] ?>">
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
                                    <input type="checkbox" class="btn-check" name="grados[]" id="sg_<?= $gs['id'] ?>" value="<?= $gs['id'] ?>" checked autocomplete="off">
                                    <label class="btn btn-outline-primary btn-sm rounded-pill px-3 py-1 fw-semibold" for="sg_<?= $gs['id'] ?>">
                                        <?= htmlspecialchars($gs['nombre']) ?>
                                    </label>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </div>
                </div>

                <!-- Switch activador: Marcar como Taller / Electivo -->
                <div class="form-check form-switch mb-4 p-3 bg-light rounded-3 border">
                    <input class="form-check-input ms-0 me-3" type="checkbox" role="switch" name="es_taller" id="switchTaller">
                    <label class="form-check-label fw-bold text-dark" for="switchTaller">
                        Marcar como Taller / Electivo
                        <span class="d-block small text-muted fw-normal">No requiere promedio bimestral oficial.</span>
                    </label>
                </div>

                <div class="d-flex justify-content-between align-items-center pt-3 border-top">
                    <a href="<?= url('views/cursos.php') ?>" class="btn btn-light px-4">Cancelar</a>
                    <button type="submit" class="btn btn-dyl-primary px-4 py-2.5 fw-semibold shadow-sm">
                        <i class="bi bi-check-circle me-1"></i> Guardar Materia
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
