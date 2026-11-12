# Instrumento. Formato de Solicitud de Cambio
### Change Request (CR) – Gestión de Configuración del Software (Fase 3)

**Objetivo:** Dejar constancia de un cambio propuesto, explicar por qué se necesita, valorar sus posibles efectos y definir cómo se comprobará antes de aprobar su incorporación.

---

| Campo | Información de la Solicitud |
| :--- | :--- |
| **Identificador** | **CR-002** |
| **Fecha** | 5 de noviembre de 2026 |
| **Solicitante** | Equipo de Desarrollo y Aseguramiento de Calidad EduNova (Aminta Moguea / Dulce Figueroa) |
| **Módulo afectado** | Secretaría – Asignación Académica (Malla Curricular / Asignación por Grupo) |
| **Tipo de cambio** | Mejora funcional y de interfaz de usuario (UI/UX) / Control de integridad |
| **Descripción** | Incorporar en el formulario modal de Asignación Académica de Secretaría una casilla de verificación (*checkbox* / *switch* interactivo) con la etiqueta «Permitir co-docencia autorizada (segundo docente)» y un texto explicativo preventivo. |
| **Justificación** | En el backend del sistema ya se implementó la regla de negocio que previene asignaciones duplicadas accidentales y admite un segundo docente únicamente si se envía la autorización explícita de co-docencia (`permitir_co_docencia='1'`). Sin embargo, el formulario modal actual de Secretaría carece del control visual interactivo para que el usuario active voluntariamente dicha opción cuando exista autorización formal de las directivas. La inclusión de esta casilla con advertencia contextual cierra la brecha entre la interfaz y la regla de negocio, evitando confusiones y previniendo errores operativos. |
| **Impacto técnico** | Modificación menor en plantillas HTML (`templates/academico/malla_curricular.html` y `templates/academico/gestionar_asignacion_grupo.html`) para incluir el campo `input` de tipo checkbox con estilos accesibles Bootstrap. No altera el esquema de la base de datos MySQL, modelos, calificaciones, notas, tareas ni matrículas existentes. |
| **Riesgo / prioridad** | Riesgo de regresión: **BAJO, sujeto a pruebas**. Prioridad: Media-alta. |
| **Plan de implementación** | 1. Localizar el formulario modal `#asignarDocenteModal` en `templates/academico/malla_curricular.html`.<br>2. Añadir el control checkbox `permitir_co_docencia` con texto de ayuda preventivo.<br>3. Replicar el control en `templates/academico/gestionar_asignacion_grupo.html`.<br>4. Verificar la recepción armonizada del parámetro en `academico/views.py`. |
| **Plan de pruebas** | 1. **Prueba negativa:** Asignar sin marcar la casilla a una materia ya existente en un grupo y verificar que el sistema actualiza al titular sin duplicar filas.<br>2. **Prueba positiva:** Asignar marcando la casilla y comprobar que se admite el segundo docente con notificación de co-docencia autorizada.<br>3. Ejecución de la suite automatizada `scratch/test_iso25010_asignacion_academica.py` garantizando 100% de pruebas aprobadas. |
| **Responsable** | Equipo de Desarrollo / Gestión de Configuración EduNova |
| **Estado** | **APROBADA PARA IMPLEMENTACIÓN.** |
| **Aprobación** | Aprobado por el equipo de desarrollo EduNova: Aminta María Moguea Flórez y Dulce María Figueroa Padilla. |
| **Observaciones** | La aprobación corresponde al equipo de desarrollo EduNova (Aminta Moguea y Dulce María Figueroa). Se autoriza la ejecución del plan de implementación en la rama de trabajo y su verificación obligatoria mediante la suite de pruebas automatizadas previo a la integración en la línea base principal. |
