# MANUAL TÉCNICO Y DE ARQUITECTURA DEL SISTEMA
### SOFTWARE SINETEC – PROYECTO FORMATIVO ADSI (228106)
**Centro de Logística y Promoción Ecoturística del Magdalena**

---

## 1. INFORMACIÓN GENERAL DEL SOFTWARE `[CONFIRMADO]`

* **Nombre Oficial del Proyecto Formativo:**  
  *“SISTEMAS DE INFORMACIÓN Y DESARROLLO DE SOFTWARE EN EL DEPARTAMENTO DEL MAGDALENA”*
* **Nombre del Software:** **SINETEC** (*Sistema de Integración Técnica Education*).
* **Descripción:** *Sistema de Información para el Seguimiento del Proceso de Integración con la Media Técnica*.
* **Centro de Formación:** Centro de Logística y Promoción Ecoturística del Magdalena.
* **Regional:** Regional Magdalena.
* **Versión de Entrega:** 1.0 Estable.

---

## 2. ARQUITECTURA TECNOLÓGICA Y PILA DE SOFTWARE `[PROPUESTA]`

* **Lenguaje Backend:** Python 3.12 (Tipado dinámico, alto rendimiento y legibilidad).
* **Framework Web:** Django 5.0 LTS (Patrón arquitectónico MTV - *Model-Template-View*).
* **Manejador de Base de Datos:** MySQL Server 8.0 (Motor transaccional InnoDB, cotejamiento `utf8mb4_unicode_ci`).
* **Conector de Base de Datos:** PyMySQL 1.2.0 (100% Python puro, libre de compiladores C++ externos).
* **Gestión de Configuración:** `python-decouple` (Variables de entorno en `.env`).
* **Frontend:** HTML5 semántico, CSS3 personalizado (`sinetec_custom.css`), Bootstrap 5.3 y Bootstrap Icons 1.11.
* **Manipulación de Medios:** Pillow 10.2 (Procesamiento de imágenes y actas escaneadas).
* **Procesamiento de Reportes:** Openpyxl 3.1 (Exportación a hojas de cálculo `.xlsx`).

---

## 3. ESTRUCTURA MODULAR DEL CÓDIGO FUENTE

El proyecto se organiza bajo el principio de alta cohesión y bajo acoplamiento:

```text
SINETEC/
├── sinetec_project/           # Núcleo de configuración del proyecto
│   ├── settings.py            # Variables, apps, middleware, bases de datos y localización
│   ├── urls.py                # Enrutador principal de la aplicación web
│   ├── wsgi.py                # Interfaz de pasarela del servidor web
│   └── tests.py               # Pruebas unitarias y de integración de vistas
├── usuarios/                  # Módulo de Autenticación y Perfiles
│   ├── models.py              # Modelos Rol y PerfilUsuario (RN-001)
│   ├── views.py               # Login, Logout y Dashboard general
│   └── forms.py               # Formulario de login Bootstrap
├── instituciones/             # Módulo de Colegios Articulados
│   ├── models.py              # Modelo InstitucionEducativa (Código DANE único)
│   ├── views.py               # Directorio con filtros, detalle y creación
│   └── forms.py               # Formulario de registro de instituciones
├── academico/                 # Módulo Curricular y de Fichas
│   ├── models.py              # ProgramaFormacion, Competencia, RAP, Ficha, Matricula (RN-002, RN-007)
│   ├── views.py               # Gestión de fichas y matrícula de aprendices
│   └── forms.py               # Formularios FichaForm y MatriculaRapidaForm
├── seguimiento/               # Módulo de Acompañamiento Formativo
│   ├── models.py              # Modelo BitacoraSeguimiento (RN-005, RN-006)
│   ├── views.py               # Registro de visitas con adjuntos y compromisos
│   └── forms.py               # Formulario BitacoraSeguimientoForm
├── evaluaciones/              # Módulo de Juicios Evaluativos
│   ├── models.py              # Modelo JuicioEvaluativo (RN-003, RN-004)
│   ├── views.py               # Sábana masiva de notas y cierre formal de periodos
│   └── forms.py               # Formulario de evaluación
├── templates/                 # Plantillas HTML5 con herencia DTL
│   ├── base.html              # Plantilla maestra con navbar institucional
│   ├── login.html             # Pantalla de acceso seguro
│   ├── dashboard.html         # Panel métrico en tiempo real
│   └── [subcarpetas]/         # Plantillas específicas por cada módulo
├── static/                    # Archivos estáticos de diseño
│   └── css/sinetec_custom.css # Sistema de diseño y variables CSS
├── media/                     # Almacenamiento seguro de actas escaneadas
├── docs/                      # Portafolio completo de documentación de ADSI
└── venv/                      # Entorno virtual aislado de Python
```

---

## 4. PROCEDIMIENTO DE DESPLIEGUE Y MANTENIMIENTO

### Puesta en Marcha en un Servidor Local / Institucional:
1. Clonar o descargar el repositorio en el servidor:
   ```bash
   git clone https://github.com/tu-usuario/sinetec.git
   cd sinetec
   ```
2. Crear y activar el entorno virtual de Python:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Instalar las dependencias exactas:
   ```powershell
   pip install -r requirements.txt
   ```
4. Configurar las variables en el archivo `.env`:
   ```properties
   SECRET_KEY=clave_secreta_de_produccion_muy_larga_y_compleja
   DEBUG=False
   USE_MYSQL=True
   DB_NAME=sinetec_db
   DB_USER=usuario_sinetec
   DB_PASSWORD=clave_segura_mysql
   DB_HOST=localhost
   DB_PORT=3306
   ```
5. Aplicar migraciones en la base de datos MySQL:
   ```powershell
   python manage.py migrate
   ```
6. Recolectar archivos estáticos para el servidor web:
   ```powershell
   python manage.py collectstatic --noinput
   ```
7. Iniciar el servicio mediante servidor WSGI (Gunicorn / Waitress):
   ```powershell
   waitress-serve --port=8000 sinetec_project.wsgi:application
   ```

---

## 5. POLÍTICAS DE SEGURIDAD IMPLEMENTADAS

* **Autenticación y Cifrado:** Uso de PBKDF2 con salado criptográfico para almacenamiento de contraseñas en MySQL.
* **Control de Acceso Basado en Roles (RBAC):** Decoradores `@login_required` y verificaciones de perfil institucional en cada vista sensible.
* **Prevención de Ataques Web:**
  * Inyección SQL mitigada al 100% mediante el ORM de Django con consultas parametrizadas.
  * Cross-Site Scripting (XSS) prevenido mediante escape automático de variables en plantillas DTL.
  * Cross-Site Request Forgery (CSRF) bloqueado con tokens criptográficos obligatorios por formulario.
* **Integridad Referencial:** Forzada en base de datos mediante restricciones `ON DELETE RESTRICT` en tablas principales para evitar borrado accidental de expedientes académicos.

---

## 6. APORTE A LOS RESULTADOS DE APRENDIZAJE SENA
*Esta actividad contribuye al resultado de aprendizaje relacionado con **elaborar el manual técnico y de arquitectura del sistema de información**, porque documenta la infraestructura, dependencias, flujo modular y procedimientos de mantenimiento que garantizan la sostenibilidad tecnológica del software.*
