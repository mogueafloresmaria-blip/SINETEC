# DICCIONARIO DE DATOS MAESTRO
### SISTEMA SINETEC – PROYECTO FORMATIVO ADSI
**Centro de Logística y Promoción Ecoturística del Magdalena**

---

## 1. INTRODUCCIÓN PEDAGÓGICA AL DICCIONARIO DE DATOS

### ¿Qué es un Diccionario de Datos?
Es un catálogo técnico detallado que describe formalmente cada una de las tablas, columnas, tipos de datos, longitudes y restricciones que componen la base de datos de nuestro sistema.

### ¿Para qué sirve y por qué lo necesitamos?
1. **Es el plano de construcción:** Indica con exactitud matemática qué tipo de valor acepta cada campo (números enteros, fechas, cadenas de texto, valores lógicos de verdadero/falso).
2. **Evita la corrupción de datos:** Define qué campos son obligatorios (`NOT NULL`) y cuáles son opcionales (`NULL`), evitando que se guarden registros incompletos.
3. **Es un entregable obligatorio de ADSI:** Los instructores del SENA y los auditores de software lo evalúan para verificar la calidad de la arquitectura de persistencia.

---

## 2. ESPECIFICACIÓN DETALLADA TABLA POR TABLA `[PROPUESTA]`

### TABLA 1: `usuarios_rol`
* **Descripción Funcional:** Almacena los perfiles o roles de seguridad que determinan las pantallas y permisos autorizados dentro de SINETEC.

| Campo | Descripción | Tipo de Dato | Tamaño | ¿Nulo? | PK | FK | Valores / Restricciones | Observaciones |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `id` | Identificador único del rol | `INT` | 11 | NO | SÍ | NO | `AUTO_INCREMENT` | Llave primaria artificial |
| `nombre` | Nombre formal del rol | `VARCHAR` | 50 | NO | NO | NO | Único (`UNIQUE`) | Ej: 'Administrador', 'Coordinador', 'Instructor' |
| `descripcion` | Detalle de funciones | `VARCHAR` | 255 | SÍ | NO | NO | Texto libre | Descripción de alcance del rol |

---

### TABLA 2: `usuarios_usuario`
* **Descripción Funcional:** Almacena los datos personales y credenciales de acceso de los usuarios del sistema (coordinadores, instructores, administradores, aprendices).

| Campo | Descripción | Tipo de Dato | Tamaño | ¿Nulo? | PK | FK | Valores / Restricciones | Observaciones |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `id` | Identificador único del usuario | `INT` | 11 | NO | SÍ | NO | `AUTO_INCREMENT` | Llave primaria |
| `rol_id` | Rol asignado al usuario | `INT` | 11 | NO | NO | SÍ | Referencia a `usuarios_rol(id)` | Llave foránea |
| `tipo_documento` | Tipo de documento de identidad | `VARCHAR` | 5 | NO | NO | NO | 'CC', 'TI', 'CE', 'PEP', 'PPT' | Sigla oficial nacional |
| `numero_documento` | Número de identificación | `VARCHAR` | 20 | NO | NO | NO | Único (`UNIQUE`) | RN-001: Unicidad |
| `nombres` | Nombres del usuario | `VARCHAR` | 100 | NO | NO | NO | Texto | 1FN: separado de apellidos |
| `apellidos` | Apellidos del usuario | `VARCHAR` | 100 | NO | NO | NO | Texto | 1FN: separado de nombres |
| `correo` | Correo electrónico de acceso | `VARCHAR` | 150 | NO | NO | NO | Formato email / Único | Usado para login |
| `password_hash` | Contraseña cifrada | `VARCHAR` | 255 | NO | NO | NO | Hash PBKDF2/SHA-256 | RNF-001: Nunca en texto plano |
| `telefono` | Teléfono móvil o fijo | `VARCHAR` | 20 | SÍ | NO | NO | Solo dígitos o formato | Opcional |
| `esta_activo` | Estado de acceso a la cuenta | `BOOLEAN` | 1 | NO | NO | NO | `DEFAULT TRUE` | RN-008: Borrado lógico |
| `fecha_creacion` | Marca de tiempo de registro | `DATETIME` | - | NO | NO | NO | `CURRENT_TIMESTAMP` | Trazabilidad temporal |

---

### TABLA 3: `instituciones_institucioneducativa`
* **Descripción Funcional:** Registra las Instituciones Educativas (I.E.) del Magdalena que mantienen convenio de articulación técnica con el Centro.

