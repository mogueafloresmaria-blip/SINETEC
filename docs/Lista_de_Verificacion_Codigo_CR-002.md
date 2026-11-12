# Instrumento. Lista de Verificación de Revisión de Código
### Aseguramiento de la Calidad del Software (SQA) y Gestión de Configuración (SCM) – EduNova

**Objetivo:** Comprobar los aspectos esenciales de calidad, buenas prácticas, seguridad, validación y fiabilidad del código fuente antes de autorizar la integración (*merge*) del cambio a la rama principal (`main`/`master`).

---

## 1. Datos Generales de la Revisión

| Campo | Detalle de la Revisión |
| :--- | :--- |
| **Identificador del Cambio** | **CR-002** (Incorporación de casilla «Permitir co-docencia autorizada») |
| **Rama de Trabajo** | `feature/CR-002-co-docencia` |
| **Rama Destino** | `main` (Merge pendiente de autorización final) |
| **Fecha de Revisión** | 5 de noviembre de 2026 |
| **Revisores / Evaluadores** | Equipo de Desarrollo y Calidad EduNova (Aminta María Moguea Flórez y Dulce María Figueroa Padilla) |
| **Entorno de Verificación** | Python 3.13.14 · Django 5.0.14 · MySQL 9.7 (`sinetec`) · Windows 10/11 x64 |
| **Archivos Inspeccionados** | 1. `templates/academico/malla_curricular.html`<br>2. `templates/academico/gestionar_asignacion_grupo.html`<br>3. `academico/views.py` |

---

## 2. Lista de Verificación Diligenciada

| N.° | Criterio / Punto de Revisión | Qué se comprueba | Evidencia Técnica Observada en CR-002 | Calificación |
| :---: | :--- | :--- | :--- | :---: |
| **1** | **Convenciones de nombres** | Clases, funciones, variables y archivos usan nombres claros, expresivos y consistentes con el estándar. | Las variables agregadas (`permitir_co_docencia`, `doc_ya_asignado`, `carga_titular_act`, `grado_normalizado`, `nivel_asignado`) siguen rigurosamente `snake_case` (PEP 8). Los identificadores en el DOM (`checkCoDocencia`, `checkCoDocenciaGrupo`) usan `camelCase` coherente con los scripts de plantilla. No se introdujeron abreviaturas ambiguas. | **Cumple** |
| **2** | **Manejo de excepciones** | Los errores se capturan de forma controlada; no se ignoran ni se muestran detalles internos al usuario. | Se utiliza `get_object_or_404` para resolver entidades. Se implementó una verificación previa de existencia con `.exists()` para neutralizar posibles errores de integridad de base de datos (`IntegrityError 1062 - Duplicate entry`). Si un docente ya está asignado, se emite una notificación amigable vía `messages.info()`. No hay bloques `except Exception: pass` ni exposición de `str(e)`. | **Cumple** |
| **3** | **Seguridad SQL** | Las consultas usan ORM o parámetros y no concatenan datos del usuario en sentencias SQL. | Todas las operaciones de lectura, actualización y creación se realizan exclusivamente mediante el ORM de Django (`filter()`, `select_related()`, `create()`, `update()`). No se utiliza SQL directo, `.raw()` ni `.extra()`. Las consultas revisadas utilizan el ORM de Django y no se identificó SQL directo en el cambio evaluado. | **Cumple** |
| **4** | **Validación de entradas** | Los datos recibidos se validan antes de guardarse en base de datos. | Se comprueba la presencia de `prog_id` y `doc_id` antes de procesar la solicitud. El parámetro `permitir_co_docencia` se parsea contra una lista blanca booleana (`['1', 'true', 'True', 'on']`). El grado escolar se normaliza mediante `normalizar_grado()` para tolerar formatos mixtos ('10' vs '10°'). Los campos HTML cuentan con validación obligatoria (`required`). | **Cumple** |
| **5** | **Modularidad** | Las vistas y funciones tienen responsabilidades claras y se dividen en módulos manejables. | La implementación reutiliza funciones auxiliares del dominio escolar (`normalizar_grado`, `determinar_nivel_educativo`, `extraer_numero_grado`). El cambio es quirúrgico, no genera dependencias circulares y mantiene un bajo acoplamiento con otros submódulos. | **Cumple** |
| **6** | **Protección CSRF** | Las solicitudes POST cuentan con protección CSRF y los formularios incluyen el token. | Ambos formularios modificados (`#formCargaAcademica` en `malla_curricular.html` y el formulario de asignación en `gestionar_asignacion_grupo.html`) contienen la directiva obligatoria `{% csrf_token %}`. Peticiones directas sin token son rechazadas por el middleware de seguridad. | **Cumple** |
| **7** | **Registro de eventos** | Los errores y eventos importantes quedan registrados para facilitar su diagnóstico y auditoría. | Las operaciones notifican al usuario en tiempo real mediante el framework de mensajes de sesión (`messages.success`, `messages.info`). Sin embargo, no se implementó registro en archivos de bitácora (`logging.getLogger`) ni inserción en la tabla `seguimiento_registroauditoria` para las asignaciones docentes. | **No cumple** |
| **8** | **Revisión antes de integrar** | Los hallazgos se documentan y el cambio se revisa y aprueba antes de pasar a main/master. | La modificación cuenta con Solicitud de Cambio formal aprobada (CR-002), se desarrolló en una rama aislada (`feature/CR-002-co-docencia`), superó las pruebas automatizadas y no se ha integrado a `main`, preservando la estabilidad de la línea base. | **Cumple** |
| **9** | **Pruebas y funcionamiento** | El cambio cuenta con pruebas automatizadas que demuestran su correcto funcionamiento y la ausencia de regresiones. | Se construyó y ejecutó una suite automatizada específica (`scratch/test_cr002_co_docencia.py`) que validó casos positivos y negativos con rollback atómico. Adicionalmente, se superaron la suite ISO 25010 y la suite maestra (23/23 pruebas aprobadas, 100% de éxito). | **Cumple** |
| **10** | **Modificaciones en esquema de base de datos** | Los cambios estructurales en modelos cuentan con sus respectivas migraciones documentadas y reversibles. | El cambio CR-002 es de naturaleza funcional y de interfaz; no requirió alterar modelos, agregar columnas ni ejecutar migraciones en la base de datos MySQL. | **No aplica** |

---

## 3. Resumen Cuantitativo de la Evaluación

- **Criterios Evaluados:** 10
- **Cumple:** 8 (80%)
- **No cumple:** 1 (10% – Deuda técnica preexistente de registro en logs/auditoría)
- **No aplica:** 1 (10% – No requirió migraciones de esquema)
- **Criterios de Seguridad:** Los criterios de seguridad revisados fueron satisfactorios según las pruebas realizadas (control CSRF, validación estricta de parámetros y prevención de duplicados).

---

## 4. Conclusión y Recomendación Técnica

1. **Estado del Código:** El código desarrollado en la rama `feature/CR-002-co-docencia` cumple con los estándares de buenas prácticas, seguridad, validación y robustez exigidos por el procedimiento SQA de EduNova.
2. **Recomendación para Futuras Fases:** Se recomienda programar en una futura solicitud de cambio (deuda técnica de logging) la integración del módulo de asignación académica con el servicio centralizado de `RegistroAuditoria`.
3. **Concepto de Revisión:** **APTO PARA INTEGRACIÓN (MERGE)** a la rama principal (`main`), una vez sea emitido el visto bueno formal de las directivas del proyecto.

