-- ==============================================================================
-- PROYECTO FORMATIVO: "SISTEMAS DE INFORMACIÓN Y DESARROLLO DE SOFTWARE EN EL MAGDALENA"
-- PROGRAMA: ANÁLISIS Y DESARROLLO DE SISTEMAS DE INFORMACIÓN (ADSI 228106 - V102)
-- SOFTWARE: SINETEC (Sistema de Integración Técnica Education)
-- CENTRO: Centro de Logística y Promoción Ecoturística del Magdalena
-- REGIONAL: Regional Magdalena
-- ARCHIVO: script_creacion_inicial_mysql.sql
-- DESCRIPCIÓN: Script DDL para la creación de la base de datos 'sinetec_db' y sus
--              11 tablas normalizadas en MySQL Server 8.0 con motor InnoDB.
-- ==============================================================================

-- ==============================================================================
-- 1. CREACIÓN DE LA BASE DE DATOS
-- ==============================================================================
-- 'CHARACTER SET utf8mb4': Permite almacenar caracteres especiales del español (tildes, eñes)
-- 'COLLATE utf8mb4_unicode_ci': Regla de ordenamiento insensible a mayúsculas/minúsculas.
CREATE DATABASE IF NOT EXISTS `sinetec_db`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Seleccionar la base de datos para ejecutar las siguientes instrucciones:
USE `sinetec_db`;

-- Desactivar temporalmente el chequeo de llaves foráneas para permitir creación o recreación ordenada
SET FOREIGN_KEY_CHECKS = 0;

