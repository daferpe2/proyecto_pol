schema_tabla_base_espf = {
    "expected_columns": [
        "fecha_asp",
        "proceso",
        "fuerza_jefatura",
        "comando_direccion_brigada_flotilla_grupo",
        "batallon_buque_unidad_labora",
        "no_cedula",
        "clase",
        "grado",
        "apellidos_nombre",
        "cargo",
        "resultados_obtenidos",
        "tipo_hallazgo",
        "observacion",
        "regional", 
    ],

    "schema": {
        "fecha_asp": {
            "type": "date",
            "required": True
        },
        "proceso": {
            "type": "str",
            "required": True
        },
        "fuerza_jefatura": {
            "type": "str",
            "required": True
        },
        "comando_direccion_brigada_flotilla_grupo": {
            "type": "str",
            "required": True
        },
        "batallon_buque_unidad_labora": {
            "type": "str",
            "required": True
        },
        "no_cedula": {
            "type": "str",
            "required": True,
            "numeric": True,
            "min_length": 5,
            "max_length": 15
        },
        "clase": {
            "type": "str",
            "required": True
        },
        "grado": {
            "type": "str",
            "required": True
        },
        "apellidos_nombre": {
            "type": "str",
            "required": True
        },
        "cargo": {
            "type": "str",
            "required": True
        },
        "resultados_obtenidos": {
            "type": "str",
            "required": True
        },
        "tipo_hallazgo": {
            "type": "str",
            "required": True
        },
        "observacion": {
            "type": "str",
            "required": True
        },
        "regional": {
            "type": "str",
            "required": True
        },
        "texto_busqueda": {"type": "str", "required": False}
    }
}
