from datetime import datetime

class RowTransformer:
    def _to_bool(self, value):
        if value is None:
            return None
        value = str(value).strip().upper()
        return value in ["SI", "TRUE", "1"]

    def _to_date(self, value):
        from datetime import datetime
        if not value:
            return None

        formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
        for fmt in formatos:
            try:
                return datetime.strptime(value, fmt).date()
            except:
                pass
        return None

    def _convert_types(self, row, schema):
        converted = {}
        for campo, reglas in schema.items():
            valor = row.get(campo)

            tipo = reglas.get("type")
            if tipo == "date":
                converted[campo] = self._to_date(valor)
            elif tipo == "bool":
                converted[campo] = self._to_bool(valor)
            elif tipo == "int":
                converted[campo] = int(valor) if valor and str(valor).isdigit() else None
            else:
                converted[campo] = valor.strip() if isinstance(valor, str) else valor

        return converted

    def _build_texto_busqueda(self, row_data, campos):
        return " ".join([str(row_data.get(c, "")) for c in campos if row_data.get(c)])

    def transform(self, valid_rows: list[dict], context: dict, model_class: any, schema: dict):
        modelos = []

        for row in valid_rows:
            row_data = self._convert_types(row, schema)

            # Campos automáticos
            if "usuario_id" in context:
                row_data["usuario"] = context["usuario_id"]

            if "lista_esp_id" in context:
                row_data["lista_esp_id"] = context["lista_esp_id"]

            # NUEVO: texto_busqueda para ambas tablas
            if "no_cedula" in row_data and "apellidos_nombre" in row_data:
                # ESPF
                campos_espf = [
                    "no_cedula",
                    "apellidos_nombre",
                    "resultados_obtenidos",
                    "tipo_hallazgo",
                    "observacion"
                ]
                row_data["texto_busqueda"] = self._build_texto_busqueda(row_data, campos_espf)

            if "apellidos_nombres" in row_data:
                # POLI
                campos_poli = [
                    "no_cedula",
                    "apellidos_nombres",
                    "resultado_epp",
                    "tema_sr_di",
                    "observaciones"
                ]
                row_data["texto_busqueda"] = self._build_texto_busqueda(row_data, campos_poli)

            instancia = model_class(**row_data)
            modelos.append(instancia)

        return modelos