-- ==============================================================================
-- 2. TABLA: usuarios_rol
-- ==============================================================================
DROP TABLE IF EXISTS `usuarios_rol`;
CREATE TABLE `usuarios_rol` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `nombre` VARCHAR(50) NOT NULL,
  `descripcion` VARCHAR(255) NULL,
  CONSTRAINT `pk_usuarios_rol` PRIMARY KEY (`id`),
  CONSTRAINT `uq_usuarios_rol_nombre` UNIQUE (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 3. TABLA: usuarios_usuario
-- ==============================================================================
DROP TABLE IF EXISTS `usuarios_usuario`;
CREATE TABLE `usuarios_usuario` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `rol_id` INT NOT NULL,
  `tipo_documento` VARCHAR(5) NOT NULL,
  `numero_documento` VARCHAR(20) NOT NULL,
  `nombres` VARCHAR(100) NOT NULL,
  `apellidos` VARCHAR(100) NOT NULL,
  `correo` VARCHAR(150) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `telefono` VARCHAR(20) NULL,
  `esta_activo` BOOLEAN NOT NULL DEFAULT TRUE,
  `fecha_creacion` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `pk_usuarios_usuario` PRIMARY KEY (`id`),
  CONSTRAINT `uq_usuarios_usuario_documento` UNIQUE (`numero_documento`),
  CONSTRAINT `uq_usuarios_usuario_correo` UNIQUE (`correo`),
  CONSTRAINT `fk_usuarios_usuario_rol` FOREIGN KEY (`rol_id`) 
      REFERENCES `usuarios_rol` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX `idx_usuario_documento` ON `usuarios_usuario` (`numero_documento`);
CREATE INDEX `idx_usuario_correo` ON `usuarios_usuario` (`correo`);

-- ==============================================================================
-- 4. TABLA: instituciones_institucioneducativa
-- ==============================================================================
DROP TABLE IF EXISTS `instituciones_institucioneducativa`;
CREATE TABLE `instituciones_institucioneducativa` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `codigo_dane` VARCHAR(20) NOT NULL,
  `nombre` VARCHAR(200) NOT NULL,
  `municipio` VARCHAR(100) NOT NULL,
  `direccion` VARCHAR(255) NULL,
  `telefono` VARCHAR(20) NULL,
  `rector_nombre` VARCHAR(150) NULL,
  `enlace_nombre` VARCHAR(150) NULL,
  `enlace_telefono` VARCHAR(20) NULL,
  `activa` BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT `pk_instituciones_colegio` PRIMARY KEY (`id`),
  CONSTRAINT `uq_instituciones_codigo_dane` UNIQUE (`codigo_dane`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX `idx_institucion_dane` ON `instituciones_institucioneducativa` (`codigo_dane`);
CREATE INDEX `idx_institucion_municipio` ON `instituciones_institucioneducativa` (`municipio`);

-- ==============================================================================
-- 5. TABLA: academico_programa
-- ==============================================================================
DROP TABLE IF EXISTS `academico_programa`;
CREATE TABLE `academico_programa` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `codigo_programa` VARCHAR(20) NOT NULL,
  `denominacion` VARCHAR(200) NOT NULL,
  `version` VARCHAR(10) NOT NULL DEFAULT '1',
  `activo` BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT `pk_academico_programa` PRIMARY KEY (`id`),
  CONSTRAINT `uq_academico_programa_codigo` UNIQUE (`codigo_programa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 6. TABLA: academico_competencia
-- ==============================================================================
DROP TABLE IF EXISTS `academico_competencia`;
CREATE TABLE `academico_competencia` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `programa_id` INT NOT NULL,
  `codigo` VARCHAR(20) NOT NULL,
  `descripcion` TEXT NOT NULL,
  CONSTRAINT `pk_academico_competencia` PRIMARY KEY (`id`),
  CONSTRAINT `fk_competencia_programa` FOREIGN KEY (`programa_id`) 
      REFERENCES `academico_programa` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 7. TABLA: academico_resultadoaprendizaje
-- ==============================================================================
DROP TABLE IF EXISTS `academico_resultadoaprendizaje`;
CREATE TABLE `academico_resultadoaprendizaje` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `competencia_id` INT NOT NULL,
  `codigo` VARCHAR(20) NOT NULL,
  `descripcion` TEXT NOT NULL,
  CONSTRAINT `pk_academico_resultado` PRIMARY KEY (`id`),
  CONSTRAINT `fk_resultado_competencia` FOREIGN KEY (`competencia_id`) 
      REFERENCES `academico_competencia` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 8. TABLA: academico_ficha
-- ==============================================================================
DROP TABLE IF EXISTS `academico_ficha`;
CREATE TABLE `academico_ficha` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `codigo_ficha` VARCHAR(20) NOT NULL,
  `programa_id` INT NOT NULL,
  `institucion_id` INT NOT NULL,
  `instructor_lider_id` INT NOT NULL,
  `fecha_inicio` DATE NOT NULL,
  `fecha_fin` DATE NOT NULL,
  `estado` VARCHAR(20) NOT NULL DEFAULT 'En Ejecucion',
  `periodo_cerrado` BOOLEAN NOT NULL DEFAULT FALSE,
  CONSTRAINT `pk_academico_ficha` PRIMARY KEY (`id`),
  CONSTRAINT `uq_academico_ficha_codigo` UNIQUE (`codigo_ficha`),
  CONSTRAINT `fk_ficha_programa` FOREIGN KEY (`programa_id`) 
      REFERENCES `academico_programa` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_ficha_institucion` FOREIGN KEY (`institucion_id`) 
      REFERENCES `instituciones_institucioneducativa` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_ficha_instructor` FOREIGN KEY (`instructor_lider_id`) 
      REFERENCES `usuarios_usuario` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX `idx_ficha_codigo` ON `academico_ficha` (`codigo_ficha`);

-- ==============================================================================
-- 9. TABLA: academico_matricula
-- ==============================================================================
DROP TABLE IF EXISTS `academico_matricula`;
CREATE TABLE `academico_matricula` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `ficha_id` INT NOT NULL,
  `aprendiz_id` INT NOT NULL,
  `fecha_matricula` DATE NOT NULL,
  `grado_escolar` VARCHAR(5) NOT NULL,
  `estado_formacion` VARCHAR(25) NOT NULL DEFAULT 'En Formacion',
  `acudiente_nombre` VARCHAR(150) NULL,
  `acudiente_telefono` VARCHAR(20) NULL,
  CONSTRAINT `pk_academico_matricula` PRIMARY KEY (`id`),
  CONSTRAINT `uq_matricula_ficha_aprendiz` UNIQUE (`ficha_id`, `aprendiz_id`),
  CONSTRAINT `fk_matricula_ficha` FOREIGN KEY (`ficha_id`) 
      REFERENCES `academico_ficha` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_matricula_aprendiz` FOREIGN KEY (`aprendiz_id`) 
      REFERENCES `usuarios_usuario` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 10. TABLA: seguimiento_bitacora
-- ==============================================================================
DROP TABLE IF EXISTS `seguimiento_bitacora`;
CREATE TABLE `seguimiento_bitacora` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `ficha_id` INT NOT NULL,
  `matricula_id` INT NULL,
  `instructor_id` INT NOT NULL,
  `fecha_visita` DATE NOT NULL,
  `tipo_seguimiento` VARCHAR(30) NOT NULL DEFAULT 'Presencial Aula',
  `observaciones` TEXT NOT NULL,
  `compromisos` TEXT NULL,
  `fecha_verificacion` DATE NULL,
  `archivo_adjunto_url` VARCHAR(255) NULL,
  `fecha_registro` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `pk_seguimiento_bitacora` PRIMARY KEY (`id`),
  CONSTRAINT `fk_bitacora_ficha` FOREIGN KEY (`ficha_id`) 
      REFERENCES `academico_ficha` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_bitacora_matricula` FOREIGN KEY (`matricula_id`) 
      REFERENCES `academico_matricula` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_bitacora_instructor` FOREIGN KEY (`instructor_id`) 
      REFERENCES `usuarios_usuario` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 11. TABLA: evaluaciones_juicioevaluativo
-- ==============================================================================
DROP TABLE IF EXISTS `evaluaciones_juicioevaluativo`;
CREATE TABLE `evaluaciones_juicioevaluativo` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `matricula_id` INT NOT NULL,
  `resultado_aprendizaje_id` INT NOT NULL,
  `instructor_id` INT NOT NULL,
  `juicio_valor` CHAR(1) NOT NULL,
  `observaciones` TEXT NULL,
  `fecha_evaluacion` DATE NOT NULL,
  `fecha_registro` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `pk_evaluaciones_juicio` PRIMARY KEY (`id`),
  CONSTRAINT `uq_juicio_matricula_resultado` UNIQUE (`matricula_id`, `resultado_aprendizaje_id`),
  CONSTRAINT `chk_juicio_valor` CHECK (`juicio_valor` IN ('A', 'D')),
  CONSTRAINT `fk_juicio_matricula` FOREIGN KEY (`matricula_id`) 
      REFERENCES `academico_matricula` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_juicio_resultado` FOREIGN KEY (`resultado_aprendizaje_id`) 
      REFERENCES `academico_resultadoaprendizaje` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_juicio_instructor` FOREIGN KEY (`instructor_id`) 
      REFERENCES `usuarios_usuario` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==============================================================================
-- 12. TABLA: auditoria_registroauditoria
-- ==============================================================================
DROP TABLE IF EXISTS `auditoria_registroauditoria`;
CREATE TABLE `auditoria_registroauditoria` (
  `id` INT AUTO_INCREMENT NOT NULL,
  `usuario_id` INT NULL,
  `accion` VARCHAR(20) NOT NULL,
  `tabla_afectada` VARCHAR(50) NOT NULL,
  `registro_id` VARCHAR(50) NULL,
  `ip_origen` VARCHAR(45) NULL,
  `fecha_hora` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `detalle_cambio` TEXT NULL,
  CONSTRAINT `pk_auditoria_registro` PRIMARY KEY (`id`),
  CONSTRAINT `fk_auditoria_usuario` FOREIGN KEY (`usuario_id`) 
      REFERENCES `usuarios_usuario` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reactivar chequeo de llaves foráneas
SET FOREIGN_KEY_CHECKS = 1;

-- ==============================================================================
-- FIN DEL SCRIPT DDL INICIAL DE BASE DE DATOS SINETEC
-- ==============================================================================
