<?php
// views/alumno_nuevo.php - Módulo 2: Registro de Nuevo Alumno DYL SCHOOL
$pageTitle = 'Registrar Alumno';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();
$error = null;

$grados = $pdo->query("SELECT * FROM grados ORDER BY orden ASC")->fetchAll();
$secciones = $pdo->query("SELECT * FROM secciones ORDER BY nombre ASC")->fetchAll();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $nombres = trim($_POST['nombres'] ?? '');
    $apellidos = trim($_POST['apellidos'] ?? '');
    $fecha_nacimiento = !empty($_POST['fecha_nacimiento']) ? $_POST['fecha_nacimiento'] : null;
    $genero = $_POST['genero'] ?? 'Masculino';
    $dni = trim($_POST['dni'] ?? '');
    $correo = trim($_POST['correo'] ?? '');
    $apoderado_nombre = trim($_POST['apoderado_nombre'] ?? '');
    $telefono_apoderado = trim($_POST['telefono_apoderado'] ?? $_POST['telefono'] ?? '');
    $direccion = trim($_POST['direccion'] ?? '');
    $grado_id = (int)($_POST['grado_id'] ?? 0);
    $seccion_id = (int)($_POST['seccion_id'] ?? 0);

    if (empty($nombres) || empty($apellidos) || empty($dni)) {
        $error = 'Los campos Nombres, Apellidos y DNI son obligatorios.';
    } else {
        // Validar DNI único
        $stmtCheck = $pdo->prepare("SELECT id FROM alumnos WHERE dni = ?");
        $stmtCheck->execute([$dni]);
        if ($stmtCheck->fetch()) {
            $error = 'Ya existe un alumno registrado con el DNI ' . htmlspecialchars($dni);
        } else {
            try {
                // 1. Regla de Negocio: Crear usuario automático con DNI como usuario y contraseña inicial
                $passHash = password_hash($dni, PASSWORD_BCRYPT);
                $stmtUser = $pdo->prepare("INSERT INTO usuarios (username, password_hash, rol, nombres, apellidos, email, dni, telefono, estado) 
                                           VALUES (?, ?, 'alumno', ?, ?, ?, ?, ?, 'Activo')");
                $stmtUser->execute([$dni, $passHash, $nombres, $apellidos, $correo, $dni, $telefono_apoderado]);
                $usuarioId = $pdo->lastInsertId();

                // 2. Insertar Alumno
                $stmtAlum = $pdo->prepare("INSERT INTO alumnos (usuario_id, nombres, apellidos, dni, fecha_nacimiento, genero, correo, apoderado_nombre, telefono_apoderado, direccion, estado) 
                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVO')");
                $stmtAlum->execute([$usuarioId, $nombres, $apellidos, $dni, $fecha_nacimiento, $genero, $correo, $apoderado_nombre, $telefono_apoderado, $direccion]);
                $alumnoId = $pdo->lastInsertId();

                // 3. Si se seleccionó Grado y Sección, registrar matrícula automáticamente para 2026
                if ($grado_id > 0 && $seccion_id > 0) {
                    $stmtMat = $pdo->prepare("INSERT INTO matriculas (alumno_id, grado_id, seccion_id, anio_lectivo, fecha_matricula, estado) 
                                             VALUES (?, ?, ?, 2026, CURDATE(), 'MATRICULADO')");
                    $stmtMat->execute([$alumnoId, $grado_id, $seccion_id]);
                }

                set_flash('success', "¡Alumno {$nombres} {$apellidos} registrado exitosamente con credenciales DNI!");
                header('Location: ' . url('views/alumnos.php'));
                exit;
            } catch (Exception $e) {
                $error = 'Error al registrar alumno: ' . $e->getMessage();
            }
        }
    }
}
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h3 class="h4 fw-bold text-dark mb-1">Nuevo Alumno</h3>
        <p class="text-muted small mb-0">Complete la ficha de inscripción escolar y generación de credenciales automáticas.</p>
    </div>
    <a href="<?= url('views/alumnos.php') ?>" class="btn btn-outline-secondary btn-sm px-3 rounded-3">
        <i class="bi bi-arrow-left me-1"></i> Volver a Lista
    </a>
</div>

<?php if ($error): ?>
    <div class="alert alert-danger rounded-3 py-2 px-3 small mb-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i><?= htmlspecialchars($error) ?>
    </div>
<?php endif; ?>

<div class="dyl-card p-4">
    <form method="POST" action="" enctype="multipart/form-data">
        <!-- 1. DATOS PERSONALES -->
        <div class="border-bottom pb-4 mb-4">
            <h5 class="fw-bold text-primary mb-3 d-flex align-items-center gap-2">
                <i class="bi bi-person-lines-fill"></i> 1. DATOS PERSONALES
            </h5>
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label small fw-bold text-dark">Nombres <span class="text-danger">*</span></label>
                    <input type="text" name="nombres" class="form-control" placeholder="Ej. Juan Carlos" required value="<?= htmlspecialchars($_POST['nombres'] ?? '') ?>">
                </div>
                <div class="col-md-6">
                    <label class="form-label small fw-bold text-dark">Apellidos <span class="text-danger">*</span></label>
                    <input type="text" name="apellidos" class="form-control" placeholder="Ej. Pérez Gómez" required value="<?= htmlspecialchars($_POST['apellidos'] ?? '') ?>">
                </div>
                <div class="col-md-4">
                    <label class="form-label small fw-bold text-dark">Fecha de Nacimiento (dd/mm/aaaa)</label>
                    <input type="date" name="fecha_nacimiento" class="form-control" value="<?= htmlspecialchars($_POST['fecha_nacimiento'] ?? '') ?>">
                </div>
                <div class="col-md-4">
                    <label class="form-label small fw-bold text-dark">Género</label>
                    <select name="genero" class="form-select">
                        <option value="Masculino" <?= (isset($_POST['genero']) && $_POST['genero'] === 'Masculino') ? 'selected' : '' ?>>Masculino</option>
                        <option value="Femenino" <?= (isset($_POST['genero']) && $_POST['genero'] === 'Femenino') ? 'selected' : '' ?>>Femenino</option>
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label small fw-bold text-dark">Foto de Perfil</label>
                    <div class="d-flex align-items-center gap-2">
                        <div id="fotoPreview" class="rounded-circle border d-flex align-items-center justify-content-center bg-light text-muted" style="width: 38px; height: 38px; overflow: hidden; flex-shrink: 0;">
                            <i class="bi bi-person fs-5"></i>
                        </div>
                        <input type="file" name="foto" class="form-control" accept="image/*" onchange="previewImage(this, 'fotoPreview')">
                    </div>
                </div>
            </div>
        </div>

        <!-- 2. IDENTIFICACIÓN Y CUENTA -->
        <div class="border-bottom pb-4 mb-4">
            <h5 class="fw-bold text-primary mb-3 d-flex align-items-center gap-2">
                <i class="bi bi-shield-lock-fill"></i> 2. IDENTIFICACIÓN Y CUENTA
            </h5>
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label small fw-bold text-dark">DNI / Documento <span class="text-danger">*</span></label>
                    <input type="text" name="dni" class="form-control" placeholder="Ej. 70123456" required value="<?= htmlspecialchars($_POST['dni'] ?? '') ?>">
                    <div class="form-text text-primary small fw-semibold mt-1">
                        <i class="bi bi-info-circle me-1"></i> Será el Usuario de acceso. El DNI será la contraseña inicial.
                    </div>
                </div>
            </div>
        </div>

        <!-- 3. CONTACTO -->
        <div class="border-bottom pb-4 mb-4">
            <h5 class="fw-bold text-primary mb-3 d-flex align-items-center gap-2">
                <i class="bi bi-telephone-fill"></i> 3. CONTACTO
            </h5>
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label small fw-bold text-dark">Correo Institucional</label>
                    <input type="email" name="correo" class="form-control" placeholder="alumno@escuela.edu.pe" value="<?= htmlspecialchars($_POST['correo'] ?? '') ?>">
                </div>
                <div class="col-md-6">
                    <label class="form-label small fw-bold text-dark">Teléfono (Apoderado)</label>
                    <input type="text" name="telefono_apoderado" class="form-control" placeholder="+51 999 000 000" value="<?= htmlspecialchars($_POST['telefono_apoderado'] ?? '') ?>">
                </div>
            </div>
        </div>

        <div class="text-end">
            <a href="<?= url('views/alumnos.php') ?>" class="btn btn-light px-4 me-2">Cancelar</a>
            <button type="submit" class="btn btn-dyl-primary px-4 py-2">
                <i class="bi bi-check-lg me-1"></i> Registrar Alumno
            </button>
        </div>

    </form>
</div>

<script>
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const container = document.getElementById(previewId);
            container.innerHTML = '<img src="' + e.target.result + '" style="width:100%; height:100%; object-fit:cover;">';
        }
        reader.readAsDataURL(input.files[0]);
    }
}
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>

