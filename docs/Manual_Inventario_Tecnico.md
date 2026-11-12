# DOCUMENTO TÉCNICO 1: INVENTARIO TÉCNICO COMPLETO
## SISTEMA DE GESTIÓN ESCOLAR ADMINISTRATIVO EDUNOVA (SINETEC)
**Fecha de Generación e Inspección:** 28 de Octubre de 2026  
**Entorno de Ejecución:** Windows 10/11 x64 · Terminal PowerShell · Python 3.13.14  
**Base de Datos Activa:** MySQL 9.7 (`sinetec`) · Localhost:3306

---

### 1. ARQUITECTURA GENERAL DEL PROYECTO
El sistema escolar administrativo **EduNova** (anteriormente SINETEC) está estructurado como un monolito modular sobre Django, con arquitectura MVC (Model-View-Template) acoplado a un motor relacional MySQL. Cuenta con seis paneles de usuario delimitados por permisos y control de acceso basado en roles (RBAC):
1. **Administrador:** Parametrización institucional, gestión integral de usuarios, asignación de carga académica, trazabilidad/auditoría inmutable, supervisión de papelera de reciclaje.
2. **Rectoría:** Tablero directivo de gobierno escolar, consolidación de cobertura, indicadores de desempeño y deserción, reportes oficiales ejecutivos.
3. **Secretaría:** Matrícula escolar (grados 1° a 11°), registro individual y carga masiva mediante hojas de cálculo Excel/CSV, gestión de expedientes y solicitudes de certificados/constancias.
4. **Docente:** Gestión de asignaturas asignadas, planeación y publicación de temas/guías pedagógicas, creación y recepción de actividades/tareas, calificación con escala oficial y retroalimentación, y toma de asistencia en tiempo real con historial de correcciones auditado.
5. **Estudiante:** Acceso a contenidos y temas publicados con descarga de adjuntos, recepción y entrega de actividades, visualización de boletines por períodos académicos sin notas ficticias, buzón de comunicaciones institucionales y radicación de solicitudes a secretaría.
6. **Familia / Acudiente:** Monitoreo exclusivo de los estudiantes vinculados a su acudiente, visualización de circulares oficiales con acuse de recibo y descarga de PDF, consulta de asistencias y calificaciones vigentes.

---

### 2. FRAMEWORK, LENGUAJE Y VERSIONES VERIFICADAS
- **Lenguaje:** Python versión exacta verificada `3.13.14` (CPython tags/v3.13.14:fd17997).
- **Framework Web:** Django versión exacta `5.0.14`.
- **Motor de Base de Datos:** MySQL versión `9.7` (usando conector `mysqlclient` compilado para Python 3.13).
- **Frontend / UI:** Vanilla CSS + Bootstrap 5.3.0 + Bootstrap Icons (paleta institucional EduNova: café moca `#5A3825`, acento `#8B5E3C`, arena `#F5F2EB`, fondo `#FAF8F5`).

---

### 3. DEPENDENCIAS Y LIBRERÍAS VERIFICADAS
Del archivo `requirements.txt` y entorno virtual `.\venv\`:
- `Django==5.0.14`
- `mysqlclient>=2.2.0` (Conexión nativa MySQL C API)
- `openpyxl>=3.1.2` (Procesamiento y exportación de archivos Excel `.xlsx`)
- `reportlab>=4.1.0` (Generación de boletines y reportes oficiales en formato PDF)
- `Pillow>=10.2.0` (Gestión y compresión de imágenes y fotografías de perfiles)

---

### 4. CONFIGURACIÓN DE BASE DE DATOS Y CONEXIÓN
Declarada en `sinetec_project/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sinetec',
        'USER': 'root',
        'PASSWORD': '***',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
