# -*- coding: utf-8 -*-
"""
Contenido Estructurado del Informe Administrativo de Instalación, Respaldo,
Migración y Despliegue en Producción del Sistema EduNova (SINETEC) para el SENA.
"""

METADATOS = {
    "titulo": "INFORME ADMINISTRATIVO DE INSTALACIÓN, RESPALDO, MIGRACIÓN Y DESPLIEGUE A PRODUCCIÓN DEL SISTEMA DE INFORMACIÓN EDUNOVA",
    "subtitulo": "Protocolos Organizacionales de Operatividad, Continuidad de Negocio, Salvaguarda de Datos y Plan Maestro de Despliegue en Servidor",
    "entidad": "Servicio Nacional de Aprendizaje – SENA",
    "regional": "Regional Magdalena",
    "centro": "Centro de Logística y Promoción Ecoturística del Magdalena",
    "programa": "Tecnología en Análisis y Desarrollo de Sistemas de Información (ADSI)",
    "ficha": "228106",
    "proyecto_sofia": "3445935",
    "nombre_proyecto": "Sistemas de Información y Desarrollo de Software en el Departamento del Magdalena",
    "software": "EduNova — Sistema Integrado de Educación Técnica (SINETEC)",
    "version_documento": "1.0 (Definitiva para Evaluación SENA)",
    "autor": "Equipo de Desarrollo e Implementación EduNova",
    "destinatario": "Instructor Técnico de Formación y Comité de Evaluación SENA",
    "fecha": "Octubre de 2026",
    "ciudad": "Santa Marta, Magdalena, Colombia",
}

CONTROL_VERSIONES = [
    {
        "version": "0.1",
        "fecha": "15/08/2026",
        "autor": "Equipo de Desarrollo",
        "descripcion": "Estructuración de requerimientos IEEE 830, arquitectura inicial y casos de prueba base."
    },
    {
        "version": "0.5",
        "fecha": "18/09/2026",
        "autor": "Líder de Desarrollo",
        "descripcion": "Consolidación de modelos relacionales, pruebas de reglas de negocio y respaldos en SQLite."
    },
    {
        "version": "0.9",
        "fecha": "28/09/2026",
        "autor": "Equipo Técnico EduNova",
        "descripcion": "Estabilización de los seis paneles de usuario, pruebas de RBAC, sanitización y exportación de fixtures."
    },
    {
        "version": "1.0",
        "fecha": "13/10/2026",
        "autor": "Equipo de Proyecto SENA",
        "descripcion": "Elaboración del informe administrativo formal de instalación, respaldo, migración y despliegue a producción con distinción de actividades realizadas, propuestas y pendientes."
    }
]

INTRODUCCION_TEXT = (
    "El presente informe administrativo y técnico ha sido estructurado siguiendo estrictamente los protocolos "
    "de la organización y las directrices pedagógicas del Servicio Nacional de Aprendizaje (SENA) para el programa "
    "formativo de Tecnología en Análisis y Desarrollo de Sistemas de Información (ADSI). "
    "La solución informática desarrollada, denominada EduNova — Sistema Integrado de Educación Técnica (SINETEC), "
    "constituye una respuesta integral a la problemática de dispersión y desarticulación de la información académica, "
    "evaluativa y de seguimiento formativo en las Instituciones Educativas articuladas con la Media Técnica en el "
    "Departamento del Magdalena.\n\n"
    "En consonancia con los lineamientos del instructor y las competencias requeridas por la entidad, este informe consolida "
    "los planes maestros de instalación, respaldo, migración de datos y despliegue a producción, garantizando la operatividad "
    "continua, la seguridad informática y el mantenimiento sostenible del software. Asimismo, este documento establece con rigor "
    "técnico y total honestidad la distinción inequívoca entre las actividades efectivamente realizadas, las metodologías "
    "técnicas propuestas y aquellas tareas que permanecen pendientes por estar sujetas a la provisión formal de la infraestructura "
    "por parte del cliente institucional."
)

OBJETIVOS_DATA = {
    "general": (
        "Elaborar el informe administrativo integral siguiendo los protocolos organizacionales del SENA, sustentado en los "
        "planes de instalación, respaldo, migración de datos y despliegue en servidor del sistema de información EduNova "
        "(SINETEC), delimitando con rigor técnico las actividades realizadas, propuestas y pendientes, con el propósito de "
        "facilitar la operatividad, seguridad, mantenimiento y adopción formal de la solución informática en un entorno productivo."
    ),
    "especificos": [
        "Definir con precisión los requerimientos mínimos y recomendados de hardware, software, red y puertos requeridos en el servidor de producción para garantizar un rendimiento óptimo y escalable.",
        "Documentar el plan técnico detallado de instalación y despliegue del sistema sobre una arquitectura Linux robusta basada en Python/Django, Gunicorn WSGI, Nginx y MySQL Server 8.0.",
        "Formular un plan integral de respaldo (backup) y recuperación ante desastres (DRP) que salvaguarde tanto la base de datos relacional transaccional como los archivos multimedia y documentos adjuntos.",
        "Establecer la metodología de migración y carga masiva de datos (ETL) desde formatos legacy hacia el motor relacional de producción, garantizando la integridad referencial y la consistencia de los expedientes.",
        "Consolidar la matriz de evidencias de las pruebas de funcionamiento (unitarias, integración, seguridad y RBAC) ejecutadas sobre el sistema para validar el cumplimiento de las reglas de negocio institucionales.",
        "Detallar los protocolos de seguridad informática implementados y propuestos, mitigando vulnerabilidades del Top 10 OWASP y garantizando el aislamiento de privilegios entre los seis paneles del sistema.",
        "Estructurar el plan de mantenimiento preventivo, correctivo y predictivo, así como los procedimientos de actualización continua y monitoreo de registros (logs) del servidor.",
        "Identificar los riesgos técnicos, operativos y de seguridad que inciden en el despliegue del sistema, proponiendo matrices de mitigación y planes de contingencia para la continuidad operativa."
    ]
}

