/**
 * Módulo genérico para manejar buscadores Excel (ESP y RDP)
 * Cada buscador se inicializa llamando initExcelBuscador(config)
 */

function initExcelBuscador({
    formId,
    statusId,
    messageId,
    spinnerId,
    downloadBtnId,
    uploadUrl,
    resultUrlBase,
    downloadFilenamePrefix
}) {

    const form = document.getElementById(formId);
    const status = document.getElementById(statusId);
    const message = document.getElementById(messageId);
    const spinner = document.getElementById(spinnerId);
    const btnDescargar = document.getElementById(downloadBtnId);

    let jobId = null;

    // -----------------------------
    // 1. SUBIR ARCHIVO EXCEL
    // -----------------------------
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);

        status.style.display = "block";
        spinner.style.display = "block";
        message.textContent = "Subiendo archivo Excel...";

        try {
            const resp = await fetch(uploadUrl, {
                method: "POST",
                body: formData
            });

            const data = await resp.json();

            if (!resp.ok) {
                message.textContent = "Error: " + (data.detail || "Error desconocido");
                spinner.style.display = "none";
                return;
            }

            jobId = data.job_id;

            message.textContent = "Archivo recibido. Procesando...";
            verificarEstadoJob();

        } catch (error) {
            message.textContent = "Error al subir archivo.";
            spinner.style.display = "none";
        }
    });

    // -----------------------------
    // 2. VERIFICAR ESTADO DEL JOB
    // -----------------------------
    async function verificarEstadoJob() {
        if (!jobId) return;

        try {
            const resp = await fetch(`${resultUrlBase}/${jobId}`);
            const data = await resp.json();

            if (data.estado === "PENDIENTE" || data.estado === "EN_PROCESO") {
                message.textContent = "Procesando archivo...";
                setTimeout(verificarEstadoJob, 2000);
                return;
            }

            if (data.estado === "COMPLETADO") {
                spinner.style.display = "none";
                message.textContent = "Procesamiento completado.";
                btnDescargar.style.display = "block";
                return;
            }

            if (data.estado.startsWith("ERROR")) {
                spinner.style.display = "none";
                message.textContent = "Error: " + (data.mensaje_error_global || data.error_detalle || "Error en el procesamiento");
                return;
            }

            if (data.estado === "EXPIRADO") {
                spinner.style.display = "none";
                message.textContent = "El archivo ya no está disponible.";
                return;
            }

        } catch (error) {
            spinner.style.display = "none";
            message.textContent = "Error al consultar estado del job.";
        }
    }

    // -----------------------------
    // 3. DESCARGAR ARCHIVO EXCEL
    // -----------------------------
    btnDescargar.addEventListener("click", async () => {
        if (!jobId) return;

        try {
            const resp = await fetch(`${resultUrlBase}/${jobId}?descargar=true`);

            if (!resp.ok) {
                message.textContent = "Error al descargar archivo.";
                return;
            }

            const blob = await resp.blob();
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = `${downloadFilenamePrefix}_${jobId}.xlsx`;
            a.click();

            window.URL.revokeObjectURL(url);

        } catch (error) {
            message.textContent = "Error al descargar archivo.";
        }
    });
}


// =====================================================
// Inicializar buscador ESP
// =====================================================
initExcelBuscador({
    formId: "form-upload",
    statusId: "job-status",
    messageId: "job-message",
    spinnerId: "spinner",
    downloadBtnId: "btn-descargar",
    uploadUrl: "/buscador-csv/upload",   // ← si cambias la ruta, actualízala aquí
    resultUrlBase: "/buscador-csv/result",
    downloadFilenamePrefix: "resultado_job"
});

// =====================================================
// Inicializar buscador RDP
// =====================================================
initExcelBuscador({
    formId: "form-upload-rdp",
    statusId: "job-status-rdp",
    messageId: "job-message-rdp",
    spinnerId: "spinner-rdp",
    downloadBtnId: "btn-descargar-rdp",
    uploadUrl: "/tabla-poligraf/upload",
    resultUrlBase: "/tabla-poligraf/result",
    downloadFilenamePrefix: "buscador_rdp_resultados"
});
