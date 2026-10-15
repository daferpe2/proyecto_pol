import { encryptJSON } from "/app/static/js/encryption.js";

document.getElementById("form-rdp").addEventListener("submit", async (e) => {
    e.preventDefault();

    const form = e.target;

    // ============================
    // 1. Obtener clave AES del backend
    // ============================
    const resKey = await fetch("/crypto/key");
    const data = await resKey.json();

    const AES_KEY_BASE64 = data.key.AES_KEY_BASE64;   // ← ESTA ES LA CLAVE REAL
    console.log("CLAVE RECIBIDA:", AES_KEY_BASE64);
    // ============================
    // 2. Asegurar que campos disabled entren al JSON
    // ============================
    const resultadoTmd = document.getElementById("resultado_tmd");
    const tipoSustancia = document.getElementById("tipo_sustancia");

    const disabledFields = [];

    [resultadoTmd, tipoSustancia].forEach(field => {
        if (field.disabled) {
            disabledFields.push(field);
            field.disabled = false;
        }
    });

    // ============================
    // 3. Construir JSON
    // ============================
    const formData = new FormData(form);
    const json = Object.fromEntries(formData.entries());

    // ============================
    // 4. Restaurar disabled
    // ============================
    disabledFields.forEach(field => field.disabled = true);

    // ============================
    // 5. Encriptar
    // ============================

    const encrypted = await encryptJSON(json, AES_KEY_BASE64);

    // ============================
    // 6. Enviar al backend
    // ============================
    const response = await fetch("/tabla-poligraf/create_poli", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(encrypted)
    });

    if (response.ok) {
        alert("Formulario enviado de forma cifrada");
        form.reset();
    } else {
        alert("Error al enviar");
    }
});
