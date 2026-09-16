# GUION TÉCNICO Y ORAL PARA LA SUSTENTACIÓN DEL PROYECTO FORMATIVO
### PROGRAMA: ANÁLISIS Y DESARROLLO DE SISTEMAS DE INFORMACIÓN (ADSI - 228106)
**Centro de Logística y Promoción Ecoturística del Magdalena – Regional Magdalena**
*Proyecto SOFIA Plus: 3445935*

---

## 1. INSTRUCCIONES GENERALES PARA EL APRENDIZ
* **Tiempo Estimado de Exposición:** 15 a 20 minutos de exposición + 10 minutos de preguntas del jurado.
* **Tono y Actitud:** Seguro, pausado, profesional, mirando al jurado a los ojos. No memorices mecánicamente; comprende la lógica de cada fase.
* **Regla de Oro en la Presentación:** Distingue siempre entre el nombre oficial del proyecto formativo y el nombre del software.

---

## 2. GUION PALABRA POR PALABRA (PASO A PASO)

### INTRODUCCIÓN Y SALUDO PROTOCOLARIO (Minuto 0:00 - 1:30)
> *"Buenos días (o buenas tardes), estimados instructores y miembros del comité evaluador.*  
> *Mi nombre es [Tu Nombre Completo], aprendiz del programa **Análisis y Desarrollo de Sistemas de Información (ADSI)**, con código de ficha **228106**, versión **102**, del **Centro de Logística y Promoción Ecoturística del Magdalena**.*  
>  
> *En el día de hoy tengo el honor de presentar ante ustedes la sustentación final de nuestro proyecto formativo oficial, titulado:*  
> *“**SISTEMAS DE INFORMACIÓN Y DESARROLLO DE SOFTWARE EN EL DEPARTAMENTO DEL MAGDALENA**”, registrado en SOFIA Plus con el código **3445935**.*  
>  
> *Como respuesta técnica a las necesidades de nuestro Centro y de la Regional, hemos diseñado, desarrollado y probado el software denominado **SINETEC**, que significa: **Sistema de Integración Técnica Education**, y cuya descripción oficial es: **“Sistema de Información para el Seguimiento del Proceso de Integración con la Media Técnica”**.*

---

### PLANTEAMIENTO DEL PROBLEMA Y OBJETIVOS (Minuto 1:30 - 4:00)
> *"Para iniciar, hablemos del problema central que dio origen a este desarrollo.*  
> *Actualmente, los registros de seguimiento y evaluación de la Media Técnica en los colegios articulados con nuestro Centro en el Magdalena se venían manejando de forma dispersa, manual y descentralizada en múltiples hojas de cálculo de Excel personales.*  
> *Esto generaba riesgos de duplicidad, demoras en la consolidación de notas y dificultades para conocer en tiempo real la situación académica de nuestros jóvenes.*  
>  
> *Frente a esto, nuestro objetivo general oficial es:*  
> *‘Diseñar, desarrollar un sistema de información que permita sistematizar los registros que se manejan en la evaluación y el seguimiento del proceso de articulación en la Regional Magdalena en el Centro de Logística y Promoción Ecoturística del Magdalena’.*  
>  
> *Para alcanzarlo, estructuramos una metodología rigurosa en 16 fases, asegurando que antes de escribir una sola línea de código levantáramos formalmente los requerimientos, diseñáramos la arquitectura y normalizáramos la base de datos."*

---

### LEVANTAMIENTO DE REQUERIMIENTOS Y REGLAS DE NEGOCIO (Minuto 4:00 - 7:00)
> *"En la fase de análisis, elaboramos el documento de Especificación de Requerimientos bajo el estándar internacional **IEEE 830**, identificando **15 Requerimientos Funcionales** prioritarios y **8 Requerimientos No Funcionales** de seguridad, usabilidad y rendimiento.*  
>  
> *Asimismo, definimos **8 Reglas de Negocio institucionales** que condicionan el comportamiento del sistema. Quiero destacar tres de ellas:*  
> * *Primero, la **RN-001**, que exige unicidad absoluta de documentos de identidad.*  
> * *Segundo, la **RN-003**, que restringe las calificaciones a la escala cualitativa oficial del SENA: **A (Aprobado)** o **D (No Aprobado / Por Mejorar)**.*  
> * *Y tercero, la **RN-004**, que garantiza la inmutabilidad de las notas: una vez que la coordinación formaliza el cierre de un periodo evaluativo para una ficha, el sistema bloquea automáticamente cualquier edición no autorizada por parte de los instructores."*

---

