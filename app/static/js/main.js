// app/static/js/main.js

const API_BASE = 'http://127.0.0.1:8000';

// ============ NAVBAR ============
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('bg-negro', 'border-b', 'border-gris-medio', 'shadow-lg');
    } else {
        navbar.classList.remove('bg-negro', 'border-b', 'border-gris-medio', 'shadow-lg');
    }
});

// ============ MENÚ MÓVIL ============
const menuToggle = document.getElementById('menu-toggle');
const mobileMenu = document.getElementById('mobile-menu');
if (menuToggle) {
    menuToggle.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
    });
}

// ============ CERRAR MENÚ AL HACER CLIC EN LINK ============
document.querySelectorAll('#mobile-menu a').forEach(link => {
    link.addEventListener('click', () => {
        mobileMenu.classList.add('hidden');
    });
});

// ============ CARGAR SERVICIOS ============
async function cargarServicios() {
    try {
        const res = await fetch(`${API_BASE}/api/servicios/`);
        const servicios = await res.json();

        // Grid de servicios en la sección de presentación
        const grid = document.getElementById('servicios-grid');
        if (grid) {
            if (servicios.length === 0) {
                grid.innerHTML = `<p class="text-gris-claro col-span-3 text-center">
                    No hay servicios disponibles aún.</p>`;
            } else {
                grid.innerHTML = servicios.map(s => `
                    <div class="card-servicio" onclick="seleccionarServicioDesdeCard(${s.id})">
                        <div class="w-8 h-px bg-dorado mb-6 group-hover:w-16 transition-all duration-500"></div>
                        <h3 class="font-serif text-xl text-blanco mb-3">${s.nombre}</h3>
                        <p class="text-gris-claro text-sm leading-relaxed mb-6">
                            ${s.descripcion || 'Servicio profesional de calidad.'}
                        </p>
                        <div class="flex items-center justify-between">
                            <span class="text-dorado font-medium">$${Number(s.precio).toLocaleString('es-AR')}</span>
                            <span class="text-gris-claro text-xs tracking-wider">${s.duracion} min</span>
                        </div>
                    </div>
                `).join('');
            }
        }

        // Selector de servicios en el formulario de reserva
        const selector = document.getElementById('servicios-selector');
        if (selector) {
            if (servicios.length === 0) {
                selector.innerHTML = `<p class="text-gris-claro text-sm">
                    No hay servicios disponibles.</p>`;
            } else {
                selector.innerHTML = servicios.map(s => `
                    <div class="servicio-opcion border border-gris-medio p-4 cursor-pointer
                                hover:border-dorado transition-all duration-300"
                         data-id="${s.id}"
                         onclick="seleccionarServicio(this, ${s.id})">
                        <p class="text-blanco text-sm font-medium mb-1">${s.nombre}</p>
                        <p class="text-dorado text-xs">$${Number(s.precio).toLocaleString('es-AR')} — ${s.duracion} min</p>
                    </div>
                `).join('');
            }
        }

    } catch (err) {
        console.error('Error cargando servicios:', err);
    }
}

// ============ SELECCIONAR SERVICIO ============
let servicioSeleccionadoId = null;

function seleccionarServicio(elemento, id) {
    document.querySelectorAll('.servicio-opcion').forEach(el => {
        el.classList.remove('border-dorado', 'bg-gris-oscuro');
    });
    elemento.classList.add('border-dorado', 'bg-gris-oscuro');
    servicioSeleccionadoId = id;
    cargarHorariosDisponibles();
}

function seleccionarServicioDesdeCard(id) {
    document.getElementById('reservar').scrollIntoView({ behavior: 'smooth' });
    setTimeout(() => {
        const opcion = document.querySelector(`.servicio-opcion[data-id="${id}"]`);
        if (opcion) seleccionarServicio(opcion, id);
    }, 800);
}

// ============ CARGAR HORARIOS DISPONIBLES ============
async function cargarHorariosDisponibles() {
    const fecha = document.getElementById('fecha')?.value;
    const horaSelect = document.getElementById('hora');
    if (!fecha || !servicioSeleccionadoId || !horaSelect) return;

    horaSelect.innerHTML = '<option value="">Cargando horarios...</option>';

    try {
        const res = await fetch(
            `${API_BASE}/api/turnos/disponibles/${fecha}/${servicioSeleccionadoId}`
        );
        const data = await res.json();
        const horarios = data.horarios_disponibles || [];

        if (horarios.length === 0) {
            horaSelect.innerHTML = '<option value="">Sin horarios disponibles</option>';
        } else {
            horaSelect.innerHTML = '<option value="">Seleccioná un horario</option>' +
                horarios.map(h => `<option value="${h}">${h}</option>`).join('');
        }
    } catch (err) {
        horaSelect.innerHTML = '<option value="">Error al cargar horarios</option>';
    }
}

