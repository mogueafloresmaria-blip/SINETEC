/**
 * SINETEC - Script de Antigravity para transformación de color
 * Identifica todos los elementos con tonalidades verdes y los sustituye de forma
 * persistente por el azul oficial #2196F3 sin alterar otros colores.
 */
(function () {
    const TARGET_BLUE = '#2196F3';
    const TARGET_BLUE_HOVER = '#1976D2';
    const TARGET_BLUE_LIGHT = '#E3F2FD';
    const TARGET_BLUE_BORDER = '#BBDEFB';

    function injectAntigravityStyles() {
        if (document.getElementById('antigravity-color-override')) return;
        const style = document.createElement('style');
        style.id = 'antigravity-color-override';
        style.textContent = `
            :root {
                --sinetec-blue: ${TARGET_BLUE} !important;
                --sinetec-primary: ${TARGET_BLUE} !important;
                --sinetec-primary-dark: ${TARGET_BLUE_HOVER} !important;
                --sinetec-secondary: #64B5F6 !important;
                --sinetec-accent: ${TARGET_BLUE_LIGHT} !important;
                --sinetec-blue-soft: #F0F9FF !important;
                --sinetec-blue-border: ${TARGET_BLUE_BORDER} !important;
                --sinetec-blue-deep: #0D47A1 !important;
                --bs-primary: ${TARGET_BLUE} !important;
                --bs-primary-rgb: 33, 150, 243 !important;
                --bs-link-color: ${TARGET_BLUE} !important;
                --bs-link-hover-color: ${TARGET_BLUE_HOVER} !important;
            }

            /* Forzar reemplazo de clases verdes de Bootstrap a azul #2196F3 */
            .text-success, .text-sinetec-green {
                color: ${TARGET_BLUE} !important;
            }
            .btn-success, .btn-sinetec-primary, .sinetec-btn-primary {
                background-color: ${TARGET_BLUE} !important;
                border-color: ${TARGET_BLUE} !important;
                color: #ffffff !important;
            }
            .btn-success:hover, .btn-sinetec-primary:hover, .sinetec-btn-primary:hover {
                background-color: ${TARGET_BLUE_HOVER} !important;
                border-color: ${TARGET_BLUE_HOVER} !important;
                color: #ffffff !important;
            }
            .btn-outline-success {
                color: ${TARGET_BLUE} !important;
                border-color: ${TARGET_BLUE} !important;
            }
            .btn-outline-success:hover {
                background-color: ${TARGET_BLUE} !important;
                border-color: ${TARGET_BLUE} !important;
                color: #ffffff !important;
            }
            .badge.bg-success:not(.badge-status-keep),
            .badge-success {
                background-color: ${TARGET_BLUE} !important;
                color: #ffffff !important;
            }
            .bg-success.bg-opacity-10, .bg-success.bg-opacity-15 {
                background-color: ${TARGET_BLUE_LIGHT} !important;
            }
            .border-success {
                border-color: ${TARGET_BLUE_BORDER} !important;
            }

            /* Resaltes y selecciones de navegación activa */
            .sinetec-nav .nav-link.active,
            .sinetec-nav .nav-link:hover {
                background: linear-gradient(135deg, rgba(33, 150, 243, 0.25), rgba(33, 150, 243, 0.10)) !important;
                border-color: rgba(33, 150, 243, 0.40) !important;
            }
            .sinetec-nav .nav-link.active i,
            .sinetec-nav .nav-link:hover i {
                color: #64B5F6 !important;
            }
        `;
        document.head.appendChild(style);
    }

    function isGreenColor(colorStr) {
        if (!colorStr) return false;
        colorStr = colorStr.toLowerCase().trim();
        // Verificar hex verdes conocidos del SENA
        if (colorStr.includes('#39a900') || colorStr.includes('#1f5e2d') || colorStr.includes('#8ccb65') || colorStr.includes('#059669')) {
            return true;
        }
        // Verificar formato rgb(r, g, b)
        const match = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        if (match) {
            const r = parseInt(match[1], 10);
            const g = parseInt(match[2], 10);
            const b = parseInt(match[3], 10);
            // Si el verde predomina notablemente sobre rojo y azul (tono verdoso)
            if (g > 100 && g > r * 1.35 && g > b * 1.35) {
                return true;
            }
        }
        return false;
    }

    function scanAndTransform(rootElement) {
        const elements = (rootElement || document).querySelectorAll('*');
        elements.forEach(el => {
            // Verificar color de texto en línea
            if (el.style.color && isGreenColor(el.style.color)) {
                el.style.color = TARGET_BLUE;
            }
            // Verificar color de fondo en línea
            if (el.style.backgroundColor && isGreenColor(el.style.backgroundColor)) {
                el.style.backgroundColor = TARGET_BLUE;
                el.style.borderColor = TARGET_BLUE;
            }
            // Verificar bordes en línea
            if (el.style.borderColor && isGreenColor(el.style.borderColor)) {
                el.style.borderColor = TARGET_BLUE;
            }
            // Elementos SVG
            if (el.tagName && el.tagName.toLowerCase() === 'path' || el.tagName.toLowerCase() === 'circle') {
                const fill = el.getAttribute('fill');
                if (fill && isGreenColor(fill)) {
                    el.setAttribute('fill', TARGET_BLUE);
                }
                const stroke = el.getAttribute('stroke');
                if (stroke && isGreenColor(stroke)) {
                    el.setAttribute('stroke', TARGET_BLUE);
                }
            }
        });
    }

    // Inicialización inmediata y persistente
    function initAntigravityColor() {
        injectAntigravityStyles();
        scanAndTransform(document.body);

        // Observer para asegurar persistencia ante mutaciones del DOM (modales, filtrado dinámico, AJAX)
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        scanAndTransform(node);
                    }
                });
            });
        });

        if (document.body) {
            observer.observe(document.body, { childList: true, subtree: true });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAntigravityColor);
    } else {
        initAntigravityColor();
    }
})();
