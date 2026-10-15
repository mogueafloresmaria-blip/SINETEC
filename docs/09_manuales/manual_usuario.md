# MANUAL DE USUARIO OFICIAL DEL SISTEMA DE INFORMACIÓN EDUNOVA
### Sistema Integrado de Educación Técnica (Anteriormente SINETEC)
**SENA Regional Magdalena — Centro de Logística y Promoción Ecoturística del Magdalena**  
**Programa:** Tecnología en Análisis y Desarrollo de Sistemas de Información (ADSI)  
**Ficha de Caracterización:** 3173430  
**Instructor Evaluador:** Ing. Anybal López  
**Aprendices Desarrolladoras:** Aminta María Moguea Florez y Dulce María Figueroa  
**Publicación en Producción:** [https://sinetec-1.onrender.com/](https://sinetec-1.onrender.com/)  
**Versión Actual:** 2.4.0 (Octubre de 2026)

---

## 1. INTRODUCCIÓN Y PROPÓSITO
¡Bienvenido a **EduNova**! EduNova es una plataforma web integral basada en software libre (Python, Django, MySQL Server y Nginx) diseñada para centralizar, digitalizar y automatizar la gestión académica, formativa y administrativa de las Instituciones Educativas articuladas con la Media Técnica en el Departamento del Magdalena.

Este manual práctico está dirigido a toda la comunidad educativa: **Administradores**, **Rectoría**, **Secretaría Académica**, **Docentes/Instructores**, **Estudiantes (Aprendices)** y **Familias/Acudientes**.

---

## 2. REQUISITOS PARA EL ACCESO
Para utilizar EduNova únicamente necesita:
* Un computador, tableta o teléfono inteligente con conexión a internet.
* Un navegador web moderno (Google Chrome, Mozilla Firefox, Microsoft Edge o Safari).
* Sus credenciales institucionales asignadas (Usuario o Documento y Contraseña).
* **Dirección oficial en producción:** `https://sinetec-1.onrender.com/` (o `http://127.0.0.1:8000/` en servidor local).

---

## 3. CÓMO INICIAR Y CERRAR SESIÓN

1. Abra su navegador e ingrese a: `https://sinetec-1.onrender.com/accounts/login/` (o presione **"Ingresar a la Plataforma"** en la página principal).
2. En el formulario de autenticación:
   * Ingrese su **Usuario institucional o Número de Documento** en el primer campo.
   * Ingrese su **Contraseña** en el segundo campo.
3. Presione el botón **"Iniciar Sesión"**. El sistema validará su perfil activo y lo dirigirá automáticamente a su portal correspondiente.
4. **Cierre de Sesión Seguro:** En la barra superior, abra el menú desplegable con su nombre o avatar y seleccione **"Cerrar sesión"**.

> **Nota para entornos de prueba:** En modo desarrollo (`DEBUG=True`), se habilita un acceso directo para demostraciones de interfaz (*demo_estudiante*). En producción (`DEBUG=False`), dicho acceso se encuentra deshabilitado por seguridad, requiriendo siempre credenciales válidas.

---

## 4. LIBRETO GUÍA PARA DEMOSTRACIÓN INSTITUCIONAL (20 MINUTOS)

| Tiempo | Módulo / Pantalla | Acciones a Demostrar |
| :--- | :--- | :--- |
| **0:00–1:00** | Acceso y Bienvenida | Inicio de sesión, validación de credenciales y selección de portal según el rol asignado. |
| **1:00–4:00** | Panel de Administrador | Dashboard general (`/dashboard/`), alumnos, matrículas, carga académica (en dos columnas balanceadas), usuarios y papelera de reciclaje. |
| **4:00–6:00** | Portal de Rectoría | Indicadores de gestión (`/rectoria/`), rendimiento por periodos, circulares institucionales y reportes. |
| **6:00–8:30** | Portal de Secretaría | Búsqueda de matrículas (`/secretaria/`), registro de estudiantes, certificados y caja/pensiones. |
| **8:30–11:30** | Portal Docente | Listado de grupos (`/docentes/dashboard/`), asistencia diaria con escáner, publicación de actividades y calificación por RAPs. |
| **11:30–14:00** | Portal de Estudiante | Horario de clases (`/estudiantes/dashboard/`), consulta de calificaciones, boletines y entrega de actividades. |
| **14:00–16:30** | Portal de Familia | Monitoreo del estudiante acudido (`/familia/dashboard/`), observaciones, estado de pensiones y comunicación. |
| **16:30–19:00** | Recorrido Conectado | Publicación de un taller por el docente Miguel González y consulta/entrega inmediata desde el perfil de Juan Pérez (10°A). |
| **19:00–20:00** | Cierre de Auditoría | Verificación de políticas RBAC, aislamiento de perfiles y cierre de sesión. |

---

## 5. GUÍA DETALLADA DE LOS SEIS (6) PANELES DEL SISTEMA

### 5.1 Portal de Administrador (`/dashboard/`)
El Administrador cuenta con el control técnico y operativo global del sistema:
* **Alumnos y Matrículas (`/estudiantes/`, `/matriculas/`):** Consulta del padrón general, filtros por grado (10° y 11°) y edición de expedientes.
* **Carga Académica y Malla Curricular (`/carga-academica/`):** Formulario ergonómico distribuido en dos columnas que permite vincular asignaturas, docentes, niveles y cursos sin recargar la página.
* **Horarios y Cursos:** Programación de bloques académicos semanales y asignación de aulas.
* **Pensiones y Caja (`/pensiones/`):** Control general de cobros y estados de cuenta.
* **Usuarios y Roles (`/usuarios/`):** Creación de cuentas, restablecimiento de contraseñas y asignación de roles RBAC.
* **Auditoría Forense (`/auditoria/`):** Registro cronológico de acciones ejecutadas en la plataforma con timestamp e IP.
* **Papelera de Reciclaje (`/papelera/`):** Mecanismo de borrado lógico (*soft delete*) que permite recuperar matrículas, notas o registros eliminados accidentalmente.

---

### 5.2 Portal de Rectoría y Coordinación (`/rectoria/`, `/coordinacion/`)
Orientado a la toma de decisiones gerenciales y supervisión formativa:
* **Tablero de Indicadores:** Estadísticas consolidadas de cobertura escolar, porcentaje de aprobación y alertas tempranas de deserción.
* **Supervisión de Notas:** Consulta de sábanas académicas consolidadas por periodo.
* **Circulares y Comunicados:** Redacción y difusión de noticias o circulares oficiales dirigidas a docentes o familias.
* **Informes Directivos:** Exportación de reportes institucionales en formato PDF y Excel.

---

### 5.3 Portal de Secretaría Académica (`/secretaria/`)
Dedicado a la gestión documental y trámites administrativos:
* **Búsqueda Avanzada de Expedientes:** Localización instantánea de estudiantes por documento, nombre o acudiente.
* **Registro de Estudiantes (`/estudiantes/registrar/`):** Registro de nuevos aprendices vinculándolos directamente a su ficha y grado formativo.
* **Emisión de Certificados:** Generación de constancias de estudio y certificados de notas oficiales.
* **Caja y Pensiones:** Registro de pagos en taquilla y generación de comprobantes de pago.
* **Bandeja de Solicitudes:** Recepción y trámite de peticiones y traslados escolares.

---

### 5.4 Portal de Docentes e Instructores (`/docentes/dashboard/`)
Centro de gestión académica y pedagógica para los profesores:
* **Mis Grupos y Asignaturas:** Visualización de las asignaciones de clase correspondientes a su carga académica.
* **Control de Asistencia (`/asistencia/`):** Pase de lista diario por asignatura con estados (Presente, Ausente, Excusa, Retardo). Incluye lector de código QR para registro rápido.
* **Actividades y Tareas (`/actividades-y-tareas/`):** Creación de talleres y tareas con fecha límite de entrega, archivos adjuntos e instrucciones detalladas.
* **Planilla de Calificaciones:** Asentamiento de notas cuantitativas y juicios cualitativos por Resultados de Aprendizaje (RAP: Aprobado / No Aprobado) según el modelo SENA.
* **Horario del Docente:** Consulta del cronograma semanal de clases asignadas.

---

### 5.5 Portal de Estudiantes y Aprendices (`/estudiantes/dashboard/`)
Interfaz personal, intuitiva y protegida para el estudiante (ejemplo validado: *Juan Pérez en 10°A*):
* **Mi Perfil:** Consulta de datos personales y académicos verificados en base de datos.
* **Mis Calificaciones:** Visualización transparente de notas parciales y juicios de RAPs asentados por sus profesores. Si no hay notas registradas, el sistema muestra: *"Aún no tienes calificaciones registradas"*.
* **Tareas y Actividades:** Bandeja de actividades pendientes con opción para adjuntar archivos de respuesta y consultar retroalimentaciones.
* **Mi Horario Escolar:** Consulta del horario de clases organizado por días y bloques formativos.
* **Mi Asistencia:** Porcentaje de asistencia acumulada y registro de inasistencias.
* **Avisos Institucionales:** Recepción de circulares y comunicados de rectoría y docentes.

---

### 5.6 Portal de Familias y Acudientes (`/familia/dashboard/`)
Permite a padres y tutores realizar el seguimiento formativo de sus hijos:
* **Expediente del Acudido:** Consulta de la ficha de matrícula y datos del aprendiz.
* **Boletines Periódicos:** Descarga directa de los boletines de calificaciones al cierre de cada periodo.
* **Control de Asistencia:** Notificación y seguimiento diario de inasistencias o retardos.
* **Estado de Pensiones:** Consulta del historial de pagos y cuotas pendientes.
* **Comunicación con Docentes:** Canal directo de mensajería para contactar a directores de grupo.

---

## 6. PREGUNTAS FRECUENTES Y SOLUCIÓN DE PROBLEMAS (FAQ)

1. **¿Qué hago si olvidé mi contraseña de acceso?**  
   *Respuesta:* Solicite el restablecimiento de su clave ante la Secretaría Académica o el Administrador del sistema mediante el módulo de usuarios.
2. **¿Por qué un docente no puede calificar a un grupo?**  
   *Respuesta:* Verifique que la Asignación Docente (Carga Académica) se encuentre registrada y activa para esa materia, grado y ficha específica.
3. **¿Cómo recupero un registro borrado por error?**  
   *Respuesta:* El Administrador puede ingresar a la ruta `/papelera/` y pulsar el botón **"Restaurar"** sobre el elemento enviado a eliminación lógica.
4. **¿Cómo se visualiza el sistema en teléfonos celulares?**  
   *Respuesta:* EduNova cuenta con diseño responsivo (responsive design). Ingrese desde cualquier navegador móvil (Chrome o Safari) a `https://sinetec-1.onrender.com/` y los menús se adaptarán automáticamente a la pantalla.

---

## 7. CRÉDITOS Y CERTIFICACIÓN FORMATIVA
Manual elaborado y verificado en cumplimiento del Resultado de Aprendizaje del SENA Regional Magdalena por las aprendices **Aminta María Moguea Florez** y **Dulce María Figueroa**, bajo la dirección del instructor **Ing. Anybal López**. Ficha de caracterización: **3173430**.
