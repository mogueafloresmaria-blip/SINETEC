# HISTORIAS DE USUARIO (HU)
### METODOLOGÍA ÁGIL – PROYECTO SINETEC
**Centro de Logística y Promoción Ecoturística del Magdalena**

---

## 1. ESTRUCTURA DE ESPECIFICACIÓN
Cada historia de usuario representa un incremento funcional de valor para el usuario final y sigue la estructura:
* **Narrativa:** *Como [Actor], quiero [Funcionalidad], para [Beneficio o Valor aportado].*
* **Criterios de Aceptación:** Estructurados bajo la sintaxis estándar de comportamiento esperado:
  * **Dado que** (Contexto / Precondición)
  * **Cuando** (Acción del usuario o evento)
  * **Entonces** (Resultado verificable en el sistema)

---

## 2. CATÁLOGO DE HISTORIAS DE USUARIO `[PROPUESTA]`

### HU-001: Autenticación Segura en la Plataforma
* **ID:** HU-001
* **Actor:** Todos los roles (Usuario del sistema).
* **Módulo:** MOD-01 Autenticación y Perfil.
* **Requerimiento Relacionado:** RF-001
* **Historia:**  
  *Como usuario de SINETEC,*  
  *quiero ingresar con mi documento/correo y contraseña cifrada,*  
  *para acceder a las herramientas y funciones autorizadas de acuerdo con mi rol institucional.*
* **Criterios de Aceptación:**
  * **Criterio 1:**  
    *Dado que* el usuario tiene una cuenta registrada y activa,  
    *cuando* digita su correo y contraseña correcta y presiona "Ingresar",  
    *entonces* el sistema le permite el acceso y lo redirige a su panel principal según su rol.
  * **Criterio 2:**  
    *Dado que* el usuario ingresa una contraseña errónea,  
    *cuando* envía el formulario,  
    *entonces* el sistema muestra el mensaje *"Credenciales no válidas"* y no inicia sesión.
  * **Criterio 3:**  
    *Dado que* un usuario acumula 5 intentos fallidos consecutivos,  
    *cuando* intenta ingresar por sexta vez,  
    *entonces* el sistema bloquea temporalmente el inicio de sesión durante 15 minutos.
* **Prioridad:** Alta | **Dependencias:** Ninguna | **Estado:** `[PROPUESTA]`

---

### HU-002: Registro y Consulta de Colegios Articulados
* **ID:** HU-002
* **Actor:** Coordinador de Articulación.
* **Módulo:** MOD-03 Instituciones Educativas.
* **Requerimiento Relacionado:** RF-003
* **Historia:**  
  *Como Coordinador de Articulación con la Media Técnica,*  
  *quiero registrar y consultar las Instituciones Educativas en convenio con sus datos de contacto y rector,*  
  *para mantener el directorio oficial de colegios articulados en el Magdalena.*
* **Criterios de Aceptación:**
  * **Criterio 1:**  
    *Dado que* el coordinador cuenta con los datos de un nuevo colegio en convenio,  
    *cuando* ingresa código DANE, nombre, municipio, dirección, rector y docente enlace y guarda,  
    *entonces* el colegio queda almacenado y aparece en el listado de instituciones activas.
  * **Criterio 2:**  
    *Dado que* se intenta registrar un colegio con un código DANE ya existente,  
    *cuando* se envía el formulario,  
    *entonces* el sistema rechaza el guardado informando *"El código DANE ya se encuentra registrado"*.
* **Prioridad:** Alta | **Dependencias:** HU-001 | **Estado:** `[PROPUESTA]`

---

### HU-003: Matrícula de Aprendices en Ficha de Media Técnica
* **ID:** HU-003
* **Actor:** Instructor SENA / Coordinador.
* **Módulo:** MOD-06 Aprendices.
* **Requerimiento Relacionado:** RF-006, RN-001, RN-002
* **Historia:**  
  *Como Instructor o Coordinador,*  
  *quiero matricular los datos personales de los estudiantes de grado 10° u 11° en su ficha técnica correspondiente,*  
  *para asociarlos a las competencias y habilitar su posterior seguimiento y evaluación.*
* **Criterios de Aceptación:**
  * **Criterio 1:**  
    *Dado que* una ficha técnica está activa,  
    *cuando* se registran los datos completos del estudiante (documento, nombres, apellidos, teléfono, acudiente) y se guarda,  
    *entonces* el estudiante aparece como aprendiz en estado "En Formación" dentro de la ficha.
  * **Criterio 2:**  
    *Dado que* un número de documento ya pertenece a otro aprendiz activo,  
    *cuando* se intenta matricular nuevamente,  
    *entonces* el sistema alerta sobre la duplicidad y detiene la operación.
* **Prioridad:** Alta | **Dependencias:** HU-002 | **Estado:** `[PROPUESTA]`

---

