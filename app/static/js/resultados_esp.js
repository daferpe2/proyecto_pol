// ===============================
// RESULTADOS ESP - LÓGICA COMPLETA
// ===============================

// Mapeo de secciones en orden fijo
const SECCIONES = [
  "ACADÉMICO",
  "LABORAL",
  "LISTAS RESTRICTIVAS",
  "ANTECEDENTES (BASES / ADVERSOS)",
  "NÚCLEO FAMILIAR",
  "VISITA DE SEGURIDAD",
  "SALUD",
  "OTRO"
];

// Selects del formulario
const selects = {
  "ACADÉMICO": document.querySelector('select[name="acad"]'),
  "LABORAL": document.querySelector('select[name="lab"]'),
  "LISTAS RESTRICTIVAS": document.querySelector('select[name="listas"]'),
  "ANTECEDENTES (BASES / ADVERSOS)": document.querySelector('select[name="antecedentes"]'),
  "NÚCLEO FAMILIAR": document.querySelector('select[name="nucleo"]'),
  "VISITA DE SEGURIDAD": document.querySelector('select[name="visita"]'),
  "SALUD": document.querySelector('select[name="salud"]'),
  "OTRO": document.querySelector('select[name="otro"]')
};

const otroTexto = document.querySelector('input[name="otro_texto"]');
const textarea = document.getElementById("resultados_obtenidos");
const banner = document.getElementById("banner-corrupto");

// ===============================
// 1. GENERAR TEXTO AUTOMÁTICO
// ===============================
function generarTexto() {
  let resultado = "";

  SECCIONES.forEach(sec => {
    let valor = selects[sec].value || "-";

    if (sec === "OTRO") {
      const textoExtra = otroTexto.value.trim();
      valor = textoExtra !== "" ? textoExtra : valor;
    }

    resultado += `${sec}: ${valor}\n`;
  });

  textarea.value = resultado.trim();
}

// ===============================
// 2. PARSEAR TEXTO GUARDADO
// ===============================
function parsearTextoGuardado() {
  const texto = textarea.value.trim();

  if (!texto) return; // No hay nada guardado

  const lineas = texto.split("\n");

  // Validación estricta: TODAS las líneas deben cumplir el formato
  if (lineas.length !== SECCIONES.length) {
    mostrarBanner();
    return;
  }

  let valido = true;

  lineas.forEach((linea, index) => {
    const [sec, valor] = linea.split(": ");

    if (!sec || !valor || sec.trim() !== SECCIONES[index]) {
      valido = false;
    }
  });

  if (!valido) {
    mostrarBanner();
    return;
  }

  // Si es válido, reconstruimos selects
  lineas.forEach((linea, index) => {
    const [sec, valor] = linea.split(": ");

    if (sec === "OTRO") {
      if (["SH", "CH", "CHm", "N.E."].includes(valor)) {
        selects[sec].value = valor;
        otroTexto.value = "";
      } else {
        selects[sec].value = "";
        otroTexto.value = valor;
      }
    } else {
      selects[sec].value = valor;
    }
  });

  ocultarBanner();
}

// ===============================
// 3. BANNER DESTACADO
// ===============================
function mostrarBanner() {
  banner.style.display = "block";

  // Selects vacíos
  Object.values(selects).forEach(sel => sel.value = "");

  // No regeneramos texto: dejamos el corrupto tal cual
}

function ocultarBanner() {
  banner.style.display = "none";
}

// ===============================
// 4. EVENTOS
// ===============================
Object.values(selects).forEach(sel => {
  sel.addEventListener("change", () => {
    ocultarBanner();
    generarTexto();
  });
});

otroTexto.addEventListener("input", () => {
  ocultarBanner();
  generarTexto();
});

// ===============================
// 5. INICIALIZACIÓN
// ===============================
parsearTextoGuardado();
generarTexto();
window.generarTexto = generarTexto;
