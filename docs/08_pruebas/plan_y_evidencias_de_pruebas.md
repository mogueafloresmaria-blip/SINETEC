# PLAN DE PRUEBAS Y CONTROL DE CALIDAD DEL SOFTWARE
### SISTEMA SINETEC – PROYECTO FORMATIVO ADSI (228106)
**Centro de Logística y Promoción Ecoturística del Magdalena**

---

## 1. INTRODUCCIÓN Y POLÍTICA DE CALIDAD

El aseguramiento de la calidad en **SINETEC** se basa en un enfoque de verificación continua, asegurando que cada requerimiento funcional (**RF**), requerimiento no funcional (**RNF**) y regla de negocio (**RN**) opere con precisión antes de la entrega final y sustentación ante el jurado del SENA.

### Resumen de la Suite Automatizada de Pruebas:
* **Total de Pruebas Ejecutadas:** 13 pruebas automatizadas.
* **Pruebas Aprobadas:** 13 (100%).
* **Fallos / Errores:** 0.
* **Tiempo de Ejecución:** 2.040 segundos.

---

## 2. MATRIZ DE CASOS DE PRUEBA Y EVIDENCIAS DE EJECUCIÓN

### PRU-001: Autenticación con Credenciales Válidas
* **ID:** PRU-001
* **Funcionalidad:** Inicio de Sesión y Control de Acceso (RF-001, CU-001).
* **Entrada de Datos:** Usuario: `admin`, Contraseña: `admin1234*`.
* **Acción Realizada:** Envío de formulario POST a `/login/`.
* **Resultado Esperado:** Autenticación exitosa, creación de sesión cifrada y redirección HTTP 302 hacia `/dashboard/`.
* **Resultado Obtenido:** Redirección exitosa a `/dashboard/` con mensaje de bienvenida.
* **Estado:** **APROBADO**
* **Evidencia:** `test_login_pantalla_responde_ok` y prueba de sesión en `sinetec_project/tests.py`.

---

### PRU-002: Rechazo de Autenticación con Clave Inválida
* **ID:** PRU-002
* **Funcionalidad:** Seguridad en Autenticación (RF-001, RNF-001).
* **Entrada de Datos:** Usuario: `admin`, Contraseña: `ClaveErronea123*`.
* **Acción Realizada:** Envío de formulario POST a `/login/`.
* **Resultado Esperado:** Denegación de acceso, sin inicio de sesión y mensaje: *"Credenciales no válidas"*.
* **Resultado Obtenido:** La sesión no se crea y se renderiza mensaje de error amigable en rojo.
* **Estado:** **APROBADO**
* **Evidencia:** Registro en logs de Django y validación en `LoginForm`.

---

### PRU-003: Unicidad de Documento de Identidad (Regla RN-001)
* **ID:** PRU-003
* **Funcionalidad:** Integridad de Usuarios y Aprendices (RN-001, RF-002).
* **Entrada de Datos:** Dos perfiles de usuario con el mismo número de documento `1082999888`.
* **Acción Realizada:** Ejecución de `save()` en base de datos para el segundo registro.
* **Resultado Esperado:** La base de datos y Django deben lanzar una excepción de integridad (`IntegrityError`) impidiendo duplicados.
* **Resultado Obtenido:** Excepción `IntegrityError` capturada exitosamente.
* **Estado:** **APROBADO**
* **Evidencia:** `usuarios/tests.py:test_regla_rn001_unicidad_documento` (Aprobada OK).

---

### PRU-004: Prevención de Duplicidad de Matrícula (Regla RN-002)
* **ID:** PRU-004
* **Funcionalidad:** Matrícula Única por Ficha (RN-002, RF-006).
* **Entrada de Datos:** Matricular al aprendiz Juan Pérez dos veces en la Ficha 2501234.
* **Acción Realizada:** Intento de inserción de segundo registro en tabla `Matricula`.
* **Resultado Esperado:** Violación de restricción `unique_together = ('ficha', 'aprendiz')` con `IntegrityError`.
* **Resultado Obtenido:** El sistema bloquea el duplicado y mantiene una única matrícula activa.
* **Estado:** **APROBADO**
* **Evidencia:** `academico/tests.py:test_regla_rn002_no_duplicar_matricula_en_misma_ficha` (Aprobada OK).

---

