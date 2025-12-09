-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         12.0.2-MariaDB - mariadb.org binary distribution
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.11.0.7065
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para condor_airways
CREATE DATABASE IF NOT EXISTS `condor_airways` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;
USE `condor_airways`;

-- Volcando estructura para tabla condor_airways.aerolinea_capital
CREATE TABLE IF NOT EXISTS `aerolinea_capital` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `lat` double NOT NULL,
  `lon` double NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_capital: ~37 rows (aproximadamente)
INSERT INTO `aerolinea_capital` (`id`, `nombre`, `lat`, `lon`) VALUES
	(1, 'ARAUCA', 7.0847, -70.7591),
	(2, 'ARMENIA', 4.5339, -75.6811),
	(3, 'BARRANQUILLA', 10.9685, -74.7813),
	(4, 'BOGOTA', 4.711, -74.0721),
	(5, 'BUCARAMANGA', 7.1193, -73.1227),
	(6, 'CALI', 3.4516, -76.5319),
	(7, 'CARTAGENA', 10.391, -75.4794),
	(8, 'CUCUTA', 7.8939, -72.5078),
	(9, 'FLORENCIA', 1.6144, -75.6062),
	(10, 'IBAGUE', 4.4389, -75.2322),
	(11, 'INIRIDA', 3.8653, -67.9239),
	(12, 'LETICIA', -4.2153, -69.9406),
	(13, 'MANIZALES', 5.0703, -75.5138),
	(14, 'MEDELLIN', 6.2442, -75.5812),
	(15, 'MITU', 1.1983, -70.1733),
	(16, 'MOCOA', 1.1498, -76.6463),
	(17, 'MONTERIA', 8.748, -75.8814),
	(18, 'NEIVA', 2.9273, -75.2819),
	(19, 'PASTO', 1.2136, -77.2811),
	(20, 'PEREIRA', 4.8143, -75.6946),
	(21, 'POPAYAN', 2.4437, -76.6147),
	(22, 'PUERTO_CARREÑO', 6.187, -67.4859),
	(23, 'QUIBDO', 5.6947, -76.6612),
	(24, 'RIOHACHA', 11.5444, -72.9073),
	(25, 'SAN_ANDRES', 12.5847, -81.7006),
	(26, 'SAN_JOSE_DEL_GUAVIARE', 2.5658, -72.6396),
	(27, 'SANTA_MARTA', 11.2408, -74.199),
	(28, 'SINCELEJO', 9.3047, -75.3978),
	(29, 'TUNJA', 5.5353, -73.3678),
	(30, 'VALLEDUPAR', 10.4631, -73.2532),
	(31, 'VILLAVICENCIO', 4.142, -73.6266),
	(32, 'YOPAL', 5.3378, -72.3959),
	(33, 'MADRID', 40.4168, -3.7038),
	(34, 'LONDRES', 51.5074, -0.1278),
	(35, 'NUEVA_YORK', 40.7128, -74.006),
	(36, 'BUENOS_AIRES', -34.6037, -58.3816),
	(37, 'MIAMI', 25.7617, -80.1918);

-- Volcando estructura para tabla condor_airways.aerolinea_carrito
CREATE TABLE IF NOT EXISTS `aerolinea_carrito` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `creado_en` datetime(6) NOT NULL,
  `usuario_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `aerolinea_carrito_usuario_id_f9cf3b25_fk_aerolinea_usuario_id` (`usuario_id`),
  CONSTRAINT `aerolinea_carrito_usuario_id_f9cf3b25_fk_aerolinea_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `aerolinea_usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_carrito: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.aerolinea_carritoitem
CREATE TABLE IF NOT EXISTS `aerolinea_carritoitem` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `cantidad` int(10) unsigned NOT NULL CHECK (`cantidad` >= 0),
  `carrito_id` bigint(20) NOT NULL,
  `vuelo_id` bigint(20) NOT NULL,
  `reserva_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `aerolinea_carritoitem_carrito_id_vuelo_id_d797751c_uniq` (`carrito_id`,`vuelo_id`),
  KEY `aerolinea_carritoitem_vuelo_id_781f82e1_fk_aerolinea_vuelo_id` (`vuelo_id`),
  KEY `aerolinea_carritoite_reserva_id_e0c82ec3_fk_aerolinea` (`reserva_id`),
  CONSTRAINT `aerolinea_carritoite_carrito_id_6c17ceb3_fk_aerolinea` FOREIGN KEY (`carrito_id`) REFERENCES `aerolinea_carrito` (`id`),
  CONSTRAINT `aerolinea_carritoite_reserva_id_e0c82ec3_fk_aerolinea` FOREIGN KEY (`reserva_id`) REFERENCES `aerolinea_reserva` (`id`),
  CONSTRAINT `aerolinea_carritoitem_vuelo_id_781f82e1_fk_aerolinea_vuelo_id` FOREIGN KEY (`vuelo_id`) REFERENCES `aerolinea_vuelo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_carritoitem: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.aerolinea_checkin
CREATE TABLE IF NOT EXISTS `aerolinea_checkin` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `asiento` varchar(5) NOT NULL,
  `pase_abordar` varchar(100) DEFAULT NULL,
  `compra_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `aerolinea_checkin_compra_id_0a66f7be_fk_aerolinea_compra_id` (`compra_id`),
  CONSTRAINT `aerolinea_checkin_compra_id_0a66f7be_fk_aerolinea_compra_id` FOREIGN KEY (`compra_id`) REFERENCES `aerolinea_compra` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_checkin: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.aerolinea_comentario
CREATE TABLE IF NOT EXISTS `aerolinea_comentario` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `contenido` longtext NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `publicacion_id` bigint(20) NOT NULL,
  `usuario_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `aerolinea_comentario_publicacion_id_d2145a29_fk_aerolinea` (`publicacion_id`),
  KEY `aerolinea_comentario_usuario_id_d0c4a70c_fk_aerolinea_usuario_id` (`usuario_id`),
  CONSTRAINT `aerolinea_comentario_publicacion_id_d2145a29_fk_aerolinea` FOREIGN KEY (`publicacion_id`) REFERENCES `aerolinea_publicacion` (`id`),
  CONSTRAINT `aerolinea_comentario_usuario_id_d0c4a70c_fk_aerolinea_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `aerolinea_usuario` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_comentario: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.aerolinea_compra
CREATE TABLE IF NOT EXISTS `aerolinea_compra` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha_compra` datetime(6) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `codigo_reserva` varchar(50) NOT NULL,
  `metodo_pago` varchar(50) NOT NULL,
  `usuario_id` bigint(20) NOT NULL,
  `vuelo_id` bigint(20) NOT NULL,
  `monto_total` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo_reserva` (`codigo_reserva`),
  KEY `aerolinea_compra_usuario_id_f151e2a2_fk_aerolinea_usuario_id` (`usuario_id`),
  KEY `aerolinea_compra_vuelo_id_4d4c2cad_fk_aerolinea_vuelo_id` (`vuelo_id`),
  CONSTRAINT `aerolinea_compra_usuario_id_f151e2a2_fk_aerolinea_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `aerolinea_usuario` (`id`),
  CONSTRAINT `aerolinea_compra_vuelo_id_4d4c2cad_fk_aerolinea_vuelo_id` FOREIGN KEY (`vuelo_id`) REFERENCES `aerolinea_vuelo` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_compra: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.aerolinea_departamento
CREATE TABLE IF NOT EXISTS `aerolinea_departamento` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `pais_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `aerolinea_departamento_pais_id_eec98b65_fk_aerolinea_pais_id` (`pais_id`),
  CONSTRAINT `aerolinea_departamento_pais_id_eec98b65_fk_aerolinea_pais_id` FOREIGN KEY (`pais_id`) REFERENCES `aerolinea_pais` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_departamento: ~32 rows (aproximadamente)