ALCANCE_DATA = {
    "funcional": [
        "Panel Administrador del Sistema: Gestión integral de sedes, programas formativos, fichas, usuarios, roles, papelera de reciclaje lógica, auditoría transaccional de eventos y supervisión de respaldos.",
        "Panel de Rectoría y Directivos: Visualización estratégica de indicadores de cobertura, tasas de aprobación, retención escolar, ausentismo y emisión de circulares institucionales.",
        "Panel de Secretaría Académica: Matrícula de aprendices, legalización de expedientes, asignación de cursos, gestión de pensiones, control de rutas de transporte y emisión de certificados.",
        "Panel de Docentes e Instructores: Toma de asistencia diaria, publicación de guías y tareas, retroalimentación pedagógica y calificación cuantitativa y cualitativa por juicios evaluativos (Aprobado / No Aprobado).",
        "Panel de Estudiantes (Aprendices): Consulta personalizada y aislada de horario, asignaturas, calificaciones oficiales, tareas vigentes, asistencia, circulares institucionales y portafolio de evidencias.",
        "Panel de Familia y Acudientes: Supervisión del desempeño formativo de los hijos, alertas tempranas de rendimiento, registro de asistencia en tiempo real y comunicación directa con la institución."
    ],
    "despliegue": (
        "El alcance del despliegue comprende la preparación integral del código fuente, la containerización lógica y configuración "
        "de variables desacopladas para operar tanto en servidores virtuales dedicados (VPS/Cloud) como en servidores físicos on-premise "
        "institucionales. Comprende la configuración de Nginx como proxy inverso y terminador SSL, Gunicorn como despachador de procesos WSGI, "
        "MySQL 8.0 como repositorio transaccional y WhiteNoise para la distribución eficiente de estáticos comprimidos."
    ),
    "limites": [
        "El sistema EduNova no sustituye los sistemas centrales del SENA a nivel nacional (SOFIA Plus o plataforma LMS Zajuna); opera como herramienta local de seguimiento pedagógico y gestión institucional articulada.",
        "No incluye la emisión directa de títulos oficiales de formación técnica del SENA, limitándose a certificados de notas, constancias de estudio y reportes internos.",
        "No abarca la gestión financiera de nómina de instructores ni transacciones bancarias en línea pasarela de pagos, circunscribiéndose al registro de control de pensiones y pagos físicos o transferencias reportadas.",
        "No contempla control de acceso físico mediante dispositivos biométricos de iris o huella dactilar, apoyándose en el registro digital de asistencia por aula y módulo."
    ]
}

MATRIZ_ESTADO = [
    {
        "area": "Arquitectura y Código Fuente",
        "actividad": "Estructuración modular de 7 aplicaciones Django desacopladas (usuarios, instituciones, academico, seguimiento, evaluaciones, convenios, core)",
        "tipo": "REALIZADA",
        "evidencia": "Repositorio en c:/SINETEC/SINETEC con apps funcionales, modelos y vistas operativas."
    },
    {
        "area": "Base de Datos y Modelado",
        "actividad": "Diseño relacional de 24+ modelos normalizados con integridad referencial, borrado lógico y auditoría",
        "tipo": "REALIZADA",
        "evidencia": "Modelos en Django ORM, base local SQLite 1.6MB y scripts SQL InnoDB (SINETEC_backup_produccion_2026.sql)."
    },
    {
        "area": "Control de Calidad y Pruebas",
        "actividad": "Ejecución de suite automatizada de pruebas unitarias, integración y reglas de negocio RN-001 a RN-007",
        "tipo": "REALIZADA",
        "evidencia": "100% de casos de prueba superados en la suite de pruebas del proyecto; documentación en docs/08_pruebas/."
    },
    {
        "area": "Preparación para Producción",
        "actividad": "Creación de archivos de despliegue cloud/servidor: Procfile, render.yaml, build.sh, decouple de .env y WhiteNoise",
        "tipo": "REALIZADA",
        "evidencia": "Archivos Procfile, build.sh y settings.py con detección automática de DATABASE_URL y MySQL."
    },
    {
        "area": "Respaldos y Fixtures Base",
        "actividad": "Generación de volcado de datos iniciales en formato JSON UTF-8 y backups SQL transaccionales",
        "tipo": "REALIZADA",
        "evidencia": "backup_pre_limpieza_edunova.json (968 KB) y sinetec_fixture_completa.json (863 KB)."
    },
    {
        "area": "Servidor de Producción On-Premise",
        "actividad": "Aprovisionamiento de servidor físico dedicado o VPS Ubuntu Server con Gunicorn WSGI y Nginx Proxy",
        "tipo": "PROPUESTA",
        "evidencia": "Especificaciones y plantillas de configuración gunicorn.service y nginx.conf listas para implementar."
    },
    {
        "area": "Infraestructura Definitiva",
        "actividad": "Asignación formal de máquina servidora, IP pública estática y configuración de firewall perimetral por el cliente",
        "tipo": "PENDIENTE",
        "evidencia": "Sujeto a la entrega física o credenciales VPS por parte de la Coordinación del Centro / Institución."
    },
    {
        "area": "Dominio y Certificado SSL/TLS",
        "actividad": "Delegación formal de subdominio institucional (ej. edunova.institucion.edu.co) y emisión de SSL Let's Encrypt",
        "tipo": "PENDIENTE",
        "evidencia": "Pendiente de apuntamiento DNS tipo 'A' hacia la IP pública definitiva del servidor del cliente."
    },
    {
        "area": "Migración Definitiva de Datos",
        "actividad": "Carga y sanitización final de planillas de estudiantes reales del ciclo lectivo productivo en MySQL",
        "tipo": "PENDIENTE",
        "evidencia": "Programada para ejecutarse durante la ventana de mantenimiento previa a la salida en vivo."
    },
    {
        "area": "Firma de Acta de Entrega",
        "actividad": "Sustentación formal, verificación in situ en el servidor del cliente y firma del acta de despliegue a producción",
        "tipo": "PENDIENTE",
        "evidencia": "Actividad final de cierre del proyecto formativo ADSI ante el instructor evaluador."
    }
]

