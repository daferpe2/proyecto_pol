async function cargarGradoClase() {
    const res = await fetch("/grado_clase");
    const data = await res.json();

    console.log("DATA:", data); // Debug

    const claseSelect = document.querySelector("select[name='clase']");
    const gradoSelect = document.querySelector("select[name='grado']");

    // 1. Llenar clases
    claseSelect.innerHTML = `<option value="">Seleccione clase</option>`;
    Object.keys(data).forEach(clase => {
        claseSelect.innerHTML += `<option value="${clase}">${clase}</option>`;
    });

    // 2. Cuando cambia clase → llenar grados
    claseSelect.addEventListener("change", () => {
        gradoSelect.innerHTML = `<option value="">Seleccione grado</option>`;
        gradoSelect.disabled = true;

        const clase = claseSelect.value;
        if (!clase) return;

        const grados = data[clase]; // array de grados

        grados.forEach(gr => {
            gradoSelect.innerHTML += `<option value="${gr}">${gr}</option>`;
        });

        gradoSelect.disabled = false;
    });
}

document.addEventListener("DOMContentLoaded", cargarGradoClase);
