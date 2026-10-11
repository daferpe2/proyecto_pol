async function cargarCategorias() {
    const res = await fetch("/categorias");
    const data = await res.json();

    console.log("CATEGORIAS:", data); // Debug

    const categoriaSelect = document.querySelector("select[name='categoria']");
    const procesoSelect = document.querySelector("select[name='proceso']");

    // 1. Llenar categorías
    categoriaSelect.innerHTML = `<option value="">Seleccione categoría</option>`;
    Object.keys(data).forEach(cat => {
        categoriaSelect.innerHTML += `<option value="${cat}">${cat}</option>`;
    });

    // 2. Cuando cambia categoría → llenar procesos
    categoriaSelect.addEventListener("change", () => {
        procesoSelect.innerHTML = `<option value="">Seleccione proceso</option>`;
        procesoSelect.disabled = true;

        const categoria = categoriaSelect.value;
        if (!categoria) return;

        const procesos = data[categoria];
        procesos.forEach(proc => {
            procesoSelect.innerHTML += `<option value="${proc}">${proc}</option>`;
        });

        procesoSelect.disabled = false;
    });
}

document.addEventListener("DOMContentLoaded", cargarCategorias);
