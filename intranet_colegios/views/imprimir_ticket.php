<?php
// views/imprimir_ticket.php - Módulo 9: Ticket Térmico POS 80mm DYL SCHOOL
require_once __DIR__ . '/../config/app.php';
require_login();

$pdo = Database::getConnection();
$pagoId = (int)($_GET['id'] ?? 0);

if ($pagoId <= 0) {
    $first = $pdo->query("SELECT id FROM pagos ORDER BY id DESC LIMIT 1")->fetchColumn();
    $pagoId = (int)$first;
}

$stmtPago = $pdo->prepare("
    SELECT p.*, a.nombres, a.apellidos, a.dni, a.telefono_apoderado,
           u.nombres as cajero_nombres, u.apellidos as cajero_apellidos
    FROM pagos p
    JOIN alumnos a ON p.alumno_id = a.id
    LEFT JOIN usuarios u ON p.usuario_cajero_id = u.id
    WHERE p.id = ?
");
$stmtPago->execute([$pagoId]);
$pago = $stmtPago->fetch();

if (!$pago) {
    die("Recibo no encontrado.");
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ticket <?= htmlspecialchars($pago['numero_recibo']) ?> · DYL SCHOOL</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
    <link rel="stylesheet" href="<?= asset('css/dyl_school.css') ?>">
    <style>
        body {
            background-color: #E2E8F0;
            padding: 20px;
            font-family: 'Courier New', Courier, monospace;
        }
        .pos-ticket-container {
            width: 80mm;
            background: white;
            padding: 6mm;
            margin: 0 auto;
            border: 1px solid #CBD5E1;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            font-size: 12px;
            line-height: 1.3;
        }
        .ticket-divider {
            border-top: 1px dashed #475569;
            margin: 8px 0;
        }
        .ticket-double-divider {
            border-top: 2px dashed #000000;
            margin: 8px 0;
        }
        @media print {
            body {
                background: white !important;
                padding: 0 !important;
            }
            .pos-ticket-container {
                width: 80mm !important;
                border: none !important;
                box-shadow: none !important;
                padding: 2mm !important;
            }
            .no-print {
                display: none !important;
            }
        }
    </style>
</head>
<body class="pos-ticket-body">

<!-- Botones Flotantes de Control -->
<div class="text-center mb-3 no-print">
    <button onclick="window.print()" class="btn btn-primary btn-sm px-4 fw-bold me-2">
        <i class="bi bi-printer-fill me-1"></i> Imprimir Ticket
    </button>
    <button onclick="window.close()" class="btn btn-secondary btn-sm px-3">
        <i class="bi bi-x-lg me-1"></i> Cerrar Pestaña
    </button>
</div>

<!-- Ticket Térmico 80mm -->
<div class="pos-ticket-container">
    <!-- Encabezado del Colegio -->
    <div class="text-center">
        <h4 class="fw-bold mb-0" style="font-size: 18px; letter-spacing: 0.05em;">DYL SCHOOL</h4>
        <div>I.E. PRIVADA DYL SCHOOL</div>
        <div>RUC: 20601234567</div>
        <div>Av. Los Próceres 1234, Lima</div>
        <div>Telf: +51 987 654 321</div>
    </div>

    <div class="ticket-divider"></div>

    <!-- Metadatos de Transacción -->
    <div>
        <div><strong>TICKET:</strong> <?= htmlspecialchars($pago['numero_recibo']) ?></div>
        <div><strong>FECHA:</strong> <?= date('d/m/Y H:i:s', strtotime($pago['fecha_pago'])) ?></div>
        <div><strong>CAJERO:</strong> <?= htmlspecialchars($pago['cajero_nombres'] ?? 'Caja Central') ?></div>
        <div><strong>MÉTODO:</strong> <?= htmlspecialchars($pago['metodo_pago']) ?></div>
    </div>

    <div class="ticket-divider"></div>

    <!-- Datos del Alumno -->
    <div>
        <div><strong>ALUMNO:</strong> <?= htmlspecialchars($pago['apellidos'] . ', ' . $pago['nombres']) ?></div>
        <div><strong>DNI:</strong> <?= htmlspecialchars($pago['dni']) ?></div>
        <div><strong>TELF:</strong> <?= htmlspecialchars($pago['telefono_apoderado'] ?? '-') ?></div>
    </div>

    <div class="ticket-double-divider"></div>

    <!-- Desglose de Cobro -->
    <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
        <thead>
            <tr style="border-bottom: 1px dashed #000;">
                <th style="text-align: left; padding-bottom: 4px;">DESCRIPCIÓN</th>
                <th style="text-align: right; padding-bottom: 4px;">TOTAL</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 6px 0;"><?= htmlspecialchars($pago['concepto']) ?></td>
                <td style="text-align: right; font-weight: bold;"><?= money_format_pen((float)$pago['monto']) ?></td>
            </tr>
        </tbody>
    </table>

    <div class="ticket-double-divider"></div>

    <!-- Totalizador -->
    <div class="d-flex justify-content-between fs-6 fw-bold">
        <span>TOTAL PAGADO:</span>
        <span><?= money_format_pen((float)$pago['monto']) ?></span>
    </div>

    <div class="ticket-divider"></div>

    <!-- Mensaje de Despedida -->
    <div class="text-center mt-3" style="font-size: 11px;">
        <div class="fw-bold">¡Gracias por su puntualidad!</div>
        <div class="text-muted small">Conserve este comprobante para cualquier trámite o reclamo administrativo.</div>
        <div class="mt-2 text-muted" style="font-size: 9px;">DYL IMPORT Systems v1.0</div>
    </div>
</div>

</body>
</html>
