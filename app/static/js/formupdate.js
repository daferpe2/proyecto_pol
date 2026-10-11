import { encryptJSON } from "/app/static/js/encryption.js";
document.getElementById("form-resultados-esp").addEventListener("submit", async (e) => {
    e.preventDefault();

    const form = e.target;                     // referencia directa al formulario
    const formData = new FormData(form);
    const json = Object.fromEntries(formData.entries());
    const id = json.id;

    const resKey = await fetch("/crypto/key");
    const data = await resKey.json();

    const AES_KEY_BASE64 = data.key.AES_KEY_BASE64;   // ← ESTA ES LA CLAVE REAL
    console.log("CLAVE RECIBIDA:", AES_KEY_BASE64);

    const encrypted = await encryptJSON(json, AES_KEY_BASE64);

    const response = await fetch(`/tabla-base-esp/update/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(encrypted)
    });

    if (response.ok) {
        alert("Formulario enviado de forma cifrada");

        // 🔥 LIMPIAR FORMULARIO
        form.reset();

        // 🔥 OPCIONAL: limpiar selects, radios o inputs especiales
        // form.querySelectorAll("input, select, textarea").forEach(el => el.value = "");

    } else {
        alert("Error al enviar");
    }
});

