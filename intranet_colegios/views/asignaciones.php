<?php
// views/asignaciones.php - Módulo 6: Carga Académica DYL SCHOOL
$pageTitle = 'Carga Académica';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// Acción: Eliminar asignación
if (isset($_GET['action']) && $_GET['action'] === 'eliminar' && isset($_GET['id'])) {
    $asigId = (int)$_GET['id'];
    $pdo->prepare("DELETE FROM asignaciones WHERE id = ?")->execute([$asigId]);
    set_flash('success', 'Asignación académica retirada correctamente.');
    header('Location: ' . url('views/asignaciones.php'));
    exit;
}

// Acción: Crear Asignación
$error = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'asignar') {
    $profesor_id = (int)($_POST['profesor_id'] ?? 0);
    $curso_id = (int)($_POST['curso_id'] ?? 0);
    $grado_id = (int)($_POST['grado_id'] ?? 0);
    $seccion_id = (int)($_POST['seccion_id'] ?? 0);

    if ($profesor_id <= 0 || $curso_id <= 0 || $grado_id <= 0 || $seccion_id <= 0) {
        $error = 'Todos los campos son obligatorios para asignar la carga académica.';
    } else {
        // Verificar si ya existe asignación idéntica
        $stmtCheck = $pdo->prepare("SELECT id FROM asignaciones WHERE profesor_id = ? AND curso_id = ? AND grado_id = ? AND seccion_id = ? AND anio_lectivo = 2026");
        $stmtCheck->execute([$profesor_id, $curso_id, $grado_id, $seccion_id]);
        if ($stmtCheck->fetch()) {
            $error = 'Esta asignación ya se encuentra registrada para el periodo 2026.';
        } else {
            $stmtIns = $pdo->prepare("INSERT INTO asignaciones (profesor_id, curso_id, grado_id, seccion_id, anio_lectivo) VALUES (?, ?, ?, ?, 2026)");
            $stmtIns->execute([$profesor_id, $curso_id, $grado_id, $seccion_id]);
            set_flash('success', '¡Carga académica asignada exitosamente!');
            header('Location: ' . url('views/asignaciones.php'));
            exit;
        }
    }
}

// Datos para el formulario
$profesores = $pdo->query("SELECT id, nombres, apellidos, dni, foto FROM profesores WHERE estado = 'ACTIVO' ORDER BY apellidos ASC, nombres ASC")->fetchAll();
$cursos = $pdo->query("SELECT id, nombre, tipo FROM cursos WHERE activo = 1 ORDER BY nombre ASC")->fetchAll();
$grados = $pdo->query("SELECT id, nombre, nivel, orden FROM grados ORDER BY orden ASC")->fetchAll();
$secciones = $pdo->query("SELECT id, nombre FROM secciones ORDER BY nombre ASC")->fetchAll();

