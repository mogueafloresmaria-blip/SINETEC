# MODELADO Y DISEÑO DEL SISTEMA (UML)
### SISTEMA SINETEC – PROYECTO FORMATIVO ADSI (228106)
**Centro de Logística y Promoción Ecoturística del Magdalena**

---

## 1. INTRODUCCIÓN PEDAGÓGICA AL MODELADO UML

### ¿Qué es UML?
UML (*Unified Modeling Language* o Lenguaje Unificado de Modelado) es un estándar gráfico internacional utilizado en la ingeniería de software para visualizar, especificar, construir y documentar los artefactos de un sistema de información.

### ¿Para qué sirve y por qué lo necesitamos?
Así como un arquitecto dibuja los planos de un edificio antes de poner los primeros ladrillos, en el desarrollo de software necesitamos diagramas UML para:
1. Tener un plano visual claro de cómo interactúan los usuarios con el software.
2. Entender el flujo de la información antes de escribir código.
3. Evitar errores de lógica que costarían semanas de trabajo si se descubrieran durante la programación.
4. Cumplir con los entregables de diseño exigidos por el SENA en la fase de análisis y diseño de ADSI.

---

## 2. DIAGRAMA DE CONTEXTO DEL SISTEMA `[PROPUESTA]`

El diagrama de contexto delimita las fronteras de SINETEC, mostrando los actores externos que interactúan con el software y la información que intercambian:

```mermaid
flowchart TD
    subgraph Actores_Externos ["Entorno / Actores Institucionales"]
        COORD["Coordinador de Articulación"]
        INST["Instructor SENA"]
        DOC["Docente Enlace I.E."]
        EST["Estudiante Media Técnica"]
        ADMIN["Administrador del Sistema"]
    end

    subgraph SINETEC_CORE ["Límite del Sistema: SINETEC (Web)"]
        SISTEMA["SISTEMA DE INFORMACIÓN SINETEC\n(Centro de Logística y Promoción Ecoturística)"]
    end

    COORD -->|"Parametriza colegios, crea fichas, valida cierres"| SISTEMA
    SISTEMA -->|"Consolidados, alertas, reportes PDF/Excel"| COORD

    INST -->|"Registra bitácoras de visita y juicios evaluativos"| SISTEMA
    SISTEMA -->|"Listados de aprendices, estado de periodos"| INST

    DOC -->|"Consulta rendimiento de su colegio, reporta novedades"| SISTEMA
    SISTEMA -->|"Sábana de notas y seguimiento escolar"| DOC

    EST -->|"Consulta estado de resultados evaluados"| SISTEMA
    SISTEMA -->|"Visualización individual de juicios"| EST

    ADMIN -->|"Administra usuarios, roles, seguridad y auditoría"| SISTEMA
    SISTEMA -->|"Registros de auditoría, estado de servicios"| ADMIN
```

---

## 3. DIAGRAMA GENERAL DE CASOS DE USO (UML) `[PROPUESTA]`

Este diagrama agrupa los casos de uso por paquetes funcionales, mostrando qué actor tiene acceso a cada funcionalidad del sistema:

```mermaid
flowchart LR
    %% Actores
    subgraph Actores
        A_Admin((Administrador))
        A_Coord((Coordinador))
        A_Inst((Instructor SENA))
        A_Doc((Docente I.E.))
        A_Est((Estudiante))
    end

    %% Casos de Uso
    subgraph SINETEC ["Casos de Uso de SINETEC"]
        CU01["CU-001: Autenticar Usuario"]
        CU02["CU-002: Gestionar Usuarios y Roles"]
        CU03["CU-003: Gestionar Instituciones Educativas"]
        CU04["CU-004: Gestionar Programas y Fichas"]
        CU05["CU-005: Matricular Aprendices"]
        CU06["CU-006: Registrar Bitácora de Seguimiento"]
        CU07["CU-007: Calificar Resultados de Aprendizaje"]
        CU08["CU-008: Validar y Cerrar Periodos"]
        CU09["CU-009: Consultar Rendimiento por Colegio"]
        CU10["CU-010: Consultar Estado Individual"]
        CU11["CU-011: Generar Reportes PDF / Excel"]
        CU12["CU-012: Visualizar Dashboard Estadístico"]
    end

    %% Relaciones Administrador
    A_Admin --- CU01
    A_Admin --- CU02
    A_Admin --- CU03
    A_Admin --- CU11

    %% Relaciones Coordinador
    A_Coord --- CU01
    A_Coord --- CU03
    A_Coord --- CU04
    A_Coord --- CU05
    A_Coord --- CU08
    A_Coord --- CU11
    A_Coord --- CU12

    %% Relaciones Instructor SENA
    A_Inst --- CU01
    A_Inst --- CU05
    A_Inst --- CU06
    A_Inst --- CU07
    A_Inst --- CU11

    %% Relaciones Docente I.E.
    A_Doc --- CU01
    A_Doc --- CU09

    %% Relaciones Estudiante
    A_Est --- CU01
    A_Est --- CU10
```

