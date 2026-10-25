-- Esquema de VALIDACION (no usado en entrenamiento): banco — Banco: cuentas, clientes y transacciones.

CREATE TABLE `clientes_banco` (
  `id_cliente` INT NOT NULL COMMENT 'Id del cliente',
  `nombre` VARCHAR(100) COMMENT 'Nombre del cliente',
  `ciudad` VARCHAR(50) COMMENT 'Ciudad',
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Clientes del banco';

CREATE TABLE `cuentas` (
  `id_cuenta` INT NOT NULL COMMENT 'Id de la cuenta',
  `id_cliente` INT COMMENT 'Dueño',
  `tipo` VARCHAR(20) COMMENT 'Tipo de cuenta',
  `saldo` DECIMAL(12,2) COMMENT 'Saldo actual',
  PRIMARY KEY (`id_cuenta`),
  FOREIGN KEY (`id_cliente`) REFERENCES `clientes_banco` (`id_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Cuentas bancarias';

CREATE TABLE `transacciones` (
  `id_tx` INT NOT NULL COMMENT 'Id de la transacción',
  `id_cuenta` INT COMMENT 'Cuenta',
  `monto` DECIMAL(12,2) COMMENT 'Monto de la transacción',
  `tipo` VARCHAR(20) COMMENT 'Tipo',
  `fecha` DATE COMMENT 'Fecha de la transacción',
  PRIMARY KEY (`id_tx`),
  FOREIGN KEY (`id_cuenta`) REFERENCES `cuentas` (`id_cuenta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Transacciones de las cuentas';

-- Datos de ejemplo
INSERT INTO `clientes_banco` (`id_cliente`, `nombre`, `ciudad`) VALUES
(1, 'Rodrigo', 'Guatemala'),
(2, 'Valeria', 'Xela'),
(3, 'Tomás', 'Cobán');

INSERT INTO `cuentas` (`id_cuenta`, `id_cliente`, `tipo`, `saldo`) VALUES
(1, 1, 'Ahorro', 15000.00),
(2, 1, 'Monetaria', 5000.00),
(3, 2, 'Ahorro', 22000.00),
(4, 3, 'Monetaria', 800.00);

INSERT INTO `transacciones` (`id_tx`, `id_cuenta`, `monto`, `tipo`, `fecha`) VALUES
(1, 1, 2000.00, 'Depósito', '2024-07-01'),
(2, 1, 500.00, 'Retiro', '2024-07-10'),
(3, 3, 10000.00, 'Depósito', '2024-07-05'),
(4, 4, 300.00, 'Retiro', '2024-07-15'),
(5, 2, 1500.00, 'Depósito', '2024-08-01');