INSERT INTO `aerolinea_departamento` (`id`, `nombre`, `pais_id`) VALUES
	(1, 'Amazonas', 1),
	(2, 'Antioquia', 1),
	(3, 'Arauca', 1),
	(4, 'Atlántico', 1),
	(5, 'Bolívar', 1),
	(6, 'Boyacá', 1),
	(7, 'Caldas', 1),
	(8, 'Caquetá', 1),
	(9, 'Casanare', 1),
	(10, 'Cauca', 1),
	(11, 'Cesar', 1),
	(12, 'Chocó', 1),
	(13, 'Córdoba', 1),
	(14, 'Cundinamarca', 1),
	(15, 'Guainía', 1),
	(16, 'Guaviare', 1),
	(17, 'Huila', 1),
	(18, 'La Guajira', 1),
	(19, 'Magdalena', 1),
	(20, 'Meta', 1),
	(21, 'Nariño', 1),
	(22, 'Norte de Santander', 1),
	(23, 'Putumayo', 1),
	(24, 'Quindío', 1),
	(25, 'Risaralda', 1),
	(26, 'San Andrés y Providencia', 1),
	(27, 'Santander', 1),
	(28, 'Sucre', 1),
	(29, 'Tolima', 1),
	(30, 'Valle del Cauca', 1),
	(31, 'Vaupés', 1),
	(32, 'Vichada', 1);

-- Volcando estructura para tabla condor_airways.aerolinea_historialoperacion
CREATE TABLE IF NOT EXISTS `aerolinea_historialoperacion` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `tipo` varchar(30) NOT NULL,
  `descripcion` longtext NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `usuario_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `aerolinea_historialo_usuario_id_c9edf4dc_fk_aerolinea` (`usuario_id`),
  CONSTRAINT `aerolinea_historialo_usuario_id_c9edf4dc_fk_aerolinea` FOREIGN KEY (`usuario_id`) REFERENCES `aerolinea_usuario` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_historialoperacion: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.aerolinea_maleta
CREATE TABLE IF NOT EXISTS `aerolinea_maleta` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `peso` decimal(5,2) NOT NULL,
  `costo` decimal(10,2) NOT NULL,
  `checkin_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `aerolinea_maleta_checkin_id_1b7526d2_fk_aerolinea_checkin_id` (`checkin_id`),
  CONSTRAINT `aerolinea_maleta_checkin_id_1b7526d2_fk_aerolinea_checkin_id` FOREIGN KEY (`checkin_id`) REFERENCES `aerolinea_checkin` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_maleta: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.aerolinea_municipio
CREATE TABLE IF NOT EXISTS `aerolinea_municipio` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `departamento_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `aerolinea_municipio_departamento_id_83e3165c_fk_aerolinea` (`departamento_id`),
  CONSTRAINT `aerolinea_municipio_departamento_id_83e3165c_fk_aerolinea` FOREIGN KEY (`departamento_id`) REFERENCES `aerolinea_departamento` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_municipio: ~37 rows (aproximadamente)
INSERT INTO `aerolinea_municipio` (`id`, `nombre`, `departamento_id`) VALUES
	(1, 'Leticia', 1),
	(2, 'Medellín', 2),
	(3, 'Bello', 2),
	(4, 'Apartadó', 2),
	(5, 'Arauca', 3),
	(6, 'Barranquilla', 4),
	(7, 'Soledad', 4),
	(8, 'Cartagena', 5),
	(9, 'Magangué', 5),
	(10, 'Tunja', 6),
	(11, 'Duitama', 6),
	(12, 'Manizales', 7),
	(13, 'Florencia', 8),
	(14, 'Yopal', 9),
	(15, 'Popayán', 10),
	(16, 'Valledupar', 11),
	(17, 'Quibdó', 12),
	(18, 'Montería', 13),
	(19, 'Bogotá', 14),
	(20, 'Inírida', 15),
	(21, 'San José del Guaviare', 16),
	(22, 'Neiva', 17),
	(23, 'Riohacha', 18),
	(24, 'Santa Marta', 19),
	(25, 'Villavicencio', 20),
	(26, 'Pasto', 21),
	(27, 'Cúcuta', 22),
	(28, 'Mocoa', 23),
	(29, 'Armenia', 24),
	(30, 'Pereira', 25),
	(31, 'San Andrés', 26),
	(32, 'Bucaramanga', 27),
	(33, 'Sincelejo', 28),
	(34, 'Ibagué', 29),
	(35, 'Cali', 30),
	(36, 'Mitú', 31),
	(37, 'Puerto Carreño', 32);

-- Volcando estructura para tabla condor_airways.aerolinea_notificacion
CREATE TABLE IF NOT EXISTS `aerolinea_notificacion` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `mensaje` longtext NOT NULL,
  `enviada` tinyint(1) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `usuario_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `aerolinea_notificaci_usuario_id_8db648f0_fk_aerolinea` (`usuario_id`),
  CONSTRAINT `aerolinea_notificaci_usuario_id_8db648f0_fk_aerolinea` FOREIGN KEY (`usuario_id`) REFERENCES `aerolinea_usuario` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_notificacion: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.aerolinea_pais
CREATE TABLE IF NOT EXISTS `aerolinea_pais` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_pais: ~1 rows (aproximadamente)
INSERT INTO `aerolinea_pais` (`id`, `nombre`) VALUES
	(1, 'Colombia');

-- Volcando estructura para tabla condor_airways.aerolinea_publicacion
CREATE TABLE IF NOT EXISTS `aerolinea_publicacion` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(200) NOT NULL,
  `contenido` longtext NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `usuario_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `aerolinea_publicacio_usuario_id_eb27cb71_fk_aerolinea` (`usuario_id`),
  CONSTRAINT `aerolinea_publicacio_usuario_id_eb27cb71_fk_aerolinea` FOREIGN KEY (`usuario_id`) REFERENCES `aerolinea_usuario` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_publicacion: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.aerolinea_reserva
CREATE TABLE IF NOT EXISTS `aerolinea_reserva` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `fecha_reserva` datetime(6) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `num_tiquetes` int(10) unsigned NOT NULL,
  `usuario_id` bigint(20) NOT NULL,
  `vuelo_id` bigint(20) NOT NULL,
  `asiento_asignado` varchar(5) DEFAULT NULL,
  `check_in_realizado` tinyint(1) NOT NULL,
  `codigo_reserva` varchar(12) NOT NULL,
  `clase` varchar(20) NOT NULL,
  `reserved_until` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo_reserva` (`codigo_reserva`),
  KEY `aerolinea_reserva_vuelo_id_fe0e1074_fk_aerolinea_vuelo_id` (`vuelo_id`),
  KEY `aerolinea_reserva_usuario_id_b8f51962` (`usuario_id`),
  CONSTRAINT `aerolinea_reserva_usuario_id_b8f51962_fk_aerolinea_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `aerolinea_usuario` (`id`),
  CONSTRAINT `aerolinea_reserva_vuelo_id_fe0e1074_fk_aerolinea_vuelo_id` FOREIGN KEY (`vuelo_id`) REFERENCES `aerolinea_vuelo` (`id`),
  CONSTRAINT `aerolinea_reserva_num_tiquetes_39a25b19_check` CHECK (`num_tiquetes` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_reserva: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.aerolinea_reservapasajero
CREATE TABLE IF NOT EXISTS `aerolinea_reservapasajero` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `documento` varchar(50) NOT NULL,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `genero` varchar(20) NOT NULL,
  `telefono` varchar(30) NOT NULL,
  `correo` varchar(254) NOT NULL,
  `contacto_nombre` varchar(150) NOT NULL,
  `contacto_telefono` varchar(30) NOT NULL,
  `reserva_id` bigint(20) NOT NULL,
  `asiento` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_pasajero_por_reserva` (`documento`,`reserva_id`),
  KEY `aerolinea_reservapas_reserva_id_947aa226_fk_aerolinea` (`reserva_id`),
  CONSTRAINT `aerolinea_reservapas_reserva_id_947aa226_fk_aerolinea` FOREIGN KEY (`reserva_id`) REFERENCES `aerolinea_reserva` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_reservapasajero: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.aerolinea_rol
