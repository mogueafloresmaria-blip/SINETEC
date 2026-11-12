# DOCUMENTO TÉCNICO 2: PREGUNTAS Y RESPUESTAS SOBRE EL CÓDIGO
## SISTEMA DE GESTIÓN ESCOLAR ADMINISTRATIVO EDUNOVA
**Fecha de Inspección y Validación:** 28 de Octubre de 2026

---

### 1. ¿Qué hace EduNova?
**EduNova** (anteriormente SINETEC) es un sistema integral de gestión académica y escolar diseñado para instituciones educativas de educación básica y media técnica. Centraliza el ciclo de vida de la comunidad escolar: matrículas de estudiantes, asignación de carga académica a docentes, distribución de horarios semanales, publicación de contenidos y tareas, entrega y calificación de evidencias con retroalimentación, toma de asistencia con trazabilidad inmutable de correcciones, publicación de circulares oficiales con acuse de recibo y generación de boletines oficiales.

---

### 2. ¿Cómo está organizada su arquitectura?
El proyecto sigue una arquitectura modular en Django con tres aplicaciones nucleares:
- **`usuarios`:** Gestiona el control de acceso, perfiles de los seis roles (Administrador, Rectoría, Secretaría, Docente, Estudiante, Familia), gestión de credenciales, tablero directivo, núcleo familiar y papelera de reciclaje.
- **`academico`:** Modela y gestiona asignaturas (`ProgramaFormacion`), cursos escolares (`Ficha`), matrículas de alumnos (`Matricula`), carga docente (`CargaAcademica`), horarios semanales (`HorarioFicha`), tareas (`TareaClase`), entregas (`EntregaTarea`), temas pedagógicos (`GuiaClase`) y calificaciones por período (`CalificacionEscolar`).
- **`seguimiento`:** Gestiona la toma de asistencia diaria (`AsistenciaAprendiz`), el historial inmutable de correcciones de asistencia (`HistorialCorreccionAsistencia`), las circulares oficiales con acuse de lectura (`ComunicadoEscolar`, `AcuseLecturaCircular`), la auditoría de transacciones (`RegistroAuditoria`) y las solicitudes radicadas ante secretaría (`SolicitudSecretaria`).

---

### 3. ¿Qué hace el componente principal y cómo se comunican las capas?
El componente principal de navegación y autorización es el sistema de control de roles implementado en `usuarios/decorators.py` y `usuarios/views.py`. Cuando un usuario inicia sesión, es autenticado contra la tabla `auth_user` de MySQL. El decorador verifica su rol asignado en `usuarios_perfilusuario` y redirige al panel correspondiente:
- `/dashboard/` para Administrador.
- `/rectoria/` para Rectoría.
- `/secretaria/` para Secretaría.
- `/instructor/` para Docente.
- `/aprendiz/` o `/estudiante/` para Estudiante.
- `/familia/` para Familias y Acudientes.

---

### 4. ¿Qué framework utiliza y qué se deduce de su elección?
Utiliza **Django 5.0.14** sobre **Python 3.13.14**. La elección de Django responde a la necesidad de:
1. **Seguridad robusta por defecto:** Protección contra inyecciones SQL (ORM tipado), ataques CSRF en todos los formularios POST, protección contra Cross-Site Scripting (XSS) y hashing seguro de contraseñas con PBKDF2/SHA256.
2. **Integridad referencial y transaccional:** Soporte nativo para transacciones atómicas (`transaction.atomic()`), fundamental para que la matrícula, la asignación de carga y la calificación sincronicen de manera consistente entre tablas sin inconsistencias.
3. **Escalabilidad y mantenibilidad:** La división en modelos, vistas basadas en funciones con decoradores de rol y plantillas modulares (`base.html`) permite mantener el código ordenado y auditable.

---

### 5. ¿Cómo fluyen los datos desde los formularios hasta la base de datos y las pantallas?
1. **Entrada de datos:** El usuario diligencia un formulario HTML con token `{% csrf_token %}` (por ejemplo, registro de matrícula o calificación de entrega).
2. **Validación en la vista:** La vista en Django recibe el request POST, extrae los parámetros, valida la tipología de datos y permisos del usuario ejecutor, y comprueba reglas de negocio (ej. unicidad de matrícula en el mismo grado/sección o asignación de docentes).
3. **Persistencia ORM:** Se ejecutan operaciones de guardado transaccional en MySQL (`create`, `save`, o `update_or_create`). Si ocurre una modificación sobre registros auditables (como asistencia o matrícula), se genera automáticamente un registro en `HistorialCorreccionAsistencia` o `RegistroAuditoria`.
4. **Respuesta y Render:** La vista emite un mensaje mediante `django.contrib.messages` y redirige al listado o panel correspondiente con HTTP 302, recargando los datos actualizados directamente desde la base de datos.

---

