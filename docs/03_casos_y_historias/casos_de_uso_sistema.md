# ESPECIFICACIÓN DE CASOS DE USO DEL SISTEMA (CU)
### MODELADO FUNCIONAL UML – PROYECTO SINETEC
**Centro de Logística y Promoción Ecoturística del Magdalena**

---

## 1. INTRODUCCIÓN AL MODELADO DE CASOS DE USO
Los casos de uso describen la interacción entre los actores (usuarios externos) y el sistema SINETEC para alcanzar un objetivo específico de valor formativo o administrativo.

---

## 2. ESPECIFICACIÓN DETALLADA DE CASOS DE USO `[PROPUESTA]`

### CU-001: Iniciar Sesión en el Sistema
* **ID:** CU-001
* **Nombre:** Autenticar Usuario.
* **Actor Principal:** Usuario (Cualquier actor registrado).
* **Objetivo:** Validar identidad y otorgar acceso a los módulos autorizados según su rol.
* **Precondiciones:** El usuario debe poseer una cuenta activa y credenciales vigentes.
* **Flujo Principal:**
  1. El actor accede a la URL principal de SINETEC.
  2. El sistema despliega el formulario de autenticación.
  3. El actor ingresa su documento o correo y su contraseña.
  4. El actor presiona el botón "Iniciar Sesión".
  5. El sistema verifica la existencia del usuario y valida el hash de la contraseña mediante el algoritmo PBKDF2.
  6. El sistema comprueba que el estado sea "Activo".
  7. El sistema inicia la sesión HTTP, carga los permisos del rol en la sesión y redirige al panel de control correspondiente.
* **Flujos Alternativos:**
  * **FA-1 (Credenciales Incorrectas):** En el paso 5, si los datos no coinciden, el sistema muestra el mensaje *"Usuario o contraseña incorrectos"* y retorna al paso 2.
  * **FA-2 (Usuario Inactivo):** En el paso 6, si la cuenta está desactivada, el sistema informa *"Su cuenta se encuentra inactiva. Contacte a la Coordinación"* y niega el acceso.
* **Excepciones:**
  * **EX-1 (Fallo de Base de Datos):** Si no hay conexión con MySQL, el sistema muestra una página de error amigable `500` solicitando reintentar más tarde.
* **Postcondiciones:** La sesión queda activa y registrada en la pista de auditoría.
* **Requerimientos Relacionados:** RF-001, RNF-001, RNF-002.

---

### CU-002: Registrar Institución Educativa
* **ID:** CU-002
* **Nombre:** Registrar Colegio en Articulación.
* **Actor Principal:** Coordinador / Administrador.
* **Objetivo:** Incorporar una nueva I.E. en el catálogo de convenios activos del Centro.
* **Precondiciones:** Actor autenticado con rol de Coordinador o Administrador.
* **Flujo Principal:**
  1. El actor ingresa al menú "Instituciones Educativas".
  2. Presiona la opción "Registrar Nueva Institución".
  3. El sistema presenta el formulario de captura.
  4. El actor diligencia: Código DANE, Nombre de la I.E., Municipio del Magdalena, Dirección, Teléfono, Correo, Nombre del Rector y Nombre del Docente Enlace.
  5. Presiona "Guardar Institución".
  6. El sistema valida que los campos requeridos no estén vacíos y que el Código DANE no exista en la base de datos.
  7. El sistema almacena la nueva institución con estado "Activo".
  8. Muestra mensaje de éxito: *"Institución educativa registrada exitosamente"* y redirige a la lista general.
* **Flujos Alternativos:**
  * **FA-1 (Código DANE Repetido):** En el paso 6, si el código ya existe, el sistema marca el campo en rojo con la advertencia *"El código DANE ya está registrado"* y solicita corrección.
* **Postcondiciones:** La institución queda disponible para asociarle programas, fichas y aprendices.
* **Requerimientos Relacionados:** RF-003, RN-001.

---

### CU-003: Registrar Matrícula de Aprendices
* **ID:** CU-003
* **Nombre:** Matricular Aprendices en Ficha de Media Técnica.
* **Actor Principal:** Coordinador / Instructor SENA.
* **Objetivo:** Vincular formalmente a los estudiantes a una ficha técnica activa del Centro.
* **Precondiciones:** La ficha técnica y el colegio deben estar previamente creados y activos.
* **Flujo Principal:**
  1. El actor ingresa al módulo de "Fichas" y selecciona la ficha técnica destino.
  2. Presiona la acción "Agregar Aprendiz".
  3. El sistema despliega el formulario de matrícula.
  4. El actor ingresa: Tipo y número de documento, nombres, apellidos, fecha de nacimiento, género, correo, teléfono, grado actual (10° u 11°) y datos del acudiente.
  5. Presiona "Guardar Matrícula".
  6. El sistema valida que el documento no esté registrado en otra ficha activa del mismo periodo (RN-001, RN-002).
  7. El sistema guarda al aprendiz y crea el registro de matrícula en estado "En Formación".
  8. Muestra mensaje de confirmación y actualiza la lista de aprendices de la ficha.
* **Flujos Alternativos:**
  * **FA-1 (Aprendiz ya Registrado):** En el paso 6, si el documento ya existe, el sistema avisa *"El aprendiz con este documento ya se encuentra registrado"* e impide la duplicidad.
