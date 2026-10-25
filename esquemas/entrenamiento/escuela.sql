-- Esquema: escuela — Centro educativo: estudiantes, cursos y notas.

CREATE TABLE `estudiantes` (
  `id_est` INT NOT NULL COMMENT 'Id del estudiante',
  `nombre` VARCHAR(100) COMMENT 'Nombre',
  `grado` VARCHAR(20) COMMENT 'Grado',
  PRIMARY KEY (`id_est`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Estudiantes inscritos';

CREATE TABLE `cursos` (
  `id_curso` INT NOT NULL COMMENT 'Id del curso',
  `nombre` VARCHAR(80) COMMENT 'Nombre del curso',
  `creditos` INT COMMENT 'Créditos del curso',
  PRIMARY KEY (`id_curso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Cursos impartidos';

CREATE TABLE `notas` (
  `id_nota` INT NOT NULL COMMENT 'Id de la nota',
  `id_est` INT COMMENT 'Estudiante',
  `id_curso` INT COMMENT 'Curso',
  `nota` DECIMAL(5,2) COMMENT 'Nota de 0 a 100',
  PRIMARY KEY (`id_nota`),
  FOREIGN KEY (`id_est`) REFERENCES `estudiantes` (`id_est`),
  FOREIGN KEY (`id_curso`) REFERENCES `cursos` (`id_curso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Notas de los estudiantes por curso';

-- Datos de ejemplo
INSERT INTO `estudiantes` (`id_est`, `nombre`, `grado`) VALUES
(1, 'Pedro', '1ro'),
(2, 'Lucía', '1ro'),
(3, 'Jorge', '2do'),
(4, 'Sofía', '3ro');

INSERT INTO `cursos` (`id_curso`, `nombre`, `creditos`) VALUES
(1, 'Matemática', 4),
(2, 'Historia', 3),
(3, 'Ciencias', 4);

INSERT INTO `notas` (`id_nota`, `id_est`, `id_curso`, `nota`) VALUES
(1, 1, 1, 85.00),
(2, 1, 2, 70.00),
(3, 2, 1, 90.00),
(4, 3, 3, 60.00),
(5, 4, 1, 95.00),
(6, 4, 3, 88.00);