| Campo | Descripción | Tipo de Dato | Tamaño | ¿Nulo? | PK | FK | Valores / Restricciones | Observaciones |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `id` | Identificador de la institución | `INT` | 11 | NO | SÍ | NO | `AUTO_INCREMENT` | Llave primaria |
| `codigo_dane` | Código DANE oficial del colegio | `VARCHAR` | 20 | NO | NO | NO | Único (`UNIQUE`) | Identificador del MEN |
| `nombre` | Nombre oficial de la I.E. | `VARCHAR` | 200 | NO | NO | NO | Texto | Nombre completo |
| `municipio` | Municipio del Magdalena | `VARCHAR` | 100 | NO | NO | NO | Texto | Ej: Santa Marta, Ciénaga |
| `direccion` | Dirección física de la sede | `VARCHAR` | 255 | SÍ | NO | NO | Texto libre | Ubicación física |
| `telefono` | Teléfono de contacto | `VARCHAR` | 20 | SÍ | NO | NO | Texto | Línea fija o celular |
| `rector_nombre` | Nombre completo del rector(a) | `VARCHAR` | 150 | SÍ | NO | NO | Texto | Representante legal |
| `enlace_nombre` | Nombre del docente enlace | `VARCHAR` | 150 | SÍ | NO | NO | Texto | Coordinador pedagógico |
| `enlace_telefono` | Teléfono del docente enlace | `VARCHAR` | 20 | SÍ | NO | NO | Texto | Contacto directo |
| `activa` | Estado del convenio | `BOOLEAN` | 1 | NO | NO | NO | `DEFAULT TRUE` | Vigencia de la I.E. |

---

### TABLA 4: `academico_programa`
* **Descripción Funcional:** Catálogo de programas técnicos de formación ofrecidos por el Centro en articulación con la Media Técnica.

| Campo | Descripción | Tipo de Dato | Tamaño | ¿Nulo? | PK | FK | Valores / Restricciones | Observaciones |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `id` | Identificador del programa | `INT` | 11 | NO | SÍ | NO | `AUTO_INCREMENT` | Llave primaria |
| `codigo_programa` | Código curricular del SENA | `VARCHAR` | 20 | NO | NO | NO | Único (`UNIQUE`) | Código oficial en SOFIA Plus |
| `denominacion` | Nombre del programa técnico | `VARCHAR` | 200 | NO | NO | NO | Texto | Ej: 'Técnico en Sistemas' |
| `version` | Versión curricular | `VARCHAR` | 10 | NO | NO | NO | Texto | Ej: '1', '102' |
| `activo` | Disponibilidad curricular | `BOOLEAN` | 1 | NO | NO | NO | `DEFAULT TRUE` | Estado del diseño |

---

### TABLA 5: `academico_competencia`
* **Descripción Funcional:** Competencias laborales que integran la estructura curricular de cada programa de formación.

| Campo | Descripción | Tipo de Dato | Tamaño | ¿Nulo? | PK | FK | Valores / Restricciones | Observaciones |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `id` | Identificador de competencia | `INT` | 11 | NO | SÍ | NO | `AUTO_INCREMENT` | Llave primaria |
| `programa_id` | Programa al que pertenece | `INT` | 11 | NO | NO | SÍ | Referencia a `academico_programa(id)` | Llave foránea |
| `codigo` | Código oficial de norma | `VARCHAR` | 20 | NO | NO | NO | Texto | Código de la norma |
| `descripcion` | Texto descriptivo de competencia| `TEXT` | - | NO | NO | NO | Texto largo | Descripción oficial |

---

### TABLA 6: `academico_resultadoaprendizaje`
* **Descripción Funcional:** Resultados de Aprendizaje (RAP) que componen cada competencia y representan los logros a evaluar.

| Campo | Descripción | Tipo de Dato | Tamaño | ¿Nulo? | PK | FK | Valores / Restricciones | Observaciones |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `id` | Identificador del resultado | `INT` | 11 | NO | SÍ | NO | `AUTO_INCREMENT` | Llave primaria |
| `competencia_id`| Competencia a la que pertenece| `INT` | 11 | NO | NO | SÍ | Referencia a `academico_competencia(id)`| Llave foránea |
| `codigo` | Código secuencial o del RAP | `VARCHAR` | 20 | NO | NO | NO | Texto | Ej: 'RAP-01' |
| `descripcion` | Texto descriptivo del resultado | `TEXT` | - | NO | NO | NO | Texto largo | Criterio de logro |

---

### TABLA 7: `academico_ficha`
* **Descripción Funcional:** Grupos o cohortes de formación técnica asociados a un colegio y guiados por un instructor líder del Centro.

