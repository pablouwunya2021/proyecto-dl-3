-- Esquema: gimnasio — Gimnasio: socios, membresías y asistencias.

CREATE TABLE `socios` (
  `id_socio` INT NOT NULL COMMENT 'Id del socio',
  `nombre` VARCHAR(80) COMMENT 'Nombre',
  `plan` VARCHAR(20) COMMENT 'Plan de membresía',
  `cuota` DECIMAL(8,2) COMMENT 'Cuota mensual',
  `fecha_alta` DATE COMMENT 'Fecha de alta',
  PRIMARY KEY (`id_socio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Socios del gimnasio';

CREATE TABLE `asistencias` (
  `id_asis` INT NOT NULL COMMENT 'Id de asistencia',
  `id_socio` INT COMMENT 'Socio',
  `fecha` DATE COMMENT 'Fecha de asistencia',
  `minutos` INT COMMENT 'Minutos de entrenamiento',
  PRIMARY KEY (`id_asis`),
  FOREIGN KEY (`id_socio`) REFERENCES `socios` (`id_socio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Registro de asistencias';

-- Datos de ejemplo
INSERT INTO `socios` (`id_socio`, `nombre`, `plan`, `cuota`, `fecha_alta`) VALUES
(1, 'Diego', 'Básico', 150.00, '2024-01-05'),
(2, 'Elena', 'Premium', 450.00, '2024-02-10'),
(3, 'Fabio', 'Plus', 300.00, '2024-02-20'),
(4, 'Gaby', 'Básico', 150.00, '2024-03-15');

INSERT INTO `asistencias` (`id_asis`, `id_socio`, `fecha`, `minutos`) VALUES
(1, 1, '2024-03-01', 60),
(2, 1, '2024-03-03', 45),
(3, 2, '2024-03-01', 90),
(4, 3, '2024-03-02', 30),
(5, 2, '2024-03-05', 75);