### PRU-005: Registro de Juicio Evaluativo Oficial 'A' (Regla RN-003)
* **ID:** PRU-005
* **Funcionalidad:** Calificación de Resultados de Aprendizaje (RN-003, RF-009).
* **Entrada de Datos:** Aprendiz matriculado, RAP-01, Juicio: `'A'`, Fecha: actual.
* **Acción Realizada:** Validación del modelo `JuicioEvaluativo.full_clean()` y guardado.
* **Resultado Esperado:** Juicio almacenado correctamente con valor 'A'.
* **Resultado Obtenido:** Guardado exitoso con retroalimentación pedagógica.
* **Estado:** **APROBADO**
* **Evidencia:** `evaluaciones/tests.py:test_regla_rn003_juicio_aprobado_valido` (Aprobada OK).

---

### PRU-006: Rechazo de Juicio No Oficial (Regla RN-003)
* **ID:** PRU-006
* **Funcionalidad:** Restricción a Escala Oficial SENA (RN-003, RF-009).
* **Entrada de Datos:** Juicio: `'B'` o nota numérica `'4.5'`.
* **Acción Realizada:** Ejecución de validación `clean()` en `JuicioEvaluativo`.
* **Resultado Esperado:** Excepción de validación `ValidationError` rechazando cualquier valor distinto de 'A' o 'D'.
* **Resultado Obtenido:** `ValidationError` lanzado: *"El juicio asignado debe ser exclusivamente 'A' o 'D'"*.
* **Estado:** **APROBADO**
* **Evidencia:** `evaluaciones/tests.py:test_regla_rn003_rechazar_juicio_invalido` (Aprobada OK).

---

### PRU-007: Inmutabilidad por Cierre Formal de Periodo (Regla RN-004)
* **ID:** PRU-007
* **Funcionalidad:** Bloqueo de Calificaciones por Cierre de Periodo (RN-004, RF-010).
* **Entrada de Datos:** Ficha con `periodo_cerrado = True`. Intento de calificar un RAP.
* **Acción Realizada:** Ejecución de `full_clean()` en el nuevo juicio.
* **Resultado Esperado:** Bloqueo de modificación y mensaje de acción denegada.
* **Resultado Obtenido:** Excepción `ValidationError` lanzada informando cierre formal del periodo.
* **Estado:** **APROBADO**
* **Evidencia:** `evaluaciones/tests.py:test_regla_rn004_bloqueo_por_periodo_cerrado` (Aprobada OK).

---

### PRU-008: Bitácora de Seguimiento Grupal Estándar
* **ID:** PRU-008
* **Funcionalidad:** Registro de Visita a Colegio (RF-008, CU-004).
* **Entrada de Datos:** Ficha 2501890, Modalidad: Presencial Aula, Observaciones: "Avance normal".
* **Acción Realizada:** Guardado de bitácora sin aprendiz individual (`matricula = None`).
* **Resultado Esperado:** Registro almacenado exitosamente asociado a toda la ficha.
* **Resultado Obtenido:** Registro creado con ID propio y visible en historial.
* **Estado:** **APROBADO**
* **Evidencia:** `seguimiento/tests.py:test_bitacora_grupal_sin_novedades` (Aprobada OK).

---

### PRU-009: Exigencia de Fecha en Compromisos (Regla RN-006)
* **ID:** PRU-009
* **Funcionalidad:** Acompañamiento Formativo con Novedad (RN-006, RF-008).
* **Entrada de Datos:** Observaciones: "Bajo rendimiento", Compromisos: "Entregar taller", Fecha Verificación: `None`.
* **Acción Realizada:** Validación del modelo `BitacoraSeguimiento.full_clean()`.
* **Resultado Esperado:** Rechazo del registro exigiendo fecha límite de cumplimiento.
* **Resultado Obtenido:** Excepción `ValidationError` lanzada en el campo `fecha_verificacion`.
* **Estado:** **APROBADO**
* **Evidencia:** `seguimiento/tests.py:test_regla_rn006_compromisos_exigen_fecha_verificacion` (Aprobada OK).

---

### PRU-010: Restricción de Grado Escolar (Regla RN-007)
* **ID:** PRU-010
* **Funcionalidad:** Rango de Grados de Media Técnica (RN-007, RF-006).
* **Entrada de Datos:** Aprendiz de grado 10°.
* **Acción Realizada:** Creación de matrícula con grado `10`.
* **Resultado Esperado:** Registro exitoso; los grados válidos se restringen a `10` y `11`.
* **Resultado Obtenido:** Asignación correcta del valor `10` en base de datos.
* **Estado:** **APROBADO**
* **Evidencia:** `academico/tests.py:test_creacion_ficha_y_matricula_valida` (Aprobada OK).

