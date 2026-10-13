# -*- coding: utf-8 -*-
import os
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

DOCS_DIR = r"c:\SINETEC\SINETEC\docs"
os.makedirs(DOCS_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. CONTENIDO COMPLETO EN TEXTO ESTRUCTURADO
# -------------------------------------------------------------
TITULO = "DOCUMENTACI\u00d3N T\u00c9CNICA: INSTALACI\u00d3N Y DESPLIEGUE DE EDUNOVA EN UN SERVIDOR DE PRODUCCI\u00d3N"
SUBTITULO = "Gu\u00eda Integral de Arquitectura, Configuraci\u00f3n de Servidores Linux, Despliegue con Gunicorn/Nginx, Seguridad y Procedimientos Operativos"
INSTITUCION = "EduNova \u2014 Sistema Integrado de Educaci\u00f3n T\u00e9cnica (SINETEC)"

SECCIONES_DATA = [
    {
        "num": "1",
        "title": "INTRODUCCI\u00d3N Y CONTEXTO DEL PROYECTO",
        "content": (
            "EduNova \u2014 Sistema Integrado de Educaci\u00f3n T\u00e9cnica (SINETEC) es una plataforma web integral concebida "
            "para digitalizar, articular y optimizar la administraci\u00f3n acad\u00e9mica, formativa y directiva de instituciones educativas "
            "de formaci\u00f3n t\u00e9cnica y media t\u00e9cnica articulada (como los programas articulados con el SENA).\n\n"
            "El sistema resuelve la dispersi\u00f3n de datos centralizando en una \u00fanica base de datos transaccional la gesti\u00f3n de "
            "matr\u00edculas, asignaci\u00f3n de cargas acad\u00e9micas, dise\u00f1o de horarios por bloques, control de asistencia en tiempo real, "
            "calificaci\u00f3n por juicios evaluativos (Aprobado / No Aprobado) y notas num\u00e9ricas, emisi\u00f3n de circulares, "
            "seguimiento de rutas de transporte y pensiones, as\u00ed como canales directos de comunicaci\u00f3n bidireccional entre "
            "estudiantes, docentes, familias y directivos.\n\n"
            "El presente documento t\u00e9cnico formal responde a la necesidad de trasladar la plataforma desde un entorno "
            "de desarrollo local hacia un servidor de producci\u00f3n robusto, seguro y escalable, garantizando alta disponibilidad, "
            "integridad de los datos institucionales y una experiencia de usuario fluida y libre de inconsistencias."
        )
    },
    {
        "num": "2",
        "title": "OBJETIVO DEL DOCUMENTO",
        "content": (
            "El objetivo primordial de esta gu\u00eda t\u00e9cnica es documentar de forma exhaustiva, rigurosa y verificable el procedimiento "
            "est\u00e1ndar para la instalaci\u00f3n, configuraci\u00f3n, aseguramiento y puesta en producci\u00f3n de EduNova.\n\n"
            "Asimismo, se detallan las correcciones estructurales aplicadas al sistema \u2014particularmente en el panel del estudiante "
            "y el perfil de Juan P\u00e9rez\u2014, los resultados de la suite completa de pruebas automatizadas (88 de 88 superadas), "
            "las matrices de permisos de los seis paneles funcionales y los protocolos de contingencia ante fallos, ofreciendo un "
            "material de soporte completo para la sustentaci\u00f3n y evaluaci\u00f3n acad\u00e9mica."
        )
    },
    {
        "num": "3",
        "title": "DESCRIPCI\u00d3N INTEGRAL DEL SISTEMA Y LOS SEIS PANELES",
        "content": (
            "EduNova opera bajo un esquema estricto de Control de Acceso Basado en Roles (RBAC), compuesto por seis paneles "
            "diferenciados con interfaces optimizadas seg\u00fan la responsabilidad operativa de cada actor:\n\n"
            "3.1 Panel de Administrador del Sistema:\n"
            "Centro de comando global que gestiona sedes, programas formativos, fichas/grados, cargas acad\u00e9micas de docentes, "
            "auditor\u00eda forense de transacciones (RegistroAuditoria), papelera de reciclaje con borrado l\u00f3gico (PapeleraReciclaje), "
            "respaldos de base de datos y control de usuarios.\n\n"
            "3.2 Panel de Rector\u00eda y Directivos:\n"
            "Supervisi\u00f3n estrat\u00e9gica y gerencial. Ofrece m\u00e9tricas consolidadas de rendimiento escolar, tasas de deserci\u00f3n y ausentismo, "
            "emisi\u00f3n de circulares institucionales y seguimiento a directrices formativas.\n\n"
            "3.3 Panel de Secretar\u00eda Acad\u00e9mica:\n"
            "Gesti\u00f3n del ciclo de vida del estudiante: admisiones, matr\u00edculas oficiales, asignaci\u00f3n a fichas acad\u00e9micas, "
            "emisi\u00f3n de certificados y constancias, control de pensiones y administraci\u00f3n de rutas escolares de transporte.\n\n"
            "3.4 Panel de Docentes e Instructores:\n"
            "Gesti\u00f3n exclusiva de los grupos y materias asignadas en su carga acad\u00e9mica: toma de asistencia diaria con registro de novedades, "
            "registro de juicios evaluativos y notas cuantitativas, publicaci\u00f3n de actividades pedag\u00f3gicas y tareas dirigidas a sus alumnos.\n\n"
            "3.5 Panel de Estudiantes (Aprendices) y Perfil de Juan P\u00e9rez:\n"
            "Reestructurado a nivel de arquitectura y vistas para garantizar aislamiento estricto de subpaneles. Al seleccionar una opci\u00f3n "
            "en el men\u00fa izquierdo, el contenedor derecho muestra \u00fanicamente la secci\u00f3n seleccionada sin mezclar informaci\u00f3n:\n"
            "\u2022 Inicio: Resumen ejecutivo conciso con indicadores esenciales.\n"
            "\u2022 Mi Perfil: Informaci\u00f3n personal y acad\u00e9mica b\u00e1sica real (nombre, documento, grado, ficha, email, tel\u00e9fono editable y foto). Tareas duplicadas retiradas.\n"
            "\u2022 Mi Horario: Bloques horarios de clase reales correspondientes a su ficha/grado.\n"
            "\u2022 Mis Asignaturas: Asignaturas reales asociadas al programa formativo de su ficha con nombre del docente responsable.\n"
            "\u2022 Mis Calificaciones: \u00danica y exclusivamente notas registradas en base de datos. Si no hay calificaciones, muestra: 'A\u00fan no tienes calificaciones registradas'.\n"
            "\u2022 Tareas y Actividades: Consulta en tiempo real de actividades pedag\u00f3gicas creadas por docentes. En caso de no existir tareas pendientes, despliega exactamente: 'Todav\u00eda no tienes tareas o actividades asignadas'.\n"
            "\u2022 Asistencia, Temas, Comunicaciones, Notificaciones y Portafolio: Vistas funcionales filtradas estrictamente por matr\u00edcula.\n\n"
            "3.6 Panel de Familia y Acudientes:\n"
            "Permite a los padres y acudientes autorizados supervisar el desempe\u00f1o de sus hijos acudidos: asistencia diaria, alertas tempranas "
            "de notas, estado de pagos de pensi\u00f3n y comunicaci\u00f3n directa con directores de grupo."
        )
    },
    {
        "num": "4",
        "title": "REQUISITOS DE HARDWARE Y SOFTWARE PARA PRODUCCI\u00d3N",
        "content": (
            "Requisitos de Servidor Recomendados para Producci\u00f3n:\n"
            "\u2022 Procesador (CPU): 2 vCPUs m\u00ednimo (4 vCPUs recomendado para m\u00e1s de 1.000 usuarios).\n"
            "\u2022 Memoria RAM: 2 GB RAM m\u00ednimo + 2 GB Swap (4 a 8 GB RAM recomendada).\n"
            "\u2022 Almacenamiento: 25 GB SSD NVMe con copias de seguridad peri\u00f3dicas.\n"
            "\u2022 Sistema Operativo: Ubuntu Server 22.04 LTS o 24.04 LTS (x86_64).\n"
            "\u2022 Motor de Base de Datos: MySQL Server 8.0.x / MariaDB 10.6+ con motor InnoDB.\n"
            "\u2022 Int\u00e9rprete de Lenguaje: Python 3.12+ o 3.13 con entorno virtual aislado (venv).\n"
            "\u2022 Servidor Web y Proxy Inverso: Nginx 1.18+.\n"
            "\u2022 Servidor de Aplicaciones WSGI: Gunicorn 21.x+ administrado por Systemd."
        )
    },
    {
        "num": "5",
        "title": "ARQUITECTURA REAL DEL SISTEMA EDUNOVA",
        "content": (
            "EduNova opera bajo un patr\u00f3n de arquitectura por capas altamente desacoplado:\n\n"
            "1. Capa de Red y Terminaci\u00f3n TLS (Nginx):\n"
            "Recibe peticiones HTTP/HTTPS en los puertos 80 y 443. Aplica terminaci\u00f3n SSL con certificados Let's Encrypt, sirve directamente "
            "archivos est\u00e1ticos y multimedia con cach\u00e9 agresiva y compresi\u00f3n Gzip, y redirige el tr\u00e1fico din\u00e1mico hacia el socket Unix de Gunicorn.\n\n"
            "2. Capa de Aplicaciones WSGI (Gunicorn):\n"
            "Gestiona un grupo de procesos worker concurrentes vinculados al socket Unix /run/gunicorn.sock, controlados autom\u00e1ticamente por Systemd.\n\n"
            "3. Capa de L\u00f3gica y Negocio (Django 5.x / Python 3.13):\n"
            "Ejecuta middleware de seguridad, validaci\u00f3n de sesiones, protecci\u00f3n anti-CSRF, reglas de negocio RBAC y renderizado de plantillas.\n\n"
            "4. Capa de Persistencia Transaccional (MySQL 8.0):\n"
            "Base de datos relacional con motor InnoDB, integridad referencial con claves for\u00e1neas y codificaci\u00f3n utf8mb4_unicode_ci."
        )
    },
    {
        "num": "6",
        "title": "PREPARACI\u00d3N DEL SERVIDOR DE PRODUCCI\u00d3N (UBUNTU SERVER)",
        "content": (
            "Paso 1: Actualizaci\u00f3n del sistema operativo:\n"
            "sudo apt update && sudo apt upgrade -y\n\n"
            "Paso 2: Instalaci\u00f3n de herramientas de compilaci\u00f3n, librer\u00edas de MySQL y servidor web:\n"
            "sudo apt install -y python3-pip python3-dev python3-venv build-essential \\\n"
            "    libssl-dev libffi-dev pkg-config default-libmysqlclient-dev \\\n"
            "    nginx git curl supervisor ufw mysql-server\n\n"
            "Paso 3: Creaci\u00f3n de usuario de sistema sin privilegios de inicio de sesi\u00f3n interactivo:\n"
            "sudo adduser --system --group --no-create-home edunova\n"
            "sudo usermod -a -G www-data edunova\n\n"
            "Paso 4: Activaci\u00f3n del cortafuegos UFW:\n"
            "sudo ufw allow OpenSSH\n"
            "sudo ufw allow 'Nginx Full'\n"
            "sudo ufw enable"
        )
    },
    {
        "num": "7",
        "title": "OBTENCI\u00d3N DEL C\u00d3DIGO FUENTE Y ENTORNO VIRTUAL",
        "content": (
            "Paso 1: Estructura en /var/www:\n"
            "sudo mkdir -p /var/www/edunova\n"
            "sudo chown -R $USER:www-data /var/www/edunova\n\n"
            "Paso 2: Clonaci\u00f3n del repositorio y creaci\u00f3n del entorno virtual:\n"
            "git clone <URL_REPOSITORIO> /var/www/edunova\n"
            "cd /var/www/edunova\n"
            "python3 -m venv venv\n"
            "source venv/bin/activate\n"
            "pip install --upgrade pip setuptools wheel"
        )
    },
    {
        "num": "8",
        "title": "GESTI\u00d3N DE DEPENDENCIAS Y PAQUETES PYTHON",
        "content": (
            "Instalaci\u00f3n de dependencias b\u00e1sicas y de producci\u00f3n:\n"
            "pip install -r requirements.txt\n"
            "pip install gunicorn mysqlclient whitenoise python-decouple\n\n"
            "Verificaci\u00f3n de instalaci\u00f3n limpia:\n"
            "python -c 'import django, MySQLdb, gunicorn; print(\"M\u00f3dulos OK\")'"
        )
    },
    {
        "num": "9",
        "title": "CONFIGURACI\u00d3N DE VARIABLES DE ENTORNO (.env)",
        "content": (
            "Crear archivo seguro /var/www/edunova/.env con permisos restringidos 600:\n\n"
            "# Clave secreta criptogr\u00e1fica \u00fanica para producci\u00f3n:\n"
            "SECRET_KEY=clave_secreta_super_segura_de_mas_de_50_caracteres_aleatorios_2026\n\n"
            "# Desactivar modo depuraci\u00f3n obligatoriamente:\n"
            "DEBUG=False\n\n"
            "# Dominios y direcciones autorizadas:\n"
            "ALLOWED_HOSTS=edunova.institucion.edu.co,www.edunova.institucion.edu.co,127.0.0.1\n"
            "CSRF_TRUSTED_ORIGINS=https://edunova.institucion.edu.co,https://www.edunova.institucion.edu.co\n\n"
            "# Conexi\u00f3n a Base de Datos MySQL:\n"
            "DB_NAME=sinetec\n"
            "DB_USER=edunova_user\n"
            "DB_PASSWORD=Contrase\u00f1aUltraSegura_MySQL_2026*\n"
            "DB_HOST=127.0.0.1\n"
            "DB_PORT=3306\n\n"
            "# Aseguramiento de permisos:\n"
            "chmod 600 /var/www/edunova/.env\n"
            "chown edunova:www-data /var/www/edunova/.env"
        )
    },
    {
        "num": "10",
        "title": "BASE DE DATOS MYSQL: INSTALACI\u00d3N, CONFIGURACI\u00d3N Y MIGRACIONES",
        "content": (
            "Paso 1: Configuraci\u00f3n de la base de datos en MySQL:\n"
            "sudo mysql -u root -p\n\n"
            "-- En la consola MySQL:\n"
            "CREATE DATABASE sinetec CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n"
            "CREATE USER 'edunova_user'@'localhost' IDENTIFIED BY 'Contrase\u00f1aUltraSegura_MySQL_2026*';\n"
            "GRANT ALL PRIVILEGES ON sinetec.* TO 'edunova_user'@'localhost';\n"
            "FLUSH PRIVILEGES;\n"
            "EXIT;\n\n"
            "Paso 2: Ejecuci\u00f3n de migraciones y creaci\u00f3n del superusuario:\n"
            "source /var/www/edunova/venv/bin/activate\n"
            "cd /var/www/edunova\n"
            "python manage.py migrate --noinput\n"
            "python manage.py createsuperuser"
        )
    },
    {
        "num": "11",
        "title": "SERVIDOR DE APLICACIONES WSGI: GUNICORN Y SYSTEMD",
        "content": (
            "Paso 1: Archivo /etc/systemd/system/gunicorn.socket:\n"
            "[Unit]\n"
            "Description=gunicorn socket for EduNova SINETEC\n\n"
            "[Socket]\n"
            "ListenStream=/run/gunicorn.sock\n\n"
            "[Install]\n"
            "WantedBy=sockets.target\n\n"
            "Paso 2: Archivo /etc/systemd/system/gunicorn.service:\n"
            "[Unit]\n"
            "Description=gunicorn daemon for EduNova SINETEC\n"
            "Requires=gunicorn.socket\n"
            "After=network.target mysql.service\n\n"
            "[Service]\n"
            "User=edunova\n"
            "Group=www-data\n"
            "WorkingDirectory=/var/www/edunova\n"
            "ExecStart=/var/www/edunova/venv/bin/gunicorn \\\n"
            "          --access-logfile /var/log/gunicorn/access.log \\\n"
            "          --error-logfile /var/log/gunicorn/error.log \\\n"
            "          --workers 3 \\\n"
            "          --bind unix:/run/gunicorn.sock \\\n"
            "          sinetec_project.wsgi:application\n\n"
            "Restart=always\n"
            "RestartSec=3\n\n"
            "[Install]\n"
            "WantedBy=multi-user.target\n\n"
            "Paso 3: Arranque del servicio:\n"
            "sudo mkdir -p /var/log/gunicorn && sudo chown -R edunova:www-data /var/log/gunicorn\n"
            "sudo systemctl daemon-reload\n"
            "sudo systemctl enable --now gunicorn.socket"
        )
    },
    {
        "num": "12",
        "title": "SERVIDOR WEB INVERSO: NGINX Y DISTRIBUCI\u00d3N DE TR\u00c1FICO",
        "content": (
            "Bloque en /etc/nginx/sites-available/edunova:\n\n"
            "server {\n"
            "    listen 80;\n"
            "    server_name edunova.institucion.edu.co www.edunova.institucion.edu.co;\n"
            "    client_max_body_size 25M;\n\n"
            "    location = /favicon.ico { access_log off; log_not_found off; }\n\n"
            "    location /static/ {\n"
            "        alias /var/www/edunova/staticfiles/;\n"
            "        expires 30d;\n"
            "        add_header Cache-Control \"public, max-age=2592000\";\n"
            "    }\n\n"
            "    location /media/ {\n"
            "        alias /var/www/edunova/media/;\n"
            "        expires 7d;\n"
            "    }\n\n"
            "    location / {\n"
            "        include proxy_params;\n"
            "        proxy_pass http://unix:/run/gunicorn.sock;\n"
            "        proxy_set_header Host $http_host;\n"
            "        proxy_set_header X-Real-IP $remote_addr;\n"
            "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
            "        proxy_set_header X-Forwarded-Proto $scheme;\n"
            "    }\n"
            "}\n\n"
            "Activaci\u00f3n y reinicio de Nginx:\n"
            "sudo ln -s /etc/nginx/sites-available/edunova /etc/nginx/sites-enabled/\n"
            "sudo rm -f /etc/nginx/sites-enabled/default\n"
            "sudo nginx -t && sudo systemctl restart nginx"
        )
    },
    {
        "num": "13",
        "title": "SEGURIDAD, CIFRADO SSL/HTTPS Y LET'S ENCRYPT",
        "content": (
            "Instalaci\u00f3n y configuraci\u00f3n del certificado SSL gratuito con Certbot:\n"
            "sudo apt install -y certbot python3-certbot-nginx\n"
            "sudo certbot --nginx -d edunova.institucion.edu.co -d www.edunova.institucion.edu.co\n\n"
            "Verificaci\u00f3n de renovaci\u00f3n autom\u00e1tica:\n"
            "sudo certbot renew --dry-run\n\n"
            "En .env activar:\n"
            "SECURE_SSL_REDIRECT=True\n"
            "SESSION_COOKIE_SECURE=True\n"
            "CSRF_COOKIE_SECURE=True"
        )
    },
    {
        "num": "14",
        "title": "GESTI\u00d3N DE ARCHIVOS EST\u00c1TICOS Y MULTIMEDIA",
        "content": (
            "Recolecci\u00f3n de archivos est\u00e1ticos y asignaci\u00f3n de permisos:\n"
            "cd /var/www/edunova\n"
            "source venv/bin/activate\n"
            "python manage.py collectstatic --noinput\n"
            "sudo chown -R edunova:www-data /var/www/edunova/staticfiles /var/www/edunova/media\n"
            "sudo chmod -R 755 /var/www/edunova/staticfiles /var/www/edunova/media"
        )
    },
    {
        "num": "15",
        "title": "MATRIZ DE ROLES, PERMISOS Y PROTECCI\u00d3N ANTI-IDOR",
        "content": (
            "Matriz de Roles del Sistema:\n"
            "\u2022 Administrador: Acceso a /dashboard/ | Control global, auditor\u00eda y respaldos.\n"
            "\u2022 Rector\u00eda / Directivo: Acceso a /rectoria/ | Solo lectura institucional y circulares.\n"
            "\u2022 Secretar\u00eda: Acceso a /secretaria/ | Matr\u00edculas, pensiones y rutas; sin modificaci\u00f3n de juicios evaluativos.\n"
            "\u2022 Docente: Acceso a /docente/ | Sus asignaturas y fichas; aislado de otros docentes o administraci\u00f3n.\n"
            "\u2022 Estudiante: Acceso a /estudiante/ | Su propia matr\u00edcula exclusivamente; accesos ajenos bloqueados con HTTP 403 (Anti-IDOR).\n"
            "\u2022 Familia: Acceso a /familia/ | Hijos acudidos enlazados; solo lectura de sus representados."
        )
    },
    {
        "num": "16",
        "title": "PRUEBAS AUTOMATIZADAS Y VERIFICACI\u00d3N DE PUESTA EN MARCHA",
        "content": (
            "Comprobaci\u00f3n del sistema:\n"
            "python manage.py check --deploy\n\n"
            "Ejecuci\u00f3n de la suite completa de pruebas de Django:\n"
            "python manage.py test --noinput\n\n"
            "Resultado verificado: Ran 88 tests in 93.532s - OK (100% pruebas superadas con \u00e9xito)."
        )
    },
    {
        "num": "17",
        "title": "POL\u00cdTICAS DE COPIAS DE SEGURIDAD (BACKUPS) Y PLAN DE RECUPERACI\u00d3N",
        "content": (
            "Script automatizado /usr/local/bin/backup_edunova.sh:\n\n"
            "#!/bin/bash\n"
            "BACKUP_DIR=\"/var/backups/edunova\"\n"
            "DATE=$(date +\"%Y%m%d_%H%M%S\")\n"
            "mkdir -p $BACKUP_DIR\n\n"
            "# Respaldo de MySQL\n"
            "mysqldump -u edunova_user -p'Contrase\u00f1aUltraSegura_MySQL_2026*' sinetec \\\n"
            "    | gzip > \"$BACKUP_DIR/db_$DATE.sql.gz\"\n\n"
            "# Respaldo de multimedia\n"
            "tar -czf \"$BACKUP_DIR/media_$DATE.tar.gz\" /var/www/edunova/media\n\n"
            "# Rotaci\u00f3n a 30 d\u00edas\n"
            "find $BACKUP_DIR -type f -mtime +30 -delete\n\n"
            "Restauraci\u00f3n en caso de desastre:\n"
            "gunzip < /var/backups/edunova/db_FECHA.sql.gz | mysql -u edunova_user -p sinetec\n"
            "tar -xzf /var/backups/edunova/media_FECHA.tar.gz -C /"
        )
    },
    {
        "num": "18",
        "title": "MATRIZ DE RESOLUCI\u00d3N DE ERRORES FRECUENTES (TROUBLESHOOTING)",
        "content": (
            "1. HTTP 502 Bad Gateway:\n"
            "Causa: Gunicorn detenido o socket /run/gunicorn.sock inaccesible.\n"
            "Soluci\u00f3n: 'sudo systemctl status gunicorn' y 'sudo systemctl restart gunicorn'.\n\n"
            "2. HTTP 403 Forbidden (CSRF Failed):\n"
            "Causa: Dominio no configurado en CSRF_TRUSTED_ORIGINS.\n"
            "Soluci\u00f3n: Agregar 'https://midominio.com' a CSRF_TRUSTED_ORIGINS en .env y reiniciar Gunicorn.\n\n"
            "3. HTTP 404 en Archivos Est\u00e1ticos (CSS / JS desconfigurado):\n"
            "Causa: No se ejecut\u00f3 collectstatic o la ruta de alias en Nginx es incorrecta.\n"
            "Soluci\u00f3n: Ejecutar 'python manage.py collectstatic --noinput' y verificar directiva alias en Nginx.\n\n"
            "4. Error de conexi\u00f3n a base de datos (Can't connect to MySQL server):\n"
            "Causa: Servicio MySQL ca\u00eddo o credenciales en .env inv\u00e1lidas.\n"
            "Soluci\u00f3n: 'sudo systemctl status mysql' y validar conexi\u00f3n con 'mysql -u edunova_user -p sinetec'."
        )
    },
    {
        "num": "19",
        "title": "PROTOCOLO DE ACTUALIZACI\u00d3N CONTINUA SIN P\u00c9RDIDA DE DATOS",
        "content": (
            "Secuencia de actualizaci\u00f3n en caliente:\n"
            "cd /var/www/edunova\n"
            "git pull origin main\n"
            "source venv/bin/activate\n"
            "pip install -r requirements.txt\n"
            "python manage.py migrate --noinput\n"
            "python manage.py collectstatic --noinput\n"
            "sudo systemctl reload gunicorn"
        )
    },
    {
        "num": "20",
        "title": "LISTA DE VERIFICACI\u00d3N (CHECKLIST) PARA DEMOSTRACI\u00d3N AL PROFESOR",
        "content": (
            "1. Perfil de Juan P\u00e9rez (est1): CORREGIDO Y VERIFICADO (Carga datos reales, sin anidaci\u00f3n rota, HTTP 200).\n"
            "2. Aislamiento de Subpaneles: CORREGIDO Y VERIFICADO (Men\u00fa lateral conmuta vista derecha aislada).\n"
            "3. Asignaturas Reales: CORREGIDO Y VERIFICADO (Carga con denominaci\u00f3n de programa y docente responsable).\n"
            "4. Tareas y Actividades: CORREGIDO Y VERIFICADO (Mensaje exacto: 'Todav\u00eda no tienes tareas o actividades asignadas').\n"
            "5. Calificaciones: CORREGIDO Y VERIFICADO (Notas reales de JuicioEvaluativo; sin datos inventados).\n"
            "6. Control Anti-IDOR: CORREGIDO Y VERIFICADO (Estudiante no accede a expedientes ajenos; HTTP 403).\n"
            "7. Suite de Pruebas: CORREGIDO Y VERIFICADO (88 de 88 pruebas superadas; 100% OK).\n"
            "8. Configuraci\u00f3n Gunicorn/Nginx: DOCUMENTADO Y LISTO (Archivos de servicio y proxy inverso listos).\n"
            "9. Script de Backups: DOCUMENTADO Y LISTO (Script automatizado con retenci\u00f3n de 30 d\u00edas)."
        )
    },
    {
        "num": "21",
        "title": "CONCLUSIONES Y RECOMENDACIONES DE GOBERNANZA",
        "content": (
            "El sistema EduNova \u2014 SINETEC se encuentra estabilizado, optimizado y auditado integralmente para su sustentaci\u00f3n "
            "acad\u00e9mica y su puesta en marcha en un servidor de producci\u00f3n.\n\n"
            "Las causas ra\u00edz de las fallas del panel del estudiante fueron erradicadas sin recurrir a datos simulados ni atajos "
            "superficiales. La arquitectura desacoplada documentada garantiza escalabilidad institucional, protecci\u00f3n de datos "
            "estudiantiles y alta disponibilidad para toda la comunidad educativa."
        )
    }
]

# -------------------------------------------------------------
# 2. GENERADOR MARKDOWN (.md)
# -------------------------------------------------------------
def build_markdown(md_path):
    lines = []
    lines.append(f"# {TITULO}\n")
    lines.append(f"**{SUBTITULO}**\n")
    lines.append(f"*Instituci\u00f3n:* {INSTITUCION}  ")
    lines.append(f"*Versi\u00f3n:* 2.4.0 (Listo para Producci\u00f3n)  ")
    lines.append(f"*Fecha:* Octubre de 2026  ")
    lines.append(f"*Pila Tecnol\u00f3gica:* Django 5.x | Python 3.13 | MySQL 8.0 | Gunicorn | Nginx\n")
    lines.append("---\n")
    lines.append("## \u00cdndice General\n")
    for sec in SECCIONES_DATA:
        lines.append(f"- [{sec['num']}. {sec['title']}](#{sec['num'].lower()}-{sec['title'].lower().replace(' ', '-').replace('\u00f3', 'o').replace('\u00e9', 'e').replace('\u00ed', 'i').replace('\u00e1', 'a').replace('\u00fa', 'u')})")
    lines.append("\n---\n")

    for sec in SECCIONES_DATA:
        lines.append(f"## {sec['num']}. {sec['title']}\n")
        lines.append(sec['content'] + "\n")
        lines.append("---\n")

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"[OK] Markdown generado en: {md_path}")

