// Lista temporal en localStorage
const KEY = "lista_informe_poligrafico";

function agregarAInforme(id) {
    let lista = JSON.parse(localStorage.getItem(KEY)) || [];

    if (!lista.includes(id)) {
        lista.push(id);
        localStorage.setItem(KEY, JSON.stringify(lista));
        alert("Agregado al informe");
    }
}

async function generarInforme() {
    let lista = JSON.parse(localStorage.getItem(KEY)) || [];

    if (lista.length === 0) {
        alert("No hay elementos en la lista");
        return;
    }

    const response = await fetch("/resultados-poligraficos/generar-informe-depec", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids: lista })
    });

    if (!response.ok) {
        alert("Error generando informe");
        return;
    }

    // Descargar archivo
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "informe_poligrafico.docx";
    document.body.appendChild(a);
    a.click();
    a.remove();

    // Limpiar lista
    localStorage.removeItem(KEY);
}

async function generarInformeRdp() {
    let lista = JSON.parse(localStorage.getItem(KEY)) || [];

    if (lista.length === 0) {
        alert("No hay elementos en la lista");
        return;
    }

    const response = await fetch("/resultados-poligraficos/generar-informe-rdp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids: lista })
    });

    if (!response.ok) {
        alert("Error generando informe");
        return;
    }

    // Descargar archivo
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "informe_poligrafico.docx";
    document.body.appendChild(a);
    a.click();
    a.remove();

    // Limpiar lista
    localStorage.removeItem(KEY);
}
