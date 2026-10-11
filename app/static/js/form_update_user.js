import { encryptJSON } from "/app/static/js/encryption.js";

function formToJSON(form) {
    const formData = new FormData(form);
    const json = {};

    formData.forEach((value, key) => {
        if (json[key] !== undefined) {
            if (!Array.isArray(json[key])) {
                json[key] = [json[key]];
            }
            json[key].push(value);
        } else {
            json[key] = value;
        }
    });

    return json;
}

document.getElementById("form-user-update")
    .addEventListener("submit", async (e) => {

    e.preventDefault();
    const form = e.target;

    // Convertir formulario → JSON
    const json = formToJSON(form);

    // Verificar que el ID exista
    const id = json.id;
    if (!id) {
        alert("Error: el formulario no contiene el ID del usuario.");
        return;
    }

    // Obtener clave AES del backend
    const resKey = await fetch("/crypto/key");
    const data = await resKey.json();
    const AES_KEY_BASE64 = data.key.AES_KEY_BASE64;

    console.log("CLAVE RECIBIDA:", AES_KEY_BASE64);

    // Cifrar JSON
    const encrypted = await encryptJSON(json, AES_KEY_BASE64);

    // Enviar al backend
    const response = await fetch(`/usuarios/update/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(encrypted)
    });

    if (response.ok) {
        alert("Usuario actualizado correctamente");
        form.reset();
    } else {
        alert("Error al enviar");
    }
});
