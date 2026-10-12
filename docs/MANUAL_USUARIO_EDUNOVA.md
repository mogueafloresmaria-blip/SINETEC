# Manual de usuario de EduNova

Guía práctica de los portales institucionales y libreto para una demostración
de aproximadamente 20 minutos.

## Antes de empezar

1. Abra EduNova en el navegador y seleccione **Ingresar a la Plataforma**.
2. Para una cuenta institucional normal, escriba el usuario o documento y la
   contraseña asignados. El inicio de sesión valida la cuenta y su perfil
   activo, y lleva al portal correspondiente al rol.
3. En modo desarrollo (`DEBUG=True`) aparece una opción de demostración para
   **Estudiante**. Selecciónela y pulse **Entrar como Estudiante**: se inicia
   sesión como `demo_estudiante`, una cuenta sintética sin contraseña utilizable
   ni matrícula. Este acceso no está disponible en producción (`DEBUG=False`).
   La cuenta permite mostrar la interfaz y la navegación, pero no contiene
   calificaciones, tareas, horario ni asistencia de un estudiante real.
4. Para mostrar datos académicos, use una cuenta de prueba preparada y
   autorizada con matrícula y datos ficticios. No grabe expedientes,
   contraseñas ni información personal reales.
5. Para salir de una cuenta, abra el menú de usuario y seleccione **Cerrar
   sesión**.

La opción rápida de Estudiante es solo una facilidad de demostración en
desarrollo; no reemplaza el inicio de sesión institucional con usuario y
contraseña. Los accesos rápidos de otros roles, cuando estén disponibles, solo
rellenan el formulario: no omiten la autenticación.

## Libreto sugerido para el video (20 minutos)

| Tiempo | Qué mostrar |
| --- | --- |
| 0:00–1:00 | Página de ingreso, selección de rol y cambio entre cuentas de demostración o cuentas autorizadas. |
| 1:00–4:00 | Administrador: resumen, estudiantes y matrículas, gestión académica y herramientas institucionales. |
| 4:00–6:00 | Rectoría: indicadores, consulta de estudiantes, rendimiento y accesos a notas, circulares e informes. |
| 6:00–8:30 | Secretaría: panel, búsqueda de matrículas, registro de estudiante, caja y reportes. |
| 8:30–11:30 | Docente: grupos, asistencia, publicación de actividad y revisión de entregas. |
| 11:30–14:00 | Estudiante: calificaciones, horario, tareas, asistencia y comunicados. |
| 14:00–16:30 | Familia: estudiante vinculado, boletines, asistencia, pensiones y comunicación. |
| 16:30–19:00 | Recorrido conectado: actividad publicada por docente y consulta/entrega desde un estudiante con matrícula y datos de prueba preparados. |
| 19:00–20:00 | Cierre de sesión y resumen de permisos y privacidad por rol. |

El libreto prioriza un recorrido corto. Las secciones siguientes sirven como
guía de operación para explicar los módulos adicionales. La disponibilidad de
registros depende de los datos cargados y de la matrícula asociada.

## 1. Administrador

### Inicio y navegación

1. Inicie sesión con una cuenta institucional de Administrador.
2. Entre al **Dashboard** (`/dashboard/`) y presente sus métricas, gráficas y
   actividad reciente. Los valores cambian según la información registrada.
3. Use la navegación lateral para abrir las secciones disponibles. La plantilla
   contiene accesos de administración como alumnos, matrículas, horarios,
   profesores, carga académica, cursos, notas, pensiones, usuarios,
   comunicaciones, asistencia, transporte, reportes, auditoría, configuración
   y papelera.

### Operaciones representativas

- **Estudiantes y matrículas:** desde **Estudiantes** (`/estudiantes/`) o
  **Matrículas** (`/matriculas/`), localice registros con los filtros
  disponibles, abra el expediente cuando corresponda y utilice las acciones
  habilitadas para la cuenta.
- **Fichas, horarios y formación:** entre a la sección académica para consultar
  fichas, cargas y horarios. Los formularios y acciones dependen del rol y de
  los permisos que muestre la pantalla.
- **Comunicaciones:** abra **Comunicaciones** para consultar o gestionar los
  comunicados permitidos. Revise destinatarios antes de publicar.
- **Asistencia:** use el módulo de asistencia o el escáner autorizado. El
  registro QR de asistencia está destinado a personal autorizado, no al
  estudiante.
- **Reportes, auditoría y configuración:** consulte los enlaces disponibles
  en la navegación; la auditoría permite revisar acciones registradas y la
  configuración depende de los permisos de la cuenta.

