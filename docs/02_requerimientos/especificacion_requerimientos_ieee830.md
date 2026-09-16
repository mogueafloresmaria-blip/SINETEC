# ESPECIFICACIÓN DE REQUERIMIENTOS DE SOFTWARE (SRS)
### ESTÁNDAR IEEE 830 – SISTEMA SINETEC
**Centro de Logística y Promoción Ecoturística del Magdalena**

---

## 1. INTRODUCCIÓN

### 1.1 Propósito del Documento
El presente documento define formalmente los requerimientos funcionales y no funcionales del software **SINETEC** (*Sistema de Integración Técnica Education*), correspondiente al proyecto formativo *“SISTEMAS DE INFORMACIÓN Y DESARROLLO DE SOFTWARE EN EL DEPARTAMENTO DEL MAGDALENA”* (ADSI 228106), sirviendo de base contractual y técnica para las fases de diseño, desarrollo y pruebas.

### 1.2 Alcance del Software
SINETEC sistematizará los registros de seguimiento formativo y evaluación de resultados de aprendizaje en los programas de Media Técnica impartidos en los colegios articulados con el Centro de Logística y Promoción Ecoturística del Magdalena.

---

## 2. REQUERIMIENTOS FUNCIONALES (CATÁLOGO DETALLADO) `[PROPUESTA]`

### RF-001: Autenticación y Control de Acceso
* **ID:** RF-001
* **Nombre:** Inicio de Sesión y Control de Acceso por Roles.
* **Descripción:** El sistema debe autenticar al usuario mediante documento/correo y contraseña encriptada, cargando el perfil correspondiente a su rol.
* **Actor:** Todos los roles (Administrador, Coordinador, Instructor, Docente I.E., Encargado Seguimiento, Estudiante).
* **Precondiciones:** El usuario debe estar registrado y en estado "Activo".
* **Flujo Principal:**
  1. El usuario ingresa a la pantalla de login.
  2. Digita sus credenciales y pulsa "Ingresar".
  3. El sistema valida las credenciales y el estado activo.
  4. El sistema inicia la sesión de forma segura y redirige al panel de inicio del rol correspondiente.
* **Flujos Alternativos:**
  * Credenciales inválidas: Se muestra mensaje de error sin revelar si falló el usuario o la clave.
  * Usuario inactivo: Mensaje indicando comunicarse con la coordinación del Centro.
* **Resultado Esperado:** Sesión activa con permisos restringidos a su rol.
* **Criterios de Aceptación:** Bloqueo de sesión temporal tras 5 intentos fallidos consecutivos; expiración de sesión por inactividad.
* **Prioridad:** Alta | **Estado:** `[PROPUESTA]`

---

### RF-002: Gestión de Cuentas de Usuario
* **ID:** RF-002
* **Nombre:** Administración de Usuarios y Asignación de Roles.
* **Descripción:** Permitir al Administrador registrar nuevos usuarios, asignarles roles institucionales, modificar sus datos y activar o desactivar su cuenta.
* **Actor:** Administrador.
* **Precondiciones:** Administrador autenticado.
* **Flujo Principal:**
  1. El administrador ingresa al módulo de usuarios.
  2. Selecciona "Nuevo Usuario" y diligencia: tipo de documento, número, nombres, apellidos, correo institucional, teléfono y rol.
  3. El sistema valida que el documento y correo no se encuentren registrados previamente.
  4. El sistema almacena el registro y genera contraseña temporal para el primer acceso.
* **Flujos Alternativos:** Documento duplicado: El sistema advierte que el usuario ya existe y no permite duplicar el registro.
* **Resultado Esperado:** Usuario creado en la base de datos con permisos asignados.
* **Prioridad:** Alta | **Estado:** `[PROPUESTA]`

---

