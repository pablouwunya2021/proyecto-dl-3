-- Esquema: red_social — Red social: usuarios y publicaciones.

CREATE TABLE `usuarios` (
  `id_usuario` INT NOT NULL COMMENT 'Id del usuario',
  `usuario` VARCHAR(40) COMMENT 'Nombre de usuario',
  `pais` VARCHAR(40) COMMENT 'País',
  `fecha_registro` DATE COMMENT 'Fecha de registro',
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Usuarios de la red';

CREATE TABLE `publicaciones` (
  `id_pub` INT NOT NULL COMMENT 'Id de la publicación',
  `id_usuario` INT COMMENT 'Autor',
  `likes` INT COMMENT 'Cantidad de me gusta',
  `fecha` DATE COMMENT 'Fecha de publicación',
  PRIMARY KEY (`id_pub`),
  FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Publicaciones de los usuarios';

-- Datos de ejemplo
INSERT INTO `usuarios` (`id_usuario`, `usuario`, `pais`, `fecha_registro`) VALUES
(1, 'ana23', 'Guatemala', '2023-05-01'),
(2, 'luisgt', 'Guatemala', '2023-06-15'),
(3, 'sv_maria', 'El Salvador', '2024-01-10');

INSERT INTO `publicaciones` (`id_pub`, `id_usuario`, `likes`, `fecha`) VALUES
(1, 1, 10, '2024-02-01'),
(2, 1, 25, '2024-02-05'),
(3, 2, 5, '2024-02-03'),
(4, 3, 40, '2024-03-01'),
(5, 2, 15, '2024-03-10');