CREATE TABLE IF NOT EXISTS `aerolinea_rol` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_rol: ~3 rows (aproximadamente)
INSERT INTO `aerolinea_rol` (`id`, `nombre`) VALUES
	(1, 'Cliente'),
	(2, 'Root'),
	(3, 'Administrador');

-- Volcando estructura para tabla condor_airways.aerolinea_tarjeta
CREATE TABLE IF NOT EXISTS `aerolinea_tarjeta` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `tipo` varchar(10) NOT NULL,
  `numero` varchar(16) NOT NULL,
  `nombre_titular` varchar(100) NOT NULL,
  `fecha_vencimiento` date NOT NULL,
  `cvv` varchar(4) NOT NULL,
  `saldo` decimal(12,2) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `estado` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `numero` (`numero`),
  KEY `aerolinea_tarjeta_usuario_id_ae802134_fk_auth_user_id` (`usuario_id`),
  CONSTRAINT `aerolinea_tarjeta_usuario_id_ae802134_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_tarjeta: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.aerolinea_usuario
CREATE TABLE IF NOT EXISTS `aerolinea_usuario` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `email` varchar(254) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nombres` varchar(150) DEFAULT NULL,
  `apellidos` varchar(150) DEFAULT NULL,
  `fecha_nacimiento` date NOT NULL,
  `dni` varchar(20) NOT NULL,
  `direccion_facturacion` varchar(200) NOT NULL,
  `genero` varchar(20) NOT NULL,
  `imagen_usuario` varchar(100) DEFAULT NULL,
  `es_admin` tinyint(1) NOT NULL,
  `rol_id` bigint(20) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `departamento_id` bigint(20) DEFAULT NULL,
  `municipio_id` bigint(20) DEFAULT NULL,
  `pais_id` bigint(20) DEFAULT NULL,
  `es_root` tinyint(1) NOT NULL,
  `registro_completo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `dni` (`dni`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `aerolinea_usuario_rol_id_15a7aa42_fk_aerolinea_rol_id` (`rol_id`),
  KEY `aerolinea_usuario_departamento_id_0eb7bb08_fk_aerolinea` (`departamento_id`),
  KEY `aerolinea_usuario_municipio_id_f47b03ab_fk_aerolinea` (`municipio_id`),
  KEY `aerolinea_usuario_pais_id_a8cc26a4_fk_aerolinea_pais_id` (`pais_id`),
  CONSTRAINT `aerolinea_usuario_departamento_id_0eb7bb08_fk_aerolinea` FOREIGN KEY (`departamento_id`) REFERENCES `aerolinea_departamento` (`id`),
  CONSTRAINT `aerolinea_usuario_municipio_id_f47b03ab_fk_aerolinea` FOREIGN KEY (`municipio_id`) REFERENCES `aerolinea_municipio` (`id`),
  CONSTRAINT `aerolinea_usuario_pais_id_a8cc26a4_fk_aerolinea_pais_id` FOREIGN KEY (`pais_id`) REFERENCES `aerolinea_pais` (`id`),
  CONSTRAINT `aerolinea_usuario_rol_id_15a7aa42_fk_aerolinea_rol_id` FOREIGN KEY (`rol_id`) REFERENCES `aerolinea_rol` (`id`),
  CONSTRAINT `aerolinea_usuario_user_id_a42d0b57_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_usuario: ~10 rows (aproximadamente)
INSERT INTO `aerolinea_usuario` (`id`, `email`, `password`, `nombres`, `apellidos`, `fecha_nacimiento`, `dni`, `direccion_facturacion`, `genero`, `imagen_usuario`, `es_admin`, `rol_id`, `user_id`, `departamento_id`, `municipio_id`, `pais_id`, `es_root`, `registro_completo`) VALUES
	(1, 'karencarcas@gmail.com', 'karen0922', 'Karen Manuela', 'Cardona Castaño', '2002-09-22', '1004778917', 'Jardín II etapa Mz 10 Casa 15', 'F', 'usuarios/images.jfif', 0, 1, 1, 25, 30, 1, 0, 0),
	(2, 'niyica123@gmail.com', 'yineth0225', 'Nidia Yineth', 'Castaño Muñoz', '1971-02-25', '42101192', 'Avenida Simón Bolivar', 'F', '', 0, 1, 2, 25, 30, 1, 0, 0),
	(3, 'jhoncito@gmail.com', 'jhon19', 'Jhon Alexander', 'Cardona Rodas', '1971-09-19', '10141297', 'Cra 8a #3-41', 'M', '', 0, 1, 3, 25, 30, 1, 0, 0),
	(4, 'root@condorairways.com', 'root123', 'Root', 'System', '2000-01-01', '0000000000', 'Sistema Central', 'O', '', 0, 2, 4, NULL, NULL, NULL, 1, 0),
	(5, 'karenmanuela.cardona@utp.edu.co', 'karen2002', 'Karen Manuela', 'Cardona Castaño', '2002-09-22', '123456789', 'Jardín II etapa Mz 10 Casa 15', 'F', '', 1, 3, 5, NULL, NULL, 1, 0, 1),
	(6, 'juanito@gmail.com', 'juan88', 'Pendiente', 'Pendiente', '2000-01-01', 'TEMP6', 'Sin definir', 'O', '', 1, 3, 6, NULL, NULL, NULL, 0, 0),
	(7, 'nicolas22@gmail.com', 'nico22', 'Pendiente', 'Pendiente', '2000-01-01', 'TEMP7', 'Sin definir', 'O', '', 1, 3, 7, NULL, NULL, NULL, 0, 0),
	(8, 'linita@gmail.com', 'lina55', 'Pendiente', 'Pendiente', '2000-01-01', 'TEMP8', 'Sin definir', 'O', '', 1, 3, 8, NULL, NULL, NULL, 0, 0),
	(9, 'manuelita@gmail.com', 'manu123', 'Pendiente', 'Pendiente', '2000-01-01', 'TEMP9', 'Sin definir', 'O', '', 1, 3, 9, NULL, NULL, NULL, 0, 0),
	(10, 'miguelito@gmail.com', 'miguelito2501', 'Miguel', 'Gómez', '2008-01-25', '10078542781', 'Avenida Nariño', 'M', '', 0, 1, 10, 15, 20, 1, 0, 0);