### ARQUITECTURA Y DISEÑO DE BASE DE DATOS (Minuto 7:00 - 10:00)
> *"En la fase de diseño, aplicamos modelado UML completo: diagramas de casos de uso, actividades y secuencia.*  
>  
> *En la base de datos, modelamos un esquema relacional con **11 entidades normalizadas en Tercera Forma Normal (3FN)** utilizando el motor transaccional **InnoDB** de **MySQL Server**, lo que previene inconsistencias y registros huérfanos gracias al forzado de llaves foráneas.*  
>  
> *En cuanto a la arquitectura de software, adoptamos el patrón **MTV (Model - Template - View)** provisto por el framework **Django**, organizando el sistema de forma modular en 5 aplicaciones independientes: `usuarios`, `instituciones`, `academico`, `seguimiento` y `evaluaciones`."*

---

### DEMOSTRACIÓN EN VIVO DEL SISTEMA (Minuto 10:00 - 15:00)
*(Aquí pasas a mostrar la pantalla de tu computador en el proyector o pantalla compartida)*:
> 1. *"Ingresemos a la plataforma:*  
>    *Aquí tenemos la pantalla de inicio de sesión con los colores institucionales y validación de credenciales.*  
> 2. *Al ingresar con el rol de Administrador/Coordinador, observamos el **Dashboard Principal**:*  
>    *Muestra tarjetas de indicadores en tiempo real con los colegios activos, aprendices matriculados y el porcentaje de aprobación global.*  
> 3. *En el módulo de **Colegios**, podemos filtrar por municipio (por ejemplo, Ciénaga o Aracataca) y ver el código DANE oficial de cada institución.*  
> 4. *En el módulo de **Fichas**, abramos la Ficha 2501234 de Técnico en Sistemas. Vemos las pestañas de aprendices matriculados y las competencias curriculares.*  
> 5. *En el módulo de **Calificaciones**, carguemos el RAP-01. Miren la sábana interactiva: nos permite marcar de forma masiva 'A' o 'D'. Si la ficha tuviera el periodo cerrado, la regla RN-004 deshabilitaría inmediatamente los controles.*  
> 6. *En **Seguimiento**, el formulario exige una fecha límite si se registran compromisos de mejora, cumpliendo estrictamente la regla RN-006."*

---

### CALIDAD, PRUEBAS Y CONCLUSIONES (Minuto 15:00 - 18:00)
> *"Para garantizar la calidad y confiabilidad del software, programamos y ejecutamos una batería de **13 pruebas unitarias y de integración automatizadas**, cubriendo las reglas de negocio, la prevención de inyección SQL mediante el ORM y la protección contra ataques CSRF. El 100% de las pruebas pasaron con éxito.*  
>  
> *Como conclusión, **SINETEC** no es solo un proyecto académico; es una herramienta factible, viable y sostenible tecnológicamente, construida sobre tecnologías de código abierto sin costos de licenciamiento, que aporta orden, transparencia y trazabilidad a la formación técnica de nuestro departamento.*  
>  
> *Quedo a su completa disposición para responder cualquier pregunta o inquietud del jurado evaluador. ¡Muchas gracias!"*

---

## 3. PREGUNTAS CLAVE QUE SUELE HACER EL JURADO Y CÓMO RESPONDERLAS

1. **Pregunta del Jurado:** *¿Por qué decidieron utilizar Django y Python en lugar de PHP o NodeJS?*  
   * **Tu Respuesta:** *“Elegimos Python y Django porque Django incorpora por defecto una arquitectura de seguridad muy robusta que previene vulnerabilidades comunes como Inyección SQL y CSRF sin tener que programarlas manualmente. Además, su patrón MTV y su ORM permiten un desarrollo modular y limpio que facilita el mantenimiento a largo plazo.”*

2. **Pregunta del Jurado:** *¿SINETEC busca reemplazar a SOFIA Plus o Zajuna?*  
   * **Tu Respuesta:** *“No, instructor. Dejamos muy claro en la delimitación del proyecto que SINETEC no reemplaza las plataformas institucionales nacionales. Su propósito es el seguimiento y gestión operativa local en el Centro de Logística y Promoción Ecoturística del Magdalena, facilitando la recolección previa de datos de visitas y actas en los colegios articulados.”*

3. **Pregunta del Jurado:** *¿Cómo garantizaron que una persona no modifique las notas después de terminado el periodo?*  
   * **Tu Respuesta:** *“Mediante la regla de negocio **RN-004**, implementada a nivel de modelo en el método `clean()` de `JuicioEvaluativo`. Cada vez que se intenta guardar una calificación, el sistema consulta el campo booleano `periodo_cerrado` de la ficha técnica. Si es verdadero, el backend lanza una excepción de validación y la interfaz web deshabilita los controles de guardado.”*
