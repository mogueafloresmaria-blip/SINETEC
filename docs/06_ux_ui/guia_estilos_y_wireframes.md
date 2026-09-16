# GUÍA DE ESTILOS VISUALES Y WIREFRAMES ESTRUCTURALES
### SISTEMA SINETEC – PROYECTO FORMATIVO ADSI
**Centro de Logística y Promoción Ecoturística del Magdalena**

---

## 1. GUÍA DE ESTILOS VISUALES (SISTEMA DE DISEÑO) `[PROPUESTA]`

Para garantizar que SINETEC transmita seriedad, modernidad y una experiencia institucional de alto nivel sin saturar al usuario, se define el siguiente sistema de diseño:

### 1.1 Paleta de Colores Curada
* **Azul Institucional Primario (`#0A2540` / `#1E3A8A`):** Color dominante para barra lateral (Sidebar), botones principales y encabezados jerárquicos. Transmite confianza, estabilidad y formalidad académica.
* **Verde Aprobado / Éxito (`#059669` / `#10B981`):** Utilizado para juicios aprobados ('A'), confirmaciones exitosas de guardado y badges de estado "Activo".
* **Ámbar Alerta / Pendiente (`#D97706` / `#F59E0B`):** Para advertencias de periodos próximos a vencer, aprendices con compromisos pendientes o alertas del sistema.
* **Rojo Novedad / Por Mejorar (`#DC2626` / `#EF4444`):** Para juicios no aprobados ('D'), estados inactivos, alertas de deserción y botones de acción destructiva (ej. anular registro).
* **Fondo de Interfaz Neutro (`#F8FAFC`):** Gris ultra suave que reduce la fatiga visual de instructores y coordinadores durante largas jornadas de trabajo.
* **Superficie de Tarjetas (`#FFFFFF`):** Blanco puro con bordes sutiles (`#E2E8F0`) y sombras suaves (`box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05)`).

### 1.2 Tipografía
* **Familia Tipográfica:** `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`.
* **Jerarquía de Textos:**
  * **H1 (Títulos de Página):** 24px - SemiBold (600).
  * **H2 (Títulos de Sección / Tarjetas):** 18px - Medium (500).
  * **Body (Texto de Contenido y Tablas):** 14px - Regular (400) - Color `#334155`.
  * **Small / Badges (Etiquetas y Metadatos):** 12px - Medium (500).

---

## 2. WIREFRAMES ESTRUCTURALES DE LAS PANTALLAS CRÍTICAS `[PROPUESTA]`

Los wireframes son esquemas estructurales en baja fidelidad que definen la distribución espacial y los elementos interactivos antes de programar las plantillas HTML.

---

### WIREFRAME 1: Pantalla de Inicio de Sesión (`/login/`)
```
+-----------------------------------------------------------------------+
|                             SINETEC                                   |
|       Sistema de Integración Técnica Education - Regional Magdalena   |
|          Centro de Logística y Promoción Ecoturística                 |
+-----------------------------------------------------------------------+
|                                                                       |
|                     +---------------------------+                     |
|                     |      INICIAR SESIÓN       |                     |
|                     |  Acceso seguro al sistema |                     |
|                     +---------------------------+                     |
|                     |                           |                     |
|                     | Correo Electrónico:       |                     |
|                     | [ correo@sena.edu.co    ] |                     |
|                     |                           |                     |
|                     | Contraseña:               |                     |
|                     | [ ********************  ] |                     |
|                     |                           |                     |
|                     | [X] Recordar sesión       |                     |
|                     |                           |                     |
|                     | [   INGRESAR A SINETEC  ] | (Botón Azul)        |
|                     |                           |                     |
|                     | ¿Olvidó su contraseña?    |                     |
|                     +---------------------------+                     |
|                                                                       |
+-----------------------------------------------------------------------+
|  SENA - Servicio Nacional de Aprendizaje © 2026 | Proyecto ADSI 228106 |
+-----------------------------------------------------------------------+
```

---