### 6. ¿Cómo se relacionan los seis paneles del sistema?
Los seis paneles comparten una única fuente de verdad relacional:
- **Secretaría** matricula al estudiante en un grado y grupo (`Matricula`).
- **Administrador** asigna al docente la materia de ese grado y grupo (`CargaAcademica`) y define el horario semanal (`HorarioFicha`).
- **Docente** visualiza de inmediato en su lista a los estudiantes matriculados en ese grupo, publica temas y actividades, y califica las entregas.
- **Estudiante** accede a su panel y visualiza las tareas publicadas para su grado, realiza la entrega y consulta la retroalimentación y notas de sus docentes.
- **Familia** consulta el boletín de su estudiante vinculado, comprobando notas y asistencias reales, y confirma acuses de lectura de las circulares emitidas por Secretaría o Rectoría.
- **Rectoría** visualiza en tiempo real las métricas consolidadas de cobertura docente, deserción y aprobaciones generadas por la actividad de los demás cinco paneles.

---

### 7. ¿Cómo funcionan matrícula, asignación académica, asistencia y calificación?
- **Matrícula y Asignación:** Secretaría matricula un estudiante en un grado y sección (por ejemplo, 10°A). El sistema lo vincula a la ficha correspondiente. Si el grupo ya tiene docentes y asignaturas asignadas por Carga Académica, el estudiante queda inmediatamente vinculado a sus clases y horarios.
- **Asistencia y Corrección con Historial:** El docente toma asistencia seleccionando fecha, período y estado (P, T, A, J). Si en una sesión posterior se requiere corregir un registro guardado (por ejemplo, cambiar una inasistencia a justificada o presente), la función `registrar_asistencia_estudiante` detecta el cambio, almacena en `HistorialCorreccionAsistencia` el estado previo, el nuevo estado, la fecha, el usuario docente que corrigió y el motivo, garantizando que el historial original nunca se pierda ni se sobrescriba a ciegas.
- **Entregas y Calificaciones:** Cuando un estudiante envía su tarea, se almacena en `EntregaTarea`. El docente abre la entrega desde el panel de revisión, visualiza el texto y archivo adjunto del estudiante, asigna una calificación de 1.0 a 5.0 y escribe retroalimentación. Esta nota se sincroniza de forma atómica en `CalificacionEscolar`, actualizando el boletín del estudiante y la vista del acudiente en tiempo real.

---

### 8. ¿Qué archivos y componentes son los más importantes del proyecto?
- `sinetec_project/settings.py` y `urls.py`: Configuración global, base de datos MySQL, middleware y enrutamiento central.
- `academico/models.py`: Definición de mallas curriculares, matrículas, horarios, tareas y calificaciones.
- `academico/views.py`: Lógica de asignación de carga académica, creación de horarios y gestión de matrículas.
- `seguimiento/models.py`: Asistencia escolar, auditoría de correcciones, circulares y bitácoras.
- `seguimiento/services.py`: Servicios de cálculo de porcentaje de asistencia según fórmula oficial ponderada y alertas tempranas de inasistencia.
- `usuarios/views.py`: Vistas integrales de los tableros de cada rol (`instructor_dashboard`, `aprendiz_dashboard`, `familia_views`, etc.).
- `templates/base.html`: Plantilla maestra con sidebar unificado, botón de cierre de sesión al pie y estilos EduNova.

---

### 9. ¿Cómo se ejecuta y despliega el proyecto?
- **Inicio en Desarrollo Local:**
  ```powershell
  .\venv\Scripts\activate
  python manage.py runserver 127.0.0.1:8000
  ```
- **Aplicación de Migraciones:**
  ```powershell
  python manage.py migrate
  ```
- **Verificación de Pruebas Automatizadas:**
  ```powershell
  python test_suite_secretaria_y_requisitos.py
  python test_auditoria_maestra_edunova.py
  python test_recorrido_sustentacion_edunova.py
  ```

---

### 10. ¿Qué pruebas existen y qué resultados se obtuvieron realmente?
Se ejecutaron tres suites maestras de pruebas automatizadas sobre la base de datos real MySQL `sinetec`:
1. `test_suite_secretaria_y_requisitos.py`: **34 / 34 pruebas aprobadas (100%)**. Validó gestión de usuarios en secretaría, descargas de plantillas Excel/CSV, registro con ceros a la izquierda, auto-creación de credenciales cifradas y visualización de grados 1° a 11°.
2. `test_auditoria_maestra_edunova.py`: **23 / 23 pruebas aprobadas (100%)**. Validó aislamiento RBAC, protección anti-IDOR entre familias y estudiantes, ciclo completo de publicación-entrega-calificación de tareas, auditoría y lectura de circulares.
3. `test_recorrido_sustentacion_edunova.py`: **56 / 56 pruebas aprobadas (100%)**. Validó el recorrido completo de los seis roles de principio a fin, reportes en PDF y Excel, y estados vacíos pedagógicos.

**Total acumulado:** **113 pruebas automatizadas ejecutadas y 113 aprobadas al 100%**.
