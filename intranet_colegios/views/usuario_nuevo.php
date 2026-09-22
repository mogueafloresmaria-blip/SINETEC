<?php
// views/usuario_nuevo.php - Módulo 10: Crear Usuario DYL SCHOOL
$pageTitle = 'Nuevo Usuario';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();
$error = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $nombres = trim($_POST['nombres'] ?? '');
    $apellidos = trim($_POST['apellidos'] ?? '');
    $email = trim($_POST['email'] ?? '');
    $dni = trim($_POST['dni'] ?? '');
    $password = trim($_POST['password'] ?? '');
    $rol = $_POST['rol'] ?? 'alumno';

    if (empty($nombres) || empty($apellidos) || empty($dni) || empty($password)) {
        $error = 'Nombres, Apellidos, DNI y Contraseña son obligatorios.';
    } else {
        $stmtCheck = $pdo->prepare("SELECT id FROM usuarios WHERE dni = ? OR username = ?");
        $stmtCheck->execute([$dni, $dni]);
        if ($stmtCheck->fetch()) {
            $error = 'Ya existe un usuario registrado con el DNI/Usuario indicado.';
        } else {
            $passHash = password_hash($password, PASSWORD_BCRYPT);
            $stmtIns = $pdo->prepare("
                INSERT INTO usuarios (username, password_hash, rol, nombres, apellidos, email, dni, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Activo')
            ");
            $stmtIns->execute([$dni, $passHash, $rol, $nombres, $apellidos, $email, $dni]);

            set_flash('success', "¡Usuario {$nombres} {$apellidos} creado exitosamente!");
            header('Location: ' . url('views/usuarios.php'));
            exit;
        }
    }
}
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h3 class="h4 fw-bold text-dark mb-1">Nuevo Usuario del Sistema</h3>
        <p class="text-muted small mb-0">Asignación de credenciales de acceso institucional.</p>
    </div>
    <a href="<?= url('views/usuarios.php') ?>" class="btn btn-outline-secondary btn-sm px-3 rounded-3">
        <i class="bi bi-arrow-left me-1"></i> Volver a Usuarios
    </a>
</div>

<?php if ($error): ?>
    <div class="alert alert-danger rounded-3 py-2 px-3 small mb-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i><?= htmlspecialchars($error) ?>
    </div>
<?php endif; ?>

<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="dyl-card p-4">
            <form method="POST" action="">
                <div class="row g-3 mb-3">
                    <div class="col-md-6">
                        <label class="form-label small fw-bold text-dark mb-1">Nombres <span class="text-danger">*</span></label>
                        <input type="text" name="nombres" class="form-control" placeholder="Ej. Ana Lucía" required value="<?= htmlspecialchars($_POST['nombres'] ?? '') ?>">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label small fw-bold text-dark mb-1">Apellidos <span class="text-danger">*</span></label>
                        <input type="text" name="apellidos" class="form-control" placeholder="Ej. Rojas Paz" required value="<?= htmlspecialchars($_POST['apellidos'] ?? '') ?>">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label small fw-bold text-dark mb-1">DNI / Documento <span class="text-danger">*</span></label>
                        <input type="text" name="dni" class="form-control" placeholder="Ej. 70891234" required value="<?= htmlspecialchars($_POST['dni'] ?? '') ?>">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label small fw-bold text-dark mb-1">Correo Electrónico</label>
                        <input type="email" name="email" class="form-control" placeholder="usuario@colegio.com" value="<?= htmlspecialchars($_POST['email'] ?? '') ?>">
                    </div>
                    <div class="col-md-6">
                        <label class="form-label small fw-bold text-dark mb-1">Contraseña Inicial <span class="text-danger">*</span></label>
                        <input type="password" name="password" class="form-control" placeholder="••••••••" required>
                    </div>
                    <div class="col-md-6">
                        <label class="form-label small fw-bold text-dark mb-1">Rol en el Sistema <span class="text-danger">*</span></label>
                        <select name="rol" class="form-select" required>
                            <option value="alumno">Alumno</option>
                            <option value="docente">Docente / Profesor</option>
                            <option value="admin">Administrador del Sistema</option>
                        </select>
                    </div>
                    <div class="col-md-12">
                        <label class="form-label small fw-bold text-dark mb-1">Foto de Perfil</label>
                        <input type="file" name="foto" class="form-control" accept="image/*">
                    </div>
                </div>


                <div class="d-flex justify-content-between align-items-center pt-3 border-top">
                    <a href="<?= url('views/usuarios.php') ?>" class="btn btn-light px-4">Cancelar</a>
                    <button type="submit" class="btn btn-dyl-primary px-4 py-2.5">
                        <i class="bi bi-shield-check me-1"></i> Crear Usuario
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