// Escuchar cambios en la fecha
document.getElementById('fecha')?.addEventListener('change', cargarHorariosDisponibles);

// Establecer fecha mínima como hoy
const inputFecha = document.getElementById('fecha');
if (inputFecha) {
    const hoy = new Date().toISOString().split('T')[0];
    inputFecha.min = hoy;
}

// ============ ENVIAR RESERVA ============
document.getElementById('form-reserva')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const nombre = document.getElementById('nombre').value.trim();
    const apellido = document.getElementById('apellido').value.trim();
    const email = document.getElementById('email').value.trim();
    const telefono = document.getElementById('telefono').value.trim();
    const fecha = document.getElementById('fecha').value;
    const hora = document.getElementById('hora').value;
    const notas = document.getElementById('notas').value.trim();
    const mensajeDiv = document.getElementById('mensaje-reserva');
    const btnSubmit = e.target.querySelector('button[type="submit"]');

    // Validaciones
    if (!servicioSeleccionadoId) {
        mostrarMensaje(mensajeDiv, 'Por favor seleccioná un servicio.', 'error');
        return;
    }
    if (!hora) {
        mostrarMensaje(mensajeDiv, 'Por favor seleccioná un horario.', 'error');
        return;
    }

    btnSubmit.textContent = 'Procesando...';
    btnSubmit.disabled = true;

    try {
        // Paso 1: Crear o buscar cliente
        const clienteRes = await fetch(`${API_BASE}/api/clientes/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre, apellido, email, telefono })
        });

        let clienteId;
        if (clienteRes.ok) {
            const cliente = await clienteRes.json();
            clienteId = cliente.id;
        } else if (clienteRes.status === 400) {
            // El cliente ya existe — buscarlo por email no es posible públicamente
            // En este caso mostramos el error
            const err = await clienteRes.json();
            mostrarMensaje(mensajeDiv, err.detail, 'error');
            btnSubmit.textContent = 'Confirmar Reserva';
            btnSubmit.disabled = false;
            return;
        }

        // Paso 2: Crear turno
        const turnoRes = await fetch(`${API_BASE}/api/turnos/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cliente_id: clienteId,
                servicio_id: servicioSeleccionadoId,
                fecha,
                hora: hora + ':00',
                notas: notas || null
            })
        });

        if (turnoRes.ok) {
            mostrarMensaje(mensajeDiv,
                `✓ ¡Turno confirmado! Te esperamos el ${fecha} a las ${hora} hs.`,
                'exito'
            );
            e.target.reset();
            servicioSeleccionadoId = null;
            document.querySelectorAll('.servicio-opcion').forEach(el => {
                el.classList.remove('border-dorado', 'bg-gris-oscuro');
            });
        } else {
            const err = await turnoRes.json();
            mostrarMensaje(mensajeDiv, err.detail || 'Error al crear el turno.', 'error');
        }

    } catch (err) {
        mostrarMensaje(mensajeDiv, 'Error de conexión. Intentá nuevamente.', 'error');
    }

    btnSubmit.textContent = 'Confirmar Reserva';
    btnSubmit.disabled = false;
});

// ============ MOSTRAR MENSAJES ============
function mostrarMensaje(div, texto, tipo) {
    div.classList.remove('hidden');
    div.className = `text-center py-6 px-4 border ${
        tipo === 'exito'
            ? 'border-dorado text-dorado bg-dorado/5'
            : 'border-red-500 text-red-400 bg-red-500/5'
    }`;
    div.textContent = texto;
    div.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ============ ANIMACIONES AL HACER SCROLL ============
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('opacity-100', 'translate-y-0');
            entry.target.classList.remove('opacity-0', 'translate-y-8');
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('section').forEach(section => {
    section.classList.add('opacity-0', 'translate-y-8', 'transition-all', 'duration-700');
    observer.observe(section);
});

// ============ INICIALIZAR ============
document.addEventListener('DOMContentLoaded', () => {
    cargarServicios();
});