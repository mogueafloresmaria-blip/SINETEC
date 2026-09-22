// assets/js/dyl_school.js - Interactividad para DYL SCHOOL

document.addEventListener('DOMContentLoaded', function () {
    // 1. Buscador en tiempo real para tablas con atributo data-table-search
    const searchInputs = document.querySelectorAll('[data-table-search]');
    searchInputs.forEach(input => {
        const targetTableId = input.getAttribute('data-table-search');
        const targetTable = document.getElementById(targetTableId);
        if (!targetTable) return;

        input.addEventListener('input', function () {
            const query = this.value.toLowerCase().trim();
            const rows = targetTable.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    });

    // 2. Buscador en tiempo real para tarjetas con atributo data-card-search
    const cardSearchInputs = document.querySelectorAll('[data-card-search]');
    cardSearchInputs.forEach(input => {
        const targetContainerId = input.getAttribute('data-card-search');
        const targetContainer = document.getElementById(targetContainerId);
        if (!targetContainer) return;

        input.addEventListener('input', function () {
            const query = this.value.toLowerCase().trim();
            const cards = targetContainer.querySelectorAll('.searchable-card');
            cards.forEach(card => {
                const text = card.innerText.toLowerCase();
                card.style.display = text.includes(query) ? '' : 'none';
            });
        });
    });

    // 3. Alternar visibilidad de contraseña (ojo)
    const eyeToggles = document.querySelectorAll('.toggle-password');
    eyeToggles.forEach(toggle => {
        toggle.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const targetInput = document.getElementById(targetId);
            if (!targetInput) return;

            const isPassword = targetInput.type === 'password';
            targetInput.type = isPassword ? 'text' : 'password';
            
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('bi-eye', !isPassword);
                icon.classList.toggle('bi-eye-slash', isPassword);
            }
        });
    });
});

// 4. Helper de Asistencia: Marcar Todos Presentes
function marcarTodosPresentes() {
    const presentRadios = document.querySelectorAll('input[type="radio"][value="Presente"]');
    presentRadios.forEach(radio => {
        radio.checked = true;
    });
}

// 5. Helper de Horarios: Alternar AM / PM
function toggleAmPm(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    let val = input.value.trim().toUpperCase();
    if (val.includes('AM')) {
        input.value = val.replace('AM', 'PM');
    } else if (val.includes('PM')) {
        input.value = val.replace('PM', 'AM');
    } else {
        input.value = val + ' AM';
    }
}