```

---

### 5. INVENTARIO DE APLICACIONES Y MODELOS CENTRALES

#### App `academico`:
- **`ProgramaFormacion`:** Asignaturas escolares y mallas curriculares (nombre, código, área de conocimiento, intensidad horaria semanal).
- **`Ficha`:** Cursos y grupos escolares (código de grupo, jornada, grado, año de vigencia).
- **`Matricula`:** Vínculo formal de un estudiante (`aprendiz`) con un grado escolar, sección y ficha.
- **`CargaAcademica`:** Distribución de docentes titulares por asignatura, nivel, grado y grupo escolar.
- **`HorarioFicha`:** Bloques de clase semanales (día, hora de inicio, hora de fin, aula/ambiente, asignatura y docente).
- **`TareaClase`:** Actividades académicas publicadas por el docente (título, instrucciones, ponderación, fecha límite, adjunto).
- **`EntregaTarea`:** Entregas realizadas por estudiantes (archivo adjunto, texto de respuesta, calificación de 1.0 a 5.0, retroalimentación).
- **`GuiaClase`:** Temas pedagógicos publicados por los docentes (título, contenido detallado, enlaces y archivo descargable).
- **`CalificacionEscolar`:** Registro de calificaciones por período para el boletín oficial del estudiante.
- **`PeriodoAcademico`:** Configuración de los 4 períodos escolares anuales (fechas de inicio y cierre, estado activo/cerrado).

#### App `seguimiento`:
- **`AsistenciaAprendiz`:** Registro diario de asistencia por estudiante y sesión (P: Presente, A: Ausente, T: Tardanza, J: Justificada).
- **`HistorialCorreccionAsistencia`:** Modelo de auditoría inmutable de asistencia escolar (registra estado previo, estado corregido, usuario que modificó, fecha/hora y motivo).
- **`ComunicadoEscolar`:** Circulares y comunicaciones oficiales emitidas a la comunidad educativa (con soporte para archivo PDF oficial adjunto).
- **`AcuseLecturaCircular`:** Registro de acuse de lectura individual por parte de estudiantes, familias y docentes.
- **`RegistroAuditoria`:** Registro inmutable de transacciones críticas (usuario, IP, módulo, acción y detalles técnicos).
- **`SolicitudSecretaria`:** Trámites y solicitudes radicadas por estudiantes hacia secretaría escolar.
- **`Notificacion`:** Notificaciones internas multirrol del sistema.

#### App `usuarios`:
- **`PerfilUsuario`:** Extensión del modelo `User` con rol institucional, documento de identidad, teléfono, dirección y fotografía.
- **`Rol`:** Definición de roles institucionales (Administrador, Rectoría, Secretaría, Docente, Estudiante, Familia).
- **`FamiliaAcudiente`:** Vinculación legal entre el acudiente y sus estudiantes acudidos.
- **`PapeleraReciclaje`:** Modelo de retención y recuperación segura de registros eliminados.
- **`ConfiguracionColegio`:** Parámetros institucionales (nombre del plantel, NIT, DANE, rector, vigencia).

---

### 6. SEGURIDAD Y PERMISOS
- **RBAC (Role-Based Access Control):** Implementado mediante decoradores en `usuarios/decorators.py`:
  - `@solo_instructor`: Restringe acceso a vistas docentes.
  - `@solo_secretaria_o_coordinador`: Limita trámites a secretaría y directivos.
  - `@solo_aprendiz`: Protege el portal de estudiantes.
  - `@solo_acudiente_o_familia`: Aísla expedientes de familias.
- **Protección Anti-IDOR:**
  - En el portal Familia, se valida que el acudiente autenticado solo acceda a estudiantes presentes en `FamiliaAcudiente.objects.filter(estudiantes=...)`.
  - En circulares escolares, se valida que el usuario pertenezca al estamento destinatario (`Familias`, `Docentes`, `Estudiantes`).
- **Autenticación y Cifrado:**
  - Contraseñas procesadas mediante PBKDF2 con hash SHA256 (Django default).
  - En la carga masiva y creación automática de estudiantes, la contraseña inicial se hashea con el número de documento de identidad.

---

### 7. PROCEDIMIENTO DE RESPALDO Y RESTAURACIÓN VERIFICADO
1. **Respaldo de Base de Datos MySQL:**
   - Comando verificado: `mysqldump -u root -p sinetec > backup_edunova_YYYYMMDD.sql`
   - Respaldo Django verificado: `python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.Permission --indent 2 -o backup_edunova.json`
2. **Respaldo de Archivos Multimedia y Académicos (`media/`):**
   - Resguardo de carpetas de evidencias, tareas y circulares oficiales (`media/circulares_oficiales/`, `media/entregas_tareas/`, `media/guias_clase/`).
3. **Restauración en Entorno Seguro:**
   - Comando verificado: `mysql -u root -p sinetec < backup_edunova_YYYYMMDD.sql`
   - O mediante Django: `python manage.py loaddata backup_edunova.json`