-- Volcando estructura para tabla condor_airways.aerolinea_vuelo
CREATE TABLE IF NOT EXISTS `aerolinea_vuelo` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(20) NOT NULL,
  `origen` varchar(50) NOT NULL,
  `destino` varchar(50) NOT NULL,
  `fecha_salida` date DEFAULT NULL,
  `hora_salida` time(6) DEFAULT NULL,
  `fecha_llegada` date DEFAULT NULL,
  `hora_llegada` time(6) DEFAULT NULL,
  `tiempo_vuelo` bigint(20) DEFAULT NULL,
  `capacidad` int(11) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `tipo` varchar(20) NOT NULL,
  `imagen` varchar(100) DEFAULT NULL,
  `estado` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.aerolinea_vuelo: ~5 rows (aproximadamente)
INSERT INTO `aerolinea_vuelo` (`id`, `codigo`, `origen`, `destino`, `fecha_salida`, `hora_salida`, `fecha_llegada`, `hora_llegada`, `tiempo_vuelo`, `capacidad`, `precio`, `tipo`, `imagen`, `estado`) VALUES
	(2, 'VI0001', 'PEREIRA', 'MADRID', '2025-11-05', '07:15:00.000000', '2025-11-05', '15:15:00.000000', 28800000000, 250, 2000000.00, 'INTERNACIONAL', 'vuelos/madrid_RbJfUUm.jfif', 'activo'),
	(3, 'VI0002', 'BOGOTA', 'LONDRES', '2025-11-06', '08:20:00.000000', '2025-11-06', '16:20:00.000000', 28800000000, 250, 3000000.00, 'INTERNACIONAL', 'vuelos/londres_famTyT2.jpg', 'activo'),
	(4, 'VI0003', 'MEDELLIN', 'NUEVA_YORK', '2025-11-07', '10:20:00.000000', '2025-11-07', '18:20:00.000000', 28800000000, 250, 2400000.00, 'INTERNACIONAL', 'vuelos/newyork_msBijwg.jpg', 'activo'),
	(5, 'VI0004', 'CALI', 'BUENOS_AIRES', '2025-11-08', '13:20:00.000000', '2025-11-08', '21:20:00.000000', 28800000000, 250, 2500000.00, 'INTERNACIONAL', 'vuelos/29581ba3c89a845_LkK3IUr.jfif', 'activo'),
	(6, 'VI0005', 'CARTAGENA', 'MIAMI', '2025-11-10', '09:20:00.000000', '2025-11-10', '17:20:00.000000', 28800000000, 250, 2100000.00, 'INTERNACIONAL', 'vuelos/miami_EzaUsDi.jpg', 'activo');

-- Volcando estructura para tabla condor_airways.auth_group
CREATE TABLE IF NOT EXISTS `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.auth_group: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.auth_group_permissions
CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.auth_group_permissions: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.auth_permission
CREATE TABLE IF NOT EXISTS `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=117 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.auth_permission: ~112 rows (aproximadamente)
INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
	(1, 'Can add log entry', 1, 'add_logentry'),
	(2, 'Can change log entry', 1, 'change_logentry'),
	(3, 'Can delete log entry', 1, 'delete_logentry'),
	(4, 'Can view log entry', 1, 'view_logentry'),
	(5, 'Can add permission', 2, 'add_permission'),
	(6, 'Can change permission', 2, 'change_permission'),
	(7, 'Can delete permission', 2, 'delete_permission'),
	(8, 'Can view permission', 2, 'view_permission'),
	(9, 'Can add group', 3, 'add_group'),
	(10, 'Can change group', 3, 'change_group'),
	(11, 'Can delete group', 3, 'delete_group'),
	(12, 'Can view group', 3, 'view_group'),
	(13, 'Can add user', 4, 'add_user'),
	(14, 'Can change user', 4, 'change_user'),
	(15, 'Can delete user', 4, 'delete_user'),
	(16, 'Can view user', 4, 'view_user'),
	(17, 'Can add content type', 5, 'add_contenttype'),
	(18, 'Can change content type', 5, 'change_contenttype'),
	(19, 'Can delete content type', 5, 'delete_contenttype'),
	(20, 'Can view content type', 5, 'view_contenttype'),
	(21, 'Can add session', 6, 'add_session'),
	(22, 'Can change session', 6, 'change_session'),
	(23, 'Can delete session', 6, 'delete_session'),
	(24, 'Can view session', 6, 'view_session'),
	(25, 'Can add Capital', 7, 'add_capital'),
	(26, 'Can change Capital', 7, 'change_capital'),
	(27, 'Can delete Capital', 7, 'delete_capital'),
	(28, 'Can view Capital', 7, 'view_capital'),
	(29, 'Can add rol', 8, 'add_rol'),
	(30, 'Can change rol', 8, 'change_rol'),
	(31, 'Can delete rol', 8, 'delete_rol'),
	(32, 'Can view rol', 8, 'view_rol'),
	(33, 'Can add usuario', 9, 'add_usuario'),
	(34, 'Can change usuario', 9, 'change_usuario'),
	(35, 'Can delete usuario', 9, 'delete_usuario'),
	(36, 'Can view usuario', 9, 'view_usuario'),
	(37, 'Can add vuelo', 10, 'add_vuelo'),
	(38, 'Can change vuelo', 10, 'change_vuelo'),
	(39, 'Can delete vuelo', 10, 'delete_vuelo'),
	(40, 'Can view vuelo', 10, 'view_vuelo'),
	(41, 'Can add reserva', 11, 'add_reserva'),
	(42, 'Can change reserva', 11, 'change_reserva'),
	(43, 'Can delete reserva', 11, 'delete_reserva'),
	(44, 'Can view reserva', 11, 'view_reserva'),
	(45, 'Can add compra', 12, 'add_compra'),
	(46, 'Can change compra', 12, 'change_compra'),
	(47, 'Can delete compra', 12, 'delete_compra'),
	(48, 'Can view compra', 12, 'view_compra'),
	(49, 'Can add check in', 13, 'add_checkin'),
	(50, 'Can change check in', 13, 'change_checkin'),
	(51, 'Can delete check in', 13, 'delete_checkin'),
	(52, 'Can view check in', 13, 'view_checkin'),
	(53, 'Can add maleta', 14, 'add_maleta'),
	(54, 'Can change maleta', 14, 'change_maleta'),
	(55, 'Can delete maleta', 14, 'delete_maleta'),
	(56, 'Can view maleta', 14, 'view_maleta'),
	(57, 'Can add historial operacion', 15, 'add_historialoperacion'),
	(58, 'Can change historial operacion', 15, 'change_historialoperacion'),
	(59, 'Can delete historial operacion', 15, 'delete_historialoperacion'),
	(60, 'Can view historial operacion', 15, 'view_historialoperacion'),
	(61, 'Can add publicacion', 16, 'add_publicacion'),
	(62, 'Can change publicacion', 16, 'change_publicacion'),
	(63, 'Can delete publicacion', 16, 'delete_publicacion'),
	(64, 'Can view publicacion', 16, 'view_publicacion'),
	(65, 'Can add comentario', 17, 'add_comentario'),
	(66, 'Can change comentario', 17, 'change_comentario'),
	(67, 'Can delete comentario', 17, 'delete_comentario'),
	(68, 'Can view comentario', 17, 'view_comentario'),
	(69, 'Can add notificacion', 18, 'add_notificacion'),
	(70, 'Can change notificacion', 18, 'change_notificacion'),
	(71, 'Can delete notificacion', 18, 'delete_notificacion'),
	(72, 'Can view notificacion', 18, 'view_notificacion'),
	(73, 'Can add pais', 19, 'add_pais'),
	(74, 'Can change pais', 19, 'change_pais'),
	(75, 'Can delete pais', 19, 'delete_pais'),
	(76, 'Can view pais', 19, 'view_pais'),
	(77, 'Can add municipio', 20, 'add_municipio'),
	(78, 'Can change municipio', 20, 'change_municipio'),
	(79, 'Can delete municipio', 20, 'delete_municipio'),
	(80, 'Can view municipio', 20, 'view_municipio'),
	(81, 'Can add departamento', 21, 'add_departamento'),
	(82, 'Can change departamento', 21, 'change_departamento'),
	(83, 'Can delete departamento', 21, 'delete_departamento'),
	(84, 'Can view departamento', 21, 'view_departamento'),
	(85, 'Can add country', 22, 'add_country'),
	(86, 'Can change country', 22, 'change_country'),
	(87, 'Can delete country', 22, 'delete_country'),
	(88, 'Can view country', 22, 'view_country'),
	(89, 'Can add region/state', 23, 'add_region'),
	(90, 'Can change region/state', 23, 'change_region'),
	(91, 'Can delete region/state', 23, 'delete_region'),
	(92, 'Can view region/state', 23, 'view_region'),
	(93, 'Can add city', 24, 'add_city'),
	(94, 'Can change city', 24, 'change_city'),
	(95, 'Can delete city', 24, 'delete_city'),
	(96, 'Can view city', 24, 'view_city'),
	(97, 'Can add SubRegion', 25, 'add_subregion'),
	(98, 'Can change SubRegion', 25, 'change_subregion'),
	(99, 'Can delete SubRegion', 25, 'delete_subregion'),
	(100, 'Can view SubRegion', 25, 'view_subregion'),
	(101, 'Can add tarjeta', 26, 'add_tarjeta'),
	(102, 'Can change tarjeta', 26, 'change_tarjeta'),
	(103, 'Can delete tarjeta', 26, 'delete_tarjeta'),
	(104, 'Can view tarjeta', 26, 'view_tarjeta'),
	(105, 'Can add carrito', 27, 'add_carrito'),
	(106, 'Can change carrito', 27, 'change_carrito'),
	(107, 'Can delete carrito', 27, 'delete_carrito'),
	(108, 'Can view carrito', 27, 'view_carrito'),
	(109, 'Can add carrito item', 28, 'add_carritoitem'),
	(110, 'Can change carrito item', 28, 'change_carritoitem'),
	(111, 'Can delete carrito item', 28, 'delete_carritoitem'),
	(112, 'Can view carrito item', 28, 'view_carritoitem'),
	(113, 'Can add reserva pasajero', 29, 'add_reservapasajero'),
	(114, 'Can change reserva pasajero', 29, 'change_reservapasajero'),
	(115, 'Can delete reserva pasajero', 29, 'delete_reservapasajero'),
	(116, 'Can view reserva pasajero', 29, 'view_reservapasajero');

