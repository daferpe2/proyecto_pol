class LoadOrchestrator:
    def __init__(self, excel_reader, validator, separator, transformer, inserter):
        self.excel_reader = excel_reader
        self.validator = validator
        self.separator = separator
        self.transformer = transformer
        self.inserter = inserter

    def run(self, file: bytes, config: dict, context: dict, session):
        # 1. Leer Excel
        rows, total_filas = self.excel_reader.read(
            file,
            config["expected_columns"]
        )

        # 2. Validar y separar filas
        valid_rows, error_rows = self.separator.separate(
            rows,
            self.validator,
            config["schema"]
        )

        # 3. Transformar filas válidas
        models = self.transformer.transform(
            valid_rows,
            context,
            config["model_class"],
            config["schema"]
        )

        # 4. Bulk insert
        filas_insertadas = self.inserter.insert(models, session)

        # 5. Resumen final
        return {
            "total_filas": total_filas,
            "filas_insertadas": filas_insertadas,
            "filas_con_error": len(error_rows),
            "errores": error_rows
        }
