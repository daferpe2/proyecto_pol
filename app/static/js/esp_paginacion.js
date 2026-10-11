// static/js/sdp_paginacion.js
document.addEventListener("DOMContentLoaded", () => {

    const nextBtn = document.getElementById("btn-next");
    const prevBtn = document.getElementById("btn-prev");
    const espContainer = document.getElementById("esp-container");

    async function cargar(cursor, direction) {
        const params = new URLSearchParams({
            last_id: cursor || "",
            direction: direction
        });

        const resp = await fetch(`/tabla-base-esp/lista_esp_fragment?${params.toString()}`);
        const html = await resp.text();

        // Crear contenedor temporal para leer inputs ocultos
        const temp = document.createElement("div");
        temp.innerHTML = html;

        // Leer nuevos cursores
        const newNext = temp.querySelector("#fragment-next-cursor")?.value || "";
        const newPrev = temp.querySelector("#fragment-prev-cursor")?.value || "";

        // Eliminar inputs ocultos antes de insertar
        const hiddenNext = temp.querySelector("#fragment-next-cursor");
        const hiddenPrev = temp.querySelector("#fragment-prev-cursor");
        if (hiddenNext) hiddenNext.remove();
        if (hiddenPrev) hiddenPrev.remove();

        const cardsHTML = temp.innerHTML;

        // Insertar contenido
        if (direction === "next") {
            espContainer.insertAdjacentHTML("beforeend", cardsHTML);
        } else {
            espContainer.innerHTML = cardsHTML;
        }

        // Actualizar cursores en botones
        if (nextBtn) {
            if (newNext) {
                nextBtn.dataset.cursor = newNext;
                nextBtn.style.display = "inline-block";
            } else {
                nextBtn.style.display = "none";
            }
        }

        if (prevBtn) {
            if (newPrev) {
                prevBtn.dataset.cursor = newPrev;
                prevBtn.style.display = "inline-block";
            } else {
                prevBtn.style.display = "none";
            }
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
