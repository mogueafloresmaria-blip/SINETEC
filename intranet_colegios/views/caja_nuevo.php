<?php
// views/caja_nuevo.php - Módulo 9: Emisión de Cobro DYL SCHOOL
$pageTitle = 'Nuevo Cobro de Pensión';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();
$error = null;

// Obtener alumnos matriculados con su información de pagos
$stmtAlumnos = $pdo->query("
    SELECT m.id as matricula_id, a.id as alumno_id, a.nombres, a.apellidos, a.dni, g.nombre as grado_nombre,
           (SELECT COUNT(*) FROM pagos p WHERE p.matricula_id = m.id AND p.es_matricula = 1 AND p.estado = 'EMITIDO') as ya_pago_matricula,
           m.pagado_hasta
    FROM matriculas m
    JOIN alumnos a ON m.alumno_id = a.id
    JOIN grados g ON m.grado_id = g.id
    WHERE m.anio_lectivo = 2026
    ORDER BY a.apellidos ASC
");
$alumnos = $stmtAlumnos->fetchAll();

// Alumno seleccionado preliminarmente
$alumnoSeleccionadoId = (int)($_GET['alumno_id'] ?? ($alumnos[0]['alumno_id'] ?? 0));
$alumnoData = null;
foreach ($alumnos as $al) {
    if ((int)$al['alumno_id'] === $alumnoSeleccionadoId) {
        $alumnoData = $al;
        break;
    }
}
if (!$alumnoData && !empty($alumnos)) {
    $alumnoData = $alumnos[0];
    $alumnoSeleccionadoId = (int)$alumnoData['alumno_id'];
}

// Procesar Pago
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $matriculaId = (int)($_POST['matricula_id'] ?? 0);
    $alumnoId = (int)($_POST['alumno_id'] ?? 0);
    $incluirMatricula = isset($_POST['incluir_matricula']) ? 1 : 0;
    $mesPension = trim($_POST['mes_pension'] ?? '');
    $metodoPago = trim($_POST['metodo_pago'] ?? 'Efectivo');
    $montoTotal = (float)($_POST['monto_total'] ?? 0.00);

    if ($matriculaId <= 0 || $alumnoId <= 0 || $montoTotal <= 0) {
        $error = 'Debe seleccionar un alumno y al menos un concepto a pagar con monto válido.';
    } else {
        // Regla de Negocio: Validar cobro duplicado de matrícula
        if ($incluirMatricula) {
            $stmtCheckMat = $pdo->prepare("SELECT id FROM pagos WHERE matricula_id = ? AND es_matricula = 1 AND estado = 'EMITIDO'");
            $stmtCheckMat->execute([$matriculaId]);
            if ($stmtCheckMat->fetch()) {
                $error = 'Este alumno ya pagó la matrícula correspondiente al año escolar 2026.';
            }
        }

        if (!$error) {
            // Generar número de recibo oficial tipo REC-260109-123456-789
            $reciboNum = 'REC-' . date('ymd-His') . '-' . rand(100, 999);
            $conceptos = [];
            if ($incluirMatricula) $conceptos[] = 'Matrícula 2026';
            if (!empty($mesPension)) $conceptos[] = "Pensión {$mesPension}";
            $conceptoStr = implode(' + ', $conceptos);

            $stmtInsPago = $pdo->prepare("
                INSERT INTO pagos (numero_recibo, matricula_id, alumno_id, concepto, mes_pension, metodo_pago, monto, es_matricula, estado, fecha_pago, usuario_cajero_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'EMITIDO', CURRENT_TIMESTAMP, ?)
            ");
            $cajeroId = $user['id'] ?? 1;
            $stmtInsPago->execute([$reciboNum, $matriculaId, $alumnoId, $conceptoStr, $mesPension, $metodoPago, $montoTotal, $incluirMatricula, $cajeroId]);
            $pagoId = $pdo->lastInsertId();

            // Actualizar estado de pensión en matrícula
            if (!empty($mesPension)) {
                $updMat = $pdo->prepare("UPDATE matriculas SET estado_pension = 'ADELANTADO', pagado_hasta = ? WHERE id = ?");
                $updMat->execute([$mesPension, $matriculaId]);
            }

            set_flash('success', "¡Pago procesado exitosamente! Recibo emitido: {$reciboNum}");
            header('Location: ' . url("views/imprimir_ticket.php?id={$pagoId}"));
            exit;
        }
    }
}
?>

<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h3 class="h4 fw-bold text-dark mb-1">Registrar Nuevo Cobro</h3>
        <p class="text-muted small mb-0">Emisión de recibos de matrícula y cuotas mensuales de pensión escolar.</p>
    </div>
    <a href="<?= url('views/caja.php') ?>" class="btn btn-outline-secondary btn-sm px-3 rounded-3">
        <i class="bi bi-arrow-left me-1"></i> Volver a Caja
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
            <form method="POST" action="" id="formCobro">
                <!-- 1. Seleccionar Alumno -->
                <div class="mb-4">
                    <label class="form-label small fw-bold text-dark mb-1">1. Seleccionar Alumno <span class="text-danger">*</span></label>
                    <select name="alumno_id" id="selectAlumno" class="form-select form-select-lg fs-6" onchange="cambiarAlumno(this.value)" required>
                        <?php foreach ($alumnos as $al): ?>
                            <option value="<?= $al['alumno_id'] ?>" 
                                    data-matricula="<?= $al['matricula_id'] ?>"
                                    data-pago-mat="<?= $al['ya_pago_matricula'] ?>"
                                    <?= ((int)$al['alumno_id'] === $alumnoSeleccionadoId) ? 'selected' : '' ?>>
                                <?= htmlspecialchars($al['apellidos'] . ', ' . $al['nombres'] . ' (DNI: ' . $al['dni'] . ' - ' . $al['grado_nombre'] . ')') ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                    <input type="hidden" name="matricula_id" id="inputMatriculaId" value="<?= $alumnoData['matricula_id'] ?? 0 ?>">
                </div>

                <!-- 2. Concepto: Matrícula Anual (Toggle Interactivo) -->
                <div class="mb-4 p-3 rounded-3 border bg-light">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <span class="fw-bold text-dark d-block">Matrícula Anual 2026 (S/ 350.00)</span>
                            <span class="small text-muted">Pago único por apertura de expediente escolar</span>
                        </div>
                        <div class="form-check form-switch fs-4 mb-0">
                            <input class="form-check-input" type="checkbox" role="switch" id="toggleMatricula" name="incluir_matricula" value="1" onchange="recalcularTotal()">
                        </div>
                    </div>
                    <!-- Aviso si ya pagó matrícula -->
                    <div id="avisoMatriculaPagada" class="mt-2 text-success small fw-bold" style="display: none;">
                        <i class="bi bi-check-circle-fill me-1"></i> ESTE ALUMNO YA PAGÓ LA MATRÍCULA
                    </div>
                </div>

                <!-- 3. Mensualidad / Pensión -->
                <div class="mb-4">
                    <label class="form-label small fw-bold text-dark mb-1">3. Mensualidad / Pensión Escolar</label>
                    <select name="mes_pension" id="selectPension" class="form-select" onchange="recalcularTotal()">
                        <option value="" data-precio="0">-- No cobrar pensión en este recibo --</option>
                        <option value="Marzo 2026" data-precio="400">Pensión Marzo 2026 (S/ 400.00)</option>
                        <option value="Abril 2026" data-precio="400">Pensión Abril 2026 (S/ 400.00)</option>
                        <option value="Mayo 2026" data-precio="400">Pensión Mayo 2026 (S/ 400.00)</option>
                        <option value="Junio 2026" data-precio="400">Pensión Junio 2026 (S/ 400.00)</option>
                    </select>
                </div>

                <!-- 4. Método de Pago -->
                <div class="mb-4">
                    <label class="form-label small fw-bold text-dark mb-1">4. Método de Pago <span class="text-danger">*</span></label>
                    <div class="row g-2">
                        <div class="col-3">
                            <input type="radio" class="btn-check" name="metodo_pago" id="met_efectivo" value="Efectivo" checked>
                            <label class="btn btn-outline-secondary w-100 py-2 small fw-bold" for="met_efectivo">
                                <i class="bi bi-cash me-1"></i> Efectivo
                            </label>
                        </div>
                        <div class="col-3">
                            <input type="radio" class="btn-check" name="metodo_pago" id="met_yape" value="Yape">
                            <label class="btn btn-outline-secondary w-100 py-2 small fw-bold" for="met_yape">
                                <i class="bi bi-phone me-1"></i> Yape
                            </label>
                        </div>
                        <div class="col-3">
                            <input type="radio" class="btn-check" name="metodo_pago" id="met_plin" value="Plin">
                            <label class="btn btn-outline-secondary w-100 py-2 small fw-bold" for="met_plin">
                                <i class="bi bi-phone me-1"></i> Plin
                            </label>
                        </div>
                        <div class="col-3">
                            <input type="radio" class="btn-check" name="metodo_pago" id="met_bcp" value="Transferencia BCP">
                            <label class="btn btn-outline-secondary w-100 py-2 small fw-bold" for="met_bcp">
                                <i class="bi bi-bank me-1"></i> BCP
                            </label>
                        </div>
                    </div>
                </div>

                <!-- 5. Comprobante Opcional -->
                <div class="mb-4">
                    <label class="form-label small fw-bold text-dark mb-1">5. Comprobante / Voucher (Opcional)</label>
                    <input type="file" name="comprobante" class="form-control" accept="image/*">
                </div>

                <!-- TOTALIZADOR GRANDE EN PANTALLA -->
                <div class="p-3 rounded-3 text-center mb-4" style="background: linear-gradient(135deg, #1E1B4B 0%, #4338CA 100%); color: white;">
                    <div class="text-white text-opacity-75 small text-uppercase fw-bold">TOTAL A PAGAR</div>
                    <div class="display-5 fw-bolder" id="displayTotal">S/ 0.00</div>
                    <input type="hidden" name="monto_total" id="inputMontoTotal" value="0.00">
                </div>

                <div class="d-flex justify-content-between align-items-center pt-3 border-top">
                    <a href="<?= url('views/caja.php') ?>" class="btn btn-light px-4">Cancelar</a>
                    <button type="submit" class="btn btn-dyl-green px-4 py-2.5 shadow-sm fw-bold">
                        <i class="bi bi-check2-circle me-1"></i> Procesar Pago
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
function cambiarAlumno(alumnoId) {
    const select = document.getElementById('selectAlumno');
    const selectedOpt = select.options[select.selectedIndex];
    const matriculaId = selectedOpt.getAttribute('data-matricula');
    const yaPagoMat = selectedOpt.getAttribute('data-pago-mat') === '1';

    document.getElementById('inputMatriculaId').value = matriculaId;

    const toggleMat = document.getElementById('toggleMatricula');
    const aviso = document.getElementById('avisoMatriculaPagada');

    if (yaPagoMat) {
        toggleMat.checked = false;
        toggleMat.disabled = true;
        aviso.style.display = 'block';
    } else {
        toggleMat.disabled = false;
        aviso.style.display = 'none';
    }
    recalcularTotal();
}

function recalcularTotal() {
    let total = 0;
    const toggleMat = document.getElementById('toggleMatricula');
    if (toggleMat.checked && !toggleMat.disabled) {
        total += 350;
    }

    const selectPension = document.getElementById('selectPension');
    const optPension = selectPension.options[selectPension.selectedIndex];
    const precioPension = parseFloat(optPension.getAttribute('data-precio') || 0);
    total += precioPension;

    document.getElementById('displayTotal').innerText = 'S/ ' + total.toFixed(2);
    document.getElementById('inputMontoTotal').value = total.toFixed(2);
}

document.addEventListener('DOMContentLoaded', function () {
    cambiarAlumno(document.getElementById('selectAlumno').value);
});
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
