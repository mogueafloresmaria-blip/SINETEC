# CATÁLOGO DE REGLAS DE NEGOCIO (RN)
### SISTEMA SINETEC – PROYECTO FORMATIVO ADSI
**Centro de Logística y Promoción Ecoturística del Magdalena**

---

## 1. DEFINICIÓN
Las reglas de negocio definen o restringen aspectos del comportamiento del sistema, garantizando que el software respete las políticas y reglamentos del SENA y del proceso de articulación con la Media Técnica.

---

## 2. REGLAS DE NEGOCIO ESPECIFICADAS

### RN-001: Unicidad de Documento de Identidad `[CONFIRMADO]`
* **ID:** RN-001
* **Nombre:** Unicidad de Identificación de Usuario y Aprendiz.
* **Descripción:** No pueden registrarse en el sistema dos usuarios o aprendices con la misma combinación de tipo y número de documento de identidad.
* **Origen:** Principio de integridad de datos y normatividad nacional de registro civil.
* **Impacto en el Software:** Restricción `UNIQUE` en la base de datos y validación previa en los formularios del backend.
* **Estado:** `[CONFIRMADO]`

---

### RN-002: Pertenencia Exclusiva a una Institución Educativa `[PROPUESTA]`
* **ID:** RN-002
* **Nombre:** Vinculación Escolar Única por Periodo.
* **Descripción:** Un aprendiz de Media Técnica solo puede estar vinculado activamente a una sola Institución Educativa articulada durante un año lectivo determinado.
* **Origen:** Organización de los convenios interinstitucionales de articulación SENA - Colegios.
* **Impacto en el Software:** Validación en la lógica de negocio al momento de matricular o asociar al aprendiz.
* **Estado:** `[PROPUESTA]`

---

### RN-003: Escala Cualitativa de Juicios Evaluativos `[SUPUESTO]`
* **ID:** RN-003
* **Nombre:** Juicio Evaluativo Oficial SENA.
* **Descripción:** Los juicios asignados a los resultados de aprendizaje deben ser cualitativos y limitarse a los dos valores reglamentarios del SENA:
  * **A:** Aprobado (El aprendiz alcanzó los criterios de desempeño exigidos).
  * **D:** No Aprobado / Por Mejorar (El aprendiz requiere plan de mejoramiento o no alcanzó los logros).
* **Origen:** Reglamento del Aprendiz SENA (Acuerdo 007 de 2012 o normatividad vigente).
* **Impacto en el Software:** Campo tipo `ChoiceField` en Django / `ENUM` en MySQL con opciones restringidas a 'A' y 'D'.
* **Estado:** `[SUPUESTO]` *(Pendiente de revalidar si existe escala numérica interna previa en el Centro)*.

---

### RN-004: Inmutabilidad de Periodos Evaluativos Cerrados `[PROPUESTA]`
* **ID:** RN-004
* **Nombre:** Bloqueo de Modificaciones tras Cierre Formal.
* **Descripción:** Una vez que la Coordinación de Articulación ejecuta el cierre oficial de un periodo o corte evaluativo para una ficha, ningún instructor puede modificar, agregar ni eliminar juicios evaluativos de dicho corte, a menos que exista una reapertura formal autorizada por el Coordinador.
* **Origen:** Trazabilidad, seguridad jurídica y transparencia de las actas de evaluación.
* **Impacto en el Software:** Verificación de estado del periodo antes de permitir peticiones `POST`/`PUT` de actualización.
* **Estado:** `[PROPUESTA]`

---

### RN-005: Asignación Exclusiva de Permisos de Edición al Instructor `[PROPUESTA]`
* **ID:** RN-005
* **Nombre:** Restricción de Registro por Ficha Asignada.
* **Descripción:** Un instructor solo puede registrar, editar y asentar seguimientos o notas en las fichas técnicas en las que haya sido explícitamente designado como instructor responsable o de apoyo por la coordinación.
* **Origen:** Control interno de funciones y confidencialidad de la información.
* **Impacto en el Software:** Filtros de autorización basados en relaciones de modelo en las vistas de Django.
* **Estado:** `[PROPUESTA]`

---

### RN-006: Registro Obligatorio de Compromisos en Seguimientos con Novedad `[PROPUESTA]`
* **ID:** RN-006
* **Nombre:** Exigencia de Compromisos Formativos.
* **Descripción:** Cuando en una bitácora de seguimiento se califique el desempeño de un aprendiz o grupo con novedades negativas (asistencias irregulares o bajo rendimiento), el sistema obligará a registrar un campo de "Compromisos y Plan de Acción" y una fecha límite de verificación.
* **Origen:** Metodología pedagógica de acompañamiento SENA.
* **Impacto en el Software:** Validación condicional en el formulario de seguimiento (`forms.py`).
* **Estado:** `[PROPUESTA]`

---

### RN-007: Condición de Grado Escolar para Articulación `[PENDIENTE DE VALIDACIÓN]`
* **ID:** RN-007
* **Nombre:** Rango de Grados de Media Técnica.
* **Descripción:** Solo podrán ser matriculados en programas de articulación con el Centro aquellos estudiantes que se encuentren cursando formalmente los grados 10° (décimo) u 11° (undécimo) de Educación Media en el colegio en convenio.
* **Origen:** Lineamientos del Ministerio de Educación Nacional (MEN) y SENA para Articulación.
* **Impacto en el Software:** Validación en formulario de matrícula impidiendo registrar grados inferiores.
* **Estado:** `[PENDIENTE DE VALIDACIÓN]`

---

### RN-008: Trazabilidad y no Eliminación Física (Borrado Lógico) `[PROPUESTA]`
* **ID:** RN-008
* **Nombre:** Política de Borrado Lógico (Soft Delete).
* **Descripción:** Ningún registro de aprendiz, ficha, seguimiento o evaluación puede ser eliminado físicamente de la base de datos (con `DELETE`). Toda acción de anulación se realizará mediante un cambio de estado (campo `activo = False` o `estado = 'Inactivo'/'Retirado'`), preservando el histórico para auditoría.
* **Origen:** Custodia de la información y requerimientos de auditoría institucional.
* **Impacto en el Software:** Sobrescritura de métodos de eliminación en los modelos Django y filtrado por defecto de registros activos.
* **Estado:** `[PROPUESTA]`

---

## 3. APORTE A LOS RESULTADOS DE APRENDIZAJE SENA
*Esta actividad contribuye al resultado de aprendizaje relacionado con **identificar las reglas de negocio que condicionan el comportamiento del sistema de información**, porque traduce las normas institucionales y pedagógicas del SENA en restricciones lógicas que serán programadas en la base de datos y en el backend.*