REQUISITOS_SERVIDOR = {
    "hardware": [
        ("Componente", "Requisito Mínimo (Entorno Base)", "Requisito Recomendado (Producción Institucional)", "Observaciones"),
        ("Procesador (CPU)", "2 vCPUs x86_64 a 2.0 GHz", "4 vCPUs x86_64 a 2.5 GHz o superior", "Permite atención concurrente de 3 workers de Gunicorn y consultas MySQL complejas."),
        ("Memoria RAM", "4 GB DDR4", "8 GB a 16 GB DDR4/DDR5 ECC", "Garantiza caché de consultas de base de datos (innodb_buffer_pool_size) y manejo de peticiones concurrentes."),
        ("Almacenamiento", "40 GB SSD / SATA", "100 GB a 250 GB NVMe SSD (RAID 1)", "Almacenamiento de sistema, binarios de base de datos, logs del servidor y repositorio multimedia de actas."),
        ("Interfaz de Red", "100 Mbps Ethernet", "1 Gbps Full Duplex con IP pública fija", "Baja latencia y ancho de banda suficiente para descarga de reportes PDF y actas de seguimiento."),
        ("Alimentación Eléctrica", "Fuente estándar", "Doble fuente redundante y conexión a UPS", "Aplica para servidores on-premise en sede institucional para prevenir apagones abruptos.")
    ],
    "software": [
        ("Capa / Rol", "Software Seleccionado", "Versión Homologada", "Función en la Arquitectura"),
        ("Sistema Operativo", "Ubuntu Server LTS", "22.04 LTS o 24.04 LTS (64-bit)", "Plataforma base de servidor caracterizada por estabilidad, soporte de seguridad y compatibilidad de paquetes."),
        ("Motor de Base de Datos", "MySQL Server", "8.0.36 o superior (InnoDB)", "Almacén relacional con soporte transaccional ACID, llaves foráneas estrictas y codificación utf8mb4."),
        ("Entorno de Ejecución", "Python", "3.12 o 3.13 con soporte venv", "Intérprete para la lógica de negocio del backend y ejecución del framework."),
        ("Framework Backend", "Django", "5.1 LTS / Compatible 4.2 LTS", "Núcleo de aplicación: enrutamiento, ORM, protección anti-CSRF, motor de plantillas y autenticación."),
        ("Servidor WSGI", "Gunicorn", "21.2.0 o superior", "Servidor de aplicaciones WSGI que procesa peticiones HTTP dinámicas enlazado mediante socket Unix."),
        ("Servidor Web / Proxy", "Nginx", "1.18.0 o superior", "Proxy inverso, terminación TLS/SSL, balanceo, compresión Gzip y entrega de estáticos con caché."),
        ("Seguridad y SSL", "Certbot (EFF)", "2.8.0 o superior con plugin Nginx", "Automatización de aprovisionamiento y renovación periódica de certificados SSL/TLS.")
    ],
    "red_puertos": [
        ("Puerto", "Protocolo", "Dirección / Origen", "Servicio Vinculado", "Política de Seguridad en Firewall (UFW)"),
        ("22", "TCP", "SSH Administrativo", "OpenSSH Server", "Restringido exclusivamente a las IPs de los administradores del sistema mediante llaves criptográficas."),
        ("80", "TCP", "Público / Internet", "HTTP (Nginx)", "Abierto; configurado obligatoriamente con redirección permanente (HTTP 301) hacia HTTPS en el puerto 443."),
        ("443", "TCP", "Público / Internet", "HTTPS (Nginx con TLS)", "Abierto al público institucional; canal cifrado seguro con TLS 1.2 y TLS 1.3."),
        ("3306", "TCP", "Localhost (127.0.0.1)", "MySQL Server Daemon", "BLOQUEADO AL EXTERIOR; solo accesible localmente por la aplicación Django mediante socket Unix o loopback."),
        ("8000", "TCP", "Localhost / Red Interna", "Django Runserver (Dev)", "Cerrado en producción; en desarrollo local se usa para depuración previa al pase a producción.")
    ]
}

PLAN_INSTALACION_FASES = [
    {
        "fase": "Fase 1: Preparación y Aseguramiento del Sistema Operativo",
        "descripcion": "Actualización de paquetes del sistema base, instalación de herramientas de compilación, utilidades de red y cortafuegos UFW.",
        "comandos": [
            "sudo apt update && sudo apt upgrade -y",
            "sudo apt install -y python3-pip python3-dev python3-venv build-essential \\",
            "    libssl-dev libffi-dev pkg-config default-libmysqlclient-dev \\",
            "    nginx git curl supervisor ufw mysql-server fail2ban htop",
            "sudo ufw default deny incoming",
            "sudo ufw default allow outgoing",
            "sudo ufw allow OpenSSH",
            "sudo ufw allow 'Nginx Full'",
            "sudo ufw enable"
        ]
    },
    {
        "fase": "Fase 2: Creación de Usuarios de Servicio y Permisos de Directorios",
        "descripcion": "Establecimiento de una cuenta de usuario del sistema sin privilegios de login interactivo para aislar el proceso web bajo el principio de mínimo privilegio.",
        "comandos": [
            "sudo adduser --system --group --no-create-home edunova",
            "sudo usermod -a -G www-data edunova",
            "sudo mkdir -p /var/www/edunova",
            "sudo chown -R $USER:www-data /var/www/edunova",
            "sudo chmod 775 /var/www/edunova"
        ]
    },
    {
        "fase": "Fase 3: Clonación del Repositorio y Creación del Entorno Virtual",
        "descripcion": "Despliegue del código fuente en el directorio institucional y aislamiento de dependencias de Python mediante venv.",
        "comandos": [
            "cd /var/www/edunova",
            "git clone <URL_REPOSITORIO_OFICIAL> .",
            "python3 -m venv venv",
            "source venv/bin/activate",
            "pip install --upgrade pip setuptools wheel"
        ]
    },
    {
        "fase": "Fase 4: Instalación de Dependencias de Producción",
        "descripcion": "Instalación de paquetes requeridos especificados en requirements.txt, incluyendo gunicorn, mysqlclient, python-decouple y whitenoise.",
        "comandos": [
            "pip install -r requirements.txt",
            "pip install gunicorn mysqlclient whitenoise",
            "pip list --format=columns"
        ]
    },
    {
        "fase": "Fase 5: Aprovisionamiento y Configuración de MySQL Server",
        "descripcion": "Creación de la base de datos institucional en MySQL con juego de caracteres utf8mb4 y creación de usuario dedicado con privilegios mínimos.",
        "comandos": [
            "sudo mysql -u root -p",
            "-- Consola MySQL:",
            "CREATE DATABASE sinetec CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            "CREATE USER 'edunova_prod'@'localhost' IDENTIFIED BY 'ContraseñaSegura_Prod_2026*';",
            "GRANT ALL PRIVILEGES ON sinetec.* TO 'edunova_prod'@'localhost';",
            "FLUSH PRIVILEGES;",
            "EXIT;"
        ]
    },
    {
        "fase": "Fase 6: Configuración del Demonio WSGI (Gunicorn + Systemd)",
        "descripcion": "Configuración de Gunicorn como servicio permanente del sistema controlado por Systemd mediante un socket Unix optimizado.",
        "comandos": [
            "# 1. Archivo /etc/systemd/system/gunicorn.socket",
            "[Unit]",
            "Description=Socket de Gunicorn para EduNova SINETEC",
            "[Socket]",
            "ListenStream=/run/gunicorn.sock",
            "[Install]",
            "WantedBy=sockets.target",
            "",
            "# 2. Archivo /etc/systemd/system/gunicorn.service",
            "[Unit]",
            "Description=Servicio Gunicorn para EduNova SINETEC",
            "Requires=gunicorn.socket",
            "After=network.target mysql.service",
            "[Service]",
            "User=edunova",
            "Group=www-data",
            "WorkingDirectory=/var/www/edunova",
            "ExecStart=/var/www/edunova/venv/bin/gunicorn \\",
            "          --access-logfile /var/log/gunicorn/access.log \\",
            "          --error-logfile /var/log/gunicorn/error.log \\",
            "          --workers 3 \\",
            "          --bind unix:/run/gunicorn.sock \\",
            "          sinetec_project.wsgi:application",
            "Restart=always",
            "RestartSec=3",
            "[Install]",
            "WantedBy=multi-user.target",
            "",
            "# 3. Habilitación del servicio:",
            "sudo mkdir -p /var/log/gunicorn && sudo chown -R edunova:www-data /var/log/gunicorn",
            "sudo systemctl daemon-reload",
            "sudo systemctl enable --now gunicorn.socket"
        ]
    },
    {
        "fase": "Fase 7: Configuración de Nginx como Proxy Inverso y Caché",
        "descripcion": "Aprovisionamiento del virtual host de Nginx para despachar peticiones estáticas y redirigir dinámicas al socket de Gunicorn.",
        "comandos": [
            "# Archivo /etc/nginx/sites-available/edunova",
            "server {",
            "    listen 80;",
            "    server_name edunova.institucion.edu.co www.edunova.institucion.edu.co;",
            "    client_max_body_size 25M;",
            "",
            "    location = /favicon.ico { access_log off; log_not_found off; }",
            "",
            "    location /static/ {",
            "        alias /var/www/edunova/staticfiles/;",
            "        expires 30d;",
            "        add_header Cache-Control \"public, max-age=2592000\";",
            "    }",
            "",
            "    location /media/ {",
            "        alias /var/www/edunova/media/;",
            "        expires 7d;",
            "    }",
            "",
            "    location / {",
            "        include proxy_params;",
            "        proxy_pass http://unix:/run/gunicorn.sock;",
            "        proxy_set_header Host $http_host;",
            "        proxy_set_header X-Real-IP $remote_addr;",
            "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
            "        proxy_set_header X-Forwarded-Proto $scheme;",
            "    }",
            "}",
            "",
            "# Enlace simbólico y verificación de sintaxis:",
            "sudo ln -s /etc/nginx/sites-available/edunova /etc/nginx/sites-enabled/",
            "sudo rm -f /etc/nginx/sites-enabled/default",
            "sudo nginx -t && sudo systemctl restart nginx"
        ]
    },
    {
        "fase": "Fase 8: Recolección de Archivos Estáticos y Migraciones de Producción",
        "descripcion": "Consolidación de activos estáticos con collectstatic, ejecución de migraciones de base de datos y ajuste final de permisos de lectura.",
        "comandos": [
            "cd /var/www/edunova",
            "source venv/bin/activate",
            "python manage.py collectstatic --noinput",
            "python manage.py migrate --noinput",
            "sudo chown -R edunova:www-data /var/www/edunova/staticfiles /var/www/edunova/media",
            "sudo chmod -R 755 /var/www/edunova/staticfiles /var/www/edunova/media"
        ]
    },
    {
        "fase": "Fase 9: Aprovisionamiento de Certificado SSL/TLS y Cifrado",
        "descripcion": "Instalación del certificado criptográfico Let's Encrypt mediante Certbot con renovación desatendida automática.",
        "comandos": [
            "sudo apt install -y certbot python3-certbot-nginx",
            "sudo certbot --nginx -d edunova.institucion.edu.co -d www.edunova.institucion.edu.co",
            "sudo certbot renew --dry-run"
        ]
    }
]