---

## 4. DIAGRAMA DE ACTIVIDADES: PROCESO DE SEGUIMIENTO Y EVALUACIÓN `[PROPUESTA]`

Este diagrama modela el flujo de trabajo lógico desde que el instructor realiza una visita técnica a un colegio hasta que los resultados son consolidados y cerrados por la coordinación:

```mermaid
flowchart TD
    Inicio((Inicio)) --> A1["Instructor ingresa a SINETEC"]
    A1 --> A2["Selecciona la Ficha de Media Técnica asignada"]
    A2 --> A3{"¿Qué actividad realizará?"}

    %% Rama de Seguimiento
    A3 -- "Seguimiento / Visita" --> S1["Diligencia datos de bitácora y observaciones"]
    S1 --> S2{"¿Existen novedades de bajo rendimiento?"}
    S2 -- "Sí" --> S3["Registra compromisos obligatorios y fecha de revisión (RN-006)"]
    S2 -- "No" --> S4["Adjunta acta firmada opcionalmente"]
    S3 --> S4
    S4 --> S5["Guarda bitácora de seguimiento"]
    S5 --> Consolidacion

    %% Rama de Evaluaciones
    A3 -- "Evaluación Académica" --> E1{"¿El periodo evaluativo está abierto? (RN-004)"}
    E1 -- "No (Cerrado)" --> E2["Sistema bloquea edición y muestra aviso"]
    E2 --> Fin((Fin))
    E1 -- "Sí (Abierto)" --> E3["Selecciona Competencia y Resultado de Aprendizaje"]
    E3 --> E4["Asigna juicios cualitativos: 'A' o 'D' a los aprendices (RN-003)"]
    E4 --> E5["Guarda juicios evaluativos en base de datos"]
    E5 --> Consolidacion

    %% Consolidación y Cierre
    Consolidacion["Coordinación revisa dashboard y reportes consolidados"] --> C1{"¿Se cumplió el corte del periodo?"}
    C1 -- "No" --> C2["Continúa recepción de registros"]
    C1 -- "Sí" --> C3["Coordinador ejecuta Cierre Oficial del Periodo (RN-004)"]
    C3 --> C4["Generación de acta final en PDF para rectoría del colegio"]
    C4 --> Fin
```

---

## 5. DIAGRAMAS DE SECUENCIA UML `[PROPUESTA]`

Los diagramas de secuencia muestran la interacción cronológica y los mensajes intercambiados entre el Usuario, el Navegador (Frontend), el Servidor (Backend Django) y la Base de Datos (MySQL).

### 5.1 Diagrama de Secuencia: CU-001 Autenticación de Usuario
```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    participant UI as Navegador (Frontend)
    participant V as Vista Django (views.py)
    participant M as Modelo Usuario (models.py)
    participant BD as Servidor MySQL

    U->>UI: Ingresa correo y contraseña
    UI->>V: POST /login/ (credenciales + token CSRF)
    V->>V: Valida presencia de token CSRF
    V->>M: authenticate(username, password)
    M->>BD: SELECT * FROM usuarios WHERE correo = ? LIMIT 1
    BD-->>M: Retorna datos del usuario y hash PBKDF2
    M->>M: Compara hash con algoritmo seguro
    alt Credenciales Válidas y Usuario Activo
        M-->>V: Retorna objeto Usuario válido
        V->>V: login(request, user) - Crea sesión cifrada
        V-->>UI: HTTP 302 Redirigir a /dashboard/
        UI-->>U: Muestra panel de control según su Rol
    else Contraseña Incorrecta o Usuario Inactivo
        M-->>V: Retorna None
        V-->>UI: HTTP 200 Renderiza login con mensaje de error
        UI-->>U: Muestra: "Credenciales no válidas"
    end
```

