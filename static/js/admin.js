// JavaScript para funcionalidades del panel de administración

document.addEventListener('DOMContentLoaded', function () {

    // Auto-cerrar alertas después de 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirmación de eliminación de usuarios
    const deleteLinks = document.querySelectorAll('a[href*="eliminar"]');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            if (!confirm('¿Está seguro de que desea eliminar este elemento?')) {
                e.preventDefault();
            }
        });
    });

    // Búsqueda en tiempo real en tablas
    const searchInput = document.getElementById('tableSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function () {
            const searchTerm = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('tbody tr');

            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }

    // Tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Validación de formularios
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Copiar al portapapeles
    const copyButtons = document.querySelectorAll('.btn-copy');
    copyButtons.forEach(button => {
        button.addEventListener('click', function () {
            const text = this.dataset.copy;
            navigator.clipboard.writeText(text).then(() => {
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="bi bi-check"></i> Copiado';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            });
        });
    });

    // Filtros persistentes en sessionStorage
    const filterForm = document.querySelector('form[method="GET"]');
    if (filterForm) {
        // Guardar filtros
        filterForm.addEventListener('submit', function () {
            const formData = new FormData(this);
            const filters = {};
            formData.forEach((value, key) => {
                if (value) filters[key] = value;
            });
            sessionStorage.setItem('adminFilters', JSON.stringify(filters));
        });

        // Restaurar filtros
        const savedFilters = sessionStorage.getItem('adminFilters');
        if (savedFilters) {
            const filters = JSON.parse(savedFilters);
            Object.keys(filters).forEach(key => {
                const input = filterForm.querySelector(`[name="${key}"]`);
                if (input) input.value = filters[key];
            });
        }
    }

    // Estadísticas animadas (contadores)
    const animateValue = (element, start, end, duration) => {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            element.textContent = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    };

    // Animar números en cards de estadísticas
    const statNumbers = document.querySelectorAll('.card h2, .card h3');
    statNumbers.forEach(num => {
        const value = parseInt(num.textContent);
        if (!isNaN(value) && value > 0) {
            animateValue(num, 0, value, 1000);
        }
    });

    // Resaltar fila seleccionada en tablas
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function () {
            tableRows.forEach(r => r.classList.remove('table-active'));
            this.classList.add('table-active');
        });
    });

    // Prevenir doble submit de formularios
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.closest('form')?.addEventListener('submit', function () {
            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Procesando...';
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = button.dataset.originalText || 'Enviar';
            }, 3000);
        });
    });

    console.log('Panel del administrador cargado exitosamente');
});