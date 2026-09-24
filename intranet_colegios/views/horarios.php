<?php
// views/horarios.php - Módulo 4: Horarios Escolares DYL SCHOOL
$pageTitle = 'Horarios Escolares';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// 1. Mapeo de Niveles
$nivelesMap = [
    1 => 'Inicial',
    2 => 'Primaria',
    3 => 'Secundaria'
];
$nivelesInverso = [
    'Inicial' => 1,
    'Primaria' => 2,
    'Secundaria' => 3
];

// Obtener parámetros GET
$nivelRaw = $_GET['nivel_id'] ?? ($_GET['nivel'] ?? '');
$nivelId = '';
$filtroNivel = '';

if (!empty($nivelRaw)) {
    if (is_numeric($nivelRaw) && isset($nivelesMap[(int)$nivelRaw])) {
        $nivelId = (int)$nivelRaw;
        $filtroNivel = $nivelesMap[$nivelId];
    } elseif (isset($nivelesInverso[$nivelRaw])) {
        $filtroNivel = $nivelRaw;
        $nivelId = $nivelesInverso[$nivelRaw];
    }
}

$filtroGrado = isset($_GET['grado_id']) && $_GET['grado_id'] !== '' ? (int)$_GET['grado_id'] : 0;
$filtroSeccion = $_GET['seccion'] ?? ($_GET['seccion_id'] ?? 'A');
// Si viene numérico convertir a letra o viceversa
if (is_numeric($filtroSeccion)) {
    $secNombre = $pdo->query("SELECT nombre FROM secciones WHERE id = " . (int)$filtroSeccion)->fetchColumn();
    if ($secNombre) {
        $filtroSeccion = $secNombre;
    }
}
$seccionId = $pdo->prepare("SELECT id FROM secciones WHERE nombre = ?");
$seccionId->execute([$filtroSeccion]);
$filtroSeccionId = $seccionId->fetchColumn() ?: 1;

$filtroDia = $_GET['dia'] ?? 'Lunes';
$diasValidos = ['Lunes' => 'Lunes', 'Martes' => 'Martes', 'Miercoles' => 'Miercoles', 'Miércoles' => 'Miercoles', 'Jueves' => 'Jueves', 'Viernes' => 'Viernes'];
$filtroDiaNorm = $diasValidos[$filtroDia] ?? 'Lunes';
$filtroDiaDisplay = ($filtroDiaNorm === 'Miercoles') ? 'Miercoles' : $filtroDiaNorm;

// 2. Grados según Nivel
$todosLosGrados = $pdo->query("SELECT id, nivel, nombre, orden FROM grados ORDER BY orden ASC")->fetchAll();
$gradosPorNivel = [];
foreach ($todosLosGrados as $g) {
    $nid = $nivelesInverso[$g['nivel']] ?? 0;
    $gradosPorNivel[$nid][] = $g;
}

$gradosList = [];
if (!empty($nivelId) && isset($gradosPorNivel[$nivelId])) {
    $gradosList = $gradosPorNivel[$nivelId];
    // Si no tiene grado seleccionado y la lista no está vacía, no forzar si se requiere manual, o seleccionar el primero si viene grado_id
    if ($filtroGrado <= 0 && isset($_GET['nivel_id']) && isset($_GET['grado_id'])) {
        $filtroGrado = (int)$gradosList[0]['id'];
    }
}

// 3. Cursos disponibles
$cursos = $pdo->query("SELECT * FROM cursos WHERE activo = 1 ORDER BY nombre ASC")->fetchAll();

// 4. Acción: Eliminar Bloque de Horario
if (isset($_GET['action']) && $_GET['action'] === 'eliminar' && isset($_GET['horario_id'])) {
    $hid = (int)$_GET['horario_id'];
    $pdo->prepare("DELETE FROM horarios WHERE id = ?")->execute([$hid]);
    set_flash('success', 'Bloque de horario eliminado correctamente.');
    $redirUrl = "views/horarios.php?nivel_id={$nivelId}&grado_id={$filtroGrado}&seccion=" . urlencode($filtroSeccion) . "&dia=" . urlencode($filtroDiaDisplay);
    header("Location: " . url($redirUrl));
    exit;
}

