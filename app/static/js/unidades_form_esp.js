async function cargarUnidades() {
    const res = await fetch("/unidades");
    const data = await res.json();

    const fuerzaSelect = document.querySelector("select[name='fuerza_jefatura']");
    const comandoSelect = document.querySelector("select[name='comando_direccion_brigada_flotilla_grupo']");

    if (!fuerzaSelect || !comandoSelect) {
        console.error("No se encontraron los selects de fuerza o comando");
        return;
    }

    const fuerzaActual = fuerzaSelect.getAttribute("data-selected") || "";
    const comandoActual = comandoSelect.getAttribute("data-selected") || "";

    // 1. llenar fuerza
    fuerzaSelect.innerHTML = `<option value="">Seleccione fuerza/jefatura</option>`;
    Object.keys(data).forEach(f => {
        const selected = (f === fuerzaActual) ? "selected" : "";
        fuerzaSelect.innerHTML += `<option value="${f}" ${selected}>${f}</option>`;
    });

    // 2. llenar comandos si hay fuerza actual
    if (fuerzaActual && data[fuerzaActual]) {
        comandoSelect.innerHTML = `<option value="">Seleccione</option>`;
        Object.keys(data[fuerzaActual]).forEach(c => {
            const selected = (c === comandoActual) ? "selected" : "";
            comandoSelect.innerHTML += `<option value="${c}" ${selected}>${c}</option>`;
        });
    } else {
        comandoSelect.innerHTML = `<option value="">Seleccione</option>`;
    }

    // 3. evento cambio fuerza
    fuerzaSelect.addEventListener("change", () => {
        comandoSelect.innerHTML = `<option value="">Seleccione</option>`;
        const fuerza = fuerzaSelect.value;
        if (!fuerza || !data[fuerza]) return;

        Object.keys(data[fuerza]).forEach(c => {
            comandoSelect.innerHTML += `<option value="${c}">${c}</option>`;
        });
    });
}

document.addEventListener("DOMContentLoaded", cargarUnidades);