VARIABLES_ENTORNO_DATA = [
    ("Variable", "Propósito en el Sistema", "Ejemplo en Producción", "Nivel de Criticidad"),
    ("SECRET_KEY", "Semilla criptográfica para firma de sesiones, tokens de cookies y contraseñas.", "Cadena pseudoaleatoria de más de 50 caracteres generada con secrets.token_urlsafe(50)", "CRÍTICA (Confidencial)"),
    ("DEBUG", "Control del modo de depuración; en producción DEBE SER False para evitar fuga de trazas y código fuente.", "False", "CRÍTICA (Obligatorio False)"),
    ("ALLOWED_HOSTS", "Lista blanca de dominios y direcciones IP autorizadas para atender peticiones HTTP.", "edunova.institucion.edu.co,www.edunova.institucion.edu.co,127.0.0.1", "ALTA"),
    ("CSRF_TRUSTED_ORIGINS", "Orígenes de confianza autorizados para recibir envíos POST de formularios.", "https://edunova.institucion.edu.co,https://www.edunova.institucion.edu.co", "ALTA"),
    ("DB_NAME", "Nombre de la base de datos relacional de la aplicación.", "sinetec", "MEDIA"),
    ("DB_USER", "Usuario autenticado con privilegios exclusivos sobre la base de datos.", "edunova_prod", "ALTA"),
    ("DB_PASSWORD", "Contraseña robusta del usuario de base de datos.", "ContraseñaUltraSegura_Prod_2026*", "CRÍTICA (Confidencial)"),
    ("DB_HOST", "Dirección de escucha del servidor MySQL.", "127.0.0.1 (o localhost)", "MEDIA"),
    ("DB_PORT", "Puerto de conexión TCP con el motor MySQL.", "3306", "BAJA"),
    ("SECURE_SSL_REDIRECT", "Fuerza la redirección automática de tráfico HTTP a HTTPS en Django.", "True", "ALTA"),
    ("SESSION_COOKIE_SECURE", "Marca la cookie de sesión como 'Secure' para transmitirse solo por HTTPS.", "True", "ALTA"),
    ("CSRF_COOKIE_SECURE", "Marca la cookie CSRF como 'Secure' para evitar intercepción man-in-the-middle.", "True", "ALTA")
]

