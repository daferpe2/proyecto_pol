# informe_depec.py
import os
from collections import defaultdict
from datetime import datetime

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

from app.operations.generacion_documento import numero_documento


def aplicar_bordes(tabla):
    tbl = tabla._tbl
    tblPr = tbl.tblPr

    borders = OxmlElement('w:tblBorders')

    for borde in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        elem = OxmlElement(f"w:{borde}")
        elem.set(qn('w:val'), 'single')
        elem.set(qn('w:sz'), '8')
        elem.set(qn('w:space'), '0')
        elem.set(qn('w:color'), '000000')
        borders.append(elem)

    tblPr.append(borders)


class InformeDEPEC:
    def __init__(self, registros, usuario):
        self.registros = registros
        self.usuario = usuario
        self.doc = Document()
        self.personas = self.agrupar_por_persona()

    def agrupar_por_persona(self):
        personas = defaultdict(lambda: {"nombre": None, "registros": []})
        for r in self.registros:
            cedula = r.no_cedula
            if personas[cedula]["nombre"] is None:
                personas[cedula]["nombre"] = r.apellidos_nombre
            personas[cedula]["registros"].append(r)
        return personas

    def construir_encabezado(self):
        # Título institucional
        titulo = self.doc.add_paragraph()
        run = titulo.add_run("INFORMACIÓN INTEGRADA DE CREDIBILIDAD Y CONFIABILIDAD")
        run.bold = True
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run.font.size = Pt(20)

        self.doc.add_paragraph("")  # espacio

        # Tabla institucional (fecha consulta, usuario, página)
        tabla_info = self.doc.add_table(rows=1, cols=3)
        tabla_info.autofit = True
        aplicar_bordes(tabla_info)
        hdr_cells = tabla_info.rows[0].cells
        ahora = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        hdr_cells[0].text = f"FECHA CONSULTA: {ahora}"
        hdr_cells[1].text = f"Generado por: {self.usuario.nombre_apellido}"
        hdr_cells[2].text = "Página x de y"  # texto fijo

        self.doc.add_paragraph("")  # espacio

        # Datos personales del primer sujeto
        primera_cedula = next(iter(self.personas.keys()))
        primera_persona = self.personas[primera_cedula]

        p1 = self.doc.add_paragraph()
        p1.add_run("NOMBRE COMPLETO: ").bold = True
        p1.add_run(primera_persona["nombre"])

        p2 = self.doc.add_paragraph()
        p2.add_run("No. DE IDENTIFICACIÓN: ").bold = True
        p2.add_run(primera_cedula)

        self.doc.add_paragraph("")  # espacio

    def construir_bloque_persona(self, cedula, persona):
        # Nombre y cédula (igual al documento)
        p1 = self.doc.add_paragraph()
        p1.add_run("NOMBRE COMPLETO: ").bold = True
        p1.add_run(persona["nombre"])

        p2 = self.doc.add_paragraph()
        p2.add_run("No. DE IDENTIFICACIÓN: ").bold = True
        p2.add_run(cedula)

        self.doc.add_paragraph("")  # espacio

        for r in persona["registros"]:
            self.construir_tabla_epp(r)
            self.doc.add_paragraph("")  # espacio entre E.P.P.

    def construir_tabla_epp(self, r):
        # Tabla principal de dos columnas para campos cortos
        tabla = self.doc.add_table(rows=0, cols=2)
        tabla.autofit = True
        aplicar_bordes(tabla)

        def fila_corta(label, valor):
            row = tabla.add_row()
            c1, c2 = row.cells
            c1.text = label
            c2.text = str(valor)
            # negrita en encabezado
            for run in c1.paragraphs[0].runs:
                run.bold = True

        fila_corta("FECHA DEL EXAMEN", r.fecha_asp)
        fila_corta("PROCESO", r.proceso)
        fila_corta("GRADO", r.grado)
        fila_corta("UNIDAD", r.batallon_buque_unidad_labora)
        fila_corta("CARGO", r.cargo)

        # Campos largos: RESULTADO, INFORMACIÓN OBTENIDA, TIPO HALLAZGO
        def bloque_largo(label, valor):
            # fila encabezado (celdas fusionadas)
            row_hdr = tabla.add_row()
            c_hdr = row_hdr.cells[0]
            c_hdr.merge(row_hdr.cells[1])
            c_hdr.text = label
            for run in c_hdr.paragraphs[0].runs:
                run.bold = True

            # fila valor (celdas fusionadas)
            row_val = tabla.add_row()
            c_val = row_val.cells[0]
            c_val.merge(row_val.cells[1])
            c_val.text = str(valor)

        bloque_largo("RESULTADO", r.resultados_obtenidos)
        bloque_largo("INFORMACIÓN OBTENIDA", r.observacion)
        bloque_largo("TIPO HALLAZGO", r.tipo_hallazgo)

    def exportar(self):
        # Construir documento completo
        self.construir_encabezado()

        # Primera persona ya se mostró en encabezado, pero también debe tener sus tablas
        for cedula, persona in self.personas.items():
            self.construir_bloque_persona(cedula, persona)

        # Nombre dinámico por fecha
        fecha_str = numero_documento()
        filename = f"informe_depec_{fecha_str}.docx"
        os.makedirs("temp", exist_ok=True)
        filepath = os.path.join("temp", filename)
        self.doc.save(filepath)
        return filepath


