# MANUAL DE USUARIO — PANEL DEL DOCENTE (EDUNOVA)

## Objetivo
El panel del docente permite gestionar de forma integral, transparente y articulada sus grupos escolares, estudiantes asignados, asignaturas, horarios de clase, control de asistencia, diseño de actividades, revisión y calificación de entregas, comunicaciones institucionales y notificaciones.

El sistema opera estrictamente con datos reales registrados en la base de datos (4 estudiantes oficiales: 2 en Grado 10° y 2 en Grado 11°).

---

## 1. Módulo Inicio
Desde la pantalla principal, el docente accede de forma rápida a:
- **Clase Actual en Curso:** Si existe una clase programada en el horario para el día y hora del sistema, muestra Asignatura, Grupo, Aula, Horario y un botón directo **"Tomar asistencia"**. Si no hay clase en ese momento, muestra el mensaje informativo: *"No tienes clases programadas en este momento"*.
- **Resumen Métrico Real:**
  - Total estudiantes: **4**
  - Grado 10°A: **2 estudiantes** (`est1` Juan Pérez, `est2` María Gómez)
  - Grado 11°A: **2 estudiantes** (`est3` Luis Martínez, `est4` Ana López)
  - Mis Asignaturas: **3** (Matemáticas, Informática, Lengua Castellana)
  - Actividades y entregas pendientes de revisión.
- **Horario de Hoy:** Muestra la lista de clases programadas para el día de la semana actual.

---

## 2. Módulo Mis Estudiantes
Permite consultar la información académica de los estudiantes que pertenecen a los grupos a cargo:
- **Resumen Claro:** Encabezado con totales consolidados (Total: 4 | Grado 10: 2 | Grado 11: 2).
- **Filtro por Grado:** Permite alternar entre Grado 10°, Grado 11° o Ver todos.
- **Ficha y Perfil Académico del Estudiante:** Al hacer clic en un estudiante se despliegan sus 5 pestañas:
  1. *Información:* Documento, correo, acudiente y teléfono.
  2. *Calificaciones:* Registro histórico por periodo lectivo.
  3. *Asistencia:* Historial de sesiones y porcentaje de presencialidad.
  4. *Actividades:* Estado de entrega de tareas y notas recibidas.
  5. *Seguimiento:* Bitácora pedagógica, fortalezas y compromisos acordados.

---

## 3. Módulo Mis Grupos
Ofrece una vista organizada por cursos:
- **Grado 10°A** (2 estudiantes)
- **Grado 11°A** (2 estudiantes)

Desde la tarjeta de cada grupo, el profesor puede ejecutar acciones directas:
- Ver estudiantes.
- Tomar asistencia del grupo.
- Crear actividad académica.
- Consultar y registrar calificaciones.
- Enviar mensaje oficial al grupo completo.

---

## 4. Módulo Mis Asignaturas
Presenta las asignaturas a cargo del docente:
- **Matemáticas** (Grados 10° y 11°)
- **Informática** (Grados 10° y 11°)
- **Lengua Castellana** (Grados 10° y 11°)

La cantidad de estudiantes se calcula automáticamente a partir de las matrículas reales vinculadas.
Al hacer clic en **"Ver detalles"**, el docente accede a:
- Titular de la materia y aula asignada.
- Grados y grupos vinculados.
- Lista completa de estudiantes reales asignados (filtrable por Grado 10° y 11°).
- Actividades publicadas en la asignatura.
- Calificaciones y promedio general.
- Horarios de clase asociados.

---

## 5. Módulo Asistencia
Permite registrar y consultar el control de asistencia diario:
1. Seleccionar el grupo (Grado 10 o Grado 11), la fecha de la sesión y la asignatura.
2. El sistema despliega inmediatamente a los 2 estudiantes del grupo seleccionado.
3. Marcar el estado de cada uno: **Presente (P)**, **Ausente (A)** o **Tardanza (T)**.
4. Agregar observaciones o motivo de justificación si corresponde.
5. Presionar **Guardar Asistencia**. La información queda registrada en la base de datos y se actualiza en el historial de sesiones.

---

## 6. Módulo Actividades / Tareas
Permite diseñar y programar asignaciones escolares:
1. Pulsar **"+ Crear Actividad"**.
2. Ingresar la información básica: Título, Tipo de actividad, Asignatura y Grupo.
3. Definir el destinatario: Todo el grupo o un estudiante individual.
4. Seleccionar la **Guía pedagógica** desde la biblioteca o adjuntar un archivo.
5. Seleccionar el **Resultado de Aprendizaje (RAP)** o competencia a desarrollar.
6. Establecer la fecha y hora límite de entrega, ponderación porcentual e instrucciones.
7. Pulsar **Publicar Inmediatamente**.

---

## 7. Flujo del Estudiante y Entrega
1. El estudiante inicia sesión en su portal y visualiza la notificación de nueva actividad.
2. Abre la actividad, consulta las instrucciones, el Resultado de Aprendizaje y descarga la guía.
3. Redacta su respuesta, adjunta su archivo de trabajo y pulsa **"Enviar Entrega"**.
4. El sistema actualiza el estado a `ENTREGADA` y notifica al docente.

---

## 8. Revisión y Calificación por el Docente
1. El docente ingresa a la actividad desde su panel y consulta la lista de entregas.
2. Identifica quién entregó, quién está pendiente y descarga el trabajo del estudiante.
3. Asigna la calificación numérica (escala 0.0 a 5.0) y redacta la retroalimentación pedagógica.
4. Pulsa **"Guardar Calificación"**.
5. La nota se refleja en la planilla oficial de notas y en el portal del estudiante.

---

## 9. Módulo Calificaciones
Planilla oficial de evaluación por periodo lectivo (Periodo 1 a 4):
- Permite evaluar a los estudiantes por asignatura y grupo.
- Calcula de forma automática el promedio acumulado ponderado.
- Determina el nivel de desempeño cualitativo (Superior, Alto, Básico, Bajo).

---

## 10. Módulo Horario Escolar
Gestión semanal de clases (Lunes a Viernes):
- Permite programar nuevas clases indicando día, hora inicio, hora fin, asignatura, grupo y aula.
- **Control Antricruces:** Bloquea automáticamente cruces de horario para el mismo docente, para el mismo grupo de estudiantes o para la misma aula física.
- Permite editar horarios existentes o eliminarlos enviándolos a la papelera.

---

## 11. Módulo Recursos / Guías Pedagógicas
Biblioteca curricular del docente:
- Permite registrar guías de aprendizaje con título, descripción y archivo adjunto.
- Las guías almacenadas están disponibles para vincularse con un solo clic al crear una nueva tarea.

---

## 12. Módulo Documentos
Repositorio documental:
- Permite cargar y descargar planes de área, circulares, formatos institucionales y guías curriculares.

---

## 13. Módulo Eventos y Calendario
Cronograma escolar:
- Visualiza las fechas límite de entrega de actividades.
- Permite programar reuniones de docentes, comisiones de evaluación y eventos pedagógicos.

---

## 14. Módulo Comunicaciones y Notificaciones
- **Mensajería:** Redactar y enviar comunicados dirigidos a un estudiante, a un acudiente o al grupo completo.
- **Centro de Notificaciones:** Registro automático de alertas del sistema (nuevas tareas, entregas recibidas, calificaciones registradas y mensajes).
