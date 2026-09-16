# ESTRUCTURA DE DIAPOSITIVAS PARA SUSTENTACIÓN SENA ADSI
### PROYECTO FORMATIVO OFICIAL: “SISTEMAS DE INFORMACIÓN Y DESARROLLO DE SOFTWARE EN EL DEPARTAMENTO DEL MAGDALENA”
**Software:** SINETEC (Sistema de Integración Técnica Education)  
**Centro:** Centro de Logística y Promoción Ecoturística del Magdalena  

---

## DIAPOSITIVA 1: PORTADA OFICIAL
* **Logotipo del SENA:** En la esquina superior izquierda.
* **Título Principal:** Sustentación de Proyecto Formativo ADSI (Ficha 228106 · V.102).
* **Nombre Oficial del Proyecto:** *“SISTEMAS DE INFORMACIÓN Y DESARROLLO DE SOFTWARE EN EL DEPARTAMENTO DEL MAGDALENA”* (Cód. SOFIA 3445935).
* **Nombre del Software Desarrollado:** **SINETEC** (*Sistema de Integración Técnica Education*).
* **Subtítulo:** *Sistema de Información para el Seguimiento del Proceso de Integración con la Media Técnica*.
* **Aprendiz(ces):** [Tu Nombre Completo].
* **Centro y Regional:** Centro de Logística y Promoción Ecoturística del Magdalena · Regional Magdalena.
* **Año:** 2026.

---

## DIAPOSITIVA 2: PLANTEAMIENTO DEL PROBLEMA
* **Título:** Situación Problemática (AS-IS).
* **Puntos Clave:**
  * Dispersión de información en hojas de cálculo (Excel) personales de instructores y colegios.
  * Tiempos prolongados para consolidar bitácoras de visita y juicios evaluativos.
  * Riesgo constante de duplicidad de matrículas y pérdida de expedientes de contacto.
  * Ausencia de reportes e indicadores de retención y aprobación en tiempo real para la coordinación.
* **Elemento Visual:** Diagrama de flujo del proceso actual (AS-IS) de `docs/01_analisis/linea_base_analisis.md`.

---

## DIAPOSITIVA 3: OBJETIVOS DEL PROYECTO
* **Título:** Objetivos del Proyecto Formativo.
* **Objetivo General Oficial:**  
  *“Diseñar, desarrollar un sistema de información que permita sistematizar los registros que se maneja en la evaluación y el seguimiento del proceso de articulación en la Regional Magdalena en el Centro de logística y promoción ecoturística del Magdalena.”*
* **Objetivos Específicos:**
  1. Satisfacer las necesidades reales de los usuarios (coordinadores, instructores, colegios).
  2. Proporcionar una solución viable y factible técnica y económicamente.
  3. Comprender el funcionamiento del Sistema Nacional de Formación para el Trabajo (SNFT) y modelar la solución sobre sus directrices oficiales.

---

## DIAPOSITIVA 4: METODOLOGÍA DE DESARROLLO
* **Título:** Metodología y Fases de Trabajo.
* **Metodología Ágil Adaptada:** Scrum en Sprints formativos con Historias de Usuario (HU).
* **Ruta de Trazabilidad Rigurosa:**  
  $$\text{Problema} \to \text{Objetivo} \to \text{Requerimiento} \to \text{HU} \to \text{Caso de Uso} \to \text{Base de Datos} \to \text{Código} \to \text{Prueba}$$
* **Principio Fundamental:** Cero código prematuro; diseño y normalización previa antes de la construcción.

---

## DIAPOSITIVA 5: LEVANTAMIENTO DE REQUERIMIENTOS (IEEE 830)
* **Título:** Especificación de Requerimientos de Software (SRS).
* **Requerimientos Funcionales (15 RF):** Autenticación por roles, gestión de colegios, matrícula rápida de aprendices, registro de bitácoras con compromisos y sábana masiva de notas.
* **Requerimientos No Funcionales (8 RNF):** Cifrado PBKDF2/SHA-256, protección contra CSRF/XSS/SQLi, diseño responsive accesible y tiempos de respuesta inferiores a 2 segundos.
* **Reglas de Negocio Destacadas:**
  * **RN-001:** Unicidad estricta de documentos de identidad.
  * **RN-003:** Escala de juicios cualitativos oficiales ('A' y 'D').
  * **RN-004:** Inmutabilidad de notas tras el cierre formal de periodos.
  * **RN-006:** Compromisos obligatorios con fecha límite ante novedades.