class InformeRDP:
    def __init__(self, registros, usuario):
        self.registros = registros
        self.usuario = usuario
        self.doc = Document()
        self.personas = self.agrupar_por_persona()

    def agrupar_por_persona(self):
        personas = defaultdict(lambda: {"nombre": None, "registros": []})
        for r in self.registros:
            cedula = r.no_cedula
            if personas[cedula]["nombre"] is None:
                personas[cedula]["nombre"] = r.apellidos_nombres
            personas[cedula]["registros"].append(r)
        return personas

    def construir_encabezado(self):
        # Título institucional
        titulo = self.doc.add_paragraph()
        run = titulo.add_run("INFORMACIÓN INTEGRADA RDP")
        run.bold = True
        titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run.font.size = Pt(20)

        self.doc.add_paragraph("")  # espacio

        # Tabla institucional (fecha consulta, usuario, página)
        tabla_info = self.doc.add_table(rows=1, cols=3)
        tabla_info.autofit = True
        aplicar_bordes(tabla_info)
        hdr_cells = tabla_info.rows[0].cells
        ahora = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        hdr_cells[0].text = f"FECHA CONSULTA: {ahora}"
        hdr_cells[1].text = f"Generado por: {self.usuario.nombre_apellido}"
        hdr_cells[2].text = "Página x de y"  # texto fijo

        self.doc.add_paragraph("")  # espacio

        # Datos personales del primer sujeto
        primera_cedula = next(iter(self.personas.keys()))
        primera_persona = self.personas[primera_cedula]

        p1 = self.doc.add_paragraph()
        p1.add_run("NOMBRE COMPLETO: ").bold = True
        p1.add_run(primera_persona["nombre"])

        p2 = self.doc.add_paragraph()
        p2.add_run("No. DE IDENTIFICACIÓN: ").bold = True
        p2.add_run(primera_cedula)

        self.doc.add_paragraph("")  # espacio

    def construir_bloque_persona(self, cedula, persona):
        # Nombre y cédula (igual al documento)
        p1 = self.doc.add_paragraph()
        p1.add_run("NOMBRE COMPLETO: ").bold = True
        p1.add_run(persona["nombre"])

        p2 = self.doc.add_paragraph()
        p2.add_run("No. DE IDENTIFICACIÓN: ").bold = True
        p2.add_run(cedula)

        self.doc.add_paragraph("")  # espacio

        for r in persona["registros"]:
            self.construir_tabla_epp(r)
            self.doc.add_paragraph("")  # espacio entre E.P.P.

    def construir_tabla_epp(self, r):
        # Tabla principal de dos columnas para campos cortos
        tabla = self.doc.add_table(rows=0, cols=2)
        tabla.autofit = True
        aplicar_bordes(tabla)

        def fila_corta(label, valor):
            row = tabla.add_row()
            c1, c2 = row.cells
            c1.text = label
            c2.text = str(valor)
            # negrita en encabezado
            for run in c1.paragraphs[0].runs:
                run.bold = True

        fila_corta("FECHA DEL EXAMEN", r.fecha_evaluacion)
        fila_corta("CATEGORIA", r.categoria)
        fila_corta("GRADO", r.grado)
        fila_corta("UNIDAD", r.batallon_buque_unidad_labora)
        fila_corta("CARGO", r.cargo)

        # Campos largos: RESULTADO, INFORMACIÓN OBTENIDA, TIPO HALLAZGO
        def bloque_largo(label, valor):
            # fila encabezado (celdas fusionadas)
            row_hdr = tabla.add_row()
            c_hdr = row_hdr.cells[0]
            c_hdr.merge(row_hdr.cells[1])
            c_hdr.text = label
            for run in c_hdr.paragraphs[0].runs:
                run.bold = True

            # fila valor (celdas fusionadas)
            row_val = tabla.add_row()
            c_val = row_val.cells[0]
            c_val.merge(row_val.cells[1])
            c_val.text = str(valor)

        bloque_largo("INFORMACIÓN RELEVANTE", r.informacion_relevante)
        bloque_largo("INFORMACIÓN OBTENIDA", r.observaciones)
        bloque_largo("RESULTADO EPP", r.resultado_epp)

    def exportar(self):
        # Construir documento completo
        self.construir_encabezado()

        # Primera persona ya se mostró en encabezado, pero también debe tener sus tablas
        for cedula, persona in self.personas.items():
            self.construir_bloque_persona(cedula, persona)

        # Nombre dinámico por fecha
        fecha_str = numero_documento()
        filename = f"informe_rdp_{fecha_str}.docx"
        os.makedirs("temp", exist_ok=True)
        filepath = os.path.join("temp", filename)
        self.doc.save(filepath)
        return filepath