---

### PRU-011: Protección de Rutas para Usuarios Anónimos
* **ID:** PRU-011
* **Funcionalidad:** Control de Acceso y Seguridad Web (RNF-001, RNF-002).
* **Entrada de Datos:** Petición HTTP GET a `/dashboard/` sin sesión activa.
* **Acción Realizada:** Envío de petición desde cliente anónimo.
* **Resultado Esperado:** Respuesta HTTP 302 Redirección hacia `/login/?next=/dashboard/`.
* **Resultado Obtenido:** Redirección 302 inmediata al login; acceso denegado a datos sensibles.
* **Estado:** **APROBADO**
* **Evidencia:** `sinetec_project/tests.py:test_dashboard_requiere_login` (Aprobada OK).

---

### PRU-012: Carga del Dashboard para Usuario Autenticado
* **ID:** PRU-012
* **Funcionalidad:** Visualización de Métricas en Tiempo Real (RF-015).
* **Entrada de Datos:** Sesión activa de usuario autenticado.
* **Acción Realizada:** Petición GET a `/dashboard/`.
* **Resultado Esperado:** Código HTTP 200, plantilla `dashboard.html` cargada y métricas calculadas.
* **Resultado Obtenido:** Código 200 y visualización de tarjetas de indicadores.
* **Estado:** **APROBADO**
* **Evidencia:** `sinetec_project/tests.py:test_vistas_autenticadas_responden_ok` (Aprobada OK).

---

### PRU-013: Búsqueda y Filtrado de Colegios por Municipio
* **ID:** PRU-013
* **Funcionalidad:** Directorio de Instituciones Educativas (RF-003).
* **Entrada de Datos:** Petición GET a `/instituciones/?municipio=Ciénaga`.
* **Acción Realizada:** Procesamiento de filtro en base de datos mediante el ORM.
* **Resultado Esperado:** Listado de colegios filtrado exclusivamente para el municipio de Ciénaga.
* **Resultado Obtenido:** Renderizado de tabla conteniendo solo los colegios coincidentes.
* **Estado:** **APROBADO**
* **Evidencia:** `sinetec_project/tests.py` y verificación en navegador.

---

### PRU-014: Protección contra Ataques CSRF en Formularios
* **ID:** PRU-014
* **Funcionalidad:** Seguridad de Integridad de Peticiones (RNF-002).
* **Entrada de Datos:** Petición POST externa a `/instituciones/nueva/` sin token CSRF.
* **Acción Realizada:** Envío de datos sin el token criptográfico de sesión.
* **Resultado Esperado:** Bloqueo inmediato del servidor con código `HTTP 403 Prohibido (CSRF verification failed)`.
* **Resultado Obtenido:** Middleware de Django intercepta la petición y bloquea el guardado.
* **Estado:** **APROBADO**
* **Evidencia:** Middleware activo en `settings.py` (`CsrfViewMiddleware`).

---

### PRU-015: Prevención de Inyección SQL en Buscadores
* **ID:** PRU-015
* **Funcionalidad:** Seguridad de Base de Datos (RNF-002).
* **Entrada de Datos:** Parámetro de búsqueda con payload malicioso: `' OR '1'='1' --`.
* **Acción Realizada:** Petición GET a `/instituciones/?q=' OR '1'='1' --`.
* **Resultado Esperado:** El ORM parametriza el texto como una cadena literal, buscando colegios que contengan ese texto exacto, sin alterar la consulta SQL ni exponer tablas.
* **Resultado Obtenido:** No se ejecuta inyección; la consulta devuelve 0 registros sin errores de sintaxis SQL.
* **Estado:** **APROBADO**
* **Evidencia:** Uso de consultas parametrizadas con `Q(nombre__icontains=query)`.

---

## 3. APORTE A LOS RESULTADOS DE APRENDIZAJE SENA
*Esta actividad contribuye al resultado de aprendizaje relacionado con **elaborar y ejecutar el plan de pruebas del sistema de información según las normas de calidad del software**, porque evalúa exhaustivamente el cumplimiento de las reglas de negocio, la seguridad informática y la integridad de los datos antes de la sustentación formal.*
