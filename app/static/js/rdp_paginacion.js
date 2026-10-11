document.addEventListener("DOMContentLoaded", () => {

    const nextBtn = document.getElementById("btn-next");
    const prevBtn = document.getElementById("btn-prev");
    const rdpContainer = document.getElementById("rdp-container");

    async function cargar(cursor, direction) {
        const params = new URLSearchParams({
            last_id: cursor,
            direction: direction
        });

        const resp = await fetch(`/tabla-poligraf/lista_rdp_fragment?${params.toString()}`);
        const html = await resp.text();

        if (direction === "next") {
            // Agrega al final
            rdpContainer.insertAdjacentHTML("beforeend", html);
        } else {
            // Reemplaza todo
            rdpContainer.innerHTML = html;
        }
    }

    if (nextBtn) {
        nextBtn.addEventListener("click", () => {
            cargar(nextBtn.dataset.cursor, "next");
        });
    }

    if (prevBtn) {
        prevBtn.addEventListener("click", () => {
            cargar(prevBtn.dataset.cursor, "prev");
        });
    }
});
