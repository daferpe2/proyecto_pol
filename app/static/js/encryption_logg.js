// ===============================
// 1. Obtener llave pública RSA
// ===============================
async function getLoginPublicKey() {
    const res = await fetch("/crypto/login-public-key");
    const { public_key } = await res.json();
    return public_key;
}

// ===============================
// 2. Convertir PEM → ArrayBuffer
// ===============================
function pemToBinary(pem) {
    // Elimina encabezados y pies del PEM
    const pemContents = pem
        .replace("-----BEGIN PUBLIC KEY-----", "")
        .replace("-----END PUBLIC KEY-----", "")
        .replace(/\s+/g, "");

    const binaryDer = atob(pemContents);
    const bytes = new Uint8Array(binaryDer.length);

    for (let i = 0; i < binaryDer.length; i++) {
        bytes[i] = binaryDer.charCodeAt(i);
    }

    return bytes.buffer;
}

// ===============================
// 3. Importar llave pública RSA
// ===============================
async function importRSAPublicKey(pem) {
    const binary = pemToBinary(pem);

    return await crypto.subtle.importKey(
        "spki",
        binary,
        {
            name: "RSA-OAEP",
            hash: "SHA-256"
        },
        false,
        ["encrypt"]
    );
}

// ===============================
// 4. Cifrar datos del login
// ===============================
async function encryptLoginData(data) {
    const pem = await getLoginPublicKey();
    const publicKey = await importRSAPublicKey(pem);

    const encoded = new TextEncoder().encode(JSON.stringify(data));

    const encrypted = await crypto.subtle.encrypt(
        { name: "RSA-OAEP" },
        publicKey,
        encoded
    );

    return {
        payload: btoa(String.fromCharCode(...new Uint8Array(encrypted)))
    };
}
