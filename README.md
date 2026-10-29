# CRUD - Sistema de Gestión Académica

Proyecto educativo con **Python 3.10+**, **FastAPI** y **SQLite**. Se ejecuta en Visual Studio Code y se prueba en Swagger UI. No requiere PostgreSQL, MongoDB ni Docker.

## 1. Abrir el proyecto

1. Descomprime `CRUD_Gestion_Academica.zip`.
2. Abre **Visual Studio Code > Archivo > Abrir carpeta** y selecciona `CRUD_Gestion_Academica`.
3. En VS Code, abre **Terminal > Nuevo terminal** (PowerShell o CMD).
4. Comprueba que Python esté instalado: `py --version` (si no funciona, prueba `python --version`).

## 2. Crear entorno virtual e instalar dependencias (Windows)

Ejecuta los siguientes comandos **en la terminal de la carpeta del proyecto**:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Estos comandos funcionan sin tener que activar el entorno virtual; por eso no suelen tener problemas con las políticas de ejecución de PowerShell. Si `py` no existe, usa `python` en su lugar en el primer comando.

## 3. Iniciar la API

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Abre **http://127.0.0.1:8000/docs** en el navegador. Ahí estarán las operaciones GET, POST, PUT y DELETE clasificadas por tabla. SQLite crea automáticamente `universidad.db` con las 5 tablas al iniciar.

Para parar la API: `Ctrl+C` en la terminal.

## 4. Cargar registros de demostración (opcional)

En otra terminal de VS Code, con la API en marcha o detenida:

```powershell
.\.venv\Scripts\python.exe cargar_ejemplos.py
```

Esto añade estudiantes, materias, paralelos y matrículas **ficticios**. No borra tus registros existentes. Puedes volver a ejecutar el script sin duplicar esos datos.

## 5. Primera prueba del CRUD con Swagger

1. Abre `GET /usuarios` > **Try it out** > **Execute**: verás los usuarios existentes.
2. Abre `POST /usuarios` > **Try it out** > introduce:

   ```json
   {"nombre": "Carla", "apellido": "Prueba", "correo": "carla.prueba@universidad.test"}
   ```

   Pulsa **Execute**. Anota el `id_usuario` de la respuesta.
3. Abre `PUT /usuarios/{id_usuario}` > **Try it out**, ingresa ese ID y este cuerpo:

   ```json
   {"nombre": "Carla", "apellido": "Prueba", "correo": "carla.actualizada@universidad.test"}
   ```

4. Abre `GET /usuarios/{id_usuario}` y confirma el cambio.
5. Abre `DELETE /usuarios/{id_usuario}` con el mismo ID, y presiona **Execute**. El código 204 significa eliminación correcta.
6. Vuelve a hacer GET: el usuario eliminado ya no debe aparecer.

**IMPORTANTE:** Si intentas borrar una materia que tiene paralelos, o un usuario que tiene matrículas/perfil, SQLite impide el borrado hasta que elimines primero los registros relacionados. Esto comprueba que las llaves foráneas están activadas.

## 6. Cómo probar las relaciones

- `GET /materias` y `GET /paralelos`: relación 1 a muchos.
- `GET /usuarios` y `GET /perfiles`: relación 1 a 1.
- `GET /matriculas` y `GET /reportes/matriculas`: relación muchos a muchos a través de la tabla puente.
- Para crear una matrícula con `POST /matriculas`, primero debes tener un `id_usuario` y un `id_paralelo` válidos.

## 7. Archivos del proyecto

- `main.py` - FastAPI, 25 endpoints CRUD (5 por tabla), un reporte JOIN.
- `schema.sql` - creación de 5 tablas, claves primarias y foráneas.
- `datos_ejemplo.sql` - ejemplos ficticios.
- `cargar_ejemplos.py` - carga de ejemplos.
- `requirements.txt` - librerías para instalar.
- `Arquitectura_y_Modelo_Relacional.pdf` - explicación, esquema y normalización.
- `universidad.db` - base de datos SQLite, se crea **automáticamente** al ejecutar `main.py`.

## 8. Errores habituales

- **'py' no se reconoce:** usa `python` o reinstala Python activando la opción de agregarlo al PATH.
- **'No module named fastapi':** instala con `-m pip install -r requirements.txt` usando el mismo Python del entorno virtual.
- **'Address already in use':** cierra la API anterior (`Ctrl+C`) o ejecuta Uvicorn con `--port 8001`; entonces usa http://127.0.0.1:8001/docs.
- **404:** el ID solicitado no existe.
- **409:** dato único duplicado o conflicto con una relación entre tablas.
- **422:** el cuerpo JSON está incompleto o contiene datos incompatibles.
- **SQLite no aparece en el explorador de bases:** abre el archivo `universidad.db` usando una extensión de SQLite para VS Code o la aplicación gratuita DB Browser for SQLite (opcional).

### Conceptos

- **PK:** identificador único de una fila.
- **FK:** valor que apunta a la PK de otra tabla y permite validar relaciones.
- **1:1:** usuarios -> perfiles, máximo un perfil por usuario.
- **1:N:** materias -> paralelos, una materia puede tener muchos paralelos.
- **N:M:** usuarios <-> paralelos, implementado mediante matriculas.
- **Normalización:** separar entidades para evitar repetir datos y anomalías al modificar registros.

> Proyecto de práctica educativa. No incluye autenticación ni permisos: no lo expongas directamente a Internet ni guardes datos personales reales sin autorización.
