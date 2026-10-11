class RowValidator:
    def validate(self, row: dict, schema: dict):
        errores = []

        for campo, reglas in schema.items():
            valor = row.get(campo)

            # 1. Obligatorio
            if reglas.get("required") and not valor:
                errores.append(f"{campo} es obligatorio")
                continue

            # 2. Tipo
            tipo = reglas.get("type")
            if tipo == "date":
                from datetime import datetime
                formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
                valido = False
                for fmt in formatos:
                    try:
                        datetime.strptime(str(valor), fmt)
                        valido = True
                        break
                    except:
                        pass
                if not valido:
                    errores.append(f"{campo} debe ser una fecha válida")

            if tipo == "int" and (not str(valor).isdigit()):
                errores.append(f"{campo} debe ser numérico")

            if tipo == "bool":
                if str(valor).upper() not in ["SI", "NO", "TRUE", "FALSE", "1", "0"]:
                    errores.append(f"{campo} debe ser booleano (SI/NO)")

            # 3. numeric=True
            if reglas.get("numeric") and not str(valor).isdigit():
                errores.append(f"{campo} debe ser numérico")

            # 4. allowed_values
            if "allowed_values" in reglas:
                if valor not in reglas["allowed_values"]:
                    errores.append(f"{campo} debe ser uno de: {', '.join(reglas['allowed_values'])}")

            # 5. required_if
            if "required_if" in reglas:
                condicion_campo, condicion_valor = list(reglas["required_if"].items())[0]
                if row.get(condicion_campo) == condicion_valor and not valor:
                    errores.append(
                        f"{campo} es obligatorio cuando {condicion_campo}={condicion_valor}"
                    )

        return (len(errores) == 0, errores)
