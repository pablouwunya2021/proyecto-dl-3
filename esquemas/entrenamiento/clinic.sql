-- Esquema: clinic — Clinic: patients, doctors and visits.

CREATE TABLE `doctor` (
  `doc_id` INT NOT NULL COMMENT 'Doctor id',
  `dname` VARCHAR(80) COMMENT 'Doctor name',
  `spec` VARCHAR(50) COMMENT 'Specialty',
  PRIMARY KEY (`doc_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Doctors';

CREATE TABLE `patient` (
  `pat_id` INT NOT NULL COMMENT 'Patient id',
  `pname` VARCHAR(80) COMMENT 'Patient name',
  `age` INT COMMENT 'Age in years',
  `city` VARCHAR(40) COMMENT 'City',
  PRIMARY KEY (`pat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Patients';

CREATE TABLE `visit` (
  `vid` INT NOT NULL COMMENT 'Visit id',
  `pat_id` INT COMMENT 'Patient',
  `doc_id` INT COMMENT 'Doctor',
  `vdate` DATE COMMENT 'Visit date',
  `cost` DECIMAL(10,2) COMMENT 'Visit cost',
  PRIMARY KEY (`vid`),
  FOREIGN KEY (`pat_id`) REFERENCES `patient` (`pat_id`),
  FOREIGN KEY (`doc_id`) REFERENCES `doctor` (`doc_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Clinic visits';

-- Datos de ejemplo
INSERT INTO `doctor` (`doc_id`, `dname`, `spec`) VALUES
(1, 'Dr. House', 'General'),
(2, 'Dr. Grey', 'Cardiology'),
(3, 'Dr. Wilson', 'Pediatrics');

INSERT INTO `patient` (`pat_id`, `pname`, `age`, `city`) VALUES
(1, 'John', 45, 'Guatemala'),
(2, 'Mary', 30, 'Mixco'),
(3, 'Peter', 8, 'Villa Nueva'),
(4, 'Sara', 60, 'Guatemala');

INSERT INTO `visit` (`vid`, `pat_id`, `doc_id`, `vdate`, `cost`) VALUES
(1, 1, 1, '2024-01-10', 150.00),
(2, 2, 2, '2024-02-15', 300.00),
(3, 3, 3, '2024-03-20', 100.00),
(4, 1, 2, '2024-04-01', 320.00),
(5, 4, 1, '2024-05-05', 180.00);
