-- Esquema: hr — Human resources: employees and departments.

CREATE TABLE `dept` (
  `dept_id` INT NOT NULL COMMENT 'Department id',
  `dname` VARCHAR(60) COMMENT 'Department name',
  `loc` VARCHAR(40) COMMENT 'Location',
  PRIMARY KEY (`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Company departments';

CREATE TABLE `emp` (
  `emp_id` INT NOT NULL COMMENT 'Employee id',
  `ename` VARCHAR(60) COMMENT 'Employee name',
  `dept_id` INT COMMENT 'Department',
  `salary` DECIMAL(10,2) COMMENT 'Monthly salary',
  `hire_date` DATE COMMENT 'Hire date',
  `active` TINYINT(1) COMMENT '1 if currently active',
  PRIMARY KEY (`emp_id`),
  FOREIGN KEY (`dept_id`) REFERENCES `dept` (`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Employees';

-- Datos de ejemplo
INSERT INTO `dept` (`dept_id`, `dname`, `loc`) VALUES
(10, 'Engineering', 'HQ'),
(20, 'Sales', 'Branch-A'),
(30, 'Support', 'Branch-B');

INSERT INTO `emp` (`emp_id`, `ename`, `dept_id`, `salary`, `hire_date`, `active`) VALUES
(1, 'Alice', 10, 9000.00, '2021-02-01', 1),
(2, 'Bob', 10, 7500.00, '2022-05-15', 1),
(3, 'Carol', 20, 6000.00, '2020-09-10', 1),
(4, 'Dan', 20, 5500.00, '2023-01-20', 0),
(5, 'Eve', 30, 4800.00, '2023-07-01', 1);
