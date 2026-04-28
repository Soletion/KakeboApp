/**
 * Funcionalidades AJAX para Kakebo
 * Gestiona peticiones asíncronas al servidor
 */

// ===== CONFIGURACIÓN GLOBAL =====
const AJAX_CONFIG = {
    headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json'
    },
    timeout: 30000,  // 30 segundos
    retryAttempts: 3,
    retryDelay: 1000  // 1 segundo
};

// ===== CLASE PARA PETICIONES AJAX =====
class AjaxRequest {
    constructor(url, method = 'GET') {
        this.url = url;
        this.method = method;
        this.headers = { ...AJAX_CONFIG.headers };
        this.data = null;
        this.timeout = AJAX_CONFIG.timeout;
        this.retryCount = 0;
    }
    
    // Establecer headers
    setHeader(name, value) {
        this.headers[name] = value;
        return this;
    }
    
    // Establecer datos (para POST, PUT)
    setData(data) {
        this.data = data;
        return this;
    }
    
    // Establecer timeout
    setTimeout(timeout) {
        this.timeout = timeout;
        return this;
    }
    
    // Ejecutar petición
    async execute() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            const options = {
                method: this.method,
                headers: this.headers,
                signal: controller.signal,
                credentials: 'same-origin'
            };
            
            if (this.data && (this.method === 'POST' || this.method === 'PUT')) {
                options.body = JSON.stringify(this.data);
            }
            
            const response = await fetch(this.url, options);
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('La petición excedió el tiempo de espera');
            }
            
            // Reintentar si es posible
            if (this.retryCount < AJAX_CONFIG.retryAttempts) {
                this.retryCount++;
                await this.delay(AJAX_CONFIG.retryDelay);
                return this.execute();
            }
            
            throw error;
        }
    }
    
    // Delay para reintentos
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// ===== FUNCIONES DE AYUDA =====
const ajax = {
    // GET request
    get: function(url) {
        return new AjaxRequest(url, 'GET').execute();
    },
    
    // POST request
    post: function(url, data) {
        return new AjaxRequest(url, 'POST').setData(data).execute();
    },
    
    // PUT request
    put: function(url, data) {
        return new AjaxRequest(url, 'PUT').setData(data).execute();
    },
    
    // DELETE request
    delete: function(url) {
        return new AjaxRequest(url, 'DELETE').execute();
    }
};

// ===== FUNCIONES ESPECÍFICAS DE LA APLICACIÓN =====

// Obtener datos del dashboard
async function cargarDashboard(mes, año) {
    try {
        const data = await ajax.get(`/api/dashboard?mes=${mes}&año=${año}`);
        actualizarDashboardUI(data);
    } catch (error) {
        console.error('Error cargando dashboard:', error);
        mostrarError('No se pudo cargar el dashboard');
    }
}

// Obtener gastos por categoría
async function cargarGastosCategoria(mes, año) {
    try {
        const data = await ajax.get(`/api/gastos-por-categoria?mes=${mes}&año=${año}`);
        if (data.success) {
            actualizarGrafico('graficoCategorias', data.data);
        }
    } catch (error) {
        console.error('Error cargando gastos:', error);
    }
}

// Crear nuevo gasto (AJAX)
async function crearGasto(datos) {
    try {
        const response = await ajax.post('/api/gastos', datos);
        
        if (response.success) {
            mostrarNotificacion('Gasto creado correctamente', 'success');
            return response.data;
        } else {
            throw new Error(response.error || 'Error al crear el gasto');
        }
    } catch (error) {
        mostrarNotificacion(error.message, 'error');
        throw error;
    }
}

// Actualizar objetivo
async function actualizarObjetivo(id, cantidad) {
    try {
        const response = await ajax.put(`/api/objetivos/${id}`, { cantidad });
        
        if (response.success) {
            mostrarNotificacion('Objetivo actualizado', 'success');
            return response.data;
        }
    } catch (error) {
        mostrarNotificacion('Error al actualizar el objetivo', 'error');
    }
}

// Buscar gastos
async function buscarGastos(filtros) {
    try {
        const queryString = new URLSearchParams(filtros).toString();
        const data = await ajax.get(`/api/gastos/buscar?${queryString}`);
        
        if (data.success) {
            actualizarListadoGastos(data.data);
        }
    } catch (error) {
        console.error('Error en búsqueda:', error);
    }
}

// ===== ACTUALIZACIONES DE UI =====
function actualizarDashboardUI(data) {
    // Actualizar valores de tarjetas
    document.querySelectorAll('[data-update]').forEach(element => {
        const campo = element.dataset.update;
        if (data[campo] !== undefined) {
            if (element.classList.contains('currency')) {
                element.textContent = formatCurrency(data[campo]);
            } else {
                element.textContent = data[campo];
            }
        }
    });
}

function actualizarListadoGastos(gastos) {
    const container = document.getElementById('lista-gastos');
    if (!container) return;
    
    // Limpiar contenedor
    container.innerHTML = '';
    
    if (gastos.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No hay gastos</p>';
        return;
    }
    
    // Renderizar cada gasto
    gastos.forEach(gasto => {
        container.appendChild(crearElementoGasto(gasto));
    });
}

function crearElementoGasto(gasto) {
    const div = document.createElement('div');
    div.className = 'card mb-2';
    div.innerHTML = `
        <div class="card-body py-2">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <span class="badge" style="background-color: ${gasto.color}">
                        <i class="fas ${gasto.icono}"></i>
                    </span>
                    <span class="ms-2">${gasto.descripcion || gasto.categoria}</span>
                </div>
                <span class="fw-bold text-danger">${formatCurrency(gasto.cantidad)}</span>
            </div>
        </div>
    `;
    return div;
}

// ===== NOTIFICACIONES =====
function mostrarNotificacion(mensaje, tipo = 'info') {
    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alerta.style.zIndex = '9999';
    alerta.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alerta);
    
    setTimeout(() => {
        alerta.remove();
    }, 5000);
}

function mostrarError(mensaje) {
    mostrarNotificacion(mensaje, 'danger');
}

// ===== FORMATO DE MONEDA =====
function formatCurrency(value) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
    }).format(value);
}

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', function() {
    // Configurar CSRF token para todas las peticiones
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    if (csrfToken) {
        AJAX_CONFIG.headers['X-CSRFToken'] = csrfToken;
    }
    
    // Configurar formularios que usan AJAX
    document.querySelectorAll('[data-ajax-form="true"]').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            try {
                const response = await ajax.post(form.action, data);
                if (response.success) {
                    mostrarNotificacion('Operación exitosa', 'success');
                    if (form.dataset.redirect) {
                        window.location.href = form.dataset.redirect;
                    }
                }
            } catch (error) {
                mostrarError('Error en la operación');
            }
        });
    });
});