-- Esquema de VALIDACION (no usado en entrenamiento): aerolinea — Aerolínea: vuelos, aviones y pasajeros.

CREATE TABLE `aviones` (
  `id_avion` INT NOT NULL COMMENT 'Id del avión',
  `modelo` VARCHAR(40) COMMENT 'Modelo del avión',
  `capacidad` INT COMMENT 'Número de asientos',
  `aerolinea` VARCHAR(40) COMMENT 'Aerolínea',
  PRIMARY KEY (`id_avion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Aviones de la flota';

CREATE TABLE `vuelos` (
  `id_vuelo` INT NOT NULL COMMENT 'Id del vuelo',
  `id_avion` INT COMMENT 'Avión',
  `origen` VARCHAR(40) COMMENT 'Ciudad de origen',
  `destino` VARCHAR(40) COMMENT 'Ciudad de destino',
  `fecha` DATE COMMENT 'Fecha del vuelo',
  `precio` DECIMAL(10,2) COMMENT 'Precio del boleto',
  PRIMARY KEY (`id_vuelo`),
  FOREIGN KEY (`id_avion`) REFERENCES `aviones` (`id_avion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Vuelos programados';

CREATE TABLE `pasajeros` (
  `id_pasajero` INT NOT NULL COMMENT 'Id del pasajero',
  `id_vuelo` INT COMMENT 'Vuelo',
  `nombre` VARCHAR(80) COMMENT 'Nombre del pasajero',
  `edad` INT COMMENT 'Edad del pasajero',
  PRIMARY KEY (`id_pasajero`),
  FOREIGN KEY (`id_vuelo`) REFERENCES `vuelos` (`id_vuelo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Pasajeros por vuelo';

-- Datos de ejemplo
INSERT INTO `aviones` (`id_avion`, `modelo`, `capacidad`, `aerolinea`) VALUES
(1, 'A320', 180, 'Avianca'),
(2, 'B737', 160, 'Copa'),
(3, 'E190', 100, 'Avianca');

INSERT INTO `vuelos` (`id_vuelo`, `id_avion`, `origen`, `destino`, `fecha`, `precio`) VALUES
(1, 1, 'Guatemala', 'Panamá', '2024-09-01', 1200.00),
(2, 2, 'Panamá', 'Miami', '2024-09-02', 2500.00),
(3, 1, 'Guatemala', 'Miami', '2024-09-05', 3000.00),
(4, 3, 'Guatemala', 'Panamá', '2024-09-10', 1100.00);

INSERT INTO `pasajeros` (`id_pasajero`, `id_vuelo`, `nombre`, `edad`) VALUES
(1, 1, 'Ana', 34),
(2, 1, 'Luis', 28),
(3, 2, 'María', 45),
(4, 3, 'Carlos', 50),
(5, 3, 'Sofía', 19),
(6, 4, 'Pedro', 60);
