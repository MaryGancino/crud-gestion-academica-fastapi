-- Datos TOTALMENTE ficticios. Puedes modificarlos y usar los de tu curso,
-- pero pide permiso antes de registrar datos personales reales.

INSERT OR IGNORE INTO usuarios (nombre, apellido, correo) VALUES
('Ana', 'Ejemplo', 'ana.ejemplo@universidad.test'),
('Luis', 'Demo', 'luis.demo@universidad.test');

INSERT OR IGNORE INTO perfiles (id_usuario, telefono, ciudad)
SELECT id_usuario, '0990000000', 'Quito'
FROM usuarios WHERE correo = 'ana.ejemplo@universidad.test';

INSERT OR IGNORE INTO materias (codigo, nombre, creditos) VALUES
('MAT201', 'Análisis Matemático II', 5),
('PRO102', 'Programación', 4);

INSERT OR IGNORE INTO paralelos (id_materia, codigo, horario)
SELECT id_materia, '02', 'Lunes 08:00-10:00'
FROM materias WHERE codigo = 'MAT201';

INSERT OR IGNORE INTO paralelos (id_materia, codigo, horario)
SELECT id_materia, '01', 'Miércoles 10:00-12:00'
FROM materias WHERE codigo = 'PRO102';

INSERT OR IGNORE INTO matriculas (id_usuario, id_paralelo)
SELECT u.id_usuario, p.id_paralelo
FROM usuarios AS u
JOIN paralelos AS p ON p.codigo = '02'
JOIN materias AS a ON a.id_materia = p.id_materia AND a.codigo = 'MAT201'
WHERE u.correo = 'ana.ejemplo@universidad.test';