### HU-004: Registro de Bitácora de Seguimiento y Visitas Técnicas
* **ID:** HU-004
* **Actor:** Instructor SENA / Encargado de Seguimiento.
* **Módulo:** MOD-07 Seguimiento Técnico.
* **Requerimiento Relacionado:** RF-008, RN-005, RN-006
* **Historia:**  
  *Como Instructor SENA,*  
  *quiero registrar la bitácora de visita a la institución con las observaciones del grupo y compromisos adquiridos,*  
  *para dejar evidencia y trazabilidad del acompañamiento pedagógico y técnico brindado.*
* **Criterios de Aceptación:**
  * **Criterio 1:**  
    *Dado que* el instructor tiene asignada la ficha técnica,  
    *cuando* ingresa la fecha, tipo de seguimiento, observaciones técnicas y presiona "Guardar Seguimiento",  
    *entonces* el registro se almacena con la fecha del sistema y el nombre inmutable del instructor.
  * **Criterio 2:**  
    *Dado que* el instructor indica novedades de bajo rendimiento en el seguimiento,  
    *cuando* intenta guardar sin diligenciar el campo de compromisos,  
    *entonces* el sistema resalta el campo obligatorio conforme a la regla RN-006.
* **Prioridad:** Alta | **Dependencias:** HU-003 | **Estado:** `[PROPUESTA]`

---

### HU-005: Calificación de Resultados de Aprendizaje
* **ID:** HU-005
* **Actor:** Instructor SENA.
* **Módulo:** MOD-08 Evaluaciones.
* **Requerimiento Relacionado:** RF-009, RN-003, RN-004
* **Historia:**  
  *Como Instructor SENA,*  
  *quiero registrar los juicios evaluativos (Aprobado / No Aprobado) para cada resultado de aprendizaje de mi ficha,*  
  *para consolidar el rendimiento académico de los aprendices en el Centro.*
* **Criterios de Aceptación:**
  * **Criterio 1:**  
    *Dado que* el periodo evaluativo está abierto y la ficha asignada,  
    *cuando* el instructor selecciona un resultado de aprendizaje y califica con 'A' o 'D' a los aprendices,  
    *entonces* los juicios se actualizan y reflejan inmediatamente en la sábana de notas.
  * **Criterio 2:**  
    *Dado que* el periodo fue cerrado previamente por la coordinación,  
    *cuando* el instructor intenta modificar una calificación,  
    *entonces* los controles aparecen deshabilitados y el sistema notifica *"El periodo se encuentra cerrado"*.
* **Prioridad:** Alta | **Dependencias:** HU-003 | **Estado:** `[PROPUESTA]`

---

### HU-006: Exportación de Reportes Consolidados en PDF
* **ID:** HU-006
* **Actor:** Coordinador de Articulación / Instructor.
* **Módulo:** MOD-09 Reportes y Exportación.
* **Requerimiento Relacionado:** RF-013, RF-014
* **Historia:**  
  *Como Coordinador o Instructor,*  
  *quiero descargar en formato PDF y Excel los consolidados de evaluación y actas de seguimiento por colegio y ficha,*  
  *para presentar informes oficiales a la dirección del Centro y a los rectores de los colegios.*
* **Criterios de Aceptación:**
  * **Criterio 1:**  
    *Dado que* existen registros de seguimiento o notas cargados,  
    *cuando* el usuario selecciona los filtros deseados y presiona "Descargar Reporte PDF",  
    *entonces* el sistema genera y descarga un archivo PDF estandarizado con el membrete y datos oficiales.
  * **Criterio 2:**  
    *Dado que* no existen registros que coincidan con los filtros seleccionados,  
    *cuando* se solicita la descarga,  
    *entonces* el sistema avisa *"No se encontraron registros para los criterios seleccionados"* sin generar archivos en blanco.
* **Prioridad:** Media | **Dependencias:** HU-004, HU-005 | **Estado:** `[PROPUESTA]`

---

### HU-007: Visualización de Indicadores en Dashboard Central
* **ID:** HU-007
* **Actor:** Coordinador de Articulación / Administrador.
* **Módulo:** MOD-10 Dashboard / Panel de Control.
* **Requerimiento Relacionado:** RF-015
* **Historia:**  
  *Como Coordinador del Centro,*  
  *quiero visualizar tarjetas informativas y gráficas de barras con el porcentaje de aprobación, número de aprendices por municipio y visitas pendientes,*  
  *para tomar decisiones operativas oportunas sobre el proceso de articulación.*
* **Criterios de Aceptación:**
  * **Criterio 1:**  
    *Dado que* el coordinador inicia sesión en SINETEC,  
    *cuando* visualiza su pantalla de inicio,  
    *entonces* observa los totales actualizados de colegios en convenio, aprendices matriculados y tasa de aprobación.
* **Prioridad:** Media | **Dependencias:** HU-002, HU-003, HU-005 | **Estado:** `[PROPUESTA]`

---

## 3. APORTE A LOS RESULTADOS DE APRENDIZAJE SENA
*Esta actividad contribuye al resultado de aprendizaje relacionado con **elaborar historias de usuario basadas en las metodologías ágiles de desarrollo de software**, porque descompone las necesidades del cliente en incrementos verificables con criterios de aceptación claros (Dado/Cuando/Entonces).*