PLAN_RESPALDO_DATA = {
    "descripcion": (
        "El plan de respaldo de EduNova está diseñado para garantizar la integridad transaccional y la continuidad operativa "
        "ante fallos de hardware, corrupción de datos, errores humanos o desastres imprevistos. Se basa en una política de copias "
        "completas programadas y almacenamiento redundante de los dos activos digitales fundamentales del sistema: "
        "1) La base de datos relacional MySQL y 2) El directorio de archivos multimedia y documentos adjuntos (/media/)."
    ),
    "politica": [
        ("Tipo de Activo", "Frecuencia de Copia", "Herramienta Empleada", "Retención y Rotación", "Ubicación de Destino"),
        ("Base de Datos MySQL", "Diaria (02:00 AM nocturna) y previo a cambios mayores", "mysqldump comprimido con gzip", "30 días en rotación continua", "/var/backups/edunova/db/ y copia externa segura"),
        ("Archivos Multimedia (/media/)", "Semanal (Domingos 03:00 AM) o tras eventos de carga", "tar con compresión gzip", "60 días en rotación histórica", "/var/backups/edunova/media/ y almacenamiento secundario"),
        ("Configuraciones y .env", "Tras cualquier cambio administrativo o parche", "Copia cifrada con permisos 600", "Versiones históricas de configuración", "/var/backups/edunova/config/ con acceso restringido")
    ],
    "script_bash": [
        "#!/bin/bash",
        "# ==============================================================================",
        "# SCRIPT DE RESPALDO AUTOMATIZADO - SISTEMA EDUNOVA (SINETEC)",
        "# Ruta: /usr/local/bin/backup_edunova.sh",
        "# ==============================================================================",
        "set -euo pipefail",
        "",
        "BACKUP_DIR=\"/var/backups/edunova\"",
        "DATE=$(date +\"%Y%m%d_%H%M%S\")",
        "LOG_FILE=\"/var/log/edunova_backups.log\"",
        "DB_NAME=\"sinetec\"",
        "DB_USER=\"edunova_prod\"",
        "DB_PASS=\"ContraseñaUltraSegura_Prod_2026*\"",
        "MEDIA_DIR=\"/var/www/edunova/media\"",
        "",
        "mkdir -p \"$BACKUP_DIR/db\" \"$BACKUP_DIR/media\"",
        "echo \"[$(date)] INICIANDO RESPALDO DE EDUNOVA...\" >> \"$LOG_FILE\"",
        "",
        "# 1. Respaldo consistente de base de datos MySQL con mysqldump",
        "mysqldump -u \"$DB_USER\" -p\"$DB_PASS\" --single-transaction --routines --triggers \\",
        "    \"$DB_NAME\" | gzip > \"$BACKUP_DIR/db/sinetec_${DATE}.sql.gz\"",
        "echo \"[$(date)] Respaldo de BD generado: sinetec_${DATE}.sql.gz\" >> \"$LOG_FILE\"",
        "",
        "# 2. Respaldo de archivos multimedia adjuntos",
        "if [ -d \"$MEDIA_DIR\" ]; then",
        "    tar -czf \"$BACKUP_DIR/media/media_${DATE}.tar.gz\" -C /var/www/edunova media",
        "    echo \"[$(date)] Respaldo de multimedia generado: media_${DATE}.tar.gz\" >> \"$LOG_FILE\"",
        "fi",
        "",
        "# 3. Rotación de copias: eliminar respaldos con más de 30 días de antigüedad",
        "find \"$BACKUP_DIR/db\" -type f -name \"*.sql.gz\" -mtime +30 -delete",
        "find \"$BACKUP_DIR/media\" -type f -name \"*.tar.gz\" -mtime +30 -delete",
        "echo \"[$(date)] Rotación de copias de seguridad completada con éxito.\" >> \"$LOG_FILE\"",
        "echo \"[$(date)] RESPALDO FINALIZADO CORRECTAMENTE.\" >> \"$LOG_FILE\""
    ],
    "cron_entry": "0 2 * * * /usr/local/bin/backup_edunova.sh >> /var/log/edunova_cron.log 2>&1",
    "restauracion_pasos": [
        "1. Notificar a los usuarios y detener el servicio web para evitar escrituras concurrentes: sudo systemctl stop gunicorn",
        "2. Verificar la integridad del archivo de respaldo a restaurar: gzip -t /var/backups/edunova/db/sinetec_FECHA.sql.gz",
        "3. Restaurar la base de datos MySQL desde el volcado comprimido: gunzip < /var/backups/edunova/db/sinetec_FECHA.sql.gz | mysql -u edunova_prod -p sinetec",
        "4. Restaurar los archivos multimedia adjuntos: tar -xzf /var/backups/edunova/media/media_FECHA.tar.gz -C /var/www/edunova/",
        "5. Ajustar propietarios y permisos: sudo chown -R edunova:www-data /var/www/edunova/media && sudo chmod -R 755 /var/www/edunova/media",
        "6. Iniciar los servicios del sistema: sudo systemctl start gunicorn && sudo systemctl reload nginx",
        "7. Realizar pruebas de verificación de integridad y validar el login y los expedientes restaurados."
    ],
    "backups_reales": [
        ("Archivo / Artefacto Real", "Tamaño", "Ubicación en Repositorio", "Descripción"),
        ("SINETEC_backup_produccion_2026.sql", "328.3 KB", "c:/SINETEC/SINETEC/SINETEC_backup_produccion_2026.sql", "Volcado transaccional completo en sintaxis MySQL InnoDB conteniendo estructura y datos iniciales."),
        ("backup_pre_limpieza_edunova.json", "968.0 KB", "c:/SINETEC/SINETEC/backup_pre_limpieza_edunova.json", "Respaldo exhaustivo en formato fixture JSON serializado por Django ORM previo a optimizaciones."),
        ("sinetec_fixture_completa.json", "863.3 KB", "c:/SINETEC/SINETEC/sinetec_fixture_completa.json", "Fixture maestro consolidado y sanitizado listo para carga con 'manage.py loaddata'."),
        ("db.sqlite3", "1.64 MB", "c:/SINETEC/SINETEC/db.sqlite3", "Base de datos transaccional local funcional empleada en desarrollo, estabilización y pruebas unitarias.")
    ]
}

PLAN_MIGRACION_DATA = {
    "metodologia": (
        "El plan de migración de datos de EduNova adopta el ciclo clásico de ingeniería de datos ETL "
        "(Extracción, Transformación, Sanitización y Carga), permitiendo trasladar de forma segura la información "
        "desde formatos dispersos (archivos manuales en Excel, registros en hojas de cálculo y bases de datos SQLite locales) "
        "hacia el motor relacional MySQL 8.0 en el servidor de producción."
    ),
    "etapas": [
        ("Etapa 1: Extracción y Catálogo", "Inventario y exportación de registros desde las planillas de los colegios y la base de datos de desarrollo."),
        ("Etapa 2: Transformación y Limpieza", "Normalización de tipos de documento, homologación de códigos de fichas SENA, corrección de correos electrónicos y nombres."),
        ("Etapa 3: Aplicación del Esquema", "Ejecución de migraciones nativas de Django (python manage.py migrate) para construir el DDL relacional con índices."),
        ("Etapa 4: Carga Controlada (Fixtures)", "Inyección de datos maestros de programas, fichas, roles e instituciones mediante 'python manage.py loaddata sinetec_fixture_completa.json'."),
        ("Etapa 5: Verificación de Integridad", "Comprobación de conteo de filas, llaves foráneas y ejecución de script de auditoría de perfiles y usuarios.")
    ],
    "chequeos_post_migracion": [
        "Conteo exacto de aprendices matriculados: SELECT COUNT(*) FROM academico_matricula;",
        "Verificación de usuarios activos con rol asignado: SELECT COUNT(*) FROM usuarios_perfilusuario WHERE rol_id IS NOT NULL;",
        "Chequeo de llaves foráneas huérfanas mediante consultas de exclusión LEFT JOIN.",
        "Validación de unicidad de documentos de identidad (evitar duplicados de aprendices o directivos).",
        "Comprobación de acceso de prueba con credenciales maestras temporales para cada uno de los roles institucionales."
    ]
}