| Campo | Descripción | Tipo de Dato | Tamaño | ¿Nulo? | PK | FK | Valores / Restricciones | Observaciones |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `id` | Identificador de la ficha | `INT` | 11 | NO | SÍ | NO | `AUTO_INCREMENT` | Llave primaria |
| `codigo_ficha` | Número oficial de ficha | `VARCHAR` | 20 | NO | NO | NO | Único (`UNIQUE`) | Número asignado |
| `programa_id` | Programa técnico cursado | `INT` | 11 | NO | NO | SÍ | Referencia a `academico_programa(id)` | Llave foránea |
| `institucion_id`| Colegio donde opera la ficha | `INT` | 11 | NO | NO | SÍ | Referencia a `instituciones...(id)` | Llave foránea |
| `instructor_lider_id`| Instructor asignado | `INT` | 11 | NO | NO | SÍ | Referencia a `usuarios_usuario(id)` | RN-005: Responsable |
| `fecha_inicio` | Fecha de inicio lectivo | `DATE` | - | NO | NO | NO | Formato YYYY-MM-DD | Apertura de formación |
| `fecha_fin` | Fecha estimada de cierre | `DATE` | - | NO | NO | NO | Formato YYYY-MM-DD | Culminación de etapa |
| `estado` | Estado administrativo | `VARCHAR` | 20 | NO | NO | NO | 'En Ejecución', 'Terminada' | Ciclo de vida |
| `periodo_cerrado`| Indicador de cierre formal | `BOOLEAN` | 1 | NO | NO | NO | `DEFAULT FALSE` | RN-004: Inmutabilidad |

---

### TABLA 8: `academico_matricula`
* **Descripción Funcional:** Registro de vinculación de un estudiante/aprendiz a una ficha técnica, grado escolar y estado académico.

| Campo | Descripción | Tipo de Dato | Tamaño | ¿Nulo? | PK | FK | Valores / Restricciones | Observaciones |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `id` | Identificador de matrícula | `INT` | 11 | NO | SÍ | NO | `AUTO_INCREMENT` | Llave primaria |
| `ficha_id` | Ficha técnica asignada | `INT` | 11 | NO | NO | SÍ | Referencia a `academico_ficha(id)` | Llave foránea |
| `aprendiz_id` | Usuario en rol de aprendiz | `INT` | 11 | NO | NO | SÍ | Referencia a `usuarios_usuario(id)` | RN-002: Vinculación |
| `fecha_matricula`| Fecha del registro | `DATE` | - | NO | NO | NO | Formato YYYY-MM-DD | Asiento inicial |
| `grado_escolar` | Grado que cursa en el colegio | `VARCHAR` | 5 | NO | NO | NO | '10', '11' | RN-007: Media Técnica |
| `estado_formacion`| Estado del aprendiz | `VARCHAR` | 25 | NO | NO | NO | 'En Formación', 'Desertado', 'Retirado', 'Certificado' | RF-007: Novedades |
| `acudiente_nombre`| Nombre del padre o acudiente | `VARCHAR` | 150 | SÍ | NO | NO | Texto libre | Contacto familiar |
| `acudiente_telefono`| Teléfono del acudiente | `VARCHAR` | 20 | SÍ | NO | NO | Texto | Contacto emergencias |

---

### TABLA 9: `seguimiento_bitacora`
* **Descripción Funcional:** Registros cronológicos de visitas de seguimiento, observaciones técnicas y actas de compromiso.

| Campo | Descripción | Tipo de Dato | Tamaño | ¿Nulo? | PK | FK | Valores / Restricciones | Observaciones |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `id` | Identificador de la bitácora | `INT` | 11 | NO | SÍ | NO | `AUTO_INCREMENT` | Llave primaria |
| `ficha_id` | Ficha objeto de seguimiento | `INT` | 11 | NO | NO | SÍ | Referencia a `academico_ficha(id)` | Llave foránea obligatoria |
| `matricula_id` | Aprendiz específico (opcional) | `INT` | 11 | SÍ | NO | SÍ | Referencia a `academico_matricula(id)`| NULL si es grupal |
| `instructor_id`| Instructor que realizó visita | `INT` | 11 | NO | NO | SÍ | Referencia a `usuarios_usuario(id)` | Autor inmutable |
| `fecha_visita` | Fecha de la sesión/visita | `DATE` | - | NO | NO | NO | Formato YYYY-MM-DD | Fecha presencial |
| `tipo_seguimiento`| Modalidad del seguimiento | `VARCHAR` | 30 | NO | NO | NO | 'Presencial Aula', 'Virtual', 'Revisión Taller' | Clasificación |
| `observaciones`| Diagnóstico pedagógico | `TEXT` | - | NO | NO | NO | Texto libre | Hallazgos |
| `compromisos` | Tareas y acuerdos de mejora | `TEXT` | - | SÍ | NO | NO | Obligatorio si hay bajo rendimiento | RN-006: Regla condicional |
| `fecha_verificacion`| Plazo para revisar compromisos| `DATE` | - | SÍ | NO | NO | Formato YYYY-MM-DD | Plazo de mejora |
| `archivo_adjunto_url`| Ruta de acta escaneada o soporte| `VARCHAR` | 255 | SÍ | NO | NO | Ruta en disco / media | PDF o imagen de evidencia |
| `fecha_registro`| Marca de tiempo del sistema | `DATETIME` | - | NO | NO | NO | `CURRENT_TIMESTAMP` | Trazabilidad del registro |

