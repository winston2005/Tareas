// JavaScript para funcionalidades del usuario

document.addEventListener('DOMContentLoaded', function () {

    // Auto-cerrar alertas
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirmación de acciones destructivas
    const deleteButtons = document.querySelectorAll('a[href*="eliminar"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            if (!confirm('¿Está seguro de que desea eliminar este elemento?')) {
                e.preventDefault();
            }
        });
    });

    // Validación de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            // Validar fechas
            const dateInputs = form.querySelectorAll('input[type="date"]');
            dateInputs.forEach(input => {
                if (input.value) {
                    const selectedDate = new Date(input.value);
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);

                    if (selectedDate < today && input.name === 'fecha_vencimiento') {
                        alert('La fecha de vencimiento no puede ser anterior a hoy');
                        e.preventDefault();
                    }
                }
            });
        });
    });

    // Contador de caracteres en textareas
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('small');
        counter.className = 'form-text text-muted';
        counter.textContent = `0 / ${maxLength} caracteres`;
        textarea.parentNode.appendChild(counter);

        textarea.addEventListener('input', function () {
            const length = this.value.length;
            counter.textContent = `${length} / ${maxLength} caracteres`;
            counter.style.color = length > maxLength * 0.9 ? '#dc3545' : '#6c757d';
        });
    });

    // Filtros de tareas en LocalStorage
    const filterForm = document.querySelector('form[method="GET"]');
    if (filterForm) {
        const saveFilters = () => {
            const formData = new FormData(filterForm);
            const filters = {};
            formData.forEach((value, key) => {
                if (value) filters[key] = value;
            });
            localStorage.setItem('taskFilters', JSON.stringify(filters));
        };

        filterForm.querySelectorAll('select').forEach(select => {
            select.addEventListener('change', saveFilters);
        });
    }

    // Preview de color en formularios de categoría
    const colorInputs = document.querySelectorAll('input[type="color"]');
    colorInputs.forEach(input => {
        const preview = document.createElement('div');
        preview.style.width = '30px';
        preview.style.height = '30px';
        preview.style.borderRadius = '50%';
        preview.style.display = 'inline-block';
        preview.style.marginLeft = '10px';
        preview.style.verticalAlign = 'middle';
        preview.style.border = '2px solid #ddd';
        preview.style.backgroundColor = input.value;

        input.parentNode.appendChild(preview);

        input.addEventListener('input', function () {
            preview.style.backgroundColor = this.value;
        });
    });

    // Búsqueda rápida de tareas
    const searchInput = document.getElementById('taskSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase();
            const taskCards = document.querySelectorAll('.card');

            taskCards.forEach(card => {
                const title = card.querySelector('.card-title')?.textContent.toLowerCase() || '';
                const text = card.querySelector('.card-text')?.textContent.toLowerCase() || '';

                if (title.includes(searchTerm) || text.includes(searchTerm)) {
                    card.parentElement.style.display = '';
                } else {
                    card.parentElement.style.display = 'none';
                }
            });
        });
    }

    // Tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // Animación de estadísticas
    const animateCounter = (element, target, duration = 1000) => {
        let start = 0;
        const increment = target / (duration / 16);

        const timer = setInterval(() => {
            start += increment;
            element.textContent = Math.floor(start);

            if (start >= target) {
                element.textContent = target;
                clearInterval(timer);
            }
        }, 16);
    };

    // Animar contadores en cards de estadísticas
    const statCards = document.querySelectorAll('.card h2, .card h3');
    statCards.forEach(card => {
        const value = parseInt(card.textContent);
        if (!isNaN(value) && value > 0) {
            card.textContent = '0';
            setTimeout(() => animateCounter(card, value), 100);
        }
    });

    // Drag and drop para reordenar tareas (funcionalidad futura)
    const taskCards = document.querySelectorAll('.card');
    taskCards.forEach(card => {
        card.draggable = true;

        card.addEventListener('dragstart', function (e) {
            this.style.opacity = '0.5';
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/html', this.innerHTML);
        });

        card.addEventListener('dragend', function () {
            this.style.opacity = '1';
        });
    });

    // Atajos de teclado
    document.addEventListener('keydown', function (e) {
        // Ctrl + N para nueva tarea
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            const newTaskBtn = document.querySelector('a[href*="crear_tarea"]');
            if (newTaskBtn) window.location.href = newTaskBtn.href;
        }

        // Ctrl + B para buscar
        if (e.ctrlKey && e.key === 'b') {
            e.preventDefault();
            const searchInput = document.getElementById('taskSearch');
            if (searchInput) searchInput.focus();
        }
    });

    // Mostrar notificación de tareas vencidas
    const vencidasCount = document.querySelector('[data-vencidas]');
    if (vencidasCount) {
        const count = parseInt(vencidasCount.textContent);
        if (count > 0) {
            // Podrías mostrar una notificación del navegador aquí
            console.log(`Tienes ${count} tarea(s) vencida(s)`);
        }
    }

    // Prevenir envío múltiple de formularios
    forms.forEach(form => {
        form.addEventListener('submit', function () {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
            }
        });
    });

    console.log('User interface loaded successfully');
});