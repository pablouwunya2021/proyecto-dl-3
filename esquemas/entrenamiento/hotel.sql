-- Esquema: hotel — Hotel: habitaciones y reservas.

CREATE TABLE `habitaciones` (
  `id_hab` INT NOT NULL COMMENT 'Id de la habitación',
  `tipo` VARCHAR(20) COMMENT 'Tipo de habitación',
  `precio_noche` DECIMAL(8,2) COMMENT 'Precio por noche',
  PRIMARY KEY (`id_hab`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Habitaciones del hotel';

CREATE TABLE `reservas` (
  `id_reserva` INT NOT NULL COMMENT 'Id de la reserva',
  `id_hab` INT COMMENT 'Habitación',
  `huesped` VARCHAR(80) COMMENT 'Nombre del huésped',
  `noches` INT COMMENT 'Número de noches',
  `fecha_entrada` DATE COMMENT 'Fecha de entrada',
  PRIMARY KEY (`id_reserva`),
  FOREIGN KEY (`id_hab`) REFERENCES `habitaciones` (`id_hab`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Reservas de habitaciones';

-- Datos de ejemplo
INSERT INTO `habitaciones` (`id_hab`, `tipo`, `precio_noche`) VALUES
(1, 'Individual', 250.00),
(2, 'Doble', 400.00),
(3, 'Suite', 800.00),
(4, 'Doble', 400.00);

INSERT INTO `reservas` (`id_reserva`, `id_hab`, `huesped`, `noches`, `fecha_entrada`) VALUES
(1, 3, 'Ana', 2, '2024-08-01'),
(2, 1, 'Luis', 5, '2024-08-03'),
(3, 2, 'Marta', 1, '2024-08-10'),
(4, 3, 'Pablo', 3, '2024-09-01');