### Mapa de módulos del menú

| Módulo | Uso práctico |
| --- | --- |
| Alumnos y matrículas | Buscar estudiantes, abrir expedientes y consultar el padrón de matrículas. |
| Horarios, profesores, carga académica y cursos | Revisar la organización de grupos, materias, docentes y horarios; guardar cambios solo cuando el formulario y el permiso lo permitan. |
| Notas y asistencia | Consultar registros académicos y de asistencia; usar las acciones de registro habilitadas para la cuenta. |
| Pensiones | Consultar pagos y recibos, y tramitar las acciones de caja que muestre el módulo. |
| Usuarios y configuración | Administrar cuentas y parámetros institucionales disponibles para el perfil. |
| Comunicaciones y transporte | Consultar comunicados y rutas; gestionar asignaciones solo si están habilitadas. |
| Reportes | Abrir los informes y utilizar la exportación disponible (por ejemplo, Excel o PDF). |
| Auditoría | Consultar acciones institucionales registradas. |
| Papelera | Revisar elementos enviados a eliminación lógica y utilizar las opciones de recuperación que presente la pantalla. |

**Importante:** `/dashboard/` requiere inicio de sesión, pero no es exclusivo
del Administrador. El acceso a otras áreas se valida además por rol; que un
enlace aparezca en una plantilla no garantiza que todas las cuentas puedan
ejecutar la acción.

## 2. Rectoría y Coordinación

### Rectoría

1. Inicie sesión con el rol **Rectoría**. El destino habitual es el panel de
   Rectoría (`/rectoria/`).
2. Revise los indicadores de matrícula, docentes, grupos, asistencia y
   rendimiento académico. No presente los valores de ejemplo de la plantilla
   como cifras institucionales si no se han contrastado con los datos.
3. En el directorio, escriba un criterio o seleccione el filtro de grado para
   consultar estudiantes matriculados.
4. Use los accesos del panel para ir a **Notas y Actas**, **Informes PDF** o
   **Redactar Circular**, si el rol tiene permiso para la acción.
5. Regrese al panel para consultar alertas o los demás accesos directivos
   disponibles en la navegación.

El menú de Rectoría incluye accesos de consulta a estudiantes, cuerpo docente,
matrículas, cursos, rendimiento, alertas, circulares, reportes, papelera y
auditoría. Use los filtros en las pantallas que los presenten, abra el registro
que desea revisar y vuelva al panel desde la navegación. Las acciones de
edición/publicación pueden tener permisos compartidos con otros roles.

### Coordinación

El sistema dispone de un panel de Coordinación separado (`/coordinacion/`).
Desde él se consultan fichas e indicadores, y hay accesos a horarios,
evaluación y reportes. Si la cuenta se redirige al panel de Rectoría, abra
Coordinación desde la navegación o su ruta, según los permisos asignados.

Rectoría y Coordinación comparten permisos en varias áreas de gestión. No
presente todos los formularios administrativos como exclusivos de Rectoría.

## 3. Secretaría

### Consulta y registro

1. Inicie sesión con una cuenta autorizada para Secretaría y abra
   **Secretaría** (`/secretaria/`).
2. En el panel, escriba nombre, apellido, documento o acudiente en la búsqueda;
   opcionalmente filtre por ficha y estado de matrícula. Envíe el formulario
   para actualizar los resultados.
3. Use **Padrón Matrículas** o la ruta `/matriculas/` para consultar
   matrículas, y **Estudiantes** (`/estudiantes/`) para buscar expedientes.
4. Para registrar un estudiante, use **Registrar estudiante**
   (`/estudiantes/registrar/`) y complete el formulario. Si se selecciona una
   ficha, la vista contempla asociar una matrícula.
5. En **Caja/Pensiones** (`/pensiones/`), consulte los registros de pagos. La
   ruta **Nuevo cobro** (`/pensiones/nuevo/`) permite tramitar un cobro según
   el formulario y los permisos de la cuenta.
6. Para informes, abra el **Centro de reportes** (`/reportes/`) y utilice las
   opciones disponibles.

### Solicitudes de Secretaría

- **Bandeja**: `/seguimiento/secretaria/`.
- **Nueva solicitud**: `/seguimiento/secretaria/solicitud/nueva/`.
- **Mis solicitudes**: `/seguimiento/secretaria/mis-solicitudes/`.
- **Detalle**: `/seguimiento/secretaria/solicitud/<id>/`.

