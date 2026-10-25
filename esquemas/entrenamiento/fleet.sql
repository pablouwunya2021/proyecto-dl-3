-- Esquema: fleet — Vehicle fleet: cars and trips.

CREATE TABLE `car` (
  `car_id` INT NOT NULL COMMENT 'Car id',
  `plate` VARCHAR(12) COMMENT 'License plate',
  `brand` VARCHAR(30) COMMENT 'Brand',
  `year` INT COMMENT 'Model year',
  PRIMARY KEY (`car_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Fleet vehicles';

CREATE TABLE `trip` (
  `trip_id` INT NOT NULL COMMENT 'Trip id',
  `car_id` INT COMMENT 'Car',
  `km` DECIMAL(8,2) COMMENT 'Distance in km',
  `tdate` DATE COMMENT 'Trip date',
  PRIMARY KEY (`trip_id`),
  FOREIGN KEY (`car_id`) REFERENCES `car` (`car_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Trips made';

-- Datos de ejemplo
INSERT INTO `car` (`car_id`, `plate`, `brand`, `year`) VALUES
(1, 'P-001ABC', 'Toyota', 2020),
(2, 'P-002DEF', 'Nissan', 2019),
(3, 'P-003GHI', 'Ford', 2021);

INSERT INTO `trip` (`trip_id`, `car_id`, `km`, `tdate`) VALUES
(1, 1, 120.50, '2024-07-01'),
(2, 1, 80.00, '2024-07-02'),
(3, 2, 200.00, '2024-07-01'),
(4, 3, 50.25, '2024-07-03'),
(5, 2, 150.00, '2024-07-05');
