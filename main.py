"""CRUD universitario: Python + FastAPI + SQLite. Sin ORM ni Docker."""

import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


CARPETA = Path(__file__).resolve().parent
RUTA_BD = CARPETA / "universidad.db"
RUTA_SQL = CARPETA / "schema.sql"

app = FastAPI(
    title="Sistema de Gestión Académica",
    description="CRUD de usuarios, perfiles, materias, paralelos y matrículas con relaciones PK/FK.",
    version="1.0.0",
)


# 1. CONEXION A SQLITE

def conectar():
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row  # Permite convertir filas a diccionarios
    conexion.execute("PRAGMA foreign_keys = ON")  # Activar validacion de FK
    return conexion


def crear_tablas():
    with closing(conectar()) as conexion:
        conexion.executescript(RUTA_SQL.read_text(encoding="utf-8"))
        conexion.commit()


crear_tablas()


# 2. MODELOS DE DATOS: FastAPI valida lo que se recibe en POST y PUT.
class Usuario(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    apellido: str = Field(min_length=2, max_length=80)
    correo: str = Field(min_length=5, max_length=120)


class PerfilCrear(BaseModel):
    id_usuario: int = Field(gt=0)
    telefono: str | None = Field(default=None, max_length=30)
    ciudad: str | None = Field(default=None, max_length=100)


class PerfilActualizar(BaseModel):
    telefono: str | None = Field(default=None, max_length=30)
    ciudad: str | None = Field(default=None, max_length=100)


class Materia(BaseModel):
    codigo: str = Field(min_length=2, max_length=20)
    nombre: str = Field(min_length=2, max_length=100)
    creditos: int = Field(ge=1, le=12)


class Paralelo(BaseModel):
    id_materia: int = Field(gt=0)
    codigo: str = Field(min_length=1, max_length=20)
    horario: str = Field(min_length=2, max_length=100)


class Matricula(BaseModel):
    id_usuario: int = Field(gt=0)
    id_paralelo: int = Field(gt=0)


# 3. FUNCIONES QUE COMPARTEN LOS CRUD
# Solo estas tablas y columnas, definidas aqui, pueden formar consultas SQL.
CONFIG = {
    "usuarios": ("id_usuario", ("nombre", "apellido", "correo")),
    "perfiles": ("id_usuario", ("id_usuario", "telefono", "ciudad")),
    "materias": ("id_materia", ("codigo", "nombre", "creditos")),
    "paralelos": ("id_paralelo", ("id_materia", "codigo", "horario")),
    "matriculas": ("id_matricula", ("id_usuario", "id_paralelo")),
}


def error_base_datos(error):
    detalle = str(error)
    if "FOREIGN KEY" in detalle:
        mensaje = "El registro relacionado no existe o tiene dependencias que impiden borrarlo."
    elif "UNIQUE" in detalle or "PRIMARY KEY" in detalle:
        mensaje = "Registro duplicado: uno de los valores debe ser único."
    elif "CHECK" in detalle or "NOT NULL" in detalle:
        mensaje = "Un valor incumple las reglas de la tabla."
    else:
        mensaje = "No fue posible guardar los datos."
    raise HTTPException(status_code=409, detail=mensaje) from error


def listar(tabla):
    pk, _ = CONFIG[tabla]
    with closing(conectar()) as conexion:
        filas = conexion.execute(f"SELECT * FROM {tabla} ORDER BY {pk}").fetchall()
        return [dict(fila) for fila in filas]


def obtener(tabla, id_registro):
    pk, _ = CONFIG[tabla]
    with closing(conectar()) as conexion:
        fila = conexion.execute(
            f"SELECT * FROM {tabla} WHERE {pk} = ?", (id_registro,)
        ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return dict(fila)


def crear(tabla, datos):
    pk, columnas_permitidas = CONFIG[tabla]
    valores = datos.model_dump()
    columnas = [col for col in columnas_permitidas if col in valores]
    marcadores = ", ".join("?" for _ in columnas)
    sql = f"INSERT INTO {tabla} ({', '.join(columnas)}) VALUES ({marcadores})"
    try:
        with closing(conectar()) as conexion:
            cursor = conexion.execute(sql, tuple(valores[col] for col in columnas))
            conexion.commit()
            id_nuevo = valores[pk] if pk in valores else cursor.lastrowid
    except sqlite3.IntegrityError as error:
        error_base_datos(error)
    return obtener(tabla, id_nuevo)


def modificar(tabla, id_registro, datos):
    obtener(tabla, id_registro)  # Comprueba que exista antes de actualizar
    pk, columnas_permitidas = CONFIG[tabla]
    valores = datos.model_dump()
    columnas = [col for col in columnas_permitidas if col in valores and col != pk]
    asignaciones = ", ".join(f"{col} = ?" for col in columnas)
    sql = f"UPDATE {tabla} SET {asignaciones} WHERE {pk} = ?"
    parametros = tuple(valores[col] for col in columnas) + (id_registro,)
    try:
        with closing(conectar()) as conexion:
            conexion.execute(sql, parametros)
            conexion.commit()
    except sqlite3.IntegrityError as error:
        error_base_datos(error)
    return obtener(tabla, id_registro)


def eliminar(tabla, id_registro):
    pk, _ = CONFIG[tabla]
    try:
        with closing(conectar()) as conexion:
            cursor = conexion.execute(
                f"DELETE FROM {tabla} WHERE {pk} = ?", (id_registro,)
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Registro no encontrado")
            conexion.commit()
    except sqlite3.IntegrityError as error:
        error_base_datos(error)


# 4. RUTAS: GET, POST, PUT Y DELETE DE CADA TABLA
@app.get("/", tags=["Inicio"])
def inicio():
    return {"mensaje": "API funcionando", "documentacion": "/docs"}


# USUARIOS
@app.get("/usuarios", tags=["Usuarios"])
def listar_usuarios():
    return listar("usuarios")


@app.get("/usuarios/{id_usuario}", tags=["Usuarios"])
def obtener_usuario(id_usuario: int):
    return obtener("usuarios", id_usuario)


@app.post("/usuarios", status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def crear_usuario(datos: Usuario):
    return crear("usuarios", datos)


@app.put("/usuarios/{id_usuario}", tags=["Usuarios"])
def modificar_usuario(id_usuario: int, datos: Usuario):
    return modificar("usuarios", id_usuario, datos)


@app.delete("/usuarios/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT, tags=["Usuarios"])
def eliminar_usuario(id_usuario: int):
    eliminar("usuarios", id_usuario)


# PERFILES (relacion 1 a 1 con usuarios)
@app.get("/perfiles", tags=["Perfiles"])
def listar_perfiles():
    return listar("perfiles")


@app.get("/perfiles/{id_usuario}", tags=["Perfiles"])
def obtener_perfil(id_usuario: int):
    return obtener("perfiles", id_usuario)


@app.post("/perfiles", status_code=status.HTTP_201_CREATED, tags=["Perfiles"])
def crear_perfil(datos: PerfilCrear):
    return crear("perfiles", datos)


@app.put("/perfiles/{id_usuario}", tags=["Perfiles"])
def modificar_perfil(id_usuario: int, datos: PerfilActualizar):
    return modificar("perfiles", id_usuario, datos)


@app.delete("/perfiles/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT, tags=["Perfiles"])
def eliminar_perfil(id_usuario: int):
    eliminar("perfiles", id_usuario)


# MATERIAS
@app.get("/materias", tags=["Materias"])
def listar_materias():
    return listar("materias")


@app.get("/materias/{id_materia}", tags=["Materias"])
def obtener_materia(id_materia: int):
    return obtener("materias", id_materia)


@app.post("/materias", status_code=status.HTTP_201_CREATED, tags=["Materias"])
def crear_materia(datos: Materia):
    return crear("materias", datos)


@app.put("/materias/{id_materia}", tags=["Materias"])
def modificar_materia(id_materia: int, datos: Materia):
    return modificar("materias", id_materia, datos)


@app.delete("/materias/{id_materia}", status_code=status.HTTP_204_NO_CONTENT, tags=["Materias"])
def eliminar_materia(id_materia: int):
    eliminar("materias", id_materia)


# PARALELOS (cada paralelo pertenece a una materia)
@app.get("/paralelos", tags=["Paralelos"])
def listar_paralelos():
    return listar("paralelos")


@app.get("/paralelos/{id_paralelo}", tags=["Paralelos"])
def obtener_paralelo(id_paralelo: int):
    return obtener("paralelos", id_paralelo)


@app.post("/paralelos", status_code=status.HTTP_201_CREATED, tags=["Paralelos"])
def crear_paralelo(datos: Paralelo):
    return crear("paralelos", datos)


@app.put("/paralelos/{id_paralelo}", tags=["Paralelos"])
def modificar_paralelo(id_paralelo: int, datos: Paralelo):
    return modificar("paralelos", id_paralelo, datos)


@app.delete("/paralelos/{id_paralelo}", status_code=status.HTTP_204_NO_CONTENT, tags=["Paralelos"])
def eliminar_paralelo(id_paralelo: int):
    eliminar("paralelos", id_paralelo)


# MATRICULAS (tabla puente entre usuarios y paralelos)
@app.get("/matriculas", tags=["Matriculas"])
def listar_matriculas():
    return listar("matriculas")


@app.get("/matriculas/{id_matricula}", tags=["Matriculas"])
def obtener_matricula(id_matricula: int):
    return obtener("matriculas", id_matricula)


@app.post("/matriculas", status_code=status.HTTP_201_CREATED, tags=["Matriculas"])
def crear_matricula(datos: Matricula):
    return crear("matriculas", datos)


@app.put("/matriculas/{id_matricula}", tags=["Matriculas"])
def modificar_matricula(id_matricula: int, datos: Matricula):
    return modificar("matriculas", id_matricula, datos)


@app.delete("/matriculas/{id_matricula}", status_code=status.HTTP_204_NO_CONTENT, tags=["Matriculas"])
def eliminar_matricula(id_matricula: int):
    eliminar("matriculas", id_matricula)


# REPORTE CON JOIN: muestra relaciones de varias tablas al mismo tiempo
@app.get("/reportes/matriculas", tags=["Reportes"])
def reporte_matriculas():
    sql = """
        SELECT m.id_matricula, u.nombre || ' ' || u.apellido AS estudiante,
               u.correo, a.nombre AS materia, p.codigo AS paralelo,
               p.horario, m.fecha
        FROM matriculas AS m
        JOIN usuarios AS u ON u.id_usuario = m.id_usuario
        JOIN paralelos AS p ON p.id_paralelo = m.id_paralelo
        JOIN materias AS a ON a.id_materia = p.id_materia
        ORDER BY m.id_matricula
    """
    with closing(conectar()) as conexion:
        return [dict(fila) for fila in conexion.execute(sql).fetchall()]
