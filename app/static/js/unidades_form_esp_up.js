document.addEventListener("DOMContentLoaded", async () => {
    await cargarUnidades();
    // const res = await fetch("/unidades");
    // const data = await res.json();

    const fuerzaSelect = document.querySelector("select[name='fuerza_jefatura']");
    const comandoSelect = document.querySelector("select[name='comando_direccion_brigada_flotilla_grupo']");
    const unidadSelect = document.querySelector("select[name='batallon_buque_unidad_labora']");

    fuerzaSelect.value = fuerzaSelect.dataset.selected;
    fuerzaSelect.dispatchEvent(new Event("change"));

    setTimeout(() => {
        comandoSelect.value = comandoSelect.dataset.selected;
        comandoSelect.dispatchEvent(new Event("change"));

        setTimeout(() => {
            unidadSelect.value = unidadSelect.dataset.selected;
        }, 200);
    }, 200);
});