La bandeja y la radicación están implementadas. Hay una limitación de permisos
pendiente: un usuario cuyo único rol sea Secretaría puede no tener autorización
para abrir y gestionar el detalle de solicitudes ajenas. No se debe prometer en
el video que Secretaría puede completar el ciclo de respuesta/cierre sin
verificarlo con una cuenta y el registro correspondiente.

**Acción del panel que requiere atención:** el botón **Nueva Matrícula** del
panel apunta a un formulario académico que no incluye Secretaría entre los
roles habilitados. Para una demostración con Secretaría, use el flujo de
registro de estudiante anterior y no prometa que ese botón completa la
matrícula para ese rol.

## 4. Docente

### Inicio y grupos

1. Inicie sesión con una cuenta docente y abra **Inicio del docente**
   (`/instructor/`).
2. Abra **Mis Grupos** (`/mis-grupos/`) y seleccione un grupo para revisar la
   lista que presenta el sistema.
3. Abra **Mis Asignaturas** (`/mis-asignaturas/`) y consulte las asignaciones
   visibles para esa cuenta.

### Asistencia

1. Abra **Asistencia** (`/asistencia/`).
2. Seleccione grupo, fecha y asignatura cuando el formulario lo solicite.
3. Registre los estados disponibles y observaciones.
4. Pulse **Guardar** y confirme el resultado que presente la pantalla.

El sistema también tiene un flujo de escaneo QR para personal autorizado. El
docente debe confirmar el grupo y el estudiante antes de registrar asistencia.

### Actividades, tareas y evaluación

1. Abra **Actividades y tareas** (`/actividades-y-tareas/`).
2. Use **Crear actividad** si aparece habilitado; complete título,
   instrucciones, destinatarios/grupo y los campos que solicita el formulario.
3. Revise la actividad y su estado; solo las actividades publicadas se
   muestran como entregables al estudiante.
4. Abra las entregas de una actividad para revisar lo enviado y utilizar las
   acciones de evaluación que la pantalla habilite.
5. Consulte **Calificaciones** (`/calificaciones-docente/`) para revisar la
   planilla docente disponible.
6. Use **Horario Escolar** (`/horario-escolar/`) para consultar el horario
   presentado para la cuenta.

### Otros accesos del portal docente

La navegación ofrece además perfil profesional, Mis Estudiantes,
Comportamiento, Recursos/Guías, Documentos, Eventos, Reportes,
Comunicaciones, Notificaciones, Manual y Papelera. Abra cada sección desde el
menú y siga los controles visibles. El contenido y las acciones dependen de
las asignaciones y de los permisos.

| Sección | Qué revisar en pantalla |
| --- | --- |
| Perfil profesional | La información profesional asociada a la cuenta. |
| Mis Estudiantes | La lista y los registros que el portal presenta para el docente. |
| Comportamiento | El módulo de seguimiento de comportamiento disponible para esa cuenta. |
| Recursos/Guías y Documentos | Los materiales y documentos que el portal permite consultar o gestionar. |
| Eventos | Los eventos o fechas que aparecen para el docente. |
| Reportes, Comunicaciones y Notificaciones | Los informes, mensajes y avisos visibles para la cuenta. |
| Manual y Papelera | La ayuda disponible y los elementos enviados a papelera que el rol pueda consultar. |

No presente cantidades fijas de estudiantes, grupos o asignaturas. Algunos
textos de documentación/plantillas son ejemplos; la información válida es la
que se carga para la cuenta usada en la demostración.

## 5. Estudiante

### Inicio y consulta académica

1. En producción, ingrese con su usuario/documento y contraseña. En desarrollo,
   para mostrar el portal vacío de demostración, seleccione **Estudiante** y
   pulse **Entrar como Estudiante**. El portal esperado es `/aprendiz/`.
2. En la pantalla principal, revise las tarjetas de progreso, asistencia,
   tareas y horario. Las tarjetas dependen de que exista matrícula y actividad
   asociada.
3. Abra las pestañas:
   - **Mis Calificaciones y Semáforo**: consulta las valoraciones asociadas al
     estudiante.
   - **Mi Horario Escolar**: consulta el horario disponible.
   - **Mis Tareas y Evaluaciones**: abre tareas publicadas asignadas al grupo.
   - **Mi Asistencia**: revisa los registros disponibles.
   - **Avisos y Comunicados**: consulta comunicados dirigidos al estudiante.
4. Para entregar una tarea, abra una actividad publicada, lea sus
   instrucciones y utilice el formulario de respuesta/archivo disponible. Las
   rutas de entrega verifican que la tarea corresponda a la matrícula.
