/**
 * Gestión de internacionalización (i18n) en el cliente
 * Maneja el cambio de idioma y traducciones en tiempo real
 */

// ===== CONFIGURACIÓN =====
const IDIOMAS_DISPONIBLES = ['es', 'en'];
const IDIOMA_POR_DEFECTO = 'es';

// Almacén de traducciones
let traducciones = {};

// ===== CARGAR TRADUCCIONES =====
async function cargarTraducciones(idioma) {
    try {
        const response = await fetch(`/static/translations/${idioma}.json`);
        if (!response.ok) {
            throw new Error(`Error cargando traducciones para ${idioma}`);
        }
        traducciones[idioma] = await response.json();
        return traducciones[idioma];
    } catch (error) {
        console.error('Error cargando traducciones:', error);
        return {};
    }
}

// ===== OBTENER TRADUCCIÓN =====
function t(clave, idioma = null, params = {}) {
    const lang = idioma || obtenerIdiomaActual();
    
    if (!traducciones[lang]) {
        return clave;
    }
    
    // Navegar por la clave (ej: "auth.login.titulo")
    const partes = clave.split('.');
    let valor = traducciones[lang];
    
    for (const parte of partes) {
        if (valor && valor[parte] !== undefined) {
            valor = valor[parte];
        } else {
            return clave;
        }
    }
    
    // Reemplazar parámetros
    if (typeof valor === 'string') {
        Object.keys(params).forEach(key => {
            valor = valor.replace(`{${key}}`, params[key]);
        });
    }
    
    return valor;
}

// ===== OBTENER IDIOMA ACTUAL =====
function obtenerIdiomaActual() {
    return document.documentElement.lang || 
           localStorage.getItem('idioma') || 
           IDIOMA_POR_DEFECTO;
}

// ===== CAMBIAR IDIOMA =====
async function cambiarIdioma(nuevoIdioma) {
    if (!IDIOMAS_DISPONIBLES.includes(nuevoIdioma)) {
        console.error(`Idioma no soportado: ${nuevoIdioma}`);
        return false;
    }
    
    try {
        // Guardar preferencia
        localStorage.setItem('idioma', nuevoIdioma);
        document.documentElement.lang = nuevoIdioma;
        
        // Cargar traducciones si no están
        if (!traducciones[nuevoIdioma]) {
            await cargarTraducciones(nuevoIdioma);
        }
        
        // Actualizar textos en la página
        actualizarTextosPagina();
        
        // Disparar evento
        window.dispatchEvent(new CustomEvent('idiomaCambiado', { 
            detail: { idioma: nuevoIdioma } 
        }));
        
        return true;
        
    } catch (error) {
        console.error('Error cambiando idioma:', error);
        return false;
    }
}

// ===== ACTUALIZAR TEXTOS DE LA PÁGINA =====
function actualizarTextosPagina() {
    const idioma = obtenerIdiomaActual();
    
    // Elementos con data-i18n
    document.querySelectorAll('[data-i18n]').forEach(elemento => {
        const clave = elemento.dataset.i18n;
        const texto = t(clave, idioma);
        
        if (elemento.tagName === 'INPUT' || elemento.tagName === 'TEXTAREA') {
            if (elemento.type === 'submit' || elemento.type === 'button') {
                elemento.value = texto;
            } else {
                elemento.placeholder = texto;
            }
        } else {
            elemento.textContent = texto;
        }
    });
    
    // Elementos con atributos traducibles
    document.querySelectorAll('[data-i18n-attr]').forEach(elemento => {
        const data = elemento.dataset.i18nAttr;
        try {
            const mappings = JSON.parse(data);
            Object.keys(mappings).forEach(atributo => {
                const clave = mappings[atributo];
                elemento.setAttribute(atributo, t(clave, idioma));
            });
        } catch (e) {
            console.error('Error parseando data-i18n-attr:', e);
        }
    });
    
    // Placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(elemento => {
        const clave = elemento.dataset.i18nPlaceholder;
        elemento.placeholder = t(clave, idioma);
    });
    
    // Títulos de página
    if (document.querySelector('[data-i18n-title]')) {
        document.title = t(document.querySelector('[data-i18n-title]').dataset.i18nTitle, idioma);
    }
}

// ===== SELECTOR DE IDIOMA =====
function crearSelectorIdioma(container) {
    const selector = document.createElement('div');
    selector.className = 'dropdown';
    selector.innerHTML = `
        <button class="btn btn-outline-secondary dropdown-toggle" type="button" 
                data-bs-toggle="dropdown" aria-expanded="false">
            <i class="fas fa-language me-2"></i>
            <span data-i18n="nav.idioma.${obtenerIdiomaActual()}">Idioma</span>
        </button>
        <ul class="dropdown-menu">
            <li><a class="dropdown-item ${obtenerIdiomaActual() === 'es' ? 'active' : ''}" 
                   href="#" data-idioma="es">
                <i class="fas fa-flag me-2"></i>Español
            </a></li>
            <li><a class="dropdown-item ${obtenerIdiomaActual() === 'en' ? 'active' : ''}" 
                   href="#" data-idioma="en">
                <i class="fas fa-flag-usa me-2"></i>English
            </a></li>
        </ul>
    `;
    
    // Eventos
    selector.querySelectorAll('[data-idioma]').forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            const idioma = link.dataset.idioma;
            const exito = await cambiarIdioma(idioma);
            
            if (exito) {
                // Actualizar clase active
                selector.querySelectorAll('.dropdown-item').forEach(item => {
                    item.classList.remove('active');
                });
                link.classList.add('active');
                
                // Actualizar texto del botón
                const btnText = selector.querySelector('.dropdown-toggle span');
                btnText.textContent = t(`nav.idioma.${idioma}`);
            }
        });
    });
    
    container.appendChild(selector);
    return selector;
}

// ===== DETECTAR IDIOMA DEL NAVEGADOR =====
function detectarIdiomaNavegador() {
    const lang = navigator.language || navigator.userLanguage;
    const codigo = lang.split('-')[0];
    
    if (IDIOMAS_DISPONIBLES.includes(codigo)) {
        return codigo;
    }
    
    return IDIOMA_POR_DEFECTO;
}

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', async () => {
    // Determinar idioma inicial
    let idiomaInicial = localStorage.getItem('idioma');
    
    if (!idiomaInicial) {
        idiomaInicial = detectarIdiomaNavegador();
    }
    
    // Cargar traducciones iniciales
    await cargarTraducciones(idiomaInicial);
    
    // Establecer idioma
    document.documentElement.lang = idiomaInicial;
    
    // Actualizar textos
    actualizarTextosPagina();
    
    // Inicializar selector de idioma si existe
    const selectorContainer = document.getElementById('selector-idioma');
    if (selectorContainer && !selectorContainer.querySelector('.dropdown')) {
        crearSelectorIdioma(selectorContainer);
    }
    
    console.log(`Idioma inicializado: ${idiomaInicial}`);
});

// ===== EXPORTAR FUNCIONES PARA USO GLOBAL =====
window.t = t;
window.cambiarIdioma = cambiarIdioma;
window.obtenerIdiomaActual = obtenerIdiomaActual;