-- Volcando estructura para tabla condor_airways.auth_user
CREATE TABLE IF NOT EXISTS `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.auth_user: ~10 rows (aproximadamente)
INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `date_joined`) VALUES
	(1, 'pbkdf2_sha256$1000000$ulSvZOVjDym9BhmkQ5xbDc$wWNBasYXc0gcL0uJqhgar/O0rZ/H0YFqRBmfVCdR6tY=', '2025-11-04 23:25:12.924103', 0, 'karencita22', '', '', 'karencarcas@gmail.com', 0, 1, '2025-10-29 22:43:49.924190'),
	(2, 'pbkdf2_sha256$1000000$KvbZfRqEf0ZoicLT2rWKwT$Fp/U6XQf5tKWmRhkwEgnquWIoyNaJsMfJeG/s/8LBt8=', '2025-10-29 23:00:12.476635', 0, 'yineth25', '', '', 'niyica123@gmail.com', 0, 1, '2025-10-29 22:45:02.559899'),
	(3, 'pbkdf2_sha256$1000000$M4wc8IDCLSt6NeKlgnkjBv$R4hhZyTamFi9+MZCKvlOs3i3C7DTexMRCDp9K8UWpkY=', NULL, 0, 'jhoncito08', '', '', 'jhoncito@gmail.com', 0, 1, '2025-10-29 22:46:09.643117'),
	(4, 'pbkdf2_sha256$1000000$6p96hU2yJYeilytVio3VEi$hAhQxsThyyAoZopAvu3efSxX0uYUlS+epR0qtrzu1t4=', '2025-10-29 22:51:35.283073', 1, 'root', '', '', 'root@condorairways.com', 1, 1, '2025-10-29 22:50:47.035081'),
	(5, 'pbkdf2_sha256$1000000$OqgrwtHued0RYvStOykn4a$wqqsuZ0TV28oGcERWUHV7TJndenEZE0BcFr7kzZB0dI=', '2025-11-05 00:15:37.642136', 0, 'Karen09', '', '', 'karenmanuela.cardona@utp.edu.co', 0, 1, '2025-10-29 22:52:01.824766'),
	(6, 'pbkdf2_sha256$1000000$wVE4wIWbO22VX0TcZTdU4J$twCNe5cCJ2QvUO6n8D3DILDDtfnqxyT39Fy9XzkJgSM=', NULL, 0, 'Juan88', '', '', 'juanito@gmail.com', 0, 1, '2025-10-29 22:52:31.380714'),
	(7, 'pbkdf2_sha256$1000000$g9HUewIWDzBecHkHUlqvnA$eWq+FjYzpviwrxaGXa4ezB2eRhx+6UE0Fil3uvgMglM=', NULL, 0, 'Nico22', '', '', 'nicolas22@gmail.com', 0, 1, '2025-10-29 22:53:00.838761'),
	(8, 'pbkdf2_sha256$1000000$wDpAfJ3mrrfCLVitqGu337$P+WsFdiOFWz8e4yozREq3NDw+2TMZcGXpbZDKgRrKeA=', NULL, 0, 'Lina55', '', '', 'linita@gmail.com', 0, 1, '2025-10-29 22:53:27.219467'),
	(9, 'pbkdf2_sha256$1000000$0sZY93nq7KT9kDRPd9sTt7$+a5NYaxw2DEpQZC7CbiQ5FB68jRCWozBFpKdnK9oy6U=', NULL, 0, 'Manu123', '', '', 'manuelita@gmail.com', 0, 1, '2025-10-29 22:53:52.974683'),
	(10, 'pbkdf2_sha256$1000000$ZAqNNxl5tjnjSGLPlQ7ZCn$aDDLA5J64IdzfsH06ycwyrPBSzx/IWxi9cOp+6l+fC8=', '2025-10-30 00:45:46.826445', 0, 'miguel25', '', '', 'miguelito@gmail.com', 0, 1, '2025-10-30 00:45:19.405958');

-- Volcando estructura para tabla condor_airways.auth_user_groups
CREATE TABLE IF NOT EXISTS `auth_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.auth_user_groups: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.auth_user_user_permissions
CREATE TABLE IF NOT EXISTS `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.auth_user_user_permissions: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.checkin
CREATE TABLE IF NOT EXISTS `checkin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `compra_id` int(11) NOT NULL,
  `asiento` varchar(5) NOT NULL,
  `pase_abordar` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `compra_id` (`compra_id`),
  CONSTRAINT `checkin_ibfk_1` FOREIGN KEY (`compra_id`) REFERENCES `compra` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.checkin: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.cities_light_city
