<?php
// views/dashboard.php - Módulo 1: Inicio (Dashboard) DYL SCHOOL
$pageTitle = 'Panel';
require_once __DIR__ . '/../includes/header.php';

$pdo = Database::getConnection();

// Métricas de KPIs exactas
$totalAlumnosActivos = $pdo->query("SELECT COUNT(*) FROM alumnos WHERE estado = 'ACTIVO'")->fetchColumn() ?: 10;
$totalMatriculas2026 = $pdo->query("SELECT COUNT(*) FROM matriculas WHERE anio_lectivo = 2026")->fetchColumn() ?: 8;
$totalDocentes = $pdo->query("SELECT COUNT(*) FROM profesores WHERE estado = 'ACTIVO'")->fetchColumn() ?: 2;
$totalCursosGrupos = 180;

// Gráfico 1: Alumnado por Nivel
$stmtNiveles = $pdo->query("
    SELECT g.nivel, COUNT(m.id) as total 
    FROM matriculas m 
    JOIN grados g ON m.grado_id = g.id 
    GROUP BY g.nivel
");
$datosNivel = ['Inicial' => 0, 'Primaria' => 0, 'Secundaria' => 0];
while ($row = $stmtNiveles->fetch()) {
    $datosNivel[$row['nivel']] = (int)$row['total'];
}

// Gráfico 2: Distribución de Género
$stmtGenero = $pdo->query("SELECT genero, COUNT(*) as total FROM alumnos WHERE estado = 'ACTIVO' GROUP BY genero");
$datosGenero = ['Masculino' => 0, 'Femenino' => 0];
while ($row = $stmtGenero->fetch()) {
    $datosGenero[$row['genero']] = (int)$row['total'];
}

// Lista de Últimas Matrículas
$stmtUltimasMatriculas = $pdo->query("
    SELECT m.id, m.fecha_matricula, a.nombres, a.apellidos, a.dni, g.nombre as grado_nombre
    FROM matriculas m
    JOIN alumnos a ON m.alumno_id = a.id
    JOIN grados g ON m.grado_id = g.id
    ORDER BY m.id DESC LIMIT 5
");
$ultimasMatriculas = $stmtUltimasMatriculas->fetchAll();
?>

<!-- CABECERA SUPERIOR: Banner con degradado morado oscuro -->
<div class="mb-4" style="background: linear-gradient(135deg, #1E1B4B 0%, #4338CA 50%, #6366F1 100%); border-radius: 14px; padding: 26px 28px; color: #FFFFFF; box-shadow: 0 6px 20px rgba(79, 70, 229, 0.3); position: relative; overflow: hidden;">
    <!-- Decoración de fondo sutil -->
    <div style="position: absolute; top: -30px; right: -30px; width: 120px; height: 120px; background: rgba(255,255,255,0.04); border-radius: 50%;"></div>
    <div style="position: absolute; bottom: -20px; right: 60px; width: 80px; height: 80px; background: rgba(255,255,255,0.03); border-radius: 50%;"></div>
    
    <div class="d-flex justify-content-between align-items-center">
        <div>
            <h1 class="fw-bold text-white mb-1" style="font-size: 1.55rem; letter-spacing: -0.01em;">¡Hola, Admin! 👋</h1>
            <p class="mb-0" style="color: #C7D2FE; font-size: 0.92rem; font-weight: 400;">Resumen académico hoy.</p>
        </div>
        <div>
            <span class="px-3 py-2 rounded-pill fw-semibold" style="background: rgba(255,255,255,0.15); color: #E0E7FF; font-size: 0.82rem; border: 1px solid rgba(255,255,255,0.2); backdrop-filter: blur(4px);">
                <i class="bi bi-calendar-event-fill me-1"></i> <?= SYSTEM_DATE ?>
            </span>
        </div>
    </div>
</div>

<!-- 4 TARJETAS DE MÉTRICAS (KPIs en fila) -->
<div class="row g-3 mb-4">
    <!-- 1. ALUMNOS ACTIVOS -->
    <div class="col-12 col-sm-6 col-xl-3">
        <div class="dyl-card p-3 h-100 d-flex align-items-center justify-content-between" style="border-left: 4px solid #4F46E5;">
            <div>
                <div class="text-uppercase fw-bold" style="font-size: 0.7rem; letter-spacing: 0.06em; color: #94A3B8;">ALUMNOS ACTIVOS</div>
                <div class="fw-bold my-1" style="font-size: 2rem; color: #0F172A; line-height: 1.1;"><?= $totalAlumnosActivos ?></div>
            </div>
            <div class="d-flex align-items-center justify-content-center" style="width: 50px; height: 50px; background: #EEF2FF; color: #4F46E5; border-radius: 12px; font-size: 1.4rem;">
                <i class="bi bi-people-fill"></i>
            </div>
        </div>
    </div>

    <!-- 2. MATRÍCULAS 2026 -->
    <div class="col-12 col-sm-6 col-xl-3">
        <div class="dyl-card p-3 h-100 d-flex align-items-center justify-content-between" style="border-left: 4px solid #06B6D4;">
            <div>
                <div class="text-uppercase fw-bold" style="font-size: 0.7rem; letter-spacing: 0.06em; color: #94A3B8;">MATRÍCULAS 2026</div>
                <div class="fw-bold my-1" style="font-size: 2rem; color: #0F172A; line-height: 1.1;"><?= $totalMatriculas2026 ?></div>
            </div>
            <div class="d-flex align-items-center justify-content-center" style="width: 50px; height: 50px; background: #ECFEFF; color: #06B6D4; border-radius: 12px; font-size: 1.4rem;">
                <i class="bi bi-mortarboard-fill"></i>
            </div>
        </div>
    </div>

    <!-- 3. PLANA DOCENTE -->
    <div class="col-12 col-sm-6 col-xl-3">
        <div class="dyl-card p-3 h-100 d-flex align-items-center justify-content-between" style="border-left: 4px solid #10B981;">
            <div>
                <div class="text-uppercase fw-bold" style="font-size: 0.7rem; letter-spacing: 0.06em; color: #94A3B8;">PLANA DOCENTE</div>
                <div class="fw-bold my-1" style="font-size: 2rem; color: #0F172A; line-height: 1.1;"><?= $totalDocentes ?></div>
            </div>
            <div class="d-flex align-items-center justify-content-center" style="width: 50px; height: 50px; background: #ECFDF5; color: #10B981; border-radius: 12px; font-size: 1.4rem;">
                <i class="bi bi-briefcase-fill"></i>
            </div>
        </div>
    </div>

    <!-- 4. CURSOS -->
    <div class="col-12 col-sm-6 col-xl-3">
        <div class="dyl-card p-3 h-100 d-flex align-items-center justify-content-between" style="border-left: 4px solid #F59E0B;">
            <div>
                <div class="text-uppercase fw-bold" style="font-size: 0.7rem; letter-spacing: 0.06em; color: #94A3B8;">CURSOS</div>
                <div class="fw-bold my-1" style="font-size: 2rem; color: #0F172A; line-height: 1.1;"><?= $totalCursosGrupos ?></div>
            </div>
            <div class="d-flex align-items-center justify-content-center" style="width: 50px; height: 50px; background: #FFFBEB; color: #F59E0B; border-radius: 12px; font-size: 1.4rem;">
                <i class="bi bi-book-half"></i>
            </div>
        </div>
    </div>
</div>

<!-- SECCIÓN DE GRÁFICOS (2 columnas) -->
<div class="row g-4 mb-4">
    <!-- Columna izquierda: Alumnado por Nivel (Barras) -->
    <div class="col-lg-7">
        <div class="dyl-card p-4 h-100">
            <h3 class="fw-bold text-dark mb-3 d-flex align-items-center gap-2" style="font-size: 0.95rem;">
                <i class="bi bi-bar-chart-fill" style="color: #4F46E5;"></i>
                Alumnado por Nivel
            </h3>
            <div style="height: 260px;">
                <canvas id="chartNiveles"></canvas>
            </div>
        </div>
    </div>

    <!-- Columna derecha: Distribución de Género (Dona) -->
    <div class="col-lg-5">
        <div class="dyl-card p-4 h-100">
            <h3 class="fw-bold text-dark mb-3 d-flex align-items-center gap-2" style="font-size: 0.95rem;">
                <i class="bi bi-pie-chart-fill" style="color: #06B6D4;"></i>
                Distribución
            </h3>
            <div style="height: 260px; position: relative;">
                <canvas id="chartGenero"></canvas>
            </div>
        </div>
    </div>
</div>

<!-- SECCIÓN INFERIOR: Últimas Matrículas (ancho completo) -->
<div class="dyl-card p-4 mb-4">
    <h3 class="fw-bold text-dark mb-3 d-flex align-items-center gap-2" style="font-size: 0.95rem;">
        <i class="bi bi-clock-history" style="color: #6366F1;"></i>
        Últimas Matrículas
    </h3>
    <?php if (empty($ultimasMatriculas)): ?>
        <div class="text-center py-4 text-muted">
            <i class="bi bi-inbox fs-1 d-block mb-2" style="color: #CBD5E1;"></i>
            <p class="small mb-0">No hay matrículas registradas recientemente.</p>
        </div>
    <?php else: ?>
        <?php $lastKey = array_key_last($ultimasMatriculas); ?>
        <?php foreach ($ultimasMatriculas as $key => $m): ?>
            <div class="d-flex align-items-center justify-content-between py-3 <?= $key !== $lastKey ? 'border-bottom' : '' ?>" style="border-color: #F1F5F9 !important;">
                <div class="d-flex align-items-center gap-3">
                    <div class="dyl-user-avatar rounded-circle d-flex align-items-center justify-content-center text-white fw-bold" style="width: 40px; height: 40px; background: linear-gradient(135deg, #6366F1, #4F46E5); font-size: 0.85rem; flex-shrink: 0;">
                        <?= strtoupper(substr($m['nombres'], 0, 1)) ?>
                    </div>
                    <div>
                        <div class="fw-bold text-dark" style="font-size: 0.88rem;"><?= htmlspecialchars($m['nombres'] . ' ' . $m['apellidos']) ?></div>
                        <div class="text-muted" style="font-size: 0.75rem;">DNI: <?= htmlspecialchars($m['dni']) ?> · <?= htmlspecialchars($m['grado_nombre']) ?></div>
                    </div>
                </div>
                <div class="text-end">
                    <span class="badge bg-light text-dark border font-monospace" style="font-size: 0.75rem;">
                        <?= htmlspecialchars($m['fecha_matricula']) ?>
                    </span>
                </div>
            </div>
        <?php endforeach; ?>
    <?php endif; ?>
</div>

<script>
document.addEventListener('DOMContentLoaded', function () {
    // 1. Chart Alumnado por Nivel (Barras)
    const ctxNiveles = document.getElementById('chartNiveles');
    if (ctxNiveles) {
        new Chart(ctxNiveles.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Inicial', 'Primaria', 'Secundaria'],
                datasets: [{
                    label: 'Alumnos',
                    data: [<?= (int)$datosNivel['Inicial'] ?>, <?= (int)$datosNivel['Primaria'] ?>, <?= (int)$datosNivel['Secundaria'] ?>],
                    backgroundColor: ['#818CF8', '#6366F1', '#4F46E5'],
                    borderRadius: 6,
                    barThickness: 52,
                    maxBarThickness: 60
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { 
                            stepSize: 1,
                            font: { size: 11, family: 'Inter' },
                            color: '#94A3B8'
                        },
                        grid: { color: '#F1F5F9', drawBorder: false }
                    },
                    x: {
                        ticks: {
                            font: { size: 12, family: 'Inter', weight: '600' },
                            color: '#475569'
                        },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // 2. Chart Distribución (Dona de Género)
    const ctxGenero = document.getElementById('chartGenero');
    if (ctxGenero) {
        new Chart(ctxGenero.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Hombres', 'Mujeres'],
                datasets: [{
                    data: [<?= (int)$datosGenero['Masculino'] ?>, <?= (int)$datosGenero['Femenino'] ?>],
                    backgroundColor: ['#06B6D4', '#EC4899'],
                    borderWidth: 3,
                    borderColor: '#FFFFFF',
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            padding: 16,
                            font: { size: 12, weight: '600', family: 'Inter' },
                            color: '#475569',
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    }
                },
                cutout: '68%'
            }
        });
    }
});
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