// Carga asignada organizada por nivel
$stmtAsigPrimaria = $pdo->query("
    SELECT asig.id, p.id as prof_id, p.nombres as prof_nombres, p.apellidos as prof_apellidos, p.foto as prof_foto,
           c.nombre as curso_nombre, c.tipo as curso_tipo, g.nombre as grado_nombre, s.nombre as seccion_nombre
    FROM asignaciones asig
    JOIN profesores p ON asig.profesor_id = p.id
    JOIN cursos c ON asig.curso_id = c.id
    JOIN grados g ON asig.grado_id = g.id
    JOIN secciones s ON asig.seccion_id = s.id
    WHERE g.nivel = 'Primaria' AND asig.anio_lectivo = 2026
    ORDER BY g.orden ASC, c.nombre ASC
");
$asigPrimaria = $stmtAsigPrimaria->fetchAll();

$stmtAsigSecundaria = $pdo->query("
    SELECT asig.id, p.id as prof_id, p.nombres as prof_nombres, p.apellidos as prof_apellidos, p.foto as prof_foto,
           c.nombre as curso_nombre, c.tipo as curso_tipo, g.nombre as grado_nombre, s.nombre as seccion_nombre
    FROM asignaciones asig
    JOIN profesores p ON asig.profesor_id = p.id
    JOIN cursos c ON asig.curso_id = c.id
    JOIN grados g ON asig.grado_id = g.id
    JOIN secciones s ON asig.seccion_id = s.id
    WHERE g.nivel = 'Secundaria' AND asig.anio_lectivo = 2026
    ORDER BY g.orden ASC, c.nombre ASC
");
$asigSecundaria = $stmtAsigSecundaria->fetchAll();

$stmtAsigInicial = $pdo->query("
    SELECT asig.id, p.id as prof_id, p.nombres as prof_nombres, p.apellidos as prof_apellidos, p.foto as prof_foto,
           c.nombre as curso_nombre, c.tipo as curso_tipo, g.nombre as grado_nombre, s.nombre as seccion_nombre
    FROM asignaciones asig
    JOIN profesores p ON asig.profesor_id = p.id
    JOIN cursos c ON asig.curso_id = c.id
    JOIN grados g ON asig.grado_id = g.id
    JOIN secciones s ON asig.seccion_id = s.id
    WHERE g.nivel = 'Inicial' AND asig.anio_lectivo = 2026
    ORDER BY g.orden ASC, c.nombre ASC
");
$asigInicial = $stmtAsigInicial->fetchAll();

function get_foto_docente(?string $foto, int $id): string {
    if (!empty($foto) && file_exists(__DIR__ . '/../assets/img/' . $foto)) {
        return asset('img/' . $foto);
    }
    $defaults = ['docente1.jpg', 'docente2.jpg', 'docente3.jpg'];
    $idx = $id % count($defaults);
    return asset('img/' . $defaults[$idx]);
}
?>

<!-- TÍTULO Y DESCRIPCIÓN DE CABECERA -->
<div class="mb-4">
    <h3 class="fw-bold text-dark mb-1" style="font-size: 1.45rem;">Carga Académica</h3>
    <p class="text-muted small mb-0">Gestión de cursos y docentes.</p>
</div>

<?php if ($error): ?>
    <div class="alert alert-danger rounded-3 py-2 px-3 small mb-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i><?= htmlspecialchars($error) ?>
    </div>
<?php endif; ?>

<!-- ESTRUCTURA PRINCIPAL DE 2 COLUMNAS -->
<div class="row g-4 align-items-start">
    <!-- COLUMNA IZQUIERDA: Formulario Nueva Asignación -->
    <div class="col-lg-4">
        <div class="card border-0 shadow-xs" style="background: #FFFFFF; border-radius: 14px; border: 1px solid #E2E8F0 !important;">
            <div class="card-body p-4">
                <!-- Título con icono de más en círculo púrpura -->
                <div class="d-flex align-items-center gap-2 mb-4">
                    <span class="d-inline-flex align-items-center justify-content-center text-white rounded-circle" style="width: 22px; height: 22px; background: #6366F1; font-size: 13px;">
                        <i class="bi bi-plus-lg"></i>
                    </span>
                    <h5 class="fw-bold text-dark mb-0" style="font-size: 1.05rem;">Nueva Asignación</h5>
                </div>

                <form method="POST" action="">
                    <input type="hidden" name="action" value="asignar">

                    <!-- 1. SELECCIONA DOCENTE -->
                    <div class="mb-3">
                        <label class="form-label text-muted fw-bold small text-uppercase mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">1. SELECCIONA DOCENTE</label>
                        <select name="profesor_id" class="form-select bg-white" style="border-radius: 8px; border-color: #E2E8F0; font-size: 0.88rem; height: 42px;" required>
                            <option value="">-- Seleccionar Docente --</option>
                            <?php foreach ($profesores as $p): ?>
                                <option value="<?= $p['id'] ?>">
                                    <?= htmlspecialchars($p['apellidos'] . ', ' . $p['nombres']) ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </div>

                    <!-- 2. FILTRAR POR NIVEL -->
                    <div class="mb-3">
                        <label class="form-label text-muted fw-bold small text-uppercase mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">2. FILTRAR POR NIVEL</label>
                        <select id="filtroNivelAsignacion" class="form-select bg-white" style="border-radius: 8px; border-color: #E2E8F0; font-size: 0.88rem; height: 42px;" onchange="filtrarGradosPorNivelAsig(this.value)">
                            <option value="">-- Seleccionar Nivel --</option>
                            <option value="Primaria">Primaria</option>
                            <option value="Secundaria">Secundaria</option>
                            <option value="Inicial">Inicial</option>
                        </select>
                    </div>

                    <!-- 3. SELECCIONAR GRADO -->
                    <div class="mb-3">
                        <label class="form-label text-muted fw-bold small text-uppercase mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">3. SELECCIONAR GRADO</label>
                        <select name="grado_id" id="selectGradoAsignacion" class="form-select bg-white" style="border-radius: 8px; border-color: #E2E8F0; font-size: 0.88rem; height: 42px;" required>
                            <option value="">-- Seleccionar Grado --</option>
                            <?php foreach ($grados as $g): ?>
                                <option value="<?= $g['id'] ?>" data-nivel="<?= $g['nivel'] ?>">
                                    <?= htmlspecialchars($g['nombre']) ?>
                                </option>
                            <?php endforeach; ?>
                        </select>
                    </div>

                    <!-- 4. SELECCIONAR CURSO -->
                    <div class="mb-3">
                        <label class="form-label text-muted fw-bold small text-uppercase mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">4. SELECCIONAR CURSO</label>
                        <select name="curso_id" class="form-select bg-white" style="border-radius: 8px; border-color: #E2E8F0; font-size: 0.88rem; height: 42px;" required>
                            <option value="">-- Seleccionar Curso --</option>
                            <?php foreach ($cursos as $c): ?>
                                <option value="<?= $c['id'] ?>"><?= htmlspecialchars($c['nombre']) ?></option>
                            <?php endforeach; ?>
                        </select>
                    </div>

                    <!-- 5. ASIGNAR SECCIÓN -->
                    <div class="mb-4">
                        <label class="form-label text-muted fw-bold small text-uppercase mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">5. ASIGNAR SECCIÓN</label>
                        <select name="seccion_id" class="form-select bg-white" style="border-radius: 8px; border-color: #E2E8F0; font-size: 0.88rem; height: 42px;" required>
                            <?php foreach ($secciones as $s): ?>
                                <option value="<?= $s['id'] ?>">Sección "<?= htmlspecialchars($s['nombre']) ?>"</option>
                            <?php endforeach; ?>
                        </select>
                    </div>

                    <!-- BOTÓN ASIGNAR CARGA -->
                    <button type="submit" class="btn w-100 py-2.5 fw-semibold text-white shadow-xs" 
                            style="background: #6366F1; border-radius: 8px; font-size: 0.95rem; border: none; height: 42px;">
                        Asignar Carga
                    </button>
                </form>
            </div>
        </div>
    </div>

    <!-- COLUMNA DERECHA: Visualización por Niveles (Cards) -->
    <div class="col-lg-8">
        <!-- SECCIÓN 1: NIVEL PRIMARIA -->
        <div class="mb-4">
            <div class="d-flex align-items-center gap-2 mb-3">
                <span class="fs-5">🏫</span>
                <h6 class="fw-bold mb-0 text-uppercase" style="color: #D97706; letter-spacing: 0.05em; font-size: 0.85rem;">
                    NIVEL PRIMARIA
                </h6>
                <span class="badge rounded-pill fw-bold" style="background: #FEF3C7; color: #D97706; font-size: 0.72rem;">
                    <?= count($asigPrimaria) ?>
                </span>
            </div>

            <?php if (empty($asigPrimaria)): ?>
                <div class="p-4 text-center text-muted small bg-white rounded-3 border">
                    No hay asignaciones registradas para el Nivel Primaria.
                </div>
            <?php else: ?>
                <div class="row g-3">
                    <?php foreach ($asigPrimaria as $as): ?>
                        <div class="col-md-6">
                            <div class="card p-3 border shadow-xs h-100 position-relative" style="border-radius: 14px; background: #FFFFFF; border-color: #E2E8F0;">
                                <!-- Botón Eliminar en la esquina superior derecha -->
                                <a href="?action=eliminar&id=<?= $as['id'] ?>" 
                                   class="position-absolute text-muted" 
                                   style="top: 10px; right: 12px; text-decoration: none; font-size: 0.85rem;"
                                   title="Eliminar asignación"
                                   onclick="return confirm('¿Retirar esta asignación académica?')">
                                    <i class="bi bi-x-lg text-slate-400"></i>
                                </a>

                                <div class="d-flex align-items-center gap-3">
                                    <!-- Foto del Docente -->
                                    <img src="<?= get_foto_docente($as['prof_foto'] ?? null, (int)$as['prof_id']) ?>" 
                                         alt="Docente" 
                                         class="rounded-3 shadow-2xs flex-shrink-0" 
                                         style="width: 44px; height: 44px; object-fit: cover;">

                                    <!-- Datos de la Asignación -->
                                    <div class="flex-grow-1 pe-3">
                                        <div class="fw-bold text-dark mb-0" style="font-size: 0.95rem; line-height: 1.2;">
                                            <?= htmlspecialchars($as['curso_nombre']) ?>
                                        </div>
                                        <div class="text-muted small d-flex align-items-center gap-1 my-1" style="font-size: 0.78rem;">
                                            <i class="bi bi-person text-secondary"></i>
                                            <span><?= htmlspecialchars($as['prof_apellidos']) ?></span>
                                        </div>
                                        <div>
                                            <span class="badge px-2 py-0.5 fw-bold text-uppercase" 
                                                  style="background: #FFFBEB; color: #D97706; border: 1px solid #FEF3C7; font-size: 0.68rem; border-radius: 6px;">
                                                <?= strtoupper(htmlspecialchars($as['grado_nombre'] . ' "' . $as['seccion_nombre'] . '"')) ?>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        </div>

        <!-- SECCIÓN 2: NIVEL SECUNDARIA -->
        <div class="mb-4">
            <div class="d-flex align-items-center gap-2 mb-3">
                <span class="fs-5">🎓</span>
                <h6 class="fw-bold mb-0 text-uppercase" style="color: #0891B2; letter-spacing: 0.05em; font-size: 0.85rem;">
                    NIVEL SECUNDARIA
                </h6>
                <span class="badge rounded-pill fw-bold" style="background: #ECFEFF; color: #0891B2; font-size: 0.72rem;">
                    <?= count($asigSecundaria) ?>
                </span>
            </div>

            <?php if (empty($asigSecundaria)): ?>
                <div class="p-4 text-center text-muted small bg-white rounded-3 border">
                    No hay asignaciones registradas para el Nivel Secundaria.
                </div>
            <?php else: ?>
                <div class="row g-3">
                    <?php foreach ($asigSecundaria as $as): ?>
                        <div class="col-md-6">
                            <div class="card p-3 border shadow-xs h-100 position-relative" style="border-radius: 14px; background: #FFFFFF; border-color: #E2E8F0;">
                                <!-- Botón Eliminar en la esquina superior derecha -->
                                <a href="?action=eliminar&id=<?= $as['id'] ?>" 
                                   class="position-absolute text-muted" 
                                   style="top: 10px; right: 12px; text-decoration: none; font-size: 0.85rem;"
                                   title="Eliminar asignación"
                                   onclick="return confirm('¿Retirar esta asignación académica?')">
                                    <i class="bi bi-x-lg text-slate-400"></i>
                                </a>

                                <div class="d-flex align-items-center gap-3">
                                    <!-- Foto del Docente -->
                                    <img src="<?= get_foto_docente($as['prof_foto'] ?? null, (int)$as['prof_id']) ?>" 
                                         alt="Docente" 
                                         class="rounded-3 shadow-2xs flex-shrink-0" 
                                         style="width: 44px; height: 44px; object-fit: cover;">

                                    <!-- Datos de la Asignación -->
                                    <div class="flex-grow-1 pe-3">
                                        <div class="fw-bold text-dark mb-0" style="font-size: 0.95rem; line-height: 1.2;">
                                            <?= htmlspecialchars($as['curso_nombre']) ?>
                                        </div>
                                        <div class="text-muted small d-flex align-items-center gap-1 my-1" style="font-size: 0.78rem;">
                                            <i class="bi bi-person text-secondary"></i>
                                            <span><?= htmlspecialchars($as['prof_apellidos']) ?></span>
                                        </div>
                                        <div>
                                            <span class="badge px-2 py-0.5 fw-bold text-uppercase" 
                                                  style="background: #ECFEFF; color: #0891B2; border: 1px solid #CFFAFE; font-size: 0.68rem; border-radius: 6px;">
                                                <?= strtoupper(htmlspecialchars($as['grado_nombre'] . ' "' . $as['seccion_nombre'] . '"')) ?>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>
        </div>

        <?php if (!empty($asigInicial)): ?>
            <!-- SECCIÓN 3: NIVEL INICIAL (Opcional si existen) -->
            <div class="mb-4">
                <div class="d-flex align-items-center gap-2 mb-3">
                    <span class="fs-5">🧸</span>
                    <h6 class="fw-bold mb-0 text-uppercase" style="color: #7E22CE; letter-spacing: 0.05em; font-size: 0.85rem;">
                        NIVEL INICIAL
                    </h6>
                    <span class="badge rounded-pill fw-bold" style="background: #F3E8FF; color: #7E22CE; font-size: 0.72rem;">
                        <?= count($asigInicial) ?>
                    </span>
                </div>

                <div class="row g-3">
                    <?php foreach ($asigInicial as $as): ?>
                        <div class="col-md-6">
                            <div class="card p-3 border shadow-xs h-100 position-relative" style="border-radius: 14px; background: #FFFFFF; border-color: #E2E8F0;">
                                <a href="?action=eliminar&id=<?= $as['id'] ?>" 
                                   class="position-absolute text-muted" 
                                   style="top: 10px; right: 12px; text-decoration: none; font-size: 0.85rem;"
                                   title="Eliminar asignación"
                                   onclick="return confirm('¿Retirar esta asignación académica?')">
                                    <i class="bi bi-x-lg text-slate-400"></i>
                                </a>

                                <div class="d-flex align-items-center gap-3">
                                    <img src="<?= get_foto_docente($as['prof_foto'] ?? null, (int)$as['prof_id']) ?>" 
                                         alt="Docente" 
                                         class="rounded-3 shadow-2xs flex-shrink-0" 
                                         style="width: 44px; height: 44px; object-fit: cover;">

                                    <div class="flex-grow-1 pe-3">
                                        <div class="fw-bold text-dark mb-0" style="font-size: 0.95rem; line-height: 1.2;">
                                            <?= htmlspecialchars($as['curso_nombre']) ?>
                                        </div>
                                        <div class="text-muted small d-flex align-items-center gap-1 my-1" style="font-size: 0.78rem;">
                                            <i class="bi bi-person text-secondary"></i>
                                            <span><?= htmlspecialchars($as['prof_apellidos']) ?></span>
                                        </div>
                                        <div>
                                            <span class="badge px-2 py-0.5 fw-bold text-uppercase" 
                                                  style="background: #F3E8FF; color: #7E22CE; border: 1px solid #E9D5FF; font-size: 0.68rem; border-radius: 6px;">
                                                <?= strtoupper(htmlspecialchars($as['grado_nombre'] . ' "' . $as['seccion_nombre'] . '"')) ?>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>
        <?php endif; ?>
    </div>
</div>

<!-- SCRIPT FILTRADO DINÁMICO DE GRADOS EN FORMULARIO -->
<script>
function filtrarGradosPorNivelAsig(nivel) {
    const selGrado = document.getElementById('selectGradoAsignacion');
    if (!selGrado) return;
    
    let firstValid = null;
    const options = selGrado.querySelectorAll('option');
    options.forEach(opt => {
        if (!opt.value) return; // Opción placeholder
        const optNivel = opt.getAttribute('data-nivel');
        if (!nivel || optNivel === nivel) {
            opt.style.display = '';
            opt.disabled = false;
            if (!firstValid) firstValid = opt.value;
        } else {
            opt.style.display = 'none';
            opt.disabled = true;
        }
    });

    if (firstValid) {
        selGrado.value = firstValid;
    } else {
        selGrado.value = '';
    }
}
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