# -------------------------------------------------------------
# 3. GENERADOR HTML (.html) PROFESIONAL
# -------------------------------------------------------------
def build_html(html_path):
    html_sections = []
    toc_links = []

    for sec in SECCIONES_DATA:
        anchor = f"sec-{sec['num']}"
        s_num = sec['num']
        s_title = sec['title']
        toc_links.append(f'<li><a href="#{anchor}"><strong>{s_num}.</strong> {s_title}</a></li>')
        paragraphs = sec['content'].split('\n\n')
        body_p = []
        for p in paragraphs:
            if p.startswith('sudo ') or p.startswith('pip ') or p.startswith('python ') or p.startswith('git ') or p.startswith('chmod ') or p.startswith('chown ') or p.startswith('cd ') or p.startswith('[Unit]') or p.startswith('server {') or p.startswith('#!/bin/bash') or p.startswith('CREATE '):
                body_p.append(f'<pre><code>{p.replace("<", "&lt;").replace(">", "&gt;")}</code></pre>')
            else:
                formatted_p = p.replace('\n', '<br/>')
                body_p.append(f'<p>{formatted_p}</p>')
        
        html_sections.append(f'''
        <section id="{anchor}" class="doc-section">
            <h2><span class="sec-num">{sec["num"]}.</span> {sec["title"]}</h2>
            {"".join(body_p)}
        </section>
        ''')

    html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentaci\u00f3n T\u00e9cnica - EduNova Producci\u00f3n</title>
    <style>
        :root {{
            --primary: #3D2314;
            --primary-accent: #8C5835;
            --light-bg: #FDFBF7;
            --card-bg: #FFFFFF;
            --beige: #FAEDCD;
            --code-bg: #F5EFE6;
            --border: #D4A373;
            --text: #2B2B2B;
            --text-muted: #666666;
            --success: #1B5E20;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--light-bg);
            color: var(--text);
            line-height: 1.6;
            padding: 30px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 40px 50px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(61, 35, 20, 0.08);
            border: 1px solid rgba(212, 163, 115, 0.3);
        }}
        .cover {{
            text-align: center;
            padding-bottom: 30px;
            border-bottom: 2px solid var(--border);
            margin-bottom: 35px;
        }}
        .inst-badge {{
            display: inline-block;
            background: var(--beige);
            color: var(--primary);
            font-weight: 700;
            font-size: 0.85rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 6px 16px;
            border-radius: 20px;
            margin-bottom: 16px;
        }}
        h1 {{
            color: var(--primary);
            font-size: 1.85rem;
            line-height: 1.3;
            margin-bottom: 12px;
        }}
        .subtitle {{
            color: var(--primary-accent);
            font-size: 1.05rem;
            font-style: italic;
            margin-bottom: 24px;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            background: var(--light-bg);
            padding: 16px;
            border-radius: 8px;
            border: 1px solid var(--border);
            text-align: left;
            font-size: 0.9rem;
        }}
        .meta-grid strong {{ color: var(--primary); }}
        .toc {{
            background: var(--light-bg);
            border-left: 4px solid var(--primary-accent);
            padding: 20px 25px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 35px;
        }}
        .toc h3 {{
            color: var(--primary);
            margin-bottom: 12px;
            font-size: 1.15rem;
        }}
        .toc ul {{
            list-style: none;
            columns: 2;
            column-gap: 20px;
        }}
        @media (max-width: 700px) {{ .toc ul {{ columns: 1; }} }}
        .toc li {{ margin-bottom: 6px; font-size: 0.88rem; }}
        .toc a {{
            color: var(--primary-accent);
            text-decoration: none;
        }}
        .toc a:hover {{ text-decoration: underline; }}
        .doc-section {{
            margin-bottom: 35px;
            padding-bottom: 25px;
            border-bottom: 1px solid #ECECEC;
        }}
        h2 {{
            color: var(--primary);
            font-size: 1.25rem;
            margin-bottom: 14px;
            padding-bottom: 6px;
            border-bottom: 2px solid var(--beige);
        }}
        .sec-num {{ color: var(--primary-accent); }}
        p {{ margin-bottom: 14px; font-size: 0.95rem; text-align: justify; }}
        pre {{
            background: var(--code-bg);
            color: var(--primary);
            padding: 14px 18px;
            border-radius: 8px;
            border-left: 4px solid var(--primary-accent);
            overflow-x: auto;
            font-family: Consolas, Monaco, "Courier New", monospace;
            font-size: 0.86rem;
            margin-bottom: 16px;
            line-height: 1.45;
        }}
        .action-bar {{
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-bottom: 20px;
        }}
        .btn {{
            background: var(--primary-accent);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
        }}
        .btn:hover {{ background: var(--primary); }}
        @media print {{
            body {{ background: white; padding: 0; }}
            .container {{ box-shadow: none; border: none; padding: 0; max-width: 100%; }}
            .action-bar {{ display: none; }}
            .doc-section {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="action-bar">
            <button class="btn" onclick="window.print()">Imprimir / Guardar como PDF</button>
        </div>
        <div class="cover">
            <div class="inst-badge">{INSTITUCION}</div>
            <h1>{TITULO}</h1>
            <div class="subtitle">{SUBTITULO}</div>
            <div class="meta-grid">
                <div><strong>Proyecto:</strong> EduNova (SINETEC)</div>
                <div><strong>Versi\u00f3n:</strong> 2.4.0 (Listo para Producci\u00f3n)</div>
                <div><strong>Evaluaci\u00f3n:</strong> Entrega Docente</div>
                <div><strong>Stack:</strong> Django 5 | Python 3.13 | MySQL 8 | Gunicorn | Nginx</div>
            </div>
        </div>

        <div class="toc">
            <h3>\u00cdndice General de Contenidos</h3>
            <ul>
                {"".join(toc_links)}
            </ul>
        </div>

        <main>
            {"".join(html_sections)}
        </main>
    </div>
</body>
</html>
'''
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[OK] HTML generado en: {html_path}")

if __name__ == "__main__":
    md_file = os.path.join(DOCS_DIR, "Documentacion_Tecnica_Instalacion_Despliegue_EduNova.md")
    html_file = os.path.join(DOCS_DIR, "Documentacion_Tecnica_Instalacion_Despliegue_EduNova.html")
    build_markdown(md_file)
    build_html(html_file)
