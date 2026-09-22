<?php
// views/profesor_nuevo.php - Módulo 5: Contratar Docente DYL SCHOOL
$pageTitle = 'Contratar Docente';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();
$error = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $nombres = trim($_POST['nombres'] ?? '');
    $apellidos = trim($_POST['apellidos'] ?? '');
    $dni = trim($_POST['dni'] ?? '');
    $genero = $_POST['genero'] ?? 'Masculino';
    $correo = trim($_POST['correo'] ?? '');
    $telefono = trim($_POST['telefono'] ?? '');

    if (empty($nombres) || empty($apellidos) || empty($dni)) {
        $error = 'Nombres, Apellidos y DNI son campos obligatorios.';
    } else {
        $stmtCheck = $pdo->prepare("SELECT id FROM profesores WHERE dni = ?");
        $stmtCheck->execute([$dni]);
        if ($stmtCheck->fetch()) {
            $error = 'Ya existe un docente registrado con el DNI ' . htmlspecialchars($dni);
        } else {
            try {
                // Crear usuario con DNI como usuario y contraseña inicial
                $passHash = password_hash($dni, PASSWORD_BCRYPT);
                $stmtUser = $pdo->prepare("INSERT INTO usuarios (username, password_hash, rol, nombres, apellidos, email, dni, telefono, estado) 
                                           VALUES (?, ?, 'docente', ?, ?, ?, ?, ?, 'Activo')");
                $stmtUser->execute([$dni, $passHash, $nombres, $apellidos, $correo, $dni, $telefono]);
                $usuarioId = $pdo->lastInsertId();

                // Crear profesor
                $stmtProf = $pdo->prepare("INSERT INTO profesores (usuario_id, nombres, apellidos, dni, genero, correo, telefono, estado) 
                                           VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVO')");
                $stmtProf->execute([$usuarioId, $nombres, $apellidos, $dni, $genero, $correo, $telefono]);

                set_flash('success', "¡Docente {$nombres} {$apellidos} contratado y registrado exitosamente!");
                header('Location: ' . url('views/profesores.php'));
                exit;
            } catch (Exception $e) {
                $error = 'Error al registrar contratación: ' . $e->getMessage();
            }
        }
    }
}
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h3 class="h4 fw-bold text-dark mb-1">Contratar Nuevo Docente</h3>
        <p class="text-muted small mb-0">Registro de nuevo profesor en la plana académica con acceso directo al sistema.</p>
    </div>
    <a href="<?= url('views/profesores.php') ?>" class="btn btn-outline-secondary btn-sm px-3 rounded-3">
        <i class="bi bi-arrow-left me-1"></i> Volver a Lista
    </a>
</div>

<?php if ($error): ?>
    <div class="alert alert-danger rounded-3 py-2 px-3 small mb-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i><?= htmlspecialchars($error) ?>
    </div>
<?php endif; ?>

<div class="dyl-card p-4">
    <form method="POST" action="">
        <!-- 1. Datos Personales -->
        <div class="border-bottom pb-4 mb-4">
            <h5 class="fw-bold text-primary mb-3 d-flex align-items-center gap-2">
                <i class="bi bi-person-badge-fill"></i> 1. DATOS PERSONALES
            </h5>
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label small fw-bold text-dark">Nombres <span class="text-danger">*</span></label>
                    <input type="text" name="nombres" class="form-control" placeholder="Ej. Roberto" required value="<?= htmlspecialchars($_POST['nombres'] ?? '') ?>">
                </div>
                <div class="col-md-6">
                    <label class="form-label small fw-bold text-dark">Apellidos <span class="text-danger">*</span></label>
                    <input type="text" name="apellidos" class="form-control" placeholder="Ej. Gutiérrez Palacios" required value="<?= htmlspecialchars($_POST['apellidos'] ?? '') ?>">
                </div>
                <div class="col-md-6">
                    <label class="form-label small fw-bold text-dark">Género</label>
                    <select name="genero" class="form-select">
                        <option value="Masculino">Masculino</option>
                        <option value="Femenino">Femenino</option>
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label small fw-bold text-dark">Foto de Perfil (Opcional)</label>
                    <input type="file" class="form-control" accept="image/*">
                </div>
            </div>
        </div>

        <!-- 2. Cuenta y Acceso -->
        <div class="border-bottom pb-4 mb-4">
            <h5 class="fw-bold text-primary mb-3 d-flex align-items-center gap-2">
                <i class="bi bi-shield-lock-fill"></i> 2. CUENTA Y ACCESO
            </h5>
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label small fw-bold text-dark">DNI / Documento <span class="text-danger">*</span></label>
                    <input type="text" name="dni" class="form-control" placeholder="Ej. 10293847" required value="<?= htmlspecialchars($_POST['dni'] ?? '') ?>">
                    <div class="form-text text-primary small">
                        <i class="bi bi-info-circle me-1"></i> Este número será su Usuario y Contraseña inicial.
                    </div>
                </div>
            </div>
        </div>

        <!-- 3. Información de Contacto -->
        <div class="border-bottom pb-4 mb-4">
            <h5 class="fw-bold text-primary mb-3 d-flex align-items-center gap-2">
                <i class="bi bi-telephone-fill"></i> 3. INFORMACIÓN DE CONTACTO
            </h5>
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label small fw-bold text-dark">Correo Electrónico Institucional</label>
                    <input type="email" name="correo" class="form-control" placeholder="profesor@dylschool.edu.pe" value="<?= htmlspecialchars($_POST['correo'] ?? '') ?>">
                </div>
                <div class="col-md-6">
                    <label class="form-label small fw-bold text-dark">Teléfono / Celular</label>
                    <input type="text" name="telefono" class="form-control" placeholder="+51 987 000 111" value="<?= htmlspecialchars($_POST['telefono'] ?? '') ?>">
                </div>
            </div>
        </div>

        <div class="text-end">
            <a href="<?= url('views/profesores.php') ?>" class="btn btn-light px-4 me-2">Cancelar</a>
            <button type="submit" class="btn btn-dyl-primary px-4 py-2">
                <i class="bi bi-check-lg me-1"></i> Registrar Contratación
            </button>
        </div>
    </form>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