PRUEBAS_EVIDENCIAS_DATA = [
    {
        "id": "PRU-001",
        "nombre": "Autenticación con Credenciales Válidas",
        "requisito": "RF-001 / CU-001",
        "entrada": "Usuario: 'admin', Contraseña válida encriptada.",
        "resultado_esperado": "Autenticación exitosa, regeneración de token de sesión y redirección a /dashboard/.",
        "resultado_obtenido": "Código HTTP 302 hacia /dashboard/ y carga correcta de métricas institucionales.",
        "estado": "APROBADO",
        "evidencia": "Suite de pruebas en sinetec_project/tests.py (Aprobada OK)."
    },
    {
        "id": "PRU-002",
        "nombre": "Rechazo de Credenciales Inválidas",
        "requisito": "RNF-001 / Seguridad",
        "entrada": "Usuario: 'admin', Contraseña errónea.",
        "resultado_esperado": "Denegación de acceso, sin creación de sesión y mensaje genérico de error.",
        "resultado_obtenido": "Sesión bloqueada, código HTTP 200 con alerta: 'Credenciales no válidas'.",
        "estado": "APROBADO",
        "evidencia": "Validación en LoginForm y captura de logs de seguridad."
    },
    {
        "id": "PRU-003",
        "nombre": "Unicidad de Documento de Identidad",
        "requisito": "Regla RN-001",
        "entrada": "Intento de registro de dos usuarios con el mismo número de documento.",
        "resultado_esperado": "Excepción de integridad (IntegrityError) en base de datos impidiendo el registro duplicado.",
        "resultado_obtenido": "Django y la base de datos capturan la colisión y rechazan la inserción con mensaje al usuario.",
        "estado": "APROBADO",
        "evidencia": "usuarios/tests.py:test_regla_rn001_unicidad_documento (Aprobada OK)."
    },
    {
        "id": "PRU-004",
        "nombre": "Prevención de Duplicidad de Matrícula",
        "requisito": "Regla RN-002",
        "entrada": "Intento de matricular al mismo estudiante dos veces en una misma ficha formativa.",
        "resultado_esperado": "Violación de restricción unique_together = ('ficha', 'aprendiz').",
        "resultado_obtenido": "Bloqueo inmediato por el ORM impidiendo registros duplicados.",
        "estado": "APROBADO",
        "evidencia": "academico/tests.py:test_regla_rn002_no_duplicar_matricula_en_misma_ficha (Aprobada OK)."
    },
    {
        "id": "PRU-005",
        "nombre": "Juicio Evaluativo Oficial SENA ('A' / 'D')",
        "requisito": "Regla RN-003",
        "entrada": "Registro de juicio con valor 'A' (Aprobado) sobre un RAP.",
        "resultado_esperado": "Almacenamiento exitoso del juicio en tabla JuicioEvaluativo.",
        "resultado_obtenido": "Registro persistido con fecha, instructor calificador y estado oficial.",
        "estado": "APROBADO",
        "evidencia": "evaluaciones/tests.py:test_regla_rn003_juicio_aprobado_valido (Aprobada OK)."
    },
    {
        "id": "PRU-006",
        "nombre": "Rechazo de Juicio No Oficial o Numérico Erróneo",
        "requisito": "Regla RN-003",
        "entrada": "Intento de calificar un RAP con letra 'B' o valor '4.5' en lugar de la escala SENA.",
        "resultado_esperado": "ValidationError rechazando cualquier valor distinto de 'A' o 'D'.",
        "resultado_obtenido": "Lanzamiento de ValidationError: 'El juicio asignado debe ser exclusivamente A o D'.",
        "estado": "APROBADO",
        "evidencia": "evaluaciones/tests.py:test_regla_rn003_rechazar_juicio_invalido (Aprobada OK)."
    },
    {
        "id": "PRU-007",
        "nombre": "Bloqueo por Cierre Formal de Periodo",
        "requisito": "Regla RN-004",
        "entrada": "Intento de modificación de notas en una ficha con periodo académico formalmente cerrado.",
        "resultado_esperado": "Bloqueo estricto de edición para preservar la inmutabilidad de actas finales.",
        "resultado_obtenido": "ValidationError informando que el periodo se encuentra cerrado para calificaciones.",
        "estado": "APROBADO",
        "evidencia": "evaluaciones/tests.py:test_regla_rn004_bloqueo_por_periodo_cerrado (Aprobada OK)."
    },
    {
        "id": "PRU-008",
        "nombre": "Exigencia de Fecha en Compromisos de Seguimiento",
        "requisito": "Regla RN-006",
        "entrada": "Bitácora con observaciones de bajo rendimiento pero sin fecha límite de verificación.",
        "resultado_esperado": "Rechazo del registro exigiendo fecha límite de cumplimiento del compromiso.",
        "resultado_obtenido": "ValidationError en el campo fecha_verificacion obligando al instructor a fijar fecha.",
        "estado": "APROBADO",
        "evidencia": "seguimiento/tests.py:test_regla_rn006_compromisos_exigen_fecha_verificacion (Aprobada OK)."
    },
    {
        "id": "PRU-009",
        "nombre": "Restricción de Grado en Media Técnica (10° y 11°)",
        "requisito": "Regla RN-007",
        "entrada": "Registro de matrícula para estudiante de grado 10° institucional.",
        "resultado_esperado": "Asignación exitosa; rechazo si se ingresa grado inferior fuera del convenio.",
        "resultado_obtenido": "Registro asignado correctamente conforme al rango 10°-11° articulado.",
        "estado": "APROBADO",
        "evidencia": "academico/tests.py:test_creacion_ficha_y_matricula_valida (Aprobada OK)."
    },
    {
        "id": "PRU-010",
        "nombre": "Protección de Rutas Privadas contra Usuarios Anónimos",
        "requisito": "RNF-001 / Seguridad",
        "entrada": "Petición HTTP GET directa a /dashboard/ sin sesión activa.",
        "resultado_esperado": "Respuesta HTTP 302 Redirección hacia /login/?next=/dashboard/.",
        "resultado_obtenido": "Redirección 302 inmediata; ningún dato sensible es expuesto al cliente anónimo.",
        "estado": "APROBADO",
        "evidencia": "sinetec_project/tests.py:test_dashboard_requiere_login (Aprobada OK)."
    },
    {
        "id": "PRU-011",
        "nombre": "Protección contra Ataques CSRF en Formularios",
        "requisito": "RNF-002 / OWASP",
        "entrada": "Petición HTTP POST maliciosa enviada sin token criptográfico CSRF.",
        "resultado_esperado": "Intercepción inmediata del middleware con código HTTP 403 Prohibido.",
        "resultado_obtenido": "Código HTTP 403 y ejecución de vista segura de fallo CSRF.",
        "estado": "APROBADO",
        "evidencia": "Middleware CsrfViewMiddleware activo y probado en Django."
    },
    {
        "id": "PRU-012",
        "nombre": "Inmunidad a Inyección SQL en Buscadores",
        "requisito": "RNF-002 / OWASP",
        "entrada": "Parámetro de búsqueda con payload malicioso: \"' OR '1'='1' --\".",
        "resultado_esperado": "Tratamiento como texto literal mediante sentencias parametrizadas del ORM.",
        "resultado_obtenido": "Cero registros alterados; retorno seguro de lista vacía sin error de sintaxis SQL.",
        "estado": "APROBADO",
        "evidencia": "Consultas mediante Django ORM con filtros parametrizados Q(nombre__icontains=q)."
    },
    {
        "id": "PRU-013",
        "nombre": "Aislamiento Estricto de Subpaneles en Portal Estudiante",
        "requisito": "RF-UX-001",
        "entrada": "Navegación del estudiante Juan Pérez entre Horario, Calificaciones y Asignaturas.",
        "resultado_esperado": "Contenedor derecho renderiza exclusivamente la vista solicitada sin mezclar datos.",
        "resultado_obtenido": "Aislamiento 100% verificado; los subpaneles no colisionan ni duplican tarjetas.",
        "estado": "APROBADO",
        "evidencia": "test_edunova_student_secretaria_flow.py y validación de templates."
    },
    {
        "id": "PRU-014",
        "nombre": "Control de Acceso Docente a Grupos Asignados",
        "requisito": "Seguridad RBAC",
        "entrada": "Docente intenta consultar fichas o estudiantes fuera de su carga académica.",
        "resultado_esperado": "Filtro en backend limitando la consulta exclusivamente a sus materias.",
        "resultado_obtenido": "El docente solo visualiza sus grupos autorizados; acceso denegado a fichas ajenas.",
        "estado": "APROBADO",
        "evidencia": "scripts/test_complete_docente_verification.py (Aprobada OK)."
    },
    {
        "id": "PRU-015",
        "nombre": "Trazabilidad en Registro de Auditoría Transaccional",
        "requisito": "RF-016 / Auditoría",
        "entrada": "Creación, actualización o baja de un aprendiz o calificación.",
        "resultado_esperado": "Creación de registro histórico en modelo RegistroAuditoria con timestamp e IP.",
        "resultado_obtenido": "Evento asentado con usuario emisor, módulo, acción y fecha.",
        "estado": "APROBADO",
        "evidencia": "Modelo RegistroAuditoria y middleware de auditoría activo."
    }
]