### WIREFRAME 2: Dashboard de la Coordinación (`/dashboard/coordinacion/`)
```
+----------------------------------------------------------------------------------------------------+
| SINETEC  |  Centro de Logística y Promoción Ecoturística               [Buscar...]  [Perfil] [Salir]|
+----------+-----------------------------------------------------------------------------------------+
| [SIDEBAR]|  PANEL DE CONTROL - COORDINACIÓN DE ARTICULACIÓN                                        |
|          |                                                                                         |
| Inicio   |  +--------------------+ +--------------------+ +--------------------+ +-----------------+
| Colegios |  | 28 Colegios        | | 1,450 Aprendices   | | 92.4% Aprobación   | | 14 Seguimientos |
| Fichas   |  | Activos en Convenio| | Matriculados 10/11 | | Vigencia Actual    | | Pendientes      |
| Matrícula|  +--------------------+ +--------------------+ +--------------------+ +-----------------+
| Seguim.  |                                                                                         |
| Notas    |  ACCIONES RÁPIDAS:                                                                      |
| Reportes |  [ + Nueva Ficha ]   [ + Vincular Colegio ]   [ Cerrar Periodo ]   [ Descargar Balance ]|
| Usuarios |                                                                                         |
|          |  ÚLTIMAS BITÁCORAS REGISTRADAS POR INSTRUCTORES:                                        |
|          |  +------------------------------------------------------------------------------------+ |
|          |  | Fecha      | Colegio                  | Ficha   | Instructor       | Estado Novedad| |
|          |  +------------+--------------------------+---------+------------------+---------------+ |
|          |  | 14/09/2026 | I.E. Técnica de Ciénaga  | 2501234 | Carlos Martínez  | [Con Acuerdo] | |
|          |  | 12/09/2026 | I.E. Simón Bolívar (S.M) | 2501890 | Andrea Gómez     | [Sin Novedad] | |
|          |  | 10/09/2026 | I.E. Agropecuaria Aracat.| 2501452 | Roberto Peña     | [Sin Novedad] | |
|          |  +------------------------------------------------------------------------------------+ |
+----------+-----------------------------------------------------------------------------------------+
```

---

### WIREFRAME 3: Formulario de Bitácora de Seguimiento (`/seguimiento/nuevo/`)
```
+----------------------------------------------------------------------------------------------------+
| SINETEC  |  Módulo de Seguimiento Formativo                                     [Instructor SENA]  |
+----------+-----------------------------------------------------------------------------------------+
| [SIDEBAR]|  REGISTRO DE BITÁCORA DE SEGUIMIENTO Y VISITA TÉCNICA                                   |
|          |                                                                                         |
| Inicio   |  +------------------------------------------------------------------------------------+ |
| Mis Fich.|  | DATOS DE LA VISITA                                                                 | |
| Seguim.  |  | Ficha Técnica: [ Ficha 2501234 - Téc. en Sistemas - I.E. Ciénaga                  v ]| |
| Notas    |  | Tipo de Asignación: ( ) Grupal (Toda la ficha)    (X) Individual (Un aprendiz)     | |
| Reportes |  | Aprendiz: [ 1082987123 - Martínez Gómez Juan David                                v ]| |
|          |  | Fecha de Visita: [ 14/09/2026 ]    Tipo Visita: [ Presencial en Aula / Taller     v ]| |
|          |  +------------------------------------------------------------------------------------+ |
|          |  | DIAGNÓSTICO Y OBSERVACIONES PEDAGÓGICAS                                             | |
|          |  | Observaciones Técnicas:                                                            | |
|          |  | [ El aprendiz presenta inasistencias reiteradas y retraso en el taller de redes.  ] | |
|          |  | [ Se cita a reunión con el docente enlace de la institución.                      ] | |
|          |  +------------------------------------------------------------------------------------+ |
|          |  | COMPROMISOS Y PLAN DE MEJORA (Exigido por regla RN-006 al haber novedad)           | |
|          |  | Compromisos Acordados:                                                             | |
|          |  | [ Entrega de evidencias de aprendizaje pendientes antes del 25 de septiembre.      ] | |
|          |  | Fecha Límite de Verificación: [ 25/09/2026 ]                                       | |
|          |  | Adjuntar Acta de Visita Escaneada (PDF / JPG): [ Seleccionar archivo... ]          | |
|          |  +------------------------------------------------------------------------------------+ |
|          |  |                                                [ Cancelar ]  [ GUARDAR SEGUIMIENTO ]| |
|          |  +------------------------------------------------------------------------------------+ |
+----------+-----------------------------------------------------------------------------------------+
```