---

## DIAPOSITIVA 6: MODELADO UML DEL SISTEMA
* **Título:** Diseño Funcional mediante Diagramas UML.
* **Diagramas Elaborados:**
  * Diagrama de Contexto de SINETEC.
  * Diagrama General de Casos de Uso (12 casos de uso categorizados).
  * Diagrama de Actividades del Proceso de Seguimiento y Evaluación.
  * Diagramas de Secuencia (Login y Registro de Bitácora).
* **Elemento Visual:** Diagrama General de Casos de Uso de `docs/04_diseno_sistema/modelado_uml_sistema.md`.

---

## DIAPOSITIVA 7: DISEÑO DE BASE DE DATOS Y NORMALIZACIÓN
* **Título:** Modelo Entidad-Relación y Persistencia.
* **Características Técnicas:**
  * 11 Entidades normalizadas en Tercera Forma Normal (3FN).
  * Motor transaccional `InnoDB` en MySQL Server 8.0.
  * Llaves foráneas con integridad referencial y restricciones de unicidad.
  * Cotejamiento `utf8mb4_unicode_ci` para soporte total de caracteres en español.
* **Elemento Visual:** Diagrama Entidad-Relación (MER) de `docs/05_base_de_datos/modelo_relacional.md`.

---

## DIAPOSITIVA 8: ARQUITECTURA TECNOLÓGICA (MTV)
* **Título:** Arquitectura del Software (Patrón MTV).
* **Componentes del Patrón:**
  * **Modelo (M):** ORM de Django mapeado a tablas MySQL con validaciones automáticas.
  * **Plantilla (T):** HTML5, CSS3 personalizado y Bootstrap 5 para interfaces adaptables.
  * **Vista (V):** Controladores de lógica de negocio y despacho de peticiones.
* **Modularización:** 5 aplicaciones Django desacopladas (`usuarios`, `instituciones`, `academico`, `seguimiento`, `evaluaciones`).
* **Elemento Visual:** Diagrama MTV de `docs/07_arquitectura_tecnologica/arquitectura_software_sad.md`.

---

## DIAPOSITIVA 9: DEMOSTRACIÓN DEL SOFTWARE EN VIVO
* **Título:** Demostración del Software SINETEC.
* **Recorrido Demostrativo:**
  1. Login institucional seguro con control de acceso por roles.
  2. Dashboard interactivo con indicadores en tiempo real.
  3. Directorio de colegios articulados con filtros por municipio.
  4. Expediente de ficha técnica con aprendices y bitácoras.
  5. Sábana interactiva de notas con juicios 'A' / 'D' y control de cierre de periodo.
  6. Registro de visitas técnicas con compromisos obligatorios (RN-006).

---

## DIAPOSITIVA 10: PLAN DE PRUEBAS Y CALIDAD DEL SOFTWARE
* **Título:** Verificación, Calidad y Plan de Pruebas.
* **Resultados de la Suite Automatizada:**
  * 13 Casos de prueba ejecutados y aprobados (100%).
  * Validación estricta de las reglas de negocio institucionales.
  * Comprobación de seguridad contra Inyección SQL y ataques CSRF.
* **Elemento Visual:** Tabla resumen de resultados de `docs/08_pruebas/plan_y_evidencias_de_pruebas.md`.

---

## DIAPOSITIVA 11: VIABILIDAD E IMPACTO INSTITUCIONAL
* **Título:** Viabilidad del Proyecto Formativo.
* **Viabilidad Técnica:** Basado en tecnologías estándar de la industria (Python, Django, MySQL) con alta comunidad y soporte.
* **Viabilidad Económica:** **$0.00 COP** en licenciamiento; desarrollo 100% en software libre y código abierto.
* **Viabilidad Operativa:** Interfaz ergonómica de fácil adopción para los instructores y directivos del Magdalena.
* **Impacto:** Centralización, trazabilidad e inmediatez en el seguimiento a los aprendices de Media Técnica.

---

## DIAPOSITIVA 12: CONCLUSIONES Y CIERRE
* **Título:** Conclusiones y Agradecimientos.
* **Logros Alcanzados:**
  * Software SINETEC completamente funcional, probado y documentado.
  * Trazabilidad total desde el problema del Centro hasta la prueba unitaria.
  * Cumplimiento del 100% de los resultados de aprendizaje del programa ADSI.
* **Espacio:** *“Quedamos atentos a las preguntas y observaciones del comité evaluador. ¡Muchas gracias!”*