CREATE TABLE IF NOT EXISTS `cities_light_city` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_ascii` varchar(200) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `geoname_id` int(11) DEFAULT NULL,
  `alternate_names` longtext DEFAULT NULL,
  `name` varchar(200) NOT NULL,
  `display_name` varchar(200) NOT NULL,
  `search_names` longtext NOT NULL,
  `latitude` decimal(8,5) DEFAULT NULL,
  `longitude` decimal(8,5) DEFAULT NULL,
  `region_id` int(11) DEFAULT NULL,
  `country_id` int(11) NOT NULL,
  `population` bigint(20) DEFAULT NULL,
  `feature_code` varchar(10) DEFAULT NULL,
  `timezone` varchar(40) DEFAULT NULL,
  `subregion_id` int(11) DEFAULT NULL,
  `translations` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`translations`)),
  PRIMARY KEY (`id`),
  UNIQUE KEY `geoname_id` (`geoname_id`),
  UNIQUE KEY `cities_light_city_region_id_subregion_id_name_cdfc77ea_uniq` (`region_id`,`subregion_id`,`name`),
  UNIQUE KEY `cities_light_city_region_id_subregion_id_slug_efb2e768_uniq` (`region_id`,`subregion_id`,`slug`),
  KEY `cities_light_city_country_id_cf310fd2_fk_cities_light_country_id` (`country_id`),
  KEY `cities_light_city_name_ascii_1e56323b` (`name_ascii`),
  KEY `cities_light_city_slug_cb2251f8` (`slug`),
  KEY `cities_light_city_name_4859e2a5` (`name`),
  KEY `cities_light_city_population_d597eeb6` (`population`),
  KEY `cities_light_city_feature_code_d43c9217` (`feature_code`),
  KEY `cities_light_city_timezone_0fb51b1e` (`timezone`),
  KEY `cities_light_city_subregion_id_0926d2ad_fk_cities_li` (`subregion_id`),
  KEY `cities_light_city_region_id_f7ab977b` (`region_id`),
  CONSTRAINT `cities_light_city_country_id_cf310fd2_fk_cities_light_country_id` FOREIGN KEY (`country_id`) REFERENCES `cities_light_country` (`id`),
  CONSTRAINT `cities_light_city_region_id_f7ab977b_fk_cities_light_region_id` FOREIGN KEY (`region_id`) REFERENCES `cities_light_region` (`id`),
  CONSTRAINT `cities_light_city_subregion_id_0926d2ad_fk_cities_li` FOREIGN KEY (`subregion_id`) REFERENCES `cities_light_subregion` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.cities_light_city: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.cities_light_country
CREATE TABLE IF NOT EXISTS `cities_light_country` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_ascii` varchar(200) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `geoname_id` int(11) DEFAULT NULL,
  `alternate_names` longtext DEFAULT NULL,
  `name` varchar(200) NOT NULL,
  `code2` varchar(2) DEFAULT NULL,
  `code3` varchar(3) DEFAULT NULL,
  `continent` varchar(2) NOT NULL,
  `tld` varchar(5) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `translations` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`translations`)),
  PRIMARY KEY (`id`),
  UNIQUE KEY `geoname_id` (`geoname_id`),
  UNIQUE KEY `code2` (`code2`),
  UNIQUE KEY `code3` (`code3`),
  KEY `cities_light_country_name_ascii_648cc5e3` (`name_ascii`),
  KEY `cities_light_country_slug_3707a22c` (`slug`),
  KEY `cities_light_country_continent_e2c412a4` (`continent`),
  KEY `cities_light_country_tld_1fb2faaa` (`tld`),
  KEY `cities_light_country_name_1d61d0d2` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.cities_light_country: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.cities_light_region
CREATE TABLE IF NOT EXISTS `cities_light_region` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_ascii` varchar(200) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `geoname_id` int(11) DEFAULT NULL,
  `alternate_names` longtext DEFAULT NULL,
  `name` varchar(200) NOT NULL,
  `display_name` varchar(200) NOT NULL,
  `geoname_code` varchar(50) DEFAULT NULL,
  `country_id` int(11) NOT NULL,
  `translations` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`translations`)),
  PRIMARY KEY (`id`),
  UNIQUE KEY `cities_light_region_country_id_name_6e5b3799_uniq` (`country_id`,`name`),
  UNIQUE KEY `cities_light_region_country_id_slug_3dd02103_uniq` (`country_id`,`slug`),
  UNIQUE KEY `geoname_id` (`geoname_id`),
  KEY `cities_light_region_name_ascii_f085cb82` (`name_ascii`),
  KEY `cities_light_region_slug_1653969f` (`slug`),
  KEY `cities_light_region_name_775f9496` (`name`),
  KEY `cities_light_region_geoname_code_1b0d4e58` (`geoname_code`),
  CONSTRAINT `cities_light_region_country_id_b2782d49_fk_cities_li` FOREIGN KEY (`country_id`) REFERENCES `cities_light_country` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.cities_light_region: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.cities_light_subregion
CREATE TABLE IF NOT EXISTS `cities_light_subregion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `name_ascii` varchar(200) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `geoname_id` int(11) DEFAULT NULL,
  `alternate_names` longtext DEFAULT NULL,
  `display_name` varchar(200) NOT NULL,
  `geoname_code` varchar(50) DEFAULT NULL,
  `country_id` int(11) NOT NULL,
  `region_id` int(11) DEFAULT NULL,
  `translations` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`translations`)),
  PRIMARY KEY (`id`),
  UNIQUE KEY `geoname_id` (`geoname_id`),
  KEY `cities_light_subregi_country_id_9b32b484_fk_cities_li` (`country_id`),
  KEY `cities_light_subregion_name_2882337e` (`name`),
  KEY `cities_light_subregion_name_ascii_ecf9a336` (`name_ascii`),
  KEY `cities_light_subregion_slug_43494546` (`slug`),
  KEY `cities_light_subregion_geoname_code_843acdc3` (`geoname_code`),
  KEY `cities_light_subregi_region_id_c6e0b71f_fk_cities_li` (`region_id`),
  CONSTRAINT `cities_light_subregi_country_id_9b32b484_fk_cities_li` FOREIGN KEY (`country_id`) REFERENCES `cities_light_country` (`id`),
  CONSTRAINT `cities_light_subregi_region_id_c6e0b71f_fk_cities_li` FOREIGN KEY (`region_id`) REFERENCES `cities_light_region` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.cities_light_subregion: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.compra
CREATE TABLE IF NOT EXISTS `compra` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `vuelo_id` int(11) NOT NULL,
  `fecha_compra` datetime NOT NULL DEFAULT current_timestamp(),
  `estado` enum('activa','cancelada') DEFAULT 'activa',
  `codigo_reserva` varchar(50) NOT NULL,
  `metodo_pago` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo_reserva` (`codigo_reserva`),
  KEY `usuario_id` (`usuario_id`),
  KEY `vuelo_id` (`vuelo_id`),
  CONSTRAINT `compra_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`),
  CONSTRAINT `compra_ibfk_2` FOREIGN KEY (`vuelo_id`) REFERENCES `vuelo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.compra: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.django_admin_log
