// Convierte texto a bytes
function encodeUTF8(str) {
    return new TextEncoder().encode(str);
}

// Convierte bytes a Base64
function bytesToBase64(bytes) {
    return btoa(String.fromCharCode(...bytes));
}

// Convierte Base64 a bytes
function base64ToBytes(base64) {
    return Uint8Array.from(atob(base64), c => c.charCodeAt(0));
}

// Cifra un objeto JSON usando AES-GCM
async function encryptJSON(data, base64Key) {
    const keyBytes = base64ToBytes(base64Key);

    const cryptoKey = await crypto.subtle.importKey(
        "raw",
        keyBytes,
        { name: "AES-GCM" },
        false,
        ["encrypt"]
    );

    const iv = crypto.getRandomValues(new Uint8Array(12));

    const encoded = encodeUTF8(JSON.stringify(data));

    const encrypted = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv },
        cryptoKey,
        encoded
    );

    return {
        iv: bytesToBase64(iv),
        payload: bytesToBase64(new Uint8Array(encrypted))
    };
}

export { encryptJSON };
