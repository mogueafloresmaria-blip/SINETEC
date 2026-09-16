# DIAGRAMAS DE COMPONENTES Y DESPLIEGUE (UML)
### SISTEMA SINETEC – PROYECTO FORMATIVO ADSI (228106)
**Centro de Logística y Promoción Ecoturística del Magdalena**

---

## 1. INTRODUCCIÓN PEDAGÓGICA A LOS DIAGRAMAS FÍSICOS Y ESTRUCTURALES

### ¿Qué es un Diagrama de Componentes?
Muestra la organización del código fuente en bloques lógicos independientes y reutilizables llamados **Componentes** (en Django, cada componente es una *App* o aplicación desacoplada).

### ¿Qué es un Diagrama de Despliegue?
Muestra la arquitectura física de hardware y red: en qué computadores o servidores se ejecuta cada parte del sistema (servidor web, servidor de base de datos, navegador del cliente).

---

## 2. DIAGRAMA DE COMPONENTES DEL SOFTWARE (DJANGO APPS) `[PROPUESTA]`

SINETEC se estructurará modularmente en **7 aplicaciones Django**, evitando proyectos monolíticos desordenados:

```mermaid
flowchart TD
    subgraph SINETEC_CORE ["Proyecto Django: sinetec_project"]
        APP_CORE["App: core\n(Configuración base, navbar, dashboard principal)"]
        APP_USERS["App: usuarios\n(Modelos Usuario, Rol, Login, Perfil)"]
        APP_INST["App: instituciones\n(Colegios, Sedes, Rectores, Enlaces)"]
        APP_ACAD["App: academico\n(Programas, Competencias, RAP, Fichas, Matrícula)"]
        APP_SEG["App: seguimiento\n(Bitácoras de visita, observaciones, compromisos)"]
        APP_EVAL["App: evaluaciones\n(Juicios evaluativos 'A'/'D', cierre de periodos)"]
        APP_REP["App: reportes\n(Exportador PDF y generador de Excel)"]
    end

    subgraph Dependencias_Externas ["Librerías Externas de Python"]
        LIB_MYSQL["mysqlclient / PyMySQL\n(Driver de comunicación con MySQL)"]
        LIB_REPORT["ReportLab / WeasyPrint\n(Generador binario de archivos PDF)"]
        LIB_EXCEL["openpyxl\n(Generador de hojas de cálculo .xlsx)"]
        LIB_ENV["python-decouple / python-dotenv\n(Gestión de variables de entorno seguras)"]
    end

    APP_CORE --> APP_USERS
    APP_CORE --> APP_INST
    APP_CORE --> APP_ACAD
    APP_SEG --> APP_ACAD
    APP_SEG --> APP_USERS
    APP_EVAL --> APP_ACAD
    APP_EVAL --> APP_USERS
    APP_REP --> APP_SEG
    APP_REP --> APP_EVAL
    APP_REP --> LIB_REPORT
    APP_REP --> LIB_EXCEL

    SINETEC_CORE --> LIB_MYSQL
    SINETEC_CORE --> LIB_ENV
```

---

## 3. DIAGRAMA DE DESPLIEGUE DEL SISTEMA `[PROPUESTA]`

El diagrama de despliegue detalla los nodos físicos y de red en un entorno de desarrollo local y su proyección hacia un servidor de red institucional:

```mermaid
flowchart LR
    subgraph Nodo_Cliente ["Nodo: Dispositivo de Usuario (PC / Tablet / Celular)"]
        BROWSER["Navegador Web Moderno\n(Chrome, Firefox, Edge, Safari)\nHTML5 / CSS3 / JavaScript"]
    end

    subgraph Nodo_Servidor_Web ["Nodo: Servidor de Aplicación (Host Windows / Linux)"]
        subgraph Entorno_Python ["Entorno Virtual Python (venv)"]
            DJANGO_SRV["Servidor Web de Aplicación\n(Django WSGI / runserver :8000)"]
            STATIC_FILES["Archivos Estáticos\n(Bootstrap 5 CSS, JS, Iconos)"]
            MEDIA_FILES["Archivos Multimedia / Adjuntos\n(/media/actas_seguimiento/)"]
        end
    end

    subgraph Nodo_Base_Datos ["Nodo: Servidor de Base de Datos"]
        MYSQL_SRV["MySQL Server 8.0\n(Servicio MySQL en Puerto 3306)"]
        DB_FILES[("Base de Datos Física\nsinetec_db (Tablas InnoDB)")]
        MYSQL_SRV --> DB_FILES
    end

    BROWSER -->|"Protocolo HTTP / HTTPS\nPuerto 8000 (o 80/443)"| DJANGO_SRV
    DJANGO_SRV -->|"Peticiones de recursos estáticos"| STATIC_FILES
    DJANGO_SRV -->|"Carga / Descarga de actas"| MEDIA_FILES
    DJANGO_SRV -->|"Conexión TCP/IP Socket\nPuerto 3306 con credenciales cifradas"| MYSQL_SRV
```

---

## 4. ESPECIFICACIÓN DE NODOS Y PUERTOS DE COMUNICACIÓN `[PROPUESTA]`

1. **Nodo Cliente (Navegador Web):**
   * **Requisitos:** Cualquier dispositivo con navegador estándar actualizado y conexión de red (LAN o Internet).
   * **Protocolo:** HTTP (en desarrollo local) o HTTPS (en producción institucional mediante certificado SSL).
2. **Nodo Servidor de Aplicación:**
   * **Software:** Python 3.10+, Entorno Virtual aislado (`venv`), Django 4.2 LTS.
   * **Puerto Predeterminado de Desarrollo:** `8000` (accesible en `http://127.0.0.1:8000/`).
   * **Almacenamiento de Archivos:** Carpeta `static/` para diseño y `media/` para actas de seguimiento y soportes escaneados.
3. **Nodo Servidor de Base de Datos:**
   * **Software:** MySQL Community Server 8.0.
   * **Puerto Predeterminado:** `3306`.
   * **Seguridad de Comunicación:** Usuario con permisos restringidos exclusivamente a la base de datos `sinetec_db`.

---

## 5. APORTE A LOS RESULTADOS DE APRENDIZAJE SENA
*Esta actividad contribuye al resultado de aprendizaje relacionado con **definir los componentes y el modelo de despliegue del sistema de información según los requerimientos de la infraestructura tecnológica**, porque planifica la distribución física, puertos de red y dependencias de software antes de iniciar la instalación de librerías.*
