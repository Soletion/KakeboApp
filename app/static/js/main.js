/**
 * Archivo principal de JavaScript para Kakebo
 * Gestiona funcionalidades comunes y utilidades
 */

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('Kakebo App inicializada');
    
    // Inicializar tooltips de Bootstrap
    initTooltips();
    
    // Inicializar popovers
    initPopovers();
    
    // Configurar validación de formularios
    setupFormValidation();
    
    // Configurar auto-guardado
    setupAutoSave();
    
    // Detectar preferencia de idioma
    detectLanguage();
});

// ===== TOOLTIPS Y POPOVERS =====
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
}

function initPopovers() {
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(popover => {
        new bootstrap.Popover(popover);
    });
}

// ===== VALIDACIÓN DE FORMULARIOS =====
function setupFormValidation() {
    const forms = document.querySelectorAll('form[novalidate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
                event.stopPropagation();
                showFirstError(this);
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            markAsInvalid(input, 'Este campo es obligatorio');
            isValid = false;
        } else {
            markAsValid(input);
        }
    });
    
    // Validación específica para emails
    const emailInputs = form.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        if (input.value && !validateEmail(input.value)) {
            markAsInvalid(input, 'Introduce un email válido');
            isValid = false;
        }
    });
    
    return isValid;
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function markAsInvalid(element, message) {
    element.classList.add('is-invalid');
    
    // Buscar o crear mensaje de error
    let feedback = element.nextElementSibling;
    if (!feedback || !feedback.classList.contains('invalid-feedback')) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        element.parentNode.insertBefore(feedback, element.nextSibling);
    }
    feedback.textContent = message;
}

function markAsValid(element) {
    element.classList.remove('is-invalid');
}

function showFirstError(form) {
    const firstInvalid = form.querySelector('.is-invalid');
    if (firstInvalid) {
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstInvalid.focus();
    }
}

// ===== AUTO-GUARDADO =====
function setupAutoSave() {
    const autoSaveForms = document.querySelectorAll('[data-auto-save="true"]');
    
    autoSaveForms.forEach(form => {
        let timeoutId;
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    saveFormData(form);
                }, 2000);
            });
        });
    });
}

function saveFormData(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Guardar en localStorage
    localStorage.setItem(`form_${form.id}`, JSON.stringify(data));
    
    // Mostrar indicador de guardado
    showNotification('Cambios guardados automáticamente', 'success');
}

// ===== NOTIFICACIONES =====
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// ===== MANEJO DE ERRORES AJAX =====
function handleAjaxError(error) {
    console.error('Error AJAX:', error);
    
    let message = 'Error en la operación';
    
    if (error.response) {
        // El servidor respondió con un código de error
        message = `Error ${error.response.status}: ${error.response.statusText}`;
    } else if (error.request) {
        // La petición se hizo pero no hubo respuesta
        message = 'No se pudo conectar con el servidor';
    }
    
    showNotification(message, 'danger');
}

// ===== FORMATO DE MONEDA =====
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

// ===== FORMATO DE FECHAS =====
function formatDate(date) {
    return new Intl.DateTimeFormat('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).format(new Date(date));
}

// ===== DETECCIÓN DE IDIOMA =====
function detectLanguage() {
    const htmlLang = document.documentElement.lang;
    const savedLang = localStorage.getItem('preferred_language');
    
    if (!savedLang && htmlLang) {
        localStorage.setItem('preferred_language', htmlLang);
    }
}

// ===== CARGA DE DATOS (LAZY LOADING) =====
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// ===== EXPORTAR DATOS =====
function exportToCSV(data, filename) {
    const csv = convertToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (navigator.msSaveBlob) {
        // IE 10+
        navigator.msSaveBlob(blob, filename);
    } else {
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
    }
}

function convertToCSV(data) {
    if (!data.length) return '';
    
    const headers = Object.keys(data[0]);
    const rows = data.map(obj => headers.map(header => obj[header]).join(','));
    
    return [headers.join(','), ...rows].join('\n');
}

// ===== TECLAS RÁPIDAS =====
document.addEventListener('keydown', function(e) {
    // Ctrl + S para guardar
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        const form = document.querySelector('form');
        if (form) {
            form.requestSubmit();
        }
    }
    
    // Esc para cerrar modales
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    }
});