### 5.2 Diagrama de Secuencia: CU-004 Registro de Bitácora de Seguimiento
```mermaid
sequenceDiagram
    autonumber
    actor I as Instructor SENA
    participant UI as Navegador (Frontend)
    participant V as Vista Django (views.py)
    participant F as Formulario Validación (forms.py)
    participant BD as Servidor MySQL

    I->>UI: Diligencia formulario de visita/seguimiento
    UI->>V: POST /seguimiento/nuevo/ (datos + adjunto)
    V->>V: Verifica rol de Instructor y ficha asignada (RN-005)
    V->>F: Valida campos y regla RN-006 (compromisos obligatorios)
    alt Formulario Válido
        F-->>V: Datos limpios (cleaned_data)
        V->>BD: INSERT INTO seguimiento_bitacora (campos, fecha, usuario_id)
        BD-->>V: Confirmación de registro exitoso (ID generado)
        V->>BD: INSERT INTO auditoria_log (accion="INSERT", tabla="bitacora")
        BD-->>V: Ok
        V-->>UI: Mensaje Toast: "Seguimiento guardado exitosamente"
        UI-->>I: Actualiza lista histórica de seguimientos
    else Errores de Validación (ej. falta compromiso)
        F-->>V: Errores de campo
        V-->>UI: Muestra formulario con errores resaltados en rojo
        UI-->>I: Solicita corrección del campo obligatorio
    end
```

---

## 6. DIAGRAMA DE CLASES DEL DOMINIO `[PROPUESTA]`

Representa las entidades conceptuales del sistema, sus atributos principales, métodos de negocio y las relaciones de cardinalidad:

```mermaid
classDiagram
    class Rol {
        +int id
        +string nombre
        +string descripcion
        +listarPermisos()
    }

    class Usuario {
        +int id
        +string tipo_documento
        +string numero_documento
        +string nombres
        +string apellidos
        +string correo
        +string password_hash
        +string telefono
        +bool esta_activo
        +autenticar()
        +cambiarPassword()
    }

    class InstitucionEducativa {
        +int id
        +string codigo_dane
        +string nombre
        +string municipio
        +string direccion
        +string telefono
        +string rector_nombre
        +string enlace_nombre
        +bool activa
        +obtenerFichasActivas()
    }

    class ProgramaFormacion {
        +int id
        +string codigo_programa
        +string denominacion
        +string version
        +bool activo
        +listarCompetencias()
    }

    class Competencia {
        +int id
        +string codigo
        +text descripcion
    }

    class ResultadoAprendizaje {
        +int id
        +string codigo
        +text descripcion
    }

    class Ficha {
        +int id
        +string codigo_ficha
        +date fecha_inicio
        +date fecha_fin
        +string estado
        +obtenerTotalAprendices()
        +cerrarPeriodo()
    }

    class Matricula {
        +int id
        +date fecha_matricula
        +string grado_escolar
        +string estado_formacion
        +string acudiente_nombre
        +string acudiente_telefono
        +cambiarEstado()
    }

    class BitacoraSeguimiento {
        +int id
        +date fecha_visita
        +string tipo_seguimiento
        +text observaciones
        +text compromisos
        +date fecha_verificacion_compromiso
        +string archivo_adjunto_url
        +registrarSeguimiento()
    }

    class JuicioEvaluativo {
        +int id
        +char juicio_valor
        +date fecha_evaluacion
        +text observaciones
        +bool periodo_cerrado
        +asignarJuicio()
    }

    class RegistroAuditoria {
        +int id
        +datetime fecha_hora
        +string accion
        +string tabla_afectada
        +string registro_id
        +string ip_origen
    }

    %% Relaciones
    Rol "1" <-- "N" Usuario : posee
    Usuario "1" <-- "N" Ficha : lidera_como_instructor
    InstitucionEducativa "1" <-- "N" Ficha : alberga
    ProgramaFormacion "1" <-- "N" Ficha : pertenece_a
    ProgramaFormacion "1" *-- "N" Competencia : contiene
    Competencia "1" *-- "N" ResultadoAprendizaje : desglosa_en
    Ficha "1" <-- "N" Matricula : inscribe
    Usuario "1" <-- "N" Matricula : es_aprendiz
    Ficha "1" <-- "N" BitacoraSeguimiento : registra_en
    Matricula "0..1" <-- "N" BitacoraSeguimiento : aplica_a
    Matricula "1" <-- "N" JuicioEvaluativo : recibe
    ResultadoAprendizaje "1" <-- "N" JuicioEvaluativo : califica
    Usuario "1" <-- "N" JuicioEvaluativo : evalua_como_instructor
    Usuario "1" <-- "N" RegistroAuditoria : realizado_por
```

---

## 7. APORTE A LOS RESULTADOS DE APRENDIZAJE SENA
*Esta actividad contribuye al resultado de aprendizaje relacionado con **diseñar la estructura del software mediante diagramas UML conforme a los requerimientos del cliente**, porque traduce los casos de uso y las reglas de negocio en esquemas visuales de interacción, secuencia y clases que orientan con exactitud la futura programación en Django.*
