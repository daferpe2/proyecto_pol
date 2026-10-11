async function cargarUnidades() {
    const res = await fetch("/unidades");
    const data = await res.json();

    const fuerzaSelect = document.querySelector("select[name='fuerza_jefatura']");
    const comandoSelect = document.querySelector("select[name='comando_direccion_brigada_flotilla_grupo']");

    if (!fuerzaSelect || !comandoSelect) return;

    const fuerzaActual = fuerzaSelect.getAttribute("data-selected") || "";
    const comandoActual = comandoSelect.getAttribute("data-selected") || "";

    // 1. llenar fuerza
    fuerzaSelect.innerHTML = `
        <option value="${fuerzaActual}" selected>${fuerzaActual}</option>
        <option value="">Seleccione fuerza/jefatura</option>
    `;

    Object.keys(data).forEach(f => {
        if (f !== fuerzaActual) {
            fuerzaSelect.innerHTML += `<option value="${f}">${f}</option>`;
        }
    });

    // 2. llenar comandos si hay fuerza actual
    comandoSelect.innerHTML = `
        <option value="${comandoActual}" selected>${comandoActual}</option>
        <option value="">Seleccione</option>
    `;

    if (fuerzaActual && data[fuerzaActual]) {
        Object.keys(data[fuerzaActual]).forEach(c => {
            if (c !== comandoActual) {
                comandoSelect.innerHTML += `<option value="${c}">${c}</option>`;
            }
        });
    }

    // 3. evento cambio fuerza
    fuerzaSelect.addEventListener("change", () => {
        const fuerza = fuerzaSelect.value;

        comandoSelect.innerHTML = `<option value="">Seleccione</option>`;

        if (!fuerza || !data[fuerza]) return;

        Object.keys(data[fuerza]).forEach(c => {
            comandoSelect.innerHTML += `<option value="${c}">${c}</option>`;
        });
    });

    // 4. disparar carga automática en actualización
    fuerzaSelect.dispatchEvent(new Event("change"));
    comandoSelect.dispatchEvent(new Event("change"));
}

document.addEventListener("DOMContentLoaded", cargarUnidades);