-- Esquema: restaurante — Restaurante: platos, meseros y ventas.

CREATE TABLE `platos` (
  `id_plato` INT NOT NULL COMMENT 'Id del plato',
  `nombre` VARCHAR(80) COMMENT 'Nombre del plato',
  `tipo` VARCHAR(30) COMMENT 'Tipo de plato',
  `precio` DECIMAL(8,2) COMMENT 'Precio',
  PRIMARY KEY (`id_plato`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Platos del menú';

CREATE TABLE `meseros` (
  `id_mesero` INT NOT NULL COMMENT 'Id del mesero',
  `nombre` VARCHAR(60) COMMENT 'Nombre',
  `turno` VARCHAR(20) COMMENT 'Turno',
  PRIMARY KEY (`id_mesero`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Meseros del restaurante';

CREATE TABLE `ventas` (
  `id_venta` INT NOT NULL COMMENT 'Id de la venta',
  `id_plato` INT COMMENT 'Plato vendido',
  `id_mesero` INT COMMENT 'Mesero',
  `cantidad` INT COMMENT 'Cantidad vendida',
  `fecha` DATE COMMENT 'Fecha de la venta',
  PRIMARY KEY (`id_venta`),
  FOREIGN KEY (`id_plato`) REFERENCES `platos` (`id_plato`),
  FOREIGN KEY (`id_mesero`) REFERENCES `meseros` (`id_mesero`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Ventas de platos';

-- Datos de ejemplo
INSERT INTO `platos` (`id_plato`, `nombre`, `tipo`, `precio`) VALUES
(1, 'Sopa', 'Entrada', 25.00),
(2, 'Pepián', 'Fuerte', 55.00),
(3, 'Flan', 'Postre', 20.00),
(4, 'Jugo', 'Bebida', 15.00);

INSERT INTO `meseros` (`id_mesero`, `nombre`, `turno`) VALUES
(1, 'Rosa', 'Mañana'),
(2, 'Juan', 'Tarde'),
(3, 'Mario', 'Noche');

INSERT INTO `ventas` (`id_venta`, `id_plato`, `id_mesero`, `cantidad`, `fecha`) VALUES
(1, 2, 1, 3, '2024-06-01'),
(2, 1, 1, 2, '2024-06-01'),
(3, 3, 2, 5, '2024-06-02'),
(4, 2, 3, 1, '2024-06-03'),
(5, 4, 2, 4, '2024-06-03');
