// ===============================
// 1. Abrir/cerrar acordeones
// ===============================
document.querySelectorAll(".qc-acordeon-title").forEach(title => {
    title.addEventListener("click", () => {
        const acordeon = title.parentElement;

        // Alternar clase "open"
        acordeon.classList.toggle("open");

        // Scroll suave al acordeón
        acordeon.scrollIntoView({ behavior: "smooth", block: "start" });
    });
});


// ===============================
// 2. Botones superiores → scroll + abrir acordeón
// ===============================
document.querySelectorAll(".qc-nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        const targetSelector = btn.getAttribute("data-target");
        const acordeon = document.querySelector(targetSelector);

        if (!acordeon) return;

        // Abrir acordeón si está cerrado
        if (!acordeon.classList.contains("open")) {
            acordeon.classList.add("open");
        }

        // Scroll suave al acordeón
        acordeon.scrollIntoView({ behavior: "smooth", block: "start" });
    });
});


// ===============================
// 3. Cerrar todos los acordeones excepto el que se abre
//    (opcional, pero mejora la experiencia)
// ===============================
document.querySelectorAll(".qc-acordeon-title").forEach(title => {
    title.addEventListener("click", () => {
        const current = title.parentElement;

        document.querySelectorAll(".qc-acordeon").forEach(acordeon => {
            if (acordeon !== current) {
                acordeon.classList.remove("open");
            }
        });
    });
});


// ===============================
// 4. Botones superiores también cierran los demás acordeones
// ===============================
document.querySelectorAll(".qc-nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        const targetSelector = btn.getAttribute("data-target");
        const target = document.querySelector(targetSelector);

        document.querySelectorAll(".qc-acordeon").forEach(acordeon => {
            if (acordeon !== target) {
                acordeon.classList.remove("open");
            }
        });
    });
});

// ===============================
// 5. Controlar el scroll al hacer focus en inputs
// ===============================
document.querySelectorAll("input, textarea, select").forEach(el => {
    el.addEventListener("focus", () => {

        // Encuentra el acordeón padre
        const acordeon = el.closest(".qc-acordeon");

        if (acordeon && !acordeon.classList.contains("open")) {
            acordeon.classList.add("open");
        }

        // Scroll controlado: evita que el navegador centre el input
        acordeon.scrollIntoView({
            behavior: "smooth",
            block: "nearest"   // ← ESTA ES LA CLAVE
        });
    });
});