5. Abra **Comunicados** o **Mensajería** para consultar mensajes habilitados.
   El estudiante no puede publicar circulares institucionales.
6. En **Mi Portafolio**, consulte las evidencias y los registros que estén
   asociados a su usuario/matrícula. **Biblioteca** y **Notificaciones** son
   accesibles con sesión iniciada.

El portal protege calificaciones, tareas y otras consultas para que el
estudiante acceda a sus propios datos; las tareas disponibles se filtran por
estado publicado y matrícula activa.

**Cuenta sintética de demostración:** `demo_estudiante` no tiene matrícula.
Por eso puede mostrar la interfaz, pero presenta estados sin registros; no
debe usarse para afirmar que existe una calificación, horario o tarea asignada.
Si la tarjeta de asistencia muestra un porcentaje con cero registros, no lo
interprete como evidencia de asistencia: en este usuario de demostración no
hay sesiones asociadas.

## 6. Familia / Acudiente

### Consulta del estudiante vinculado

1. Inicie sesión con una cuenta de Familia/Acudiente. El destino esperado es
   `/familia/`.
2. Revise el resumen del estudiante o estudiantes vinculados. Si hay más de
   uno, seleccione el perfil correspondiente antes de consultar módulos.
3. Abra **Ficha de Matrícula** (`/familia/matricula/`) para revisar la
   información que el sistema muestra de la matrícula.
4. Abra **Boletines** (`/familia/boletines/`), seleccione el período si está
   disponible y consulte o descargue el boletín.
5. Abra **Asistencia** (`/familia/asistencia/`) para revisar los registros
   mostrados.
6. Abra **Pensiones** (`/familia/pensiones/`) para consultar los pagos y
   recibos disponibles.
7. Use **Escribir a Docente** o el área de comunicaciones para enviar un
   mensaje si la cuenta tiene esa opción habilitada. Consulte también las
   circulares disponibles en el portal.

La familia solo debe consultar estudiantes vinculados a su cuenta. Para una
demostración de mensajería, use una cuenta con un solo estudiante asociado:
hay una limitación conocida al elegir el estudiante cuando el acudiente tiene
varios hijos.

## Recorrido conectado entre roles

Para grabar el flujo académico de punta a punta, prepare de antemano cuentas y
registros ficticios con una misma ficha/grupo:

1. Como docente, cree una actividad para el grupo y publíquela.
2. Cierre sesión e ingrese como un estudiante **matriculado en ese grupo**.
3. Abra sus tareas, localice la actividad publicada y envíe la respuesta o
   archivo que permita el formulario.
4. Vuelva a iniciar sesión como docente, abra la actividad y revise la entrega.
5. Muestre la información resultante en las vistas disponibles para ambos
   roles. No afirme que una nota se refleja automáticamente en todos los
   módulos si no se ha comprobado con el registro de prueba utilizado.

La cuenta sintética de demostración no sirve para este recorrido porque no
tiene matrícula. No cambie la matrícula de un usuario real para preparar el
video.

## Permisos, datos y solución de problemas

- Si una cuenta termina en un panel distinto, confirme el rol asignado en su
  perfil institucional y que el perfil esté activo.
- Si el usuario no ve una tarea, compruebe que esté publicada y que corresponda
  a una matrícula activa del grupo.
- Si no hay registros de notas, asistencia u horario, puede que todavía no se
  hayan cargado datos para esa matrícula; una pantalla sin filas no implica
  que se haya guardado información.
- Si aparece **Acceso restringido**, el rol actual no tiene permiso para esa
  acción. No intente continuar con una URL de otro rol.
- En el entorno de demostración, la entrada rápida de Estudiante solo se
  habilita con `DEBUG=True`. La cuenta sintética no puede usarse para iniciar
  sesión normal con contraseña.
- Los permisos no son exclusivos de un solo rol en todas las vistas. En
  particular, algunas pantallas exigen sesión y bloquean al estudiante, pero
  no limitan la operación únicamente a Secretaría o Rectoría. Siga los
  permisos efectivos de cada pantalla.

## Referencias de implementación

Las rutas y nombres de módulos descritos se contrastaron con las rutas, vistas,
plantillas y pruebas de `usuarios`, `academico`, `evaluaciones`, `seguimiento`,
`instituciones` y `convenios`. Este manual describe el comportamiento
implementado en el repositorio; no sustituye la validación de registros ni la
confirmación de permisos en cada instalación.
