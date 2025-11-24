-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 06-11-2025 a las 21:44:47
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `gimnasio_db`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `asistencias`
--

CREATE TABLE `asistencias` (
  `id` int(11) NOT NULL,
  `miembro_id` int(11) NOT NULL,
  `clase_id` int(11) DEFAULT NULL,
  `fecha_entrada` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_salida` timestamp NULL DEFAULT NULL,
  `tipo` enum('area_pesas','cardio','clase') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clases`
--

CREATE TABLE `clases` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `instructor` varchar(100) NOT NULL,
  `horario` time NOT NULL,
  `duracion_minutos` int(11) NOT NULL,
  `capacidad_maxima` int(11) NOT NULL,
  `dias_semana` varchar(50) NOT NULL,
  `activa` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `clases`
--

INSERT INTO `clases` (`id`, `nombre`, `descripcion`, `instructor`, `horario`, `duracion_minutos`, `capacidad_maxima`, `dias_semana`, `activa`) VALUES
(1, 'Yoga Matutino', 'Clase de yoga para principiantes', 'Ana García', '07:00:00', 60, 20, 'Lunes,Miércoles,Viernes', 1),
(2, 'Spinning Intenso', 'Entrenamiento cardiovascular en bicicleta', 'Carlos López', '18:00:00', 45, 15, 'Martes,Jueves', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `logs`
--

CREATE TABLE `logs` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `accion` varchar(100) NOT NULL,
  `tabla_afectada` varchar(50) NOT NULL,
  `registro_id` int(11) DEFAULT NULL,
  `detalles` text DEFAULT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `logs`
--

INSERT INTO `logs` (`id`, `usuario_id`, `accion`, `tabla_afectada`, `registro_id`, `detalles`, `fecha`) VALUES
(1, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-10-29 06:02:47'),
(2, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-10-29 06:03:04'),
(3, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-10-29 06:06:43'),
(4, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-10-29 06:13:57'),
(5, 1, 'INSERT', 'miembros', 1, 'Nuevo miembro: Jonathan Sebastian - Código: MEM001', '2025-10-29 06:27:50'),
(6, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-10-29 18:12:08'),
(7, 1, 'UPDATE', 'miembros', 1, 'Actualización de datos del miembro ID: 1', '2025-10-29 18:26:24'),
(8, 1, 'INSERT', 'miembros', 2, 'Nuevo miembro: Jose Barrera - Código: MEM002', '2025-10-29 18:28:13'),
(9, 1, 'LOGOUT', 'usuarios', 1, 'Cierre de sesión', '2025-10-29 18:31:11'),
(10, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-10-29 18:31:23'),
(11, 1, 'INSERT', 'miembros', 3, 'Nuevo miembro: churs cuevas - Código: MEM003', '2025-10-29 18:33:35'),
(12, 1, 'LOGOUT', 'usuarios', 1, 'Cierre de sesión', '2025-10-29 18:33:52'),
(13, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-05 04:03:07'),
(14, 1, 'UPDATE', 'miembros', 3, 'Actualización de datos del miembro ID: 3', '2025-11-05 04:04:13'),
(15, 1, 'DELETE', 'miembros', 3, 'Miembro marcado como inactivo', '2025-11-05 04:04:26'),
(16, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-05 04:29:44'),
(17, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-05 04:35:02'),
(18, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 04:11:38'),
(19, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 04:15:15'),
(20, 1, 'INSERT', 'pagos', 1, 'Pago registrado: $500.00 - Miembro: Jonathan Sebastian', '2025-11-06 04:17:58'),
(21, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 04:26:33'),
(22, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 04:33:29'),
(23, 1, 'INSERT', 'pagos', 2, 'Pago registrado: $500.0 - Miembro: Jose Barrera', '2025-11-06 04:33:51'),
(24, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 05:23:01'),
(25, 1, 'LOGOUT', 'usuarios', 1, 'Cierre de sesión', '2025-11-06 05:27:55'),
(26, 2, 'LOGIN', 'usuarios', 2, 'Inicio de sesión exitoso', '2025-11-06 05:27:59'),
(27, 2, 'LOGOUT', 'usuarios', 2, 'Cierre de sesión', '2025-11-06 05:28:13'),
(28, 3, 'LOGIN', 'usuarios', 3, 'Inicio de sesión exitoso', '2025-11-06 05:28:19'),
(29, 3, 'LOGOUT', 'usuarios', 3, 'Cierre de sesión', '2025-11-06 05:28:48'),
(30, 2, 'LOGIN', 'usuarios', 2, 'Inicio de sesión exitoso', '2025-11-06 05:28:54'),
(31, 2, 'LOGOUT', 'usuarios', 2, 'Cierre de sesión', '2025-11-06 05:28:59'),
(32, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 05:29:03'),
(33, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 06:30:30'),
(34, 1, 'LOGOUT', 'usuarios', 1, 'Cierre de sesión', '2025-11-06 06:31:57'),
(35, 2, 'LOGIN', 'usuarios', 2, 'Inicio de sesión exitoso', '2025-11-06 06:32:02'),
(36, 2, 'LOGOUT', 'usuarios', 2, 'Cierre de sesión', '2025-11-06 06:32:18'),
(37, 3, 'LOGIN', 'usuarios', 3, 'Inicio de sesión exitoso', '2025-11-06 06:32:24'),
(38, 3, 'LOGOUT', 'usuarios', 3, 'Cierre de sesión', '2025-11-06 06:35:04'),
(39, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 06:35:09'),
(40, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 06:44:14'),
(41, 1, 'LOGOUT', 'usuarios', 1, 'Cierre de sesión', '2025-11-06 06:44:51'),
(42, 2, 'LOGIN', 'usuarios', 2, 'Inicio de sesión exitoso', '2025-11-06 06:44:56'),
(43, 2, 'LOGOUT', 'usuarios', 2, 'Cierre de sesión', '2025-11-06 06:45:04'),
(44, 3, 'LOGIN', 'usuarios', 3, 'Inicio de sesión exitoso', '2025-11-06 06:45:10'),
(45, 3, 'LOGOUT', 'usuarios', 3, 'Cierre de sesión', '2025-11-06 06:45:39'),
(46, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 18:06:58'),
(47, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 18:10:48'),
(48, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 18:18:49'),
(49, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 18:53:35'),
(50, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 19:32:01'),
(51, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 19:46:52'),
(52, 1, 'LOGIN', 'usuarios', 1, 'Inicio de sesión exitoso', '2025-11-06 20:28:53');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `membresias`
--

CREATE TABLE `membresias` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `precio` decimal(10,2) NOT NULL,
  `duracion_dias` int(11) NOT NULL,
  `acceso_clases` tinyint(1) DEFAULT 0,
  `acceso_area_pesas` tinyint(1) DEFAULT 1,
  `acceso_cardio` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `membresias`
--

INSERT INTO `membresias` (`id`, `nombre`, `descripcion`, `precio`, `duracion_dias`, `acceso_clases`, `acceso_area_pesas`, `acceso_cardio`) VALUES
(1, 'Básica', 'Acceso a área de pesas y cardio', 300.00, 30, 0, 1, 1),
(2, 'Premium', 'Acceso completo incluyendo clases grupales', 500.00, 30, 1, 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `miembros`
--

CREATE TABLE `miembros` (
  `id` int(11) NOT NULL,
  `codigo_miembro` varchar(20) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `direccion` text DEFAULT NULL,
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp(),
  `activo` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `miembros`
--

INSERT INTO `miembros` (`id`, `codigo_miembro`, `nombre`, `apellido`, `email`, `telefono`, `fecha_nacimiento`, `direccion`, `fecha_registro`, `activo`) VALUES
(1, 'MEM001', 'Jonathan', 'Sebastian', 'jona@gmail.com', '555-1234', '2005-08-11', 'Calle Pacheco 34', '2025-10-29 06:27:50', 1),
(2, 'MEM002', 'Jose', 'Barrera', 'jose@gmail.com', '321-2389', '2000-02-15', 'Col. San Jose', '2025-10-29 18:28:13', 1),
(3, 'MEM003', 'churs', 'Patino', 'chursroyal@gmail.com', '7331254789', '2004-09-18', 'zapata', '2025-10-29 18:33:35', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pagos`
--

CREATE TABLE `pagos` (
  `id` int(11) NOT NULL,
  `miembro_id` int(11) NOT NULL,
  `membresia_id` int(11) NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `fecha_pago` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `metodo_pago` enum('efectivo','tarjeta','transferencia') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pagos`
--

INSERT INTO `pagos` (`id`, `miembro_id`, `membresia_id`, `monto`, `fecha_pago`, `fecha_inicio`, `fecha_fin`, `metodo_pago`) VALUES
(1, 1, 2, 500.00, '2025-11-06 04:17:57', '2025-11-06', '2025-12-06', 'efectivo'),
(2, 2, 2, 500.00, '2025-11-06 04:33:51', '2025-11-06', '2025-12-06', 'tarjeta');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `rol` enum('admin','responsable','usuario') NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `activo` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `username`, `password`, `rol`, `nombre`, `email`, `fecha_creacion`, `activo`) VALUES
(1, 'admin', '$2b$12$2.QZ00zeqfEdgyaKEc45yu9BFzKLyf9dpE4Vk5LtpMsHuOM5Qvkum', 'admin', 'Administrador Principal', 'admin@gimnasio.com', '2025-10-29 05:05:13', 1),
(2, 'responsable1', '$2b$12$2.QZ00zeqfEdgyaKEc45yu9BFzKLyf9dpE4Vk5LtpMsHuOM5Qvkum', 'responsable', 'Responsable Operativo', 'responsable@gimnasio.com', '2025-10-29 05:05:13', 1),
(3, 'usuario1', '$2b$12$2.QZ00zeqfEdgyaKEc45yu9BFzKLyf9dpE4Vk5LtpMsHuOM5Qvkum', 'usuario', 'Usuario Consulta', 'usuario@gimnasio.com', '2025-10-29 05:05:13', 1);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `asistencias`
--
ALTER TABLE `asistencias`
  ADD PRIMARY KEY (`id`),
  ADD KEY `miembro_id` (`miembro_id`),
  ADD KEY `clase_id` (`clase_id`);

--
-- Indices de la tabla `clases`
--
ALTER TABLE `clases`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `logs`
--
ALTER TABLE `logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `membresias`
--
ALTER TABLE `membresias`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `miembros`
--
ALTER TABLE `miembros`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `codigo_miembro` (`codigo_miembro`);

--
-- Indices de la tabla `pagos`
--
ALTER TABLE `pagos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `miembro_id` (`miembro_id`),
  ADD KEY `membresia_id` (`membresia_id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `asistencias`
--
ALTER TABLE `asistencias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `clases`
--
ALTER TABLE `clases`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `logs`
--
ALTER TABLE `logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT de la tabla `membresias`
--
ALTER TABLE `membresias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `miembros`
--
ALTER TABLE `miembros`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `pagos`
--
ALTER TABLE `pagos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `asistencias`
--
ALTER TABLE `asistencias`
  ADD CONSTRAINT `asistencias_ibfk_1` FOREIGN KEY (`miembro_id`) REFERENCES `miembros` (`id`),
  ADD CONSTRAINT `asistencias_ibfk_2` FOREIGN KEY (`clase_id`) REFERENCES `clases` (`id`);

--
-- Filtros para la tabla `logs`
--
ALTER TABLE `logs`
  ADD CONSTRAINT `logs_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `pagos`
--
ALTER TABLE `pagos`
  ADD CONSTRAINT `pagos_ibfk_1` FOREIGN KEY (`miembro_id`) REFERENCES `miembros` (`id`),
  ADD CONSTRAINT `pagos_ibfk_2` FOREIGN KEY (`membresia_id`) REFERENCES `membresias` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
