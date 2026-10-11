class UnknownTableError(Exception):
    pass


class LoadConfig:
    def __init__(self, schemas, models):
        self.schemas = schemas
        self.models = models

    def get_config(self, table_name: str):
        if table_name not in self.schemas or table_name not in self.models:
            raise UnknownTableError(f"No existe configuración para '{table_name}'")

        return {
            "expected_columns": self.schemas[table_name]["expected_columns"],
            "schema": self.schemas[table_name]["schema"],
            "model_class": self.models[table_name],
            "transformer": self.schemas[table_name]["transformer"]
        }
