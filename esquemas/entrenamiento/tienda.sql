-- Esquema: tienda — Comercio en línea: clientes, productos y pedidos.

CREATE TABLE `clientes` (
  `id_cliente` INT NOT NULL COMMENT 'Identificador del cliente',
  `nombre` VARCHAR(100) COMMENT 'Nombre completo',
  `ciudad` VARCHAR(50) COMMENT 'Ciudad de residencia',
  `fecha_registro` DATE COMMENT 'Fecha de alta',
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Clientes registrados en la tienda';

CREATE TABLE `productos` (
  `id_producto` INT NOT NULL COMMENT 'Identificador del producto',
  `nombre` VARCHAR(100) COMMENT 'Nombre del producto',
  `categoria` VARCHAR(50) COMMENT 'Categoría',
  `precio` DECIMAL(10,2) COMMENT 'Precio unitario en quetzales',
  PRIMARY KEY (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Catálogo de productos';

CREATE TABLE `pedidos` (
  `id_pedido` INT NOT NULL COMMENT 'Identificador del pedido',
  `id_cliente` INT COMMENT 'Cliente que hizo el pedido',
  `id_producto` INT COMMENT 'Producto pedido',
  `cantidad` INT COMMENT 'Unidades pedidas',
  `fecha` DATE COMMENT 'Fecha del pedido',
  PRIMARY KEY (`id_pedido`),
  FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`),
  FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Pedidos realizados por los clientes';

-- Datos de ejemplo
INSERT INTO `clientes` (`id_cliente`, `nombre`, `ciudad`, `fecha_registro`) VALUES
(1, 'Ana López', 'Guatemala', '2023-01-15'),
(2, 'Luis Pérez', 'Quetzaltenango', '2023-03-22'),
(3, 'María Gómez', 'Guatemala', '2024-02-10'),
(4, 'Carlos Ruiz', 'Escuintla', '2024-06-01');

INSERT INTO `productos` (`id_producto`, `nombre`, `categoria`, `precio`) VALUES
(1, 'Audífonos', 'Electrónica', 250.00),
(2, 'Lámpara', 'Hogar', 120.50),
(3, 'Camisa', 'Ropa', 85.00),
(4, 'Rompecabezas', 'Juguetes', 60.00),
(5, 'Teclado', 'Electrónica', 180.00);

INSERT INTO `pedidos` (`id_pedido`, `id_cliente`, `id_producto`, `cantidad`, `fecha`) VALUES
(1, 1, 1, 2, '2024-07-01'),
(2, 1, 3, 1, '2024-07-03'),
(3, 2, 2, 3, '2024-07-05'),
(4, 3, 5, 1, '2024-08-10'),
(5, 3, 1, 1, '2024-08-11'),
(6, 4, 4, 2, '2024-09-01');
