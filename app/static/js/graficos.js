/**
 * Gestión de gráficos con Chart.js para Kakebo
 * Crea y actualiza los diferentes gráficos de la aplicación
 */

// ===== CONFIGURACIÓN GLOBAL DE CHART.JS =====
Chart.defaults.font.family = "'Segoe UI', 'Helvetica Neue', 'Arial', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#2c3e50';
Chart.defaults.plugins.tooltip.backgroundColor = '#2c3e50';

// ===== GESTOR DE GRÁFICOS =====
const GraficosManager = {
    graficos: {},
    
    // Crear o actualizar un gráfico
    crearGrafico: function(id, tipo, datos, opciones = {}) {
        const canvas = document.getElementById(id);
        if (!canvas) return null;
        
        const ctx = canvas.getContext('2d');
        
        // Destruir gráfico existente
        if (this.graficos[id]) {
            this.graficos[id].destroy();
        }
        
        // Configuración base
        const config = {
            type: tipo,
            data: datos,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: '#2c3e50',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#fff',
                        borderWidth: 1,
                        padding: 10,
                        cornerRadius: 8
                    }
                },
                ...opciones
            }
        };
        
        this.graficos[id] = new Chart(ctx, config);
        return this.graficos[id];
    },
    
    // Destruir todos los gráficos
    destruirTodos: function() {
        Object.keys(this.graficos).forEach(key => {
            if (this.graficos[key]) {
                this.graficos[key].destroy();
            }
        });
        this.graficos = {};
    }
};

// ===== GRÁFICO DE GASTOS POR CATEGORÍA =====
function crearGraficoGastosCategoria(id, datos) {
    return GraficosManager.crearGrafico(id, 'doughnut', {
        labels: datos.labels,
        datasets: [{
            data: datos.data,
            backgroundColor: datos.backgroundColors || [
                '#27ae60', '#e74c3c', '#f39c12', '#3498db', '#9b59b6',
                '#1abc9c', '#e67e22', '#2c3e50', '#7f8c8d', '#16a085'
            ],
            borderWidth: 2,
            borderColor: '#ffffff'
        }]
    }, {
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.raw;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        return `${label}: ${formatCurrency(value)} (${percentage}%)`;
                    }
                }
            }
        },
        cutout: '60%'
    });
}

// ===== GRÁFICO DE EVOLUCIÓN MENSUAL =====
function crearGraficoEvolucion(id, datos) {
    return GraficosManager.crearGrafico(id, 'line', {
        labels: datos.labels,
        datasets: [
            {
                label: 'Ingresos',
                data: datos.ingresos,
                borderColor: '#27ae60',
                backgroundColor: 'rgba(39, 174, 96, 0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#27ae60',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 8
            },
            {
                label: 'Gastos',
                data: datos.gastos,
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#e74c3c',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 8
            },
            {
                label: 'Ahorro',
                data: datos.ahorro,
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#3498db',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 8
            }
        ]
    }, {
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0,0,0,0.05)'
                },
                ticks: {
                    callback: function(value) {
                        return formatCurrency(value);
                    }
                }
            }
        }
    });
}

// ===== GRÁFICO DE COMPARATIVA ANUAL =====
function crearGraficoComparativa(id, datos) {
    return GraficosManager.crearGrafico(id, 'bar', {
        labels: datos.labels,
        datasets: [
            {
                label: 'Ingresos',
                data: datos.ingresos,
                backgroundColor: 'rgba(39, 174, 96, 0.7)',
                borderColor: '#27ae60',
                borderWidth: 1,
                borderRadius: 8
            },
            {
                label: 'Gastos',
                data: datos.gastos,
                backgroundColor: 'rgba(231, 76, 60, 0.7)',
                borderColor: '#e74c3c',
                borderWidth: 1,
                borderRadius: 8
            }
        ]
    }, {
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return formatCurrency(value);
                    }
                }
            }
        }
    });
}

// ===== GRÁFICO DE PROGRESO DE OBJETIVOS =====
function crearGraficoObjetivos(id, datos) {
    return GraficosManager.crearGrafico(id, 'bar', {
        labels: datos.labels,
        datasets: [{
            label: 'Progreso (%)',
            data: datos.data,
            backgroundColor: '#3498db',
            borderRadius: 8
        }]
    }, {
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                ticks: {
                    callback: function(value) {
                        return value + '%';
                    }
                }
            }
        },
        indexAxis: 'y'  // Barras horizontales
    });
}

// ===== GRÁFICO DE DISTRIBUCIÓN DE GASTOS =====
function crearGraficoDistribucion(id, datos) {
    return GraficosManager.crearGrafico(id, 'pie', {
        labels: datos.labels,
        datasets: [{
            data: datos.data,
            backgroundColor: [
                '#27ae60', '#e74c3c', '#f39c12', '#3498db', '#9b59b6',
                '#1abc9c', '#e67e22', '#2c3e50'
            ]
        }]
    }, {
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const value = context.raw;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        return `${context.label}: ${percentage}%`;
                    }
                }
            }
        }
    });
}

// ===== ACTUALIZAR DATOS DE GRÁFICO =====
function actualizarGrafico(id, nuevosDatos) {
    if (GraficosManager.graficos[id]) {
        const grafico = GraficosManager.graficos[id];
        
        // Actualizar labels
        if (nuevosDatos.labels) {
            grafico.data.labels = nuevosDatos.labels;
        }
        
        // Actualizar datasets
        if (nuevosDatos.datasets) {
            nuevosDatos.datasets.forEach((dataset, index) => {
                if (grafico.data.datasets[index]) {
                    grafico.data.datasets[index].data = dataset.data;
                    if (dataset.backgroundColor) {
                        grafico.data.datasets[index].backgroundColor = dataset.backgroundColor;
                    }
                }
            });
        }
        
        grafico.update();
    }
}

// ===== EXPORTAR GRÁFICO COMO IMAGEN =====
function exportarGrafico(id, formato = 'png') {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    
    const link = document.createElement('a');
    link.download = `grafico-${id}.${formato}`;
    link.href = canvas.toDataURL(`image/${formato}`);
    link.click();
}

// ===== FORMATO DE MONEDA PARA GRÁFICOS =====
function formatCurrency(value) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// Inicializar gráficos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Los gráficos se inicializarán según los datos disponibles
    // Esto se maneja desde los templates con datos embebidos
});