### RF-003: Gestión de Instituciones Educativas (I.E.)
* **ID:** RF-003
* **Nombre:** Registro y Mantenimiento de Colegios Articulados.
* **Descripción:** Registrar y administrar las Instituciones Educativas que mantienen convenio de articulación con el Centro.
* **Actor:** Administrador, Coordinador.
* **Precondiciones:** Rol administrativo.
* **Flujo Principal:** Registro de código DANE (único), nombre del colegio, municipio del Magdalena, dirección física, teléfono, nombre del rector y docente de enlace.
* **Resultado Esperado:** Colegio registrado y disponible para vincular a fichas y programas.
* **Prioridad:** Alta | **Estado:** `[PROPUESTA]`

---

### RF-004: Gestión de Programas Técnicos y Estructura Curricular
* **ID:** RF-004
* **Nombre:** Parametrización de Programas, Competencias y Resultados de Aprendizaje.
* **Descripción:** Registrar los programas de formación técnica del Centro, sus competencias laborales y los resultados de aprendizaje a evaluar.
* **Actor:** Administrador, Coordinador.
* **Precondiciones:** Rol administrativo.
* **Flujo Principal:** Registro del código de programa, denominación, versión curricular, y desglose de competencias con sus respectivos códigos de resultados de aprendizaje.
* **Resultado Esperado:** Catálogo curricular configurado en el sistema.
* **Prioridad:** Alta | **Estado:** `[PROPUESTA]`

---

### RF-005: Creación y Asignación de Fichas de Media Técnica
* **ID:** RF-005
* **Nombre:** Apertura de Fichas y Asignación de Instructores.
* **Descripción:** Crear fichas técnicas vinculando el programa curricular, la Institución Educativa asociada, el instructor líder responsable y el periodo académico de vigencia.
* **Actor:** Coordinador, Administrador.
* **Precondiciones:** Programa, I.E. e instructor registrados previamente.
* **Flujo Principal:** Seleccionar I.E., programa formativo, digitar número de ficha, seleccionar instructor responsable y fechas de inicio/fin.
* **Resultado Esperado:** Ficha abierta lista para recibir matrícula de aprendices.
* **Prioridad:** Alta | **Estado:** `[PROPUESTA]`

---

### RF-006: Matrícula y Vinculación de Aprendices a Fichas
* **ID:** RF-006
* **Nombre:** Registro de Aprendices de Media Técnica.
* **Descripción:** Registrar aprendices (grado 10° u 11°) y asociarlos a su ficha técnica correspondiente.
* **Actor:** Coordinador, Instructor SENA.
* **Precondiciones:** Ficha creada y activa.
* **Flujo Principal:**
  1. Seleccionar ficha técnica.
  2. Diligenciar tipo y número de documento, nombres, apellidos, género, correo, teléfono, grado escolar y datos del acudiente.
  3. Guardar el registro de matrícula.
* **Flujos Alternativos:** Posibilidad de importación masiva mediante archivo estructurado (Excel / CSV) para agilizar el proceso al inicio del año lectivo.
* **Resultado Esperado:** Aprendices matriculados y listados en la ficha.
* **Prioridad:** Alta | **Estado:** `[PROPUESTA]`

---

### RF-007: Registro de Novedades de Matrícula (Deserción, Traslado, Retiro)
* **ID:** RF-007
* **Nombre:** Control de Novedades y Estados del Aprendiz.
* **Descripción:** Registrar cambios en el estado formativo del aprendiz (En Formación, Desertado, Trasladado, Cancelado, Retiro Voluntario) con su respectiva justificación.
* **Actor:** Coordinador, Instructor SENA.
* **Precondiciones:** Aprendiz previamente matriculado.
* **Flujo Principal:** Seleccionar aprendiz, indicar nuevo estado, fecha de novedad y observación o motivo.
* **Resultado Esperado:** Estado del aprendiz actualizado en el sistema manteniendo el historial de novedades.
* **Prioridad:** Media | **Estado:** `[PROPUESTA]`

---

### RF-008: Registro de Bitácora de Seguimiento Formativo
* **ID:** RF-008
* **Nombre:** Asiento de Seguimiento y Visitas Técnicas.
* **Descripción:** Registrar las bitácoras periódicas de seguimiento a la formación, visitas presenciales a los colegios, compromisos adquiridos y estado de los ambientes de aprendizaje.
* **Actor:** Instructor SENA, Encargado de Seguimiento.
* **Precondiciones:** Ficha asignada al instructor.
* **Flujo Principal:**
  1. Seleccionar ficha y aprendiz o grupo completo.
  2. Ingresar fecha de seguimiento, tipo de visita, descripción técnica del avance y compromisos establecidos.
  3. Adjuntar acta escaneada o soporte digital si aplica.
  4. Guardar registro.
* **Resultado Esperado:** Bitácora almacenada con autor y fecha inmutable.
* **Prioridad:** Alta | **Estado:** `[PROPUESTA]`

---

### RF-009: Registro y Actualización de Juicios Evaluativos
* **ID:** RF-009
* **Nombre:** Calificación de Resultados de Aprendizaje.
* **Descripción:** Registrar el juicio evaluativo cualitativo (Aprobado / No Aprobado) para cada aprendiz respecto a los resultados de aprendizaje de la ficha.
* **Actor:** Instructor SENA.
* **Precondiciones:** Ficha asignada, periodo académico abierto y aprendices activos.
* **Flujo Principal:**
  1. El instructor accede a su ficha y selecciona la competencia y resultado a evaluar.
  2. El sistema despliega la lista de aprendices activos.
  3. El instructor asigna el juicio (A / D) y observaciones formativas.
  4. Confirma el guardado masivo o individual.
* **Resultado Esperado:** Juicios evaluativos guardados en base de datos.
* **Prioridad:** Alta | **Estado:** `[PROPUESTA]`

---

### RF-010: Cierre y Bloqueo de Periodos de Evaluación
* **ID:** RF-010
* **Nombre:** Validación y Cierre Oficial de Periodos.
* **Descripción:** Permitir al Coordinador cerrar oficialmente un corte o periodo evaluativo, bloqueando la edición de notas por parte de los instructores.
* **Actor:** Coordinador.
* **Precondiciones:** Juicios evaluativos registrados.
* **Flujo Principal:** El coordinador revisa la ficha, valida que las notas estén completas y ejecuta la acción "Cerrar Periodo".
* **Resultado Esperado:** El sistema bloquea modificaciones en ese periodo para la ficha seleccionada.
* **Prioridad:** Media | **Estado:** `[PROPUESTA]`

---

### RF-011: Consulta de Estados y Desempeño para Colegios
* **ID:** RF-011
* **Nombre:** Consulta Institucional para Docentes Enlace y Rectores.
* **Descripción:** Permitir a los docentes de las Instituciones Educativas consultar el desempeño, notas y seguimientos exclusivamente de los alumnos de su propio colegio.
* **Actor:** Docente Enlace I.E.
* **Precondiciones:** Docente autenticado y vinculado a su I.E.
* **Resultado Esperado:** Visualización filtrada únicamente de su institución escolar.
* **Prioridad:** Media | **Estado:** `[PROPUESTA]`

---

### RF-012: Consulta Individual para Aprendices
* **ID:** RF-012
* **Nombre:** Consulta de Estado Académico por el Aprendiz.
* **Descripción:** Permitir al aprendiz consultar en línea sus resultados de aprendizaje evaluados, estado de matrícula y observaciones de seguimiento.
* **Actor:** Estudiante de Media Técnica.
* **Precondiciones:** Aprendiz autenticado con sus credenciales.
* **Resultado Esperado:** Vista de solo lectura de su expediente formativo individual.
* **Prioridad:** Baja | **Estado:** `[PROPUESTA]`

---

### RF-013: Generación de Reportes Consolidados en PDF
* **ID:** RF-013
* **Nombre:** Exportación de Actas y Fichas de Seguimiento en PDF.
* **Descripción:** Generar documentos formales en formato PDF con membrete institucional para firmas de actas de seguimiento, fichas individuales y consolidados.
* **Actor:** Coordinador, Instructor SENA.
* **Precondiciones:** Existencia de registros en la ficha o periodo.
* **Resultado Esperado:** Documento PDF descargable con formato estandarizado.
* **Prioridad:** Alta | **Estado:** `[PROPUESTA]`

---

### RF-014: Exportación de Datos a Hojas de Cálculo (Excel)
* **ID:** RF-014
* **Nombre:** Exportación de Tablas de Seguimiento y Notas a Excel.
* **Descripción:** Permitir la descarga de datos tabulares (listados de aprendices, matrices de evaluación) en formato `.xlsx` para procesamiento administrativo.
* **Actor:** Coordinador, Administrador, Instructor.
* **Resultado Esperado:** Archivo Excel generado con filtros y encabezados correctos.
* **Prioridad:** Media | **Estado:** `[PROPUESTA]`

---

### RF-015: Panel de Control (Dashboard) con Indicadores
* **ID:** RF-015
* **Nombre:** Visualización de Métricas y Estadísticas de Articulación.
* **Descripción:** Presentar gráficos y tarjetas informativas con: Total colegios activos, total aprendices por municipio, porcentaje de aprobación y seguimientos realizados vs pendientes.
* **Actor:** Coordinador, Administrador.
* **Resultado Esperado:** Panel gráfico interactivo actualizado en tiempo real.
* **Prioridad:** Media | **Estado:** `[PROPUESTA]`

---

## 3. REQUERIMIENTOS NO FUNCIONALES (RNF) `[PROPUESTA]`

* **RNF-001 (Seguridad - Cifrado):** Toda contraseña debe ser almacenada en la base de datos bajo algoritmos criptográficos unidireccionales seguros (PBKDF2 con SHA-256).
* **RNF-002 (Seguridad - Vulnerabilidades Web):** El sistema debe implementar tokens CSRF en todos los formularios POST, sanitización de entradas para mitigar XSS y consultas mediante ORM parametrizado para evitar Inyección SQL.
* **RNF-003 (Rendimiento):** El tiempo de renderizado de las vistas y procesamiento de peticiones HTTP no debe exceder los 2.0 segundos bajo una concurrencia estimada de 30 usuarios simultáneos en red local o web.
* **RNF-004 (Usabilidad y Accesibilidad):** Interfaz gráfica intuitiva, con contraste adecuado de colores conforme a estándares WCAG 2.1 AA y diseño responsivo para computadores, tablets y celulares.
* **RNF-005 (Mantenibilidad):** Arquitectura modular desacoplada basada en aplicaciones Django, con separación de lógica de negocio, plantillas y persistencia, siguiendo la guía PEP 8.
* **RNF-006 (Integridad Referencial):** La base de datos MySQL debe forzar integridad referencial mediante llaves foráneas e índices en campos de búsqueda recurrente (documento, código DANE, número de ficha).
* **RNF-007 (Disponibilidad):** El sistema debe estar disponible para operaciones el 99% del tiempo durante jornadas laborales académicas.
* **RNF-008 (Compatibilidad):** El sistema debe operar de forma homogénea en los navegadores Google Chrome, Mozilla Firefox, Microsoft Edge y Safari sin requerir plugins adicionales.

---

## 4. APORTE A LOS RESULTADOS DE APRENDIZAJE SENA
*Esta actividad contribuye al resultado de aprendizaje relacionado con **especificar los requisitos del software según las normas y estándares de la industria**, porque estructura formalmente las necesidades bajo el estándar internacional IEEE 830, definiendo prioridades, actores y criterios verificables.*
