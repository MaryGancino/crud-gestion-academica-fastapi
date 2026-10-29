-- SISTEMA DE GESTION ACADEMICA
-- Las cinco tablas se crean cuando se inicia main.py por primera vez.
-- PK = clave primaria; FK = clave foranea.

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE
);

-- Relacion 1 a 1: cada usuario puede tener solo un perfil.
-- id_usuario es simultaneamente PK y FK.
CREATE TABLE IF NOT EXISTS perfiles (
    id_usuario INTEGER PRIMARY KEY,
    telefono TEXT,
    ciudad TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS materias (
    id_materia INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    creditos INTEGER NOT NULL CHECK(creditos BETWEEN 1 AND 12)
);

-- Relacion 1 a muchos: una materia puede tener varios paralelos.
CREATE TABLE IF NOT EXISTS paralelos (
    id_paralelo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_materia INTEGER NOT NULL,
    codigo TEXT NOT NULL,
    horario TEXT NOT NULL,
    FOREIGN KEY (id_materia) REFERENCES materias(id_materia) ON DELETE RESTRICT,
    UNIQUE(id_materia, codigo)
);

-- Relacion muchos a muchos entre usuarios y paralelos.
-- Se materializa con una tabla intermedia: matriculas.
CREATE TABLE IF NOT EXISTS matriculas (
    id_matricula INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_paralelo INTEGER NOT NULL,
    fecha TEXT NOT NULL DEFAULT (date('now')),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    FOREIGN KEY (id_paralelo) REFERENCES paralelos(id_paralelo) ON DELETE RESTRICT,
    UNIQUE(id_usuario, id_paralelo)
);
