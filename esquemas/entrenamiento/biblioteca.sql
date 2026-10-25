-- Esquema: biblioteca — Biblioteca: libros, autores y préstamos.

CREATE TABLE `autores` (
  `id_autor` INT NOT NULL COMMENT 'Id del autor',
  `nombre` VARCHAR(100) COMMENT 'Nombre del autor',
  `pais` VARCHAR(40) COMMENT 'País de origen',
  PRIMARY KEY (`id_autor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Autores de los libros';

CREATE TABLE `libros` (
  `id_libro` INT NOT NULL COMMENT 'Id del libro',
  `titulo` VARCHAR(150) COMMENT 'Título',
  `id_autor` INT COMMENT 'Autor',
  `anio` INT COMMENT 'Año de publicación',
  `genero` VARCHAR(40) COMMENT 'Género',
  PRIMARY KEY (`id_libro`),
  FOREIGN KEY (`id_autor`) REFERENCES `autores` (`id_autor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Libros del catálogo';

CREATE TABLE `prestamos` (
  `id_prestamo` INT NOT NULL COMMENT 'Id del préstamo',
  `id_libro` INT COMMENT 'Libro prestado',
  `fecha_prestamo` DATE COMMENT 'Fecha del préstamo',
  `dias` INT COMMENT 'Días de préstamo',
  PRIMARY KEY (`id_prestamo`),
  FOREIGN KEY (`id_libro`) REFERENCES `libros` (`id_libro`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Préstamos de libros';

-- Datos de ejemplo
INSERT INTO `autores` (`id_autor`, `nombre`, `pais`) VALUES
(1, 'Miguel Ángel Asturias', 'Guatemala'),
(2, 'Gabriel García Márquez', 'Colombia'),
(3, 'Octavio Paz', 'México');

INSERT INTO `libros` (`id_libro`, `titulo`, `id_autor`, `anio`, `genero`) VALUES
(1, 'El Señor Presidente', 1, 1946, 'Novela'),
(2, 'Hombres de maíz', 1, 1949, 'Novela'),
(3, 'Cien años de soledad', 2, 1967, 'Novela'),
(4, 'El laberinto de la soledad', 3, 1950, 'Ensayo');

INSERT INTO `prestamos` (`id_prestamo`, `id_libro`, `fecha_prestamo`, `dias`) VALUES
(1, 1, '2024-03-01', 7),
(2, 3, '2024-03-05', 14),
(3, 1, '2024-04-10', 7),
(4, 4, '2024-05-01', 21);