// 5. Acción: Guardar Nueva Clase
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'nueva_clase') {
    $cursoParam = trim($_POST['curso_id'] ?? '');
    $es_recreo = ($cursoParam === 'recreo' || isset($_POST['es_recreo'])) ? 1 : 0;
    $curso_id = ($es_recreo || empty($cursoParam) || $cursoParam === 'recreo') ? null : (int)$cursoParam;

    $hora_ini_val = trim($_POST['hora_inicio'] ?? '08:00');
    $ampm_ini = trim($_POST['ampm_inicio'] ?? 'AM');
    $hora_fin_val = trim($_POST['hora_fin'] ?? '09:30');
    $ampm_fin = trim($_POST['ampm_fin'] ?? 'AM');

    // Formatear tiempos ej: 08:00 AM
    if (!str_contains($hora_ini_val, 'AM') && !str_contains($hora_ini_val, 'PM')) {
        $hora_inicio = sprintf('%s %s', $hora_ini_val, $ampm_ini);
    } else {
        $hora_inicio = $hora_ini_val;
    }

    if (!str_contains($hora_fin_val, 'AM') && !str_contains($hora_fin_val, 'PM')) {
        $hora_fin = sprintf('%s %s', $hora_fin_val, $ampm_fin);
    } else {
        $hora_fin = $hora_fin_val;
    }

    if ($filtroGrado > 0 && $filtroSeccionId > 0) {
        $stmtIns = $pdo->prepare("
            INSERT INTO horarios (curso_id, grado_id, seccion_id, dia, hora_inicio, hora_fin, modalidad, es_recreo)
            VALUES (?, ?, ?, ?, ?, ?, 'Presencial', ?)
        ");
        $stmtIns->execute([$curso_id, $filtroGrado, $filtroSeccionId, $filtroDiaDisplay, $hora_inicio, $hora_fin, $es_recreo]);
        set_flash('success', '¡Clase agregada exitosamente al horario!');
    }

    $redirUrl = "views/horarios.php?nivel_id={$nivelId}&grado_id={$filtroGrado}&seccion=" . urlencode($filtroSeccion) . "&dia=" . urlencode($filtroDiaDisplay);
    header("Location: " . url($redirUrl));
    exit;
}

// 6. Consultar Bloques si Nivel y Grado están seleccionados
$bloques = [];
if (!empty($filtroNivel) && $filtroGrado > 0) {
    $stmtHorarios = $pdo->prepare("
        SELECT h.*, c.nombre as curso_nombre, c.tipo as curso_tipo
        FROM horarios h
        LEFT JOIN cursos c ON h.curso_id = c.id
        WHERE h.grado_id = ? AND h.seccion_id = ? AND (h.dia = ? OR h.dia = 'Miércoles' OR h.dia = 'Miercoles')
        ORDER BY h.hora_inicio ASC
    ");
    $stmtHorarios->execute([$filtroGrado, $filtroSeccionId, $filtroDiaDisplay]);
    $todosBloques = $stmtHorarios->fetchAll();

    // Filtrar para el día exacto (considerando Miercoles/Miércoles)
    foreach ($todosBloques as $b) {
        $bDiaNorm = $diasValidos[$b['dia']] ?? $b['dia'];
        if ($bDiaNorm === $filtroDiaNorm) {
            $bloques[] = $b;
        }
    }
}
?>

<!-- TÍTULO Y DESCRIPCIÓN DE CABECERA -->
<div class="mb-4">
    <h3 class="fw-bold text-dark mb-1" style="font-size: 1.45rem;">Gestión de Horarios</h3>
    <p class="text-muted small mb-0">Organiza las clases por nivel, grado y día.</p>
</div>

<!-- BARRA DE FILTROS SUPERIOR EN TARJETA BLANCA -->
<div class="card border-0 shadow-xs mb-4" style="background: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0 !important;">
    <div class="card-body p-3">
        <form id="formFiltrosHorario" method="GET" action="" class="row g-3 align-items-center">
            <!-- 1. NIVEL ACADÉMICO -->
            <div class="col-md-3">
                <label class="form-label text-muted fw-bold small text-uppercase mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">1. NIVEL ACADÉMICO</label>
                <select name="nivel_id" id="filtroNivel" class="form-select bg-white" style="border-radius: 8px; border-color: #E2E8F0; font-size: 0.88rem; height: 42px;" onchange="cambioNivel(this.value)">
                    <option value="">-- Seleccionar --</option>
                    <option value="1" <?= $nivelId == 1 ? 'selected' : '' ?>>Inicial</option>
                    <option value="2" <?= $nivelId == 2 ? 'selected' : '' ?>>Primaria</option>
                    <option value="3" <?= $nivelId == 3 ? 'selected' : '' ?>>Secundaria</option>
                </select>
            </div>

            <!-- 2. GRADO -->
            <div class="col-md-3">
                <label class="form-label text-muted fw-bold small text-uppercase mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">2. GRADO</label>
                <select name="grado_id" id="filtroGrado" class="form-select bg-white" style="border-radius: 8px; border-color: #E2E8F0; font-size: 0.88rem; height: 42px;" <?= empty($nivelId) ? 'disabled' : '' ?> onchange="this.form.submit()">
                    <option value="">-- Seleccionar --</option>
                    <?php if (!empty($gradosList)): ?>
                        <?php foreach ($gradosList as $g): ?>
                            <option value="<?= $g['id'] ?>" <?= $filtroGrado === (int)$g['id'] ? 'selected' : '' ?>>
                                <?= htmlspecialchars($g['nombre']) ?>
                            </option>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </select>
            </div>

            <!-- 3. SECCIÓN -->
            <div class="col-md-3">
                <label class="form-label text-muted fw-bold small text-uppercase mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">3. SECCIÓN</label>
                <select name="seccion" id="filtroSeccion" class="form-select bg-white" style="border-radius: 8px; border-color: #E2E8F0; font-size: 0.88rem; height: 42px;" onchange="this.form.submit()">
                    <option value="A" <?= $filtroSeccion === 'A' ? 'selected' : '' ?>>A</option>
                    <option value="B" <?= $filtroSeccion === 'B' ? 'selected' : '' ?>>B</option>
                    <option value="C" <?= $filtroSeccion === 'C' ? 'selected' : '' ?>>C</option>
                    <option value="D" <?= $filtroSeccion === 'D' ? 'selected' : '' ?>>D</option>
                </select>
            </div>

            <!-- 4. DÍA -->
            <div class="col-md-3">
                <label class="form-label text-muted fw-bold small text-uppercase mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">4. DÍA</label>
                <select name="dia" id="filtroDia" class="form-select bg-white" style="border-radius: 8px; border-color: #E2E8F0; font-size: 0.88rem; height: 42px;" onchange="this.form.submit()">
                    <option value="Lunes" <?= $filtroDiaNorm === 'Lunes' ? 'selected' : '' ?>>Lunes</option>
                    <option value="Martes" <?= $filtroDiaNorm === 'Martes' ? 'selected' : '' ?>>Martes</option>
                    <option value="Miercoles" <?= ($filtroDiaNorm === 'Miercoles') ? 'selected' : '' ?>>Miercoles</option>
                    <option value="Jueves" <?= $filtroDiaNorm === 'Jueves' ? 'selected' : '' ?>>Jueves</option>
                    <option value="Viernes" <?= $filtroDiaNorm === 'Viernes' ? 'selected' : '' ?>>Viernes</option>
                </select>
            </div>
        </form>
    </div>
</div>

<!-- ESTRUCTURA PRINCIPAL DE 2 COLUMNAS -->
<div class="row g-4 align-items-start">
    <!-- COLUMNA IZQUIERDA: Formulario Nueva Clase -->
    <div class="col-lg-4">
        <div class="card border-0 shadow-xs" style="background: #FFFFFF; border-radius: 14px; border: 1px solid #E2E8F0 !important;">
            <div class="card-body p-4">
                <!-- Título con icono de más en círculo púrpura -->
                <div class="d-flex align-items-center gap-2 mb-4">
                    <span class="d-inline-flex align-items-center justify-content-center text-white rounded-circle" style="width: 22px; height: 22px; background: #6366F1; font-size: 13px;">
                        <i class="bi bi-plus-lg"></i>
                    </span>
                    <h5 class="fw-bold text-dark mb-0" style="font-size: 1.05rem;">Nueva Clase</h5>
                </div>

                <?php if (empty($nivelId) || $filtroGrado <= 0): ?>
                    <!-- ESTADO VACÍO (Sin Nivel ni Grado) según Imagen 3 -->
                    <div class="d-flex flex-column align-items-center justify-content-center py-5 text-center my-3">
                        <div class="text-secondary mb-2" style="font-size: 2.2rem; opacity: 0.4; line-height: 1;">↑</div>
                        <p class="text-secondary small fw-medium mb-0" style="opacity: 0.7;">Selecciona Nivel y Grado arriba.</p>
                    </div>
                <?php else: ?>
                    <!-- FORMULARIO ACTIVO según Imagen 1 -->
                    <form method="POST" action="">
                        <input type="hidden" name="action" value="nueva_clase">

                        <!-- MATERIA / CURSO -->
                        <div class="mb-3">
                            <label class="form-label text-muted fw-bold small text-uppercase mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">MATERIA / CURSO</label>
                            <select name="curso_id" id="selectCurso" class="form-select bg-white" style="border-radius: 8px; border-color: #E2E8F0; font-size: 0.88rem; height: 42px;" required>
                                <option value="">-- Seleccionar Materia --</option>
                                <?php foreach ($cursos as $c): ?>
                                    <option value="<?= $c['id'] ?>"><?= htmlspecialchars($c['nombre']) ?></option>
                                <?php endforeach; ?>
                                <option value="recreo" style="color: #D97706; font-weight: bold;">🔔 RECREO / ALMUERZO</option>
                            </select>
                        </div>

                        <!-- HORA DE INICIO -->
                        <div class="mb-3">
                            <label class="form-label text-muted fw-bold small text-uppercase mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">HORA DE INICIO</label>
                            <div class="input-group">
                                <input type="text" name="hora_inicio" id="hora_inicio" class="form-control text-center fw-medium bg-white" value="00:00" placeholder="00:00" style="border-radius: 8px 0 0 8px; border-color: #E2E8F0; font-size: 0.9rem; height: 42px;" required>
                                <select name="ampm_inicio" id="ampm_inicio" class="form-select text-center fw-bold" style="max-width: 85px; border-radius: 0 8px 8px 0; border-color: #E2E8F0; background-color: #F8FAFC; color: #6366F1; font-size: 0.85rem; height: 42px;">
                                    <option value="AM" selected>AM</option>
                                    <option value="PM">PM</option>
                                </select>
                            </div>
                        </div>

                        <!-- HORA DE FIN -->
                        <div class="mb-4">
                            <label class="form-label text-muted fw-bold small text-uppercase mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">HORA DE FIN</label>
                            <div class="input-group">
                                <input type="text" name="hora_fin" id="hora_fin" class="form-control text-center fw-medium bg-white" value="00:00" placeholder="00:00" style="border-radius: 8px 0 0 8px; border-color: #E2E8F0; font-size: 0.9rem; height: 42px;" required>
                                <select name="ampm_fin" id="ampm_fin" class="form-select text-center fw-bold" style="max-width: 85px; border-radius: 0 8px 8px 0; border-color: #E2E8F0; background-color: #F8FAFC; color: #6366F1; font-size: 0.85rem; height: 42px;">
                                    <option value="AM" selected>AM</option>
                                    <option value="PM">PM</option>
                                </select>
                            </div>
                        </div>

                        <!-- BOTÓN GUARDAR EN HORARIO -->
                        <button type="submit" class="btn w-100 py-2.5 fw-semibold text-white shadow-xs d-flex align-items-center justify-content-center gap-2" 
                                style="background: #6366F1; border-radius: 8px; font-size: 0.92rem; border: none; height: 42px;">
                            <i class="bi bi-floppy-fill" style="font-size: 0.95rem;"></i>
                            <span>Guardar en Horario</span>
                        </button>
                    </form>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <!-- COLUMNA DERECHA: Horario del Día -->
    <div class="col-lg-8">
        <div class="card border-0 shadow-xs" style="background: #FFFFFF; border-radius: 14px; border: 1px solid #E2E8F0 !important; min-height: 380px;">
            <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h4 class="fw-bolder text-dark mb-0" style="font-size: 1.25rem; letter-spacing: 0.03em;">
                        <?= strtoupper(htmlspecialchars($filtroDiaDisplay)) ?>
                    </h4>
                    <?php if (empty($bloques)): ?>
                        <span class="badge px-3 py-1.5 fw-semibold rounded-pill" style="background: #EEF2FF; color: #4F46E5; font-size: 0.78rem;">
                            0 Bloques
                        </span>
                    <?php else: ?>
                        <span class="badge px-3 py-1.5 fw-semibold rounded-pill" style="background: #EEF2FF; color: #4F46E5; font-size: 0.78rem;">
                            <?= count($bloques) ?> Bloques
                        </span>
                    <?php endif; ?>
                </div>

                <?php if (empty($bloques)): ?>
                    <!-- ESTADO VACÍO (Día Libre) según Imagen 3 -->
                    <div class="d-flex flex-column align-items-center justify-content-center py-5 my-4 text-center">
                        <div class="mb-3 text-secondary" style="opacity: 0.35;">
                            <i class="bi bi-calendar2-check" style="font-size: 3.5rem;"></i>
                        </div>
                        <h5 class="fw-bold text-secondary mb-1" style="font-size: 1.1rem;">Día Libre</h5>
                        <p class="text-muted small mb-0" style="font-size: 0.85rem;">No hay clases programadas.</p>
                    </div>
                <?php else: ?>
                    <!-- LISTA DE BLOQUES según Imagen 1 -->
                    <div class="d-flex flex-column gap-2.5">
                        <?php foreach ($bloques as $b): ?>
                            <?php if (!empty($b['es_recreo'])): ?>
                                <!-- Bloque 🔔 RECREO / ALMUERZO -->
                                <div class="p-3 rounded-3 d-flex align-items-center justify-content-between position-relative shadow-2xs"
                                     style="background: #FFFBEB; border: 1px solid #FEF3C7; border-left: 4px solid #F59E0B !important; border-radius: 10px;">
                                    <div class="d-flex align-items-center gap-4">
                                        <!-- Columna Horas -->
                                        <div style="min-width: 90px;">
                                            <div class="fw-bold" style="color: #D97706; font-size: 0.95rem; line-height: 1.2;"><?= htmlspecialchars($b['hora_inicio']) ?></div>
                                            <div style="color: #F59E0B; font-size: 0.78rem; line-height: 1.2;"><?= htmlspecialchars($b['hora_fin']) ?></div>
                                        </div>
                                        <!-- Detalle Recreo -->
                                        <div>
                                            <div class="fw-bold d-flex align-items-center gap-1.5" style="color: #B45309; font-size: 0.95rem;">
                                                <i class="bi bi-bell-fill text-warning"></i> RECREO / ALMUERZO
                                            </div>
                                            <div class="text-muted small d-flex align-items-center gap-1.5 mt-0.5" style="font-size: 0.76rem;">
                                                <i class="bi bi-cup-hot text-secondary"></i> Tiempo Libre
                                            </div>
                                        </div>
                                    </div>
                                    <!-- Botón Eliminar -->
                                    <a href="?action=eliminar&horario_id=<?= $b['id'] ?>&nivel_id=<?= $nivelId ?>&grado_id=<?= $filtroGrado ?>&seccion=<?= urlencode($filtroSeccion) ?>&dia=<?= urlencode($filtroDiaDisplay) ?>"
                                       class="btn btn-sm d-flex align-items-center justify-content-center p-0 rounded-2"
                                       style="width: 28px; height: 28px; background: #FEF2F2; color: #EF4444; border: 1px solid #FEE2E2;"
                                       title="Eliminar bloque" onclick="return confirm('¿Desea eliminar este bloque?')">
                                        <i class="bi bi-x fs-5"></i>
                                    </a>
                                </div>
                            <?php else: ?>
                                <!-- Bloque de Clase Normal -->
                                <div class="p-3 rounded-3 bg-white border d-flex align-items-center justify-content-between position-relative shadow-2xs"
                                     style="border-color: #E2E8F0 !important; border-left: 4px solid #6366F1 !important; border-radius: 10px;">
                                    <div class="d-flex align-items-center gap-4">
                                        <!-- Columna Horas -->
                                        <div style="min-width: 90px;">
                                            <div class="fw-bold text-dark" style="font-size: 0.95rem; line-height: 1.2;"><?= htmlspecialchars($b['hora_inicio']) ?></div>
                                            <div class="text-muted" style="font-size: 0.78rem; line-height: 1.2;"><?= htmlspecialchars($b['hora_fin']) ?></div>
                                        </div>
                                        <!-- Detalle Clase -->
                                        <div>
                                            <div class="fw-bold text-dark" style="font-size: 1rem;"><?= htmlspecialchars($b['curso_nombre'] ?? 'Materia') ?></div>
                                            <div class="text-muted small d-flex align-items-center gap-2 mt-0.5" style="font-size: 0.76rem;">
                                                <span>• <?= htmlspecialchars($filtroSeccion) ?></span>
                                                <span>|</span>
                                                <span>• <?= htmlspecialchars($b['modalidad'] ?? 'Presencial') ?></span>
                                            </div>
                                        </div>
                                    </div>
                                    <!-- Botón Eliminar -->
                                    <a href="?action=eliminar&horario_id=<?= $b['id'] ?>&nivel_id=<?= $nivelId ?>&grado_id=<?= $filtroGrado ?>&seccion=<?= urlencode($filtroSeccion) ?>&dia=<?= urlencode($filtroDiaDisplay) ?>"
                                       class="btn btn-sm d-flex align-items-center justify-content-center p-0 rounded-2"
                                       style="width: 28px; height: 28px; background: #FEF2F2; color: #EF4444; border: 1px solid #FEE2E2;"
                                       title="Eliminar clase" onclick="return confirm('¿Desea retirar esta clase del horario?')">
                                        <i class="bi bi-x fs-5"></i>
                                    </a>
                                </div>
                            <?php endif; ?>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </div>
</div>

<!-- SCRIPT DE FILTROS DINÁMICOS -->
<script>
const gradosData = <?= json_encode($gradosPorNivel, JSON_UNESCAPED_UNICODE) ?>;

function cambioNivel(valNivel) {
    const selGrado = document.getElementById('filtroGrado');
    const form = document.getElementById('formFiltrosHorario');
    
    if (!valNivel) {
        selGrado.innerHTML = '<option value="">-- Seleccionar --</option>';
        selGrado.disabled = true;
        form.submit();
        return;
    }
    
    selGrado.disabled = false;
    selGrado.innerHTML = '<option value="">-- Seleccionar --</option>';
    
    const lista = gradosData[valNivel] || [];
    lista.forEach(g => {
        const opt = document.createElement('option');
        opt.value = g.id;
        opt.textContent = g.nombre;
        selGrado.appendChild(opt);
    });
    
    // Si hay grados, seleccionar el primero y enviar
    if (lista.length > 0) {
        selGrado.value = lista[0].id;
        form.submit();
    }
}
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
