class RowSeparator:
    def separate(self, rows: list[dict], validator, schema: dict):
        valid_rows = []
        error_rows = []

        for index, row in enumerate(rows):
            is_valid, errors = validator.validate(row, schema)

            if is_valid:
                valid_rows.append(row)
            else:
                error_rows.append({
                    "fila": index + 2,  # +2 porque la fila 1 es cabecera
                    "motivo": "; ".join(errors)
                })

        return valid_rows, error_rows