CREATE TABLE IF NOT EXISTS `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.django_admin_log: ~11 rows (aproximadamente)
INSERT INTO `django_admin_log` (`id`, `action_time`, `object_id`, `object_repr`, `action_flag`, `change_message`, `content_type_id`, `user_id`) VALUES
	(1, '2025-10-03 02:32:18.577308', '1', 'VN0001 - ARAUCA → CUCUTA (NACIONAL)', 1, '[{"added": {}}]', 10, 1),
	(2, '2025-10-03 02:32:47.189729', '2', 'VN0002 - ARAUCA → CUCUTA (NACIONAL)', 1, '[{"added": {}}]', 10, 1),
	(3, '2025-10-03 02:33:25.851564', '3', 'VI0001 - PEREIRA → LONDRES (INTERNACIONAL)', 1, '[{"added": {}}]', 10, 1),
	(4, '2025-10-03 02:38:41.492080', '1', 'VN0001 - ARAUCA → YOPAL (NACIONAL)', 1, '[{"added": {}}]', 10, 1),
	(5, '2025-10-03 02:39:11.178228', '2', 'VN0002 - ARMENIA → VILLAVICENCIO (NACIONAL)', 1, '[{"added": {}}]', 10, 1),
	(6, '2025-10-03 02:39:50.825667', '3', 'VN0003 - BARRANQUILLA → VALLEDUPAR (NACIONAL)', 1, '[{"added": {}}]', 10, 1),
	(7, '2025-10-03 02:40:19.618306', '4', 'VN0004 - BOGOTA → SANTA_MARTA (NACIONAL)', 1, '[{"added": {}}]', 10, 1),
	(8, '2025-10-03 02:40:48.012500', '5', 'VI0001 - PEREIRA → MADRID (INTERNACIONAL)', 1, '[{"added": {}}]', 10, 1),
	(9, '2025-10-03 02:41:15.722711', '6', 'VI0002 - BOGOTA → LONDRES (INTERNACIONAL)', 1, '[{"added": {}}]', 10, 1),
	(10, '2025-10-03 02:41:52.469471', '7', 'VI0003 - MEDELLIN → NUEVA_YORK (INTERNACIONAL)', 1, '[{"added": {}}]', 10, 1),
	(11, '2025-10-03 02:42:35.603135', '8', 'VI0004 - CALI → BUENOS_AIRES (INTERNACIONAL)', 1, '[{"added": {}}]', 10, 1),
	(12, '2025-10-20 00:57:44.271244', '1', 'VN0001 - ARMENIA → IBAGUE (NACIONAL)', 1, '[{"added": {}}]', 10, 1);

-- Volcando estructura para tabla condor_airways.django_content_type
CREATE TABLE IF NOT EXISTS `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.django_content_type: ~28 rows (aproximadamente)
INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
	(1, 'admin', 'logentry'),
	(2, 'auth', 'permission'),
	(3, 'auth', 'group'),
	(4, 'auth', 'user'),
	(5, 'contenttypes', 'contenttype'),
	(6, 'sessions', 'session'),
	(7, 'aerolinea', 'capital'),
	(8, 'aerolinea', 'rol'),
	(9, 'aerolinea', 'usuario'),
	(10, 'aerolinea', 'vuelo'),
	(11, 'aerolinea', 'reserva'),
	(12, 'aerolinea', 'compra'),
	(13, 'aerolinea', 'checkin'),
	(14, 'aerolinea', 'maleta'),
	(15, 'aerolinea', 'historialoperacion'),
	(16, 'aerolinea', 'publicacion'),
	(17, 'aerolinea', 'comentario'),
	(18, 'aerolinea', 'notificacion'),
	(19, 'aerolinea', 'pais'),
	(20, 'aerolinea', 'municipio'),
	(21, 'aerolinea', 'departamento'),
	(22, 'cities_light', 'country'),
	(23, 'cities_light', 'region'),
	(24, 'cities_light', 'city'),
	(25, 'cities_light', 'subregion'),
	(26, 'aerolinea', 'tarjeta'),
	(27, 'aerolinea', 'carrito'),
	(28, 'aerolinea', 'carritoitem'),
	(29, 'aerolinea', 'reservapasajero');

