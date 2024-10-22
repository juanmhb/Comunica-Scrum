document.addEventListener('DOMContentLoaded', () => {
    cargarTareas();
    // Agregar eventos dragover y drop
    document.querySelectorAll('.kanban-block').forEach(element => {
        element.addEventListener('dragover', allowDrop);
        element.addEventListener('drop', drop);
    });
});


function mostrarTarea(tarea) {
    const estado = tarea.estado; 
    const columna = document.getElementById(estado.toLowerCase());
    if (!columna) {
        console.error(`No se encontró una columna para el estado ${tarea.estado}`);
        return;
    }

    const divTarea = document.createElement('div');
    divTarea.classList.add('kanban-task');
    divTarea.setAttribute('id', `task-${tarea.id}`);
    divTarea.setAttribute('draggable', true);
    divTarea.addEventListener('dragstart', (event) => drag(event));

    const pHorasDedicadas = document.createElement('p');
    pHorasDedicadas.textContent = `Horas Dedicadas: ${tarea.horasDedicadas}`;

    const inputBorrar = document.createElement('input');
    inputBorrar.classList.add('btn-borrar');
    inputBorrar.setAttribute('type', 'button');
    inputBorrar.value = 'Borrar';
    inputBorrar.onclick = function() {
        eliminarTarea(tarea.id);
    };

    divTarea.appendChild(pHorasDedicadas);
    divTarea.appendChild(inputBorrar);
    columna.appendChild(divTarea);
}

async function drop(event) {
    event.preventDefault();
    const tareaId = event.dataTransfer.getData("text").replace('task-', '');
    const divTarea = document.getElementById(`task-${tareaId}`);
    const nuevaColumna = event.currentTarget.id;

    if (!event.currentTarget || !divTarea || !divTarea.parentElement) {
        console.error("Error: Elemento o evento no válido.");
        return;
    }

    const estadosValidos = ['Pendiente', 'En Proceso', 'Completada'];
    if (!estadosValidos.includes(nuevaColumna.replace('_', ' ').toLowerCase().replace(/\b\w/g, c => c.toUpperCase()))) {
        console.error('Estado no válido:', nuevaColumna);
        return;
    }

    try {
        const columnaOriginal = divTarea.parentElement.id;

        if (nuevaColumna !== columnaOriginal) {
            const response = await fetch(`/actualizar_estado_tarea/${tareaId}/${nuevaColumna.replace('_', ' ').toLowerCase().replace(/\b\w/g, c => c.toUpperCase())}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ estado: nuevaColumna }) // Añade un cuerpo vacío si es necesario
            });
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Error al cambiar el estado de la tarea: ${errorText}`);
            }

            // Mueve la tarea a la nueva columna
            const nuevaColumnaElement = document.getElementById(nuevaColumna.toLowerCase());
            if (nuevaColumnaElement) {
                nuevaColumnaElement.appendChild(divTarea);
            }
        }

    } catch (error) {
        console.error(error);
    }
}




function drag(event) {
    event.dataTransfer.setData("text", event.target.id);
}

async function eliminarTarea(tareaId) {
    try {
        const response = await fetch(`/eliminar/tarea_kanban/${tareaId}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });
        if (!response.ok) {
            throw new Error('Error al eliminar la tarea');
        }
        await cargarTareas();
    } catch (error) {
        console.error(error);
    }
}

function getCsrfToken() {
    const csrfForm = document.getElementById('csrf-form');
    if (csrfForm) {
        return csrfForm.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    console.error('Formulario CSRF no encontrado');
    return '';
}

// Permite que el elemento sea soltado
function allowDrop(event) {
    event.preventDefault();
}