---

### WIREFRAME 4: Sábana de Calificación de Evaluaciones (`/evaluaciones/calificar/`)
```
+----------------------------------------------------------------------------------------------------+
| SINETEC  |  Evaluación del Aprendizaje                                          [Instructor SENA]  |
+----------+-----------------------------------------------------------------------------------------+
| [SIDEBAR]|  CALIFICACIÓN DE RESULTADOS DE APRENDIZAJE (RAP)                                        |
|          |                                                                                         |
| Inicio   |  Ficha: [ 2501234 - Téc. Sistemas v ]   Periodo: [ 2026 - Bimestre 3 (Abierto)        ] |
| Mis Fich.|  Competencia: [ 220501001 - Mantenimiento de Equipos de Cómputo                      v ]|
| Seguim.  |  Resultado (RAP): [ RAP-02: Realizar mantenimiento preventivo según manuales del fab. v ]|
| Notas    |                                                                                         |
| Reportes |  +------------------------------------------------------------------------------------+ |
|          |  | No | Documento   | Apellidos y Nombres        | Juicio Evaluativo | Observación         | |
|          |  +----+-------------+----------------------------+-------------------+---------------------+ |
|          |  | 01 | 1082987123  | Martínez Gómez Juan David  | (X) A   ( ) D     | [ Cumple criterios] | |
|          |  | 02 | 1082544991  | Ortiz De la Rosa Camila    | (X) A   ( ) D     | [ Excelente desem.] | |
|          |  | 03 | 1082112344  | Pérez Varela Andrés Felipe | ( ) A   (X) D     | [ Plan de mejora  ] | |
|          |  | 04 | 1082776510  | Quintero Salas Valentina   | (X) A   ( ) D     | [ Cumple criterios] | |
|          |  +------------------------------------------------------------------------------------+ |
|          |  | [ Marcar Todos como Aprobados ]                        [ GUARDAR CALIFICACIONES ]   | |
|          |  +------------------------------------------------------------------------------------+ |
+----------+-----------------------------------------------------------------------------------------+
```

---

### WIREFRAME 5: Generador de Reportes Oficiales (`/reportes/`)
```
+----------------------------------------------------------------------------------------------------+
| SINETEC  |  Módulo de Reportes y Estadísticas                                  [Coordinación SENA] |
+----------+-----------------------------------------------------------------------------------------+
| [SIDEBAR]|  GENERACIÓN Y DESCARGA DE REPORTES CONSOLIDADOS                                         |
|          |                                                                                         |
| Inicio   |  +------------------------------------------------------------------------------------+ |
| Colegios |  | 1. Seleccione el Tipo de Reporte:                                                  | |
| Fichas   |  | (X) Ficha Individual de Aprendiz (Historial completo de visitas y juicios)          | |
| Seguim.  |  | ( ) Sábana Consolidada de Evaluaciones por Ficha Técnica                             | |
| Notas    |  | ( ) Directorio Institucional de Colegios Articulados en el Magdalena                | |
| Reportes |  +------------------------------------------------------------------------------------+ |
|          |  | 2. Filtros de Búsqueda:                                                            | |
|          |  | Institución: [ I.E. Técnica Departamental de Ciénaga                              v ]| |
|          |  | Ficha Técnica: [ 2501234 - Técnico en Sistemas                                    v ]| |
|          |  | Periodo / Corte: [ Todos los cortes vigencia 2026                                 v ]| |
|          |  +------------------------------------------------------------------------------------+ |
|          |  | 3. Formato de Salida:                                                              | |
|          |  | [  DESCARGAR REPORTE EN PDF (Oficial)  ]    [  DESCARGAR EN EXCEL (Para cálculo)  ]  | |
|          |  +------------------------------------------------------------------------------------+ |
+----------+-----------------------------------------------------------------------------------------+
```

---

## 3. APORTE A LOS RESULTADOS DE APRENDIZAJE SENA
*Esta actividad contribuye al resultado de aprendizaje relacionado con **elaborar prototipos de interfaz de usuario de acuerdo con las especificaciones de diseño y las necesidades del cliente**, porque define los patrones visuales, la jerarquía de contenidos y la disposición ergonómica de los formularios antes de iniciar el maquetado con Bootstrap.*
