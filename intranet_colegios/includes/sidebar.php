<?php
// includes/sidebar.php - Menú lateral compartido fijo de dos columnas para DYL SCHOOL
$currentPage = basename($_SERVER['SCRIPT_NAME'] ?? $_SERVER['PHP_SELF'] ?? '');
?>
<aside class="dyl-sidebar w-64 min-w-[260px] h-screen" id="dylSidebar" style="width: 260px !important; min-width: 260px !important; max-width: 260px !important; height: 100vh !important; position: fixed !important; top: 0 !important; left: 0 !important; bottom: 0 !important; background-color: #0F172A !important; color: #F8FAFC !important; z-index: 1050 !important; display: flex !important; flex-direction: column !important; overflow-y: auto !important; border-right: 1px solid rgba(255, 255, 255, 0.08) !important; box-shadow: 2px 0 12px rgba(0, 0, 0, 0.25) !important; visibility: visible !important; opacity: 1 !important;">
    <!-- LOGOTIPO Y CABECERA -->
    <div class="dyl-brand" style="padding: 20px 18px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
        <div class="dyl-brand-icon" style="width: 42px; height: 42px; background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #FFFFFF; font-size: 22px; box-shadow: 0 4px 14px rgba(139, 92, 246, 0.45); flex-shrink: 0;">
            <i class="bi bi-mortarboard-fill"></i>
        </div>
        <div>
            <h1 class="dyl-brand-title" style="font-size: 1.2rem; font-weight: 800; letter-spacing: 0.05em; color: #FFFFFF; margin: 0; line-height: 1.2;">DYL SCHOOL</h1>
            <span class="dyl-brand-subtitle" style="font-size: 0.72rem; color: #94A3B8; font-weight: 500; display: block; margin-top: 2px;">Gestión Escolar</span>
        </div>
    </div>

    <!-- LISTA DE NAVEGACIÓN (13 MÓDULOS EN 2 CATEGORÍAS) -->
    <ul class="dyl-menu" style="list-style: none; padding: 12px 10px; margin: 0; flex: 1;">
        <!-- SECCIÓN 1: ACADÉMICO -->
        <li class="dyl-menu-category" style="font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em; color: #94A3B8; text-transform: uppercase; padding: 10px 14px 6px 14px; user-select: none;">ACADÉMICO</li>

        <li class="dyl-menu-item" style="margin-bottom: 3px;">
            <a href="<?= url('views/dashboard.php') ?>" class="dyl-menu-link <?= $currentPage === 'dashboard.php' ? 'active' : '' ?>">
                <i class="bi bi-house-door-fill"></i>
                <span>Inicio</span>
            </a>
        </li>
        <li class="dyl-menu-item" style="margin-bottom: 3px;">
            <a href="<?= url('views/alumnos.php') ?>" class="dyl-menu-link <?= in_array($currentPage, ['alumnos.php', 'alumno_nuevo.php', 'alumno_editar.php']) ? 'active' : '' ?>">
                <i class="bi bi-person-fill"></i>
                <span>Alumnos</span>
            </a>
        </li>
        <li class="dyl-menu-item" style="margin-bottom: 3px;">
            <a href="<?= url('views/matriculas.php') ?>" class="dyl-menu-link <?= in_array($currentPage, ['matriculas.php', 'matricula_nueva.php']) ? 'active' : '' ?>">
                <i class="bi bi-file-earmark-text-fill"></i>
                <span>Matrículas</span>
            </a>
        </li>
        <li class="dyl-menu-item" style="margin-bottom: 3px;">
            <a href="<?= url('views/horarios.php') ?>" class="dyl-menu-link <?= $currentPage === 'horarios.php' ? 'active' : '' ?>">
                <i class="bi bi-clock-fill"></i>
                <span>Horarios</span>
            </a>
        </li>
        <li class="dyl-menu-item" style="margin-bottom: 3px;">
            <a href="<?= url('views/profesores.php') ?>" class="dyl-menu-link <?= in_array($currentPage, ['profesores.php', 'profesor_nuevo.php']) ? 'active' : '' ?>">
                <i class="bi bi-person-workspace"></i>
                <span>Profesores</span>
            </a>
        </li>
        <li class="dyl-menu-item" style="margin-bottom: 3px;">
            <a href="<?= url('views/asignaciones.php') ?>" class="dyl-menu-link <?= $currentPage === 'asignaciones.php' ? 'active' : '' ?>">
                <i class="bi bi-briefcase-fill"></i>
                <span>Carga Acad.</span>
            </a>
        </li>
        <li class="dyl-menu-item" style="margin-bottom: 3px;">
            <a href="<?= url('views/cursos.php') ?>" class="dyl-menu-link <?= in_array($currentPage, ['cursos.php', 'curso_nuevo.php']) ? 'active' : '' ?>">
                <i class="bi bi-book-fill"></i>
                <span>Cursos</span>
            </a>
        </li>
        <li class="dyl-menu-item" style="margin-bottom: 3px;">
            <a href="<?= url('views/notas.php') ?>" class="dyl-menu-link <?= in_array($currentPage, ['notas.php', 'calificar_alumno.php', 'ver_libreta.php']) ? 'active' : '' ?>">
                <i class="bi bi-trophy-fill"></i>
                <span>Notas</span>
            </a>
        </li>

        <!-- SECCIÓN 2: ADMINISTRACIÓN -->
        <li class="dyl-menu-category" style="font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em; color: #94A3B8; text-transform: uppercase; padding: 14px 14px 6px 14px; user-select: none;">ADMINISTRACIÓN</li>

        <li class="dyl-menu-item" style="margin-bottom: 3px;">
            <a href="<?= url('views/caja.php') ?>" class="dyl-menu-link <?= in_array($currentPage, ['caja.php', 'caja_nuevo.php', 'imprimir_ticket.php']) ? 'active' : '' ?>">
                <i class="bi bi-cash-stack"></i>
                <span>Pensiones</span>
            </a>
        </li>
        <li class="dyl-menu-item" style="margin-bottom: 3px;">
            <a href="<?= url('views/usuarios.php') ?>" class="dyl-menu-link <?= in_array($currentPage, ['usuarios.php', 'usuario_nuevo.php']) ? 'active' : '' ?>">
                <i class="bi bi-shield-lock-fill"></i>
                <span>Usuarios</span>
            </a>
        </li>
        <li class="dyl-menu-item" style="margin-bottom: 3px;">
            <a href="<?= url('views/comunicados.php') ?>" class="dyl-menu-link <?= $currentPage === 'comunicados.php' ? 'active' : '' ?>">
                <i class="bi bi-megaphone-fill"></i>
                <span>Comunicados</span>
            </a>
        </li>
        <li class="dyl-menu-item" style="margin-bottom: 3px;">
            <a href="<?= url('views/asistencia.php') ?>" class="dyl-menu-link <?= $currentPage === 'asistencia.php' ? 'active' : '' ?>">
                <i class="bi bi-clipboard-check-fill"></i>
                <span>Tomar Asist.</span>
            </a>
        </li>
        <li class="dyl-menu-item" style="margin-bottom: 3px;">
            <a href="<?= url('views/transporte.php') ?>" class="dyl-menu-link <?= in_array($currentPage, ['transporte.php', 'transporte_nuevo.php']) ? 'active' : '' ?>">
                <i class="bi bi-bus-front-fill"></i>
                <span>Transporte</span>
            </a>
        </li>
    </ul>

    <!-- PARTE INFERIOR DEL MENÚ (Línea divisoria sutil + Cerrar Sesión) -->
    <div class="dyl-sidebar-footer" style="padding: 14px; border-top: 1px solid rgba(255, 255, 255, 0.08); margin-top: auto;">
        <a href="<?= url('logout.php') ?>" class="dyl-logout-btn" style="display: flex; align-items: center; gap: 10px; width: 100%; padding: 10px 14px; background: rgba(239, 68, 68, 0.12); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 8px; font-size: 0.85rem; font-weight: 600; text-decoration: none; transition: all 0.2s ease;">
            <i class="bi bi-box-arrow-right"></i>
            <span>Cerrar Sesión</span>
        </a>
    </div>
</aside>
