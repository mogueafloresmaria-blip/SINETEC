# Plan de Implementación: Fase 4 (Diseño UML) y Fase 5 (Base de Datos y Diccionario) - SINETEC

## Contexto y Objetivo
Habiendo culminado y validado formalmente los requerimientos de software (SRS IEEE 830, Reglas de Negocio, Historias de Usuario y Casos de Uso), el siguiente paso metodológico en ADSI es el **Diseño del Sistema** y el **Diseño de la Base de Datos Relacional**.

En estricto cumplimiento de los principios pedagógicos:
* **No se crearán modelos Django en código todavía.**
* **No se construirá el frontend todavía.**
* Primero modelaremos la arquitectura lógica y el esquema relacional en papel/diseño técnico con diagramas UML estándar y normalización de bases de datos.

Este plan establece las actividades para desarrollar:
1. **Fase 4: Diseño del Sistema y Modelado UML** (Diagrama de Contexto, Diagrama General de Casos de Uso, Diagramas de Secuencia, Diagrama de Actividades y Diagrama de Clases del Dominio).
2. **Fase 5: Diseño de Base de Datos y Diccionario de Datos** (Modelo Conceptual, Lógico y Físico para MySQL normalizado en 3FN, Diccionario de Datos exhaustivo tabla por tabla y Script DDL SQL documentado).

---

## User Review Required

> [!IMPORTANT]
> **Aspectos clave que requieren tu revisión y validación:**
> 1. **Normalización Relacional (Tercera Forma Normal - 3FN):** Separación de aprendices, fichas, instituciones, seguimientos y juicios de aprendizaje para evitar redundancia de datos.
> 2. **Convención de Nombres en Base de Datos `[PROPUESTA]`:** Se propone el estándar internacional de nombres en minúsculas con guiones bajos (snake_case) y prefijo por módulo (ej: `inst_colegios`, `acad_fichas`, `seg_bitacoras`, `eval_juicios`).
> 3. **Motor de Almacenamiento MySQL `[PROPUESTA]`:** Uso de motor `InnoDB` por su soporte nativo para integridad referencial (llaves foráneas), transacciones seguras (ACID) y prevención de corrupción de datos.

---

## Open Questions

> [!NOTE]
> Preguntas para orientar el diseño relacional:
> 1. En una visita de seguimiento, ¿el instructor puede registrar observaciones para un grupo completo a la vez (toda la ficha) y también seguimientos individuales para un aprendiz específico? *(En el diseño relacional propondremos que el seguimiento pueda ser opcionalmente grupal o individual).*
> 2. ¿Deseas que preparemos de una vez el archivo de script SQL `.sql` listo para abrir y visualizar en MySQL Workbench cuando configuremos la base de datos?

---

## Proposed Changes

### Documentación y Evidencias Técnicas (`docs/`)

Organización de los nuevos entregables:

```
c:\Users\ADMIN\Documents\SENA ADSI\Proyectos\SINETEC\
└── docs\
    ├── 04_diseno_sistema\
    │   └── modelado_uml_sistema.md
    └── 05_base_de_datos\
        ├── modelo_relacional.md
        ├── diccionario_de_datos.md
        └── script_creacion_inicial_mysql.sql
```

#### [NEW] [modelado_uml_sistema.md](file:///c:/Users/ADMIN/Documents/SENA%20ADSI/Proyectos/SINETEC/docs/04_diseno_sistema/modelado_uml_sistema.md)
Documento técnico de modelado UML que incluirá:
- **Diagrama de Contexto:** Delimitación de fronteras de SINETEC con actores externos.
- **Diagrama General de Casos de Uso:** Relación entre actores y los paquetes funcionales.
- **Diagrama de Actividades:** Flujo del proceso de seguimiento técnico y visitas a colegios.
- **Diagramas de Secuencia:** Flujo paso a paso de autenticación, registro de bitácora y registro de juicio evaluativo.
- **Diagrama de Clases del Dominio:** Entidades del negocio, métodos principales y relaciones de multiplicidad (1:1, 1:N, N:M).

#### [NEW] [modelo_relacional.md](file:///c:/Users/ADMIN/Documents/SENA%20ADSI/Proyectos/SINETEC/docs/05_base_de_datos/modelo_relacional.md)
Diseño conceptual, lógico y físico de la base de datos relacional:
- Diagrama Entidad-Relación (MER) estructurado en Mermaid.
- Justificación de la normalización (Primera, Segunda y Tercera Forma Normal).
- Definición de llaves primarias (`PK`), llaves foráneas (`FK`), índices y reglas de eliminación referencial (`ON DELETE RESTRICT / SET NULL`).

#### [NEW] [diccionario_de_datos.md](file:///c:/Users/ADMIN/Documents/SENA%20ADSI/Proyectos/SINETEC/docs/05_base_de_datos/diccionario_de_datos.md)
Catálogo detallado tabla por tabla con:
- Nombre de la tabla y descripción funcional.
- Lista completa de columnas/campos.
- Tipo de dato MySQL exacto (INT, VARCHAR, TEXT, DATE, DATETIME, BOOLEAN, ENUM).
- Longitud, obligatoriedad (NULL / NOT NULL), llaves y restricciones de validación.

#### [NEW] [script_creacion_inicial_mysql.sql](file:///c:/Users/ADMIN/Documents/SENA%20ADSI/Proyectos/SINETEC/docs/05_base_de_datos/script_creacion_inicial_mysql.sql)
Script DDL de referencia con sintaxis MySQL 8.0 pura, con comentarios pedagógicos línea por línea para entender qué hace cada instrucción (`CREATE DATABASE`, `CREATE TABLE`, `ALTER TABLE ADD CONSTRAINT`, `CREATE INDEX`).

---

## Verification Plan

### Verificación Técnica y Metodológica
- **Validación de Integridad Referencial:** Comprobar que no existan tablas huérfanas ni ciclos de dependencia circular en las llaves foráneas.
- **Trazabilidad Requerimientos -> Base de Datos:** Verificar que cada campo del modelo de datos responda a un requerimiento funcional especificado en el SRS IEEE 830.
- **Sintaxis SQL:** Validar que el script DDL SQL no contenga errores de sintaxis y utilice tipos de datos óptimos para el rendimiento.
- **Aporte a Resultados de Aprendizaje SENA:** Documentar la contribución a las competencias de *“Modelar el sistema mediante UML”* y *“Diseñar la estructura de la base de datos relacional”*.
