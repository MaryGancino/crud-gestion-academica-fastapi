"""Carga registros ficticios, sin borrar los datos que ya existan."""
from contextlib import closing
from main import conectar, CARPETA

with closing(conectar()) as conexion:
    conexion.executescript((CARPETA / "datos_ejemplo.sql").read_text(encoding="utf-8"))
    conexion.commit()

print("Datos ficticios cargados. Abre http://127.0.0.1:8000/docs para ver el CRUD.")