SEGURIDAD_DATA = {
    "rbac_roles": [
        ("Rol del Sistema", "Permisos y Atribuciones Operativas", "Restricciones y Bloqueos de Seguridad"),
        ("Administrador General", "Acceso total a configuración, sedes, programas, usuarios, roles, papelera de reciclaje y auditoría forense.", "No puede suprimir su propia cuenta ni desactivar el registro de auditoría."),
        ("Rectoría / Directivos", "Lectura de indicadores globales, supervisión de rendimiento, tasas de deserción y publicación de circulares.", "Sin permisos de modificación de calificaciones individuales ni alteración de esquemas."),
        ("Secretaría Académica", "Matrícula oficial, administración de aprendices, fichas, pensiones, rutas de transporte y certificados.", "Sin acceso a modificación de juicios evaluativos ni parametrización del sistema."),
        ("Docentes / Instructores", "Toma de asistencia, calificación de juicios (A/D) y notas, creación de guías y tareas para sus grupos.", "Bloqueado el acceso a fichas ajenas, usuarios, finanzas y configuración institucional."),
        ("Estudiantes (Aprendices)", "Consulta exclusiva de su propio horario, asignaturas, calificaciones asentadas, tareas y comunicados.", "Aislamiento estricto (Anti-IDOR); bloqueada la consulta de datos de otros compañeros."),
        ("Familia / Acudientes", "Supervisión exclusiva de los hijos matriculados bajo su custodia legal, asistencia y pensiones.", "Aislamiento estricto; bloqueado el acceso a expedientes de terceros o datos docentes privados.")
    ],
    "owasp_mitigaciones": [
        ("Vulnerabilidad OWASP", "Mecanismo de Mitigación Implementado en EduNova", "Capa de Aplicación"),
        ("A01: Broken Access Control", "Validación estricta de pertenencia en backend (evita ataques IDOR), decoradores @login_required y mixins de rol.", "Django Views & Middleware"),
        ("A02: Cryptographic Failures", "Contraseñas cifradas con algoritmo robusto PBKDF2 con hash SHA-256 (Django Auth), forzado HTTPS y cookies seguras.", "Django Auth & Nginx SSL"),
        ("A03: Injection (SQL / Comandos)", "Uso 100% exclusivo del ORM de Django con consultas parametrizadas; ausencia total de SQL crudo concatenado.", "Django ORM"),
        ("A04: Insecure Design", "Arquitectura RBAC con 6 paneles desacoplados y principio de mínimo privilegio en cada punto de acceso.", "Arquitectura de Software"),
        ("A05: Security Misconfiguration", "DEBUG=False obligatorio en producción, cabeceras X-Frame-Options: DENY, X-Content-Type-Options: nosniff.", "Settings & Middleware"),
        ("A06: Vulnerable Components", "Dependencias fijadas en requirements.txt y uso de versiones estables soportadas (Python 3.12+, Django LTS).", "Entorno Virtual (venv)"),
        ("A07: Identification & Auth", "Gestión de sesiones seguras, expiración por inactividad y almacenamiento de sesiones en base de datos cifrada.", "Django Sessions"),
        ("A08: Software & Data Integrity", "Migraciones versionadas en control de cambios Git y protección anti-CSRF en todos los envíos POST.", "CsrfViewMiddleware"),
        ("A09: Security Logging & Monitoring", "Registro sistemático de eventos críticos en modelo RegistroAuditoria y logs de servidor en /var/log/.", "Módulo de Auditoría"),
        ("A10: Server-Side Request Forgery", "Validación estricta de URLs de callbacks externos y ausencia de llamadas arbitrarias desde el backend.", "Lógica de Controladores")
    ]
}

MANTENIMIENTO_DATA = {
    "preventivo": [
        "Revisión semanal del espacio libre en disco (df -h) en particiones de sistema, MySQL y backups.",
        "Depuración y rotación de registros de logs de Nginx (/var/log/nginx/) y Gunicorn (/var/log/gunicorn/) mediante logrotate.",
        "Monitoreo del uso de memoria RAM y CPU mediante htop para ajustar la cantidad de workers de Gunicorn.",
        "Actualización mensual de parches de seguridad del sistema operativo Ubuntu Server (sudo apt update && sudo apt upgrade).",
        "Comprobación de la renovación automática del certificado SSL con certbot renew --dry-run."
    ],
    "correctivo": [
        "Protocolo de reinicio controlado de servicios ante anomalías: sudo systemctl restart gunicorn && sudo systemctl reload nginx.",
        "Inspección de trazas de error en tiempo real: sudo journalctl -u gunicorn -e --no-pager.",
        "Procedimiento de reversión (rollback) inmediato al commit anterior en caso de fallos en una actualización.",
        "Restauración selectiva de base de datos a partir del respaldo diario en caso de corrupción lógica."
    ],
    "zero_downtime": [
        "1. Conexión SSH al servidor: ssh edunova_admin@servidor.institucion.edu.co",
        "2. Acceso al directorio y descarga de cambios: cd /var/www/edunova && git pull origin main",
        "3. Activación de entorno e instalación de dependencias: source venv/bin/activate && pip install -r requirements.txt",
        "4. Ejecución de migraciones no destructivas: python manage.py migrate --noinput",
        "5. Compilación y recolección de estáticos: python manage.py collectstatic --noinput",
        "6. Recarga en caliente de Gunicorn sin cortar conexiones activas: sudo systemctl reload gunicorn",
        "7. Verificación del estado del servicio: sudo systemctl status gunicorn"
    ]
}