* **Postcondiciones:** El estudiante queda habilitado para recibir seguimientos y evaluaciones.
* **Requerimientos Relacionados:** RF-006, RN-001, RN-002, RN-007.

---

### CU-004: Registrar Bitácora de Seguimiento Formativo
* **ID:** CU-004
* **Nombre:** Registrar Seguimiento Técnico a la Formación.
* **Actor Principal:** Instructor SENA / Encargado de Seguimiento.
* **Objetivo:** Dejar constancia formal de las visitas a los colegios, observaciones pedagógicas y acuerdos de mejora.
* **Precondiciones:** El instructor debe tener la ficha asignada formalmente (RN-005).
* **Flujo Principal:**
  1. El instructor ingresa a "Mis Fichas" y selecciona la ficha correspondiente.
  2. Presiona "Nuevo Seguimiento".
  3. El sistema muestra la interfaz de bitácora.
  4. El instructor selecciona si el seguimiento es grupal o a un aprendiz particular.
  5. Ingresa fecha de visita, tema tratado, observaciones técnicas del avance y estado del aula/taller.
  6. Si existen novedades de bajo desempeño, ingresa obligatoriamente los compromisos y fecha de revisión (RN-006).
  7. Puede adjuntar documento soporte o acta firmada escaneada (formato PDF o imagen).
  8. Presiona "Guardar Bitácora".
  9. El sistema valida los datos, sube el adjunto de forma segura y guarda el registro con marca de tiempo y autor inmutable.
  10. Confirma con mensaje: *"Seguimiento registrado con éxito"*.
* **Postcondiciones:** La bitácora queda visible en el historial del aprendiz y de la ficha para la coordinación.
* **Requerimientos Relacionados:** RF-008, RN-005, RN-006.

---

### CU-005: Registrar Juicios Evaluativos
* **ID:** CU-005
* **Nombre:** Calificar Resultados de Aprendizaje.
* **Actor Principal:** Instructor SENA.
* **Objetivo:** Asentar la calificación oficial de los resultados de aprendizaje de la ficha.
* **Precondiciones:** Periodo evaluativo abierto (RN-004) y ficha asignada al instructor (RN-005).
* **Flujo Principal:**
  1. El instructor selecciona su ficha y entra a la sección "Evaluaciones".
  2. Selecciona la competencia y el Resultado de Aprendizaje (RAP) a calificar.
  3. El sistema lista todos los aprendices activos de la ficha en una sábana o tabla editable.
  4. El instructor asigna a cada aprendiz el juicio cualitativo: 'A' (Aprobado) o 'D' (No Aprobado) (RN-003) y notas de retroalimentación.
  5. Presiona "Guardar Calificaciones".
  6. El sistema valida que el periodo continúe abierto.
  7. El sistema almacena los juicios en la base de datos MySQL.
  8. Presenta confirmación: *"Evaluaciones registradas correctamente"*.
* **Flujos Alternativos:**
  * **FA-1 (Periodo Cerrado):** En el paso 6, si la coordinación ya ejecutó el cierre del periodo, el sistema rechaza el guardado informando *"Acción denegada: El periodo se encuentra cerrado formalmente"*.
* **Postcondiciones:** Los juicios quedan asentados y computan para las estadísticas de aprobación de la ficha.
* **Requerimientos Relacionados:** RF-009, RN-003, RN-004, RN-005.

---

### CU-006: Generar Reporte Consolidado en PDF
* **ID:** CU-006
* **Nombre:** Exportar Reporte de Seguimiento o Evaluación.
* **Actor Principal:** Coordinador / Instructor SENA.
* **Objetivo:** Generar un documento formal descargable para archivo físico, firmas o presentación a directivos.
* **Precondiciones:** Existencia de registros evaluativos o de seguimiento para los criterios seleccionados.
* **Flujo Principal:**
  1. El actor ingresa a "Reportes".
  2. Selecciona el tipo de reporte deseado (Ficha Individual de Aprendiz, Sábana de Notas por Ficha o Directorio de Colegios).
  3. Aplica los filtros requeridos (Colegio, Ficha, Rango de Fechas).
  4. Presiona el botón "Generar PDF".
  5. El sistema ejecuta la consulta en la base de datos, compila la plantilla con membrete del Centro y genera el archivo binario PDF.
  6. El navegador inicia la descarga del documento con el nombre formateado (ejemplo: `Reporte_Ficha_2501234_Seguimiento.pdf`).
* **Flujos Alternativos:**
  * **FA-1 (Sin Datos):** Si no hay registros que coincidan con los filtros, el sistema notifica *"No se encontraron registros para generar el reporte"* y detiene la descarga.
* **Postcondiciones:** El usuario obtiene el documento listo para impresión o distribución digital.
* **Requerimientos Relacionados:** RF-013, RF-014.

---

## 3. APORTE A LOS RESULTADOS DE APRENDIZAJE SENA
*Esta actividad contribuye al resultado de aprendizaje relacionado con **modelar las funciones del sistema mediante diagramas y casos de uso UML**, porque describe con minuciosidad la interacción actor-sistema, precondiciones, excepciones y flujos alternos antes de emprender la codificación.*
