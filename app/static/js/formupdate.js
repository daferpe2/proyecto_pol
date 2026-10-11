import { encryptJSON } from "/app/static/js/encryption.js";
document.getElementById("form-resultados-esp").addEventListener("submit", async (e) => {
    e.preventDefault();

    const form = e.target;                     // referencia directa al formulario
    const formData = new FormData(form);
    const json = Object.fromEntries(formData.entries());
    const id = json.id;

    // const AES_KEY_BASE64 = "pX0e1tZp7k0Q2s3J9g8H4l52uB8cD5pG6hI7jK8lM0o=";
    const AES_KEY_BASE64 = import.meta.env.PUBLIC_AES_KEY_BASE64;

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