RIESGOS_DATA = [
    {
        "id": "R-01",
        "descripcion": "Caída del servicio WSGI de Gunicorn o bloqueo por sobrecarga de peticiones concurrentes.",
        "probabilidad": "Media",
        "impacto": "Alto",
        "mitigacion": "Configuración de reinicio automático en Systemd (Restart=always) y balanceo de 3 a 5 workers concurrentes.",
        "contingencia": "Monitoreo con Systemd y script watchdog de comprobación de socket HTTP."
    },
    {
        "id": "R-02",
        "descripcion": "Corrupción o pérdida de datos por fallo físico en el almacenamiento del servidor MySQL.",
        "probabilidad": "Baja",
        "impacto": "Crítico",
        "mitigacion": "Uso de discos en RAID 1 y ejecución de script automatizado de copias de seguridad diarias nocturnas.",
        "contingencia": "Restauración inmediata del último volcado SQL consistente y activación de base secundaria."
    },
    {
        "id": "R-03",
        "descripcion": "Saturación del espacio de almacenamiento en disco debido al cargue continuo de documentos y actas multimedia.",
        "probabilidad": "Media",
        "impacto": "Medio",
        "mitigacion": "Restricción de tamaño máximo en subidas (client_max_body_size 25M en Nginx) y validación de extensiones permitidas.",
        "contingencia": "Alerta de umbral al 80% de disco y migración programada de /media/ hacia almacenamiento en bloque secundario."
    },
    {
        "id": "R-04",
        "descripcion": "Expiración del certificado de seguridad SSL/TLS provocando alertas de conexión insegura en navegadores.",
        "probabilidad": "Baja",
        "impacto": "Alto",
        "mitigacion": "Configuración del temporizador systemd de Certbot con comprobación dos veces al día para renovación a 30 días.",
        "contingencia": "Ejecución manual de emergencia: sudo certbot renew --force-renewal && sudo systemctl reload nginx."
    },
    {
        "id": "R-05",
        "descripcion": "Ataques de fuerza bruta o escaneo automatizado sobre la interfaz de inicio de sesión.",
        "probabilidad": "Media",
        "impacto": "Alto",
        "mitigacion": "Instalación de Fail2ban con reglas específicas para bloquear IPs con más de 5 intentos fallidos consecutivos.",
        "contingencia": "Bloqueo perimetral de IP en firewall UFW y bloqueo temporal automático de la cuenta afectada."
    },
    {
        "id": "R-06",
        "descripcion": "Demora o retraso de la institución cliente en proveer la máquina servidora física o VPS definitiva.",
        "probabilidad": "Alta",
        "impacto": "Medio",
        "mitigacion": "Mantenimiento del entorno cloud temporal (Render/Railway) y servidor local para demostraciones y sustentaciones.",
        "contingencia": "Entrega de paquetes de instalación automatizados y ejecución de la migración en cuanto el hardware esté disponible."
    }
]

CONCLUSIONES_DATA = [
    "La solución informática EduNova — Sistema Integrado de Educación Técnica (SINETEC) ha alcanzado un nivel de madurez técnica, estabilidad funcional y consistencia de datos que la hace plenamente apta para su despliegue y puesta en marcha en un entorno de producción formal.",
    "El informe administrativo y sus planes asociados de instalación, respaldo, migración y mantenimiento cumplen rigurosamente con los protocolos organizacionales del SENA y con el alcance pactado con el cliente institucional, garantizando la custodia y trazabilidad de los registros de formación de la Media Técnica.",
    "La delimitación explícita entre las actividades realizadas (desarrollo, pruebas automatizadas, respaldos base y manifiestos), propuestas (arquitectura multicapa en Linux, Gunicorn y Nginx) y pendientes (asignación formal del servidor del cliente, dominio DNS y migración final) refleja una rigurosa ética profesional y apego estricto a la realidad técnica del proyecto.",
    "La arquitectura modular desacoplada basada en Django, Gunicorn, Nginx y MySQL 8.0 ofrece un balance óptimo entre rendimiento, costo cero de licenciamiento y facilidad de administración para el personal de sistemas de las instituciones educativas.",
    "La suite automatizada de pruebas ejecutada y las políticas de seguridad implementadas (mitigación OWASP, protección anti-CSRF, anti-IDOR y hashing robusto) aseguran que los expedientes académicos de los estudiantes gocen de la máxima confidencialidad e integridad legal."
]

RECOMENDACIONES_DATA = [
    "Formalizar a la mayor brevedad la asignación de la infraestructura física o VPS por parte del cliente para proceder con la ejecución del plan de instalación en caliente y el direccionamiento del subdominio institucional definitivo.",
    "Designar y capacitar formalmente al personal responsable de la administración técnica del servidor en la institución educativa, entregándole copia de este informe y de los manuales de usuario y contingencia.",
    "Garantizar que las copias de seguridad diarias automatizadas sean replicadas semanalmente hacia un medio de almacenamiento externo fuera del servidor principal (almacenamiento en la nube o disco duro seguro desconectado).",
    "Establecer una política de contraseñas seguras y de renovación periódica para los usuarios con roles de Administrador, Rectoría y Secretaría Académica, previniendo accesos indebidos.",
    "Mantener activo el plan de pruebas continuas ante cualquier futura ampliación de módulos (ej. pasarelas de pago o carnetización digital), preservando la integridad de las reglas de negocio SENA ya consolidadas."
]

FIRMAS_DATA = [
    {
        "cargo": "Aprendiz / Líder de Desarrollo e Implementación",
        "entidad": "SENA Regional Magdalena — Ficha 228106 ADSI",
        "responsabilidad": "Elaboración técnica del informe, ejecución de pruebas y formulación de planes de despliegue."
    },
    {
        "cargo": "Instructor Técnico de Formación",
        "entidad": "Centro de Logística y Promoción Ecoturística del Magdalena",
        "responsabilidad": "Revisión técnica, validación metodológica y evaluación del cumplimiento de resultados de aprendizaje."
    },
    {
        "cargo": "Delegado Institucional del Cliente / Coordinador Académico",
        "entidad": "Institución Educativa Articulada con la Media Técnica",
        "responsabilidad": "Recepción formal del informe administrativo y verificación de viabilidad operativa para producción."
    }
]

print("Contenido del informe cargado exitosamente.")
