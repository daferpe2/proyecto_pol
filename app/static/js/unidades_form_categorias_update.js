async function cargarCategorias() {
    const res = await fetch("/categorias");
    const data = await res.json();

    const categoriaSelect = document.querySelector("select[name='categoria']");
    const procesoSelect = document.querySelector("select[name='proceso']");

    const categoriaActual = categoriaSelect.getAttribute("data-selected") || "";
    const procesoActual = procesoSelect.getAttribute("data-selected") || "";

    // 1. Llenar categorías
    categoriaSelect.innerHTML = `
        <option value="${categoriaActual}" selected>${categoriaActual}</option>
        <option value="">Seleccione categoría</option>
    `;

    Object.keys(data).forEach(cat => {
        if (cat !== categoriaActual) {
            categoriaSelect.innerHTML += `<option value="${cat}">${cat}</option>`;
        }
    });

    // 2. Llenar procesos si ya hay categoría
    procesoSelect.innerHTML = `
        <option value="${procesoActual}" selected>${procesoActual}</option>
        <option value="">Seleccione proceso</option>
    `;

    if (categoriaActual && data[categoriaActual]) {
        data[categoriaActual].forEach(proc => {
            if (proc !== procesoActual) {
                procesoSelect.innerHTML += `<option value="${proc}">${proc}</option>`;
            }
        });
    }

    // 3. evento cambio categoría
    categoriaSelect.addEventListener("change", () => {
        const categoria = categoriaSelect.value;

        procesoSelect.innerHTML = `<option value="">Seleccione proceso</option>`;
        procesoSelect.disabled = true;

        if (!categoria) return;

        data[categoria].forEach(proc => {
            procesoSelect.innerHTML += `<option value="${proc}">${proc}</option>`;
        });

        procesoSelect.disabled = false;
    });

    // 4. disparar carga automática en actualización
    categoriaSelect.dispatchEvent(new Event("change"));
}

document.addEventListener("DOMContentLoaded", cargarCategorias);