---

### TABLA 10: `evaluaciones_juicioevaluativo`
* **Descripción Funcional:** Almacena los juicios evaluativos cualitativos oficiales para los resultados de aprendizaje.

| Campo | Descripción | Tipo de Dato | Tamaño | ¿Nulo? | PK | FK | Valores / Restricciones | Observaciones |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `id` | Identificador del juicio | `INT` | 11 | NO | SÍ | NO | `AUTO_INCREMENT` | Llave primaria |
| `matricula_id` | Aprendiz matriculado | `INT` | 11 | NO | NO | SÍ | Referencia a `academico_matricula(id)`| Llave foránea |
| `resultado_aprendizaje_id`| RAP calificado | `INT` | 11 | NO | NO | SÍ | Referencia a `academico_resultado...(id)`| Llave foránea |
| `instructor_id`| Instructor evaluador | `INT` | 11 | NO | NO | SÍ | Referencia a `usuarios_usuario(id)` | Responsable de nota |
| `juicio_valor` | Juicio cualitativo oficial | `CHAR` | 1 | NO | NO | NO | 'A' (Aprobado), 'D' (No Aprobado) | RN-003: Escala oficial |
| `observaciones`| Retroalimentación pedagógica | `TEXT` | - | SÍ | NO | NO | Justificación del juicio | Opcional si aprobó |
| `fecha_evaluacion`| Fecha de asignación | `DATE` | - | NO | NO | NO | Formato YYYY-MM-DD | Fecha del juicio |
| `fecha_registro`| Marca de tiempo inmutable | `DATETIME` | - | NO | NO | NO | `CURRENT_TIMESTAMP` | Auditoría de registro |

---

### TABLA 11: `auditoria_registroauditoria`
* **Descripción Funcional:** Registra las operaciones críticas realizadas en la base de datos para trazabilidad y seguridad institucional.

| Campo | Descripción | Tipo de Dato | Tamaño | ¿Nulo? | PK | FK | Valores / Restricciones | Observaciones |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `id` | Identificador del log | `INT` | 11 | NO | SÍ | NO | `AUTO_INCREMENT` | Llave primaria |
| `usuario_id` | Usuario que ejecutó la acción | `INT` | 11 | SÍ | NO | SÍ | Referencia a `usuarios_usuario(id)` | NULL si es anónimo |
| `accion` | Tipo de operación HTTP/SQL | `VARCHAR` | 20 | NO | NO | NO | 'INSERT', 'UPDATE', 'DELETE', 'LOGIN' | Tipo de evento |
| `tabla_afectada`| Nombre de la tabla modificada| `VARCHAR` | 50 | NO | NO | NO | Texto | Ej: 'juicioevaluativo' |
| `registro_id` | ID del registro intervenido | `VARCHAR` | 50 | SÍ | NO | NO | Texto | Identificador afectado |
| `ip_origen` | Dirección IP del cliente | `VARCHAR` | 45 | SÍ | NO | NO | Formato IPv4 o IPv6 | RNF-002: Trazabilidad |
| `fecha_hora` | Marca de tiempo exacta | `DATETIME` | - | NO | NO | NO | `CURRENT_TIMESTAMP` | Hora del servidor |
| `detalle_cambio`| Registro anterior vs nuevo | `TEXT` | - | SÍ | NO | NO | Formato JSON o texto | Pista de auditoría |

---

## 3. APORTE A LOS RESULTADOS DE APRENDIZAJE SENA
*Esta actividad contribuye al resultado de aprendizaje relacionado con **construir el diccionario de datos de acuerdo con los estándares de la organización y el modelo de datos**, porque define detalladamente los tipos, tamaños, restricciones y propósitos de cada campo de información antes de la creación física de la base de datos.*
