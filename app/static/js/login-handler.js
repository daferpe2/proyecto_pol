// login-handler.js
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-login");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        // 1. Obtener valores del formulario
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        if (!email || !password) {
            alert("Debe ingresar correo y contraseña.");
            return;
        }

        try {
            // 2. Cifrar con RSA‑OAEP usando encryptLoginData()
            const encrypted = await encryptLoginData({ email, password });

            // 3. Enviar al backend
            const res = await fetch("/inicio_sesion", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(encrypted)
            });

            // 4. Manejo de respuesta
            if (res.ok) {
                // Login correcto → redirigir
                window.location.href = "/home";
            } else {
                // Error del backend
                const error = await res.json().catch(() => null);
                console.error("Error en login:", error);
                alert("Credenciales incorrectas o error en el servidor.");
            }

        } catch (err) {
            console.error("Error cifrando o enviando login:", err);
            alert("Error interno al procesar el inicio de sesión.");
        }
    });
});