-- Volcando estructura para tabla condor_airways.django_migrations
CREATE TABLE IF NOT EXISTS `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.django_migrations: ~59 rows (aproximadamente)
INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
	(1, 'contenttypes', '0001_initial', '2025-09-14 22:31:04.500826'),
	(2, 'auth', '0001_initial', '2025-09-14 22:31:13.015985'),
	(3, 'admin', '0001_initial', '2025-09-14 22:31:14.725590'),
	(4, 'admin', '0002_logentry_remove_auto_add', '2025-09-14 22:31:14.805700'),
	(5, 'admin', '0003_logentry_add_action_flag_choices', '2025-09-14 22:31:15.098814'),
	(7, 'contenttypes', '0002_remove_content_type_name', '2025-09-14 22:31:18.418831'),
	(8, 'auth', '0002_alter_permission_name_max_length', '2025-09-14 22:31:19.240020'),
	(9, 'auth', '0003_alter_user_email_max_length', '2025-09-14 22:31:19.858553'),
	(10, 'auth', '0004_alter_user_username_opts', '2025-09-14 22:31:19.925124'),
	(11, 'auth', '0005_alter_user_last_login_null', '2025-09-14 22:31:21.015931'),
	(12, 'auth', '0006_require_contenttypes_0002', '2025-09-14 22:31:21.038286'),
	(13, 'auth', '0007_alter_validators_add_error_messages', '2025-09-14 22:31:21.093178'),
	(14, 'auth', '0008_alter_user_username_max_length', '2025-09-14 22:31:22.147553'),
	(15, 'auth', '0009_alter_user_last_name_max_length', '2025-09-14 22:31:22.924424'),
	(16, 'auth', '0010_alter_group_name_max_length', '2025-09-14 22:31:23.811661'),
	(17, 'auth', '0011_update_proxy_permissions', '2025-09-14 22:31:23.945929'),
	(18, 'auth', '0012_alter_user_first_name_max_length', '2025-09-14 22:31:24.943582'),
	(19, 'sessions', '0001_initial', '2025-09-14 22:31:25.975019'),
	(23, 'aerolinea', '0002_usuario_fecha_nacimiento_alter_usuario_rol', '2025-09-17 02:37:23.283008'),
	(24, 'aerolinea', '0003_usuario_es_admin', '2025-09-19 00:01:39.125052'),
	(25, 'aerolinea', '0004_vuelo_tipo', '2025-09-25 00:19:51.697836'),
	(26, 'aerolinea', '0005_remove_usuario_direccion_remove_usuario_telefono_and_more', '2025-09-27 01:33:08.634992'),
	(27, 'aerolinea', '0006_add_capital_model', '2025-09-30 21:00:40.539670'),
	(28, 'aerolinea', '0007_add_vuelo_time_fields', '2025-09-30 21:00:51.346123'),
	(29, 'aerolinea', '0008_alter_vuelo_precio', '2025-09-30 21:00:51.435827'),
	(30, 'aerolinea', '0009_alter_vuelo_fecha_llegada_alter_vuelo_fecha_salida', '2025-09-30 21:16:40.444769'),
	(31, 'aerolinea', '0002_remove_usuario_nombre_remove_usuario_nombre_completo_and_more', '2025-10-01 03:59:09.076856'),
	(32, 'aerolinea', '0003_fix_fecha_nacimiento', '2025-10-01 04:40:37.308586'),
	(34, 'aerolinea', '0001_initial', '2025-10-19 23:05:09.220352'),
	(35, 'aerolinea', '0002_departamento_pais_municipio_departamento_pais', '2025-10-19 23:05:11.760155'),
	(36, 'aerolinea', '0003_alter_usuario_lugar_nacimiento', '2025-10-19 23:05:15.278399'),
	(37, 'aerolinea', '0004_remove_usuario_lugar_nacimiento_usuario_departamento_and_more', '2025-10-19 23:22:05.758192'),
	(38, 'cities_light', '0001_initial', '2025-10-20 01:13:33.352916'),
	(39, 'cities_light', '0002_city', '2025-10-20 01:13:44.799216'),
	(40, 'cities_light', '0003_auto_20141120_0342', '2025-10-20 01:13:44.919697'),
	(41, 'cities_light', '0004_autoslug_update', '2025-10-20 01:13:45.825451'),
	(42, 'cities_light', '0005_blank_phone', '2025-10-20 01:13:45.993876'),
	(43, 'cities_light', '0006_compensate_for_0003_bytestring_bug', '2025-10-20 01:13:46.231649'),
	(44, 'cities_light', '0007_make_country_name_not_unique', '2025-10-20 01:13:52.466846'),
	(45, 'cities_light', '0008_city_timezone', '2025-10-20 01:13:54.237077'),
	(46, 'cities_light', '0009_add_subregion', '2025-10-20 01:14:02.179939'),
	(47, 'cities_light', '0010_auto_20200508_1851', '2025-10-20 01:14:18.073149'),
	(48, 'cities_light', '0011_alter_city_country_alter_city_region_and_more', '2025-10-20 01:14:18.680477'),
	(49, 'cities_light', '0012_city_translations_country_translations_and_more', '2025-10-20 01:14:28.931344'),
	(50, 'aerolinea', '0005_usuario_es_root', '2025-10-20 01:35:32.732426'),
	(51, 'aerolinea', '0006_usuario_registro_completo', '2025-10-21 21:10:46.589177'),
	(52, 'aerolinea', '0007_tarjeta', '2025-10-24 00:41:10.400222'),
	(53, 'aerolinea', '0008_alter_tarjeta_fecha_vencimiento', '2025-10-24 01:41:59.193702'),
	(54, 'aerolinea', '0009_vuelo_imagen', '2025-10-26 21:49:33.582833'),
	(55, 'aerolinea', '0010_carrito_carritoitem_reserva_asiento_asignado_and_more', '2025-10-28 22:52:38.615770'),
	(56, 'aerolinea', '0011_carritoitem_reserva_and_more', '2025-10-28 23:49:52.871363'),
	(57, 'aerolinea', '0012_remove_reserva_unique_usuario_vuelo_and_more', '2025-10-29 01:03:08.174208'),
	(58, 'aerolinea', '0013_reserva_clase', '2025-10-29 21:50:59.830980'),
	(59, 'aerolinea', '0014_alter_tarjeta_tipo', '2025-10-29 23:50:23.844719'),
	(60, 'aerolinea', '0015_tarjeta_estado', '2025-10-29 23:53:31.429648'),
	(61, 'aerolinea', '0016_compra_monto_total', '2025-10-30 00:34:13.300721'),
	(62, 'aerolinea', '0017_reservapasajero_and_more', '2025-10-31 01:08:56.650249'),
	(63, 'aerolinea', '0018_vuelo_estado', '2025-10-31 01:46:25.746812'),
	(64, 'aerolinea', '0019_reservapasajero_asiento', '2025-11-04 01:14:52.880846');

-- Volcando estructura para tabla condor_airways.django_session
CREATE TABLE IF NOT EXISTS `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.django_session: ~2 rows (aproximadamente)
INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
	('wbrt2588xdv7vzsb40s9exan50f7y48g', '.eJxVjEEOwiAQRe_C2hBKBQaX7nsGMjCMVA0kpV0Z765NutDtf-_9lwi4rSVsPS9hJnERIE6_W8T0yHUHdMd6azK1ui5zlLsiD9rl1Cg_r4f7d1Cwl2-NyCrioCEbq2xOAIq1SQTenz26DFGzHoiMU-x4NClGZyyPyIQIZhTvD_zmOKM:1vBl12:G_MLQWAP-15cbyEIQYfDyASsCiZMwjS6n2CVGotbQbA', '2025-11-06 02:25:24.185410');

-- Volcando estructura para tabla condor_airways.maleta
CREATE TABLE IF NOT EXISTS `maleta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `checkin_id` int(11) NOT NULL,
  `peso` decimal(5,2) DEFAULT 0.00,
  `costo` decimal(10,2) DEFAULT 0.00,
  PRIMARY KEY (`id`),
  KEY `checkin_id` (`checkin_id`),
  CONSTRAINT `maleta_ibfk_1` FOREIGN KEY (`checkin_id`) REFERENCES `checkin` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.maleta: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.reserva
CREATE TABLE IF NOT EXISTS `reserva` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `vuelo_id` int(11) NOT NULL,
  `fecha_reserva` datetime NOT NULL DEFAULT current_timestamp(),
  `estado` enum('activa','cancelada','vencida') DEFAULT 'activa',
  `num_tiquetes` int(11) DEFAULT NULL CHECK (`num_tiquetes` between 1 and 5),
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `vuelo_id` (`vuelo_id`),
  CONSTRAINT `reserva_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`),
  CONSTRAINT `reserva_ibfk_2` FOREIGN KEY (`vuelo_id`) REFERENCES `vuelo` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.reserva: ~0 rows (aproximadamente)

-- Volcando estructura para tabla condor_airways.rol
CREATE TABLE IF NOT EXISTS `rol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.rol: ~4 rows (aproximadamente)
INSERT INTO `rol` (`id`, `nombre`) VALUES
	(1, 'Cliente'),
	(2, 'Administrador'),
	(3, 'Root');

-- Volcando estructura para tabla condor_airways.usuario
CREATE TABLE IF NOT EXISTS `usuario` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` varchar(150) DEFAULT NULL,
  `rol_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `rol_id` (`rol_id`),
  CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `rol` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.usuario: ~0 rows (aproximadamente)
INSERT INTO `usuario` (`id`, `nombre`, `email`, `password`, `telefono`, `direccion`, `rol_id`) VALUES
	(1, 'Karen', 'karen@utp.edu.co', '1234', NULL, NULL, 1);

-- Volcando estructura para tabla condor_airways.vuelo
CREATE TABLE IF NOT EXISTS `vuelo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(20) NOT NULL,
  `origen` varchar(50) NOT NULL,
  `destino` varchar(50) NOT NULL,
  `fecha_salida` datetime NOT NULL,
  `fecha_llegada` datetime NOT NULL,
  `capacidad` int(11) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- Volcando datos para la tabla condor_airways.vuelo: ~0 rows (aproximadamente)

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
