/**
 * Validaciones específicas para Kakebo
 * Gestiona la validación de formularios y datos
 */

// ===== VALIDACIONES DE CAMPOS =====
const Validaciones = {
    // Validar cantidad (positiva y con dos decimales)
    cantidad: function(valor) {
        const num = parseFloat(valor);
        return !isNaN(num) && num > 0 && num <= 999999.99;
    },
    
    // Validar email
    email: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Validar nombre de usuario
    username: function(username) {
        const re = /^[a-zA-Z0-9_]{3,20}$/;
        return re.test(username);
    },
    
    // Validar contraseña (mínimo 8 caracteres, al menos una mayúscula y un número)
    password: function(password) {
        const re = /^(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$/;
        return re.test(password);
    },
    
    // Validar fecha (no futura)
    fecha: function(fecha) {
        const fechaObj = new Date(fecha);
        const hoy = new Date();
        return fechaObj <= hoy;
    },
    
    // Validar texto (no vacío, longitud máxima)
    texto: function(texto, maxLength = 200) {
        return texto && texto.trim().length > 0 && texto.length <= maxLength;
    }
};

// ===== VALIDADORES DE FORMULARIOS ESPECÍFICOS =====
const FormValidators = {
    // Validar formulario de gasto
    gasto: function(form) {
        const errores = [];
        
        const cantidad = form.querySelector('[name="cantidad"]').value;
        if (!Validaciones.cantidad(cantidad)) {
            errores.push('La cantidad debe ser mayor que 0');
        }
        
        const categoria = form.querySelector('[name="categoria"]').value;
        if (!categoria) {
            errores.push('Debes seleccionar una categoría');
        }
        
        const fecha = form.querySelector('[name="fecha"]').value;
        if (fecha && !Validaciones.fecha(fecha)) {
            errores.push('La fecha no puede ser futura');
        }
        
        return errores;
    },
    
    // Validar formulario de ingreso
    ingreso: function(form) {
        const errores = [];
        
        const cantidad = form.querySelector('[name="cantidad"]').value;
        if (!Validaciones.cantidad(cantidad)) {
            errores.push('La cantidad debe ser mayor que 0');
        }
        
        const fecha = form.querySelector('[name="fecha"]').value;
        if (fecha && !Validaciones.fecha(fecha)) {
            errores.push('La fecha no puede ser futura');
        }
        
        return errores;
    },
    
    // Validar formulario de objetivo
    objetivo: function(form) {
        const errores = [];
        
        const nombre = form.querySelector('[name="nombre"]').value;
        if (!Validaciones.texto(nombre, 100)) {
            errores.push('El nombre es obligatorio y no puede exceder 100 caracteres');
        }
        
        const cantidad = form.querySelector('[name="cantidad_objetivo"]').value;
        if (!Validaciones.cantidad(cantidad)) {
            errores.push('La cantidad objetivo debe ser mayor que 0');
        }
        
        const fechaInicio = form.querySelector('[name="fecha_inicio"]').value;
        const fechaLimite = form.querySelector('[name="fecha_limite"]').value;
        
        if (fechaInicio && fechaLimite && new Date(fechaInicio) > new Date(fechaLimite)) {
            errores.push('La fecha de inicio no puede ser posterior a la fecha límite');
        }
        
        return errores;
    },
    
    // Validar formulario de registro
    registro: function(form) {
        const errores = [];
        
        const email = form.querySelector('[name="email"]').value;
        if (!Validaciones.email(email)) {
            errores.push('El email no es válido');
        }
        
        const username = form.querySelector('[name="username"]').value;
        if (!Validaciones.username(username)) {
            errores.push('El usuario debe tener entre 3 y 20 caracteres (solo letras, números y _)');
        }
        
        const password = form.querySelector('[name="password"]').value;
        if (!Validaciones.password(password)) {
            errores.push('La contraseña debe tener al menos 8 caracteres, una mayúscula y un número');
        }
        
        const confirmPassword = form.querySelector('[name="confirm_password"]').value;
        if (password !== confirmPassword) {
            errores.push('Las contraseñas no coinciden');
        }
        
        const nombre = form.querySelector('[name="nombre"]').value;
        if (!nombre || nombre.trim().length < 2) {
            errores.push('El nombre es obligatorio');
        }
        
        return errores;
    }
};

// ===== VALIDACIÓN EN TIEMPO REAL =====
function setupRealTimeValidation() {
    // Validación de cantidad
    document.querySelectorAll('[name="cantidad"]').forEach(input => {
        input.addEventListener('input', function(e) {
            const valor = this.value;
            const feedback = this.nextElementSibling;
            
            if (valor && !Validaciones.cantidad(valor)) {
                this.classList.add('is-invalid');
                if (feedback && feedback.classList.contains('invalid-feedback')) {
                    feedback.textContent = 'La cantidad no es válida';
                }
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });
    
    // Validación de email
    document.querySelectorAll('[name="email"]').forEach(input => {
        input.addEventListener('blur', function(e) {
            const valor = this.value;
            
            if (valor && !Validaciones.email(valor)) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });
    
    // Validación de contraseña en tiempo real
    document.querySelectorAll('[name="password"]').forEach(input => {
        input.addEventListener('input', function(e) {
            const valor = this.value;
            const requirements = document.querySelector('.password-requirements');
            
            if (requirements) {
                // Actualizar indicadores visuales de requisitos
                updatePasswordRequirements(valor, requirements);
            }
        });
    });
}

// ===== ACTUALIZAR REQUISITOS DE CONTRASEÑA =====
function updatePasswordRequirements(password, container) {
    const requirements = [
        { test: password.length >= 8, text: 'Mínimo 8 caracteres' },
        { test: /[A-Z]/.test(password), text: 'Al menos una mayúscula' },
        { test: /\d/.test(password), text: 'Al menos un número' }
    ];
    
    const items = container.querySelectorAll('li');
    requirements.forEach((req, index) => {
        if (items[index]) {
            if (req.test) {
                items[index].classList.add('text-success');
                items[index].classList.remove('text-danger');
                items[index].innerHTML = `<i class="fas fa-check me-2"></i>${req.text}`;
            } else {
                items[index].classList.remove('text-success');
                items[index].classList.add('text-danger');
                items[index].innerHTML = `<i class="fas fa-times me-2"></i>${req.text}`;
            }
        }
    });
}

// ===== VALIDACIÓN DE FORMULARIO COMPLETO =====
function validateFormWithRules(formId, validatorType) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const validator = FormValidators[validatorType];
    if (!validator) return true;
    
    const errores = validator(form);
    
    if (errores.length > 0) {
        // Mostrar errores
        mostrarErrores(errores);
        return false;
    }
    
    return true;
}

// ===== MOSTRAR ERRORES DE VALIDACIÓN =====
function mostrarErrores(errores) {
    // Crear contenedor de errores si no existe
    let errorContainer = document.querySelector('.validation-errors');
    
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.className = 'alert alert-danger validation-errors alert-dismissible fade show';
        errorContainer.innerHTML = `
            <h6><i class="fas fa-exclamation-triangle me-2"></i>Errores de validación:</h6>
            <ul class="mb-0"></ul>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const form = document.querySelector('form');
        if (form) {
            form.parentNode.insertBefore(errorContainer, form);
        }
    }
    
    // Actualizar lista de errores
    const ul = errorContainer.querySelector('ul');
    ul.innerHTML = errores.map(error => `<li>${error}</li>`).join('');
    
    // Mostrar contenedor
    errorContainer.style.display = 'block';
    
    // Auto-ocultar después de 5 segundos
    setTimeout(() => {
        errorContainer.style.display = 'none';
    }, 5000);
}

// ===== VALIDACIÓN DE NÚMEROS EN INPUTS =====
function setupNumberValidation() {
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('keypress', function(e) {
            // Permitir solo números, punto y coma
            const char = String.fromCharCode(e.which);
            if (!/[0-9.,]/.test(char)) {
                e.preventDefault();
            }
        });
        
        input.addEventListener('blur', function(e) {
            const valor = this.value;
            if (valor) {
                // Reemplazar coma por punto
                this.value = valor.replace(',', '.');
            }
        });
    });
}

// Inicializar validaciones cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    setupRealTimeValidation();
    setupNumberValidation();
});