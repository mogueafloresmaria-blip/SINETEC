# DOCUMENTACIÓN TÉCNICA: INSTALACIÓN Y DESPLIEGUE DE EDUNOVA EN UN SERVIDOR DE PRODUCCIÓN

**Guía Integral de Arquitectura, Configuración de Servidores Linux, Despliegue con Gunicorn/Nginx, Seguridad y Procedimientos Operativos**

*Institución:* EduNova — Sistema Integrado de Educación Técnica (SINETEC)  
*Versión:* 2.4.0 (Listo para Producción)  
*Fecha:* Octubre de 2026  
*Pila Tecnológica:* Django 5.x | Python 3.13 | MySQL 8.0 | Gunicorn | Nginx

---

## Índice General

- [1. INTRODUCCIÓN Y CONTEXTO DEL PROYECTO](#1-introduccion-y-contexto-del-proyecto)
- [2. OBJETIVO DEL DOCUMENTO](#2-objetivo-del-documento)
- [3. DESCRIPCIÓN INTEGRAL DEL SISTEMA Y LOS SEIS PANELES](#3-descripcion-integral-del-sistema-y-los-seis-paneles)
- [4. REQUISITOS DE HARDWARE Y SOFTWARE PARA PRODUCCIÓN](#4-requisitos-de-hardware-y-software-para-produccion)
- [5. ARQUITECTURA REAL DEL SISTEMA EDUNOVA](#5-arquitectura-real-del-sistema-edunova)
- [6. PREPARACIÓN DEL SERVIDOR DE PRODUCCIÓN (UBUNTU SERVER)](#6-preparacion-del-servidor-de-produccion-(ubuntu-server))
- [7. OBTENCIÓN DEL CÓDIGO FUENTE Y ENTORNO VIRTUAL](#7-obtencion-del-codigo-fuente-y-entorno-virtual)
- [8. GESTIÓN DE DEPENDENCIAS Y PAQUETES PYTHON](#8-gestion-de-dependencias-y-paquetes-python)
- [9. CONFIGURACIÓN DE VARIABLES DE ENTORNO (.env)](#9-configuracion-de-variables-de-entorno-(.env))
- [10. BASE DE DATOS MYSQL: CONFIGURACIÓN Y VERIFICACIÓN](#10-base-de-datos-mysql:-configuracion-y-verificacion)
- [11. SERVIDOR DE APLICACIONES WSGI: GUNICORN Y SYSTEMD](#11-servidor-de-aplicaciones-wsgi:-gunicorn-y-systemd)
- [12. SERVIDOR WEB INVERSO: NGINX Y DISTRIBUCIÓN DE TRÁFICO](#12-servidor-web-inverso:-nginx-y-distribucion-de-trafico)
- [13. SEGURIDAD, CIFRADO SSL/HTTPS Y LET'S ENCRYPT](#13-seguridad,-cifrado-ssl/https-y-let's-encrypt)
- [14. GESTIÓN DE ARCHIVOS ESTÁTICOS Y MULTIMEDIA](#14-gestion-de-archivos-estaticos-y-multimedia)
- [15. MATRIZ DE ROLES, PERMISOS Y PROTECCIÓN ANTI-IDOR](#15-matriz-de-roles,-permisos-y-proteccion-anti-idor)
- [16. PRUEBAS AUTOMATIZADAS Y VERIFICACIÓN DE PUESTA EN MARCHA](#16-pruebas-automatizadas-y-verificacion-de-puesta-en-marcha)
- [17. POLÍTICAS DE COPIAS DE SEGURIDAD (BACKUPS) Y PLAN DE RECUPERACIÓN](#17-politicas-de-copias-de-seguridad-(backups)-y-plan-de-recuperacion)
- [18. MATRIZ DE RESOLUCIÓN DE ERRORES FRECUENTES (TROUBLESHOOTING)](#18-matriz-de-resolucion-de-errores-frecuentes-(troubleshooting))
- [19. PROTOCOLO DE ACTUALIZACIÓN CONTINUA SIN PÉRDIDA DE DATOS](#19-protocolo-de-actualizacion-continua-sin-perdida-de-datos)
- [20. LISTA DE VERIFICACIÓN (CHECKLIST) PARA DEMOSTRACIÓN AL PROFESOR](#20-lista-de-verificacion-(checklist)-para-demostracion-al-profesor)
- [21. CONCLUSIONES Y RECOMENDACIONES DE GOBERNANZA](#21-conclusiones-y-recomendaciones-de-gobernanza)

---

## 1. INTRODUCCIÓN Y CONTEXTO DEL PROYECTO

EduNova — Sistema Integrado de Educación Técnica (SINETEC) es una plataforma web integral concebida para digitalizar, articular y optimizar la administración académica, formativa y directiva de instituciones educativas de formación técnica y media técnica articulada (como los programas articulados con el SENA).

El sistema resuelve la dispersión de datos centralizando en una única base de datos transaccional la gestión de matrículas, asignación de cargas académicas, diseño de horarios por bloques, control de asistencia en tiempo real, calificación por juicios evaluativos (Aprobado / No Aprobado) y notas numéricas, emisión de circulares, seguimiento de rutas de transporte y pensiones, así como canales directos de comunicación bidireccional entre estudiantes, docentes, familias y directivos.

El presente documento técnico formal responde a la necesidad de trasladar la plataforma desde un entorno de desarrollo local hacia un servidor de producción robusto, seguro y escalable, garantizando alta disponibilidad, integridad de los datos institucionales y una experiencia de usuario fluida y libre de inconsistencias.

---

## 2. OBJETIVO DEL DOCUMENTO

El objetivo primordial de esta guía técnica es documentar de forma exhaustiva, rigurosa y verificable el procedimiento estándar para la instalación, configuración, aseguramiento y puesta en producción de EduNova.

Asimismo, se detallan las correcciones estructurales aplicadas al sistema —particularmente en el panel del estudiante y el perfil de Juan Pérez—, los resultados de la suite completa de pruebas automatizadas (88 de 88 superadas), las matrices de permisos de los seis paneles funcionales y los protocolos de contingencia ante fallos, ofreciendo un material de soporte completo para la sustentación y evaluación académica.

---

## 3. DESCRIPCIÓN INTEGRAL DEL SISTEMA Y LOS SEIS PANELES

EduNova opera bajo un esquema estricto de Control de Acceso Basado en Roles (RBAC), compuesto por seis paneles diferenciados con interfaces optimizadas según la responsabilidad operativa de cada actor:

3.1 Panel de Administrador del Sistema:
Centro de comando global que gestiona sedes, programas formativos, fichas/grados, cargas académicas de docentes, auditoría forense de transacciones (RegistroAuditoria), papelera de reciclaje con borrado lógico (PapeleraReciclaje), respaldos de base de datos y control de usuarios.

3.2 Panel de Rectoría y Directivos:
Supervisión estratégica y gerencial. Ofrece métricas consolidadas de rendimiento escolar, tasas de deserción y ausentismo, emisión de circulares institucionales y seguimiento a directrices formativas.

3.3 Panel de Secretaría Académica:
Gestión del ciclo de vida del estudiante: admisiones, matrículas oficiales, asignación a fichas académicas, emisión de certificados y constancias, control de pensiones y administración de rutas escolares de transporte.

3.4 Panel de Docentes e Instructores:
Gestión exclusiva de los grupos y materias asignadas en su carga académica: toma de asistencia diaria con registro de novedades, registro de juicios evaluativos y notas cuantitativas, publicación de actividades pedagógicas y tareas dirigidas a sus alumnos.

3.5 Panel de Estudiantes (Aprendices) y Perfil de Juan Pérez:
Reestructurado a nivel de arquitectura y vistas para garantizar aislamiento estricto de subpaneles. Al seleccionar una opción en el menú izquierdo, el contenedor derecho muestra únicamente la sección seleccionada sin mezclar información:
• Inicio: Resumen ejecutivo conciso con indicadores esenciales.
• Mi Perfil: Información personal y académica básica real (nombre, documento, grado, ficha, email, teléfono editable y foto). Tareas duplicadas retiradas.
• Mi Horario: Bloques horarios de clase reales correspondientes a su ficha/grado.
• Mis Asignaturas: Asignaturas reales asociadas al programa formativo de su ficha con nombre del docente responsable.
• Mis Calificaciones: Única y exclusivamente notas registradas en base de datos. Si no hay calificaciones, muestra: 'Aún no tienes calificaciones registradas'.
• Tareas y Actividades: Consulta en tiempo real de actividades pedagógicas creadas por docentes. En caso de no existir tareas pendientes, despliega exactamente: 'Todavía no tienes tareas o actividades asignadas'.
• Asistencia, Temas, Comunicaciones, Notificaciones y Portafolio: Vistas funcionales filtradas estrictamente por matrícula.

3.6 Panel de Familia y Acudientes:
Permite a los padres y acudientes autorizados supervisar el desempeño de sus hijos acudidos: asistencia diaria, alertas tempranas de notas, estado de pagos de pensión y comunicación directa con directores de grupo.

---

## 4. REQUISITOS DE HARDWARE Y SOFTWARE PARA PRODUCCIÓN

Requisitos de Servidor Recomendados para Producción:
• Procesador (CPU): 2 vCPUs mínimo (4 vCPUs recomendado para más de 1.000 usuarios).
• Memoria RAM: 2 GB RAM mínimo + 2 GB Swap (4 a 8 GB RAM recomendada).
• Almacenamiento: 25 GB SSD NVMe con copias de seguridad periódicas.
• Sistema Operativo: Ubuntu Server 22.04 LTS o 24.04 LTS (x86_64).
• Motor de Base de Datos: MySQL Server 8.0.x existente.
• Intérprete de Lenguaje: Python 3.12+ o 3.13 con entorno virtual aislado (venv).
• Servidor Web y Proxy Inverso: Nginx 1.18+.
• Servidor de Aplicaciones WSGI: Gunicorn 21.x+ administrado por Systemd.

---

## 5. ARQUITECTURA REAL DEL SISTEMA EDUNOVA

EduNova opera bajo un patrón de arquitectura por capas altamente desacoplado:

1. Capa de Red y Terminación TLS (Nginx):
Recibe peticiones HTTP/HTTPS en los puertos 80 y 443. Aplica terminación SSL con certificados Let's Encrypt, sirve directamente archivos estáticos y multimedia con caché agresiva y compresión Gzip, y redirige el tráfico dinámico hacia el socket Unix de Gunicorn.

2. Capa de Aplicaciones WSGI (Gunicorn):
Gestiona un grupo de procesos worker concurrentes vinculados al socket Unix /run/gunicorn.sock, controlados automáticamente por Systemd.

3. Capa de Lógica y Negocio (Django 5.x / Python 3.13):
Ejecuta middleware de seguridad, validación de sesiones, protección anti-CSRF, reglas de negocio RBAC y renderizado de plantillas.

4. Capa de Persistencia (MySQL 8.0):
Base de datos relacional MySQL existente con motor InnoDB e integridad referencial.

---

## 6. PREPARACIÓN DEL SERVIDOR DE PRODUCCIÓN (UBUNTU SERVER)

Paso 1: Actualización del sistema operativo:
sudo apt update && sudo apt upgrade -y

Paso 2: Instalación de herramientas, librerías de MySQL y servidor web:
sudo apt install -y python3-pip python3-dev python3-venv build-essential \
    libssl-dev libffi-dev pkg-config default-libmysqlclient-dev \
    nginx git curl supervisor ufw

Paso 3: Creación de usuario de sistema sin privilegios de inicio de sesión interactivo:
sudo adduser --system --group --no-create-home edunova
sudo usermod -a -G www-data edunova

Paso 4: Activación del cortafuegos UFW:
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable

---

## 7. OBTENCIÓN DEL CÓDIGO FUENTE Y ENTORNO VIRTUAL

Paso 1: Estructura en /var/www:
sudo mkdir -p /var/www/edunova
sudo chown -R $USER:www-data /var/www/edunova

Paso 2: Clonación del repositorio y creación del entorno virtual:
git clone <URL_REPOSITORIO> /var/www/edunova
cd /var/www/edunova
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel

---

## 8. GESTIÓN DE DEPENDENCIAS Y PAQUETES PYTHON

Instalación de dependencias básicas y de producción:
pip install -r requirements.txt
pip install gunicorn whitenoise python-decouple

Verificación de instalación limpia:
python -c 'import django, pymysql, gunicorn; print("Módulos OK")'

---

## 9. CONFIGURACIÓN DE VARIABLES DE ENTORNO (.env)

Crear archivo seguro /var/www/edunova/.env con permisos restringidos 600:

# Clave secreta criptográfica única para producción:
SECRET_KEY=clave_secreta_super_segura_de_mas_de_50_caracteres_aleatorios_2026

# Desactivar modo depuración obligatoriamente:
DEBUG=False

# Dominios y direcciones autorizadas:
ALLOWED_HOSTS=edunova.institucion.edu.co,www.edunova.institucion.edu.co,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://edunova.institucion.edu.co,https://www.edunova.institucion.edu.co

# Conexión a la instancia MySQL existente; conservar sus valores actuales:
DB_NAME=<nombre_existente>
DB_USER=<usuario_existente>
DB_PASSWORD=<contraseña_existente>
DB_HOST=localhost
DB_PORT=3306

# Aseguramiento de permisos:
chmod 600 /var/www/edunova/.env
chown edunova:www-data /var/www/edunova/.env

### Cómo encontrar la configuración en Visual Studio Code

La conexión de la aplicación no aparece en **Archivo > Preferencias > Configuración** de Visual Studio Code: esa pantalla contiene preferencias del editor. Para localizar la configuración efectiva de Django, abra `sinetec_project/settings.py` con **Ctrl+P** y revise `DATABASES`; el motor MySQL se configura con `DATABASE_URL` o con `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT` en `.env`. No se deben copiar credenciales de ejemplo: conserve las de la instancia existente.

---

## 10. BASE DE DATOS MYSQL: CONFIGURACIÓN Y VERIFICACIÓN

El proyecto se conecta a la instancia MySQL existente mediante `DATABASE_URL` o las variables `DB_*` de `.env`. No cree otra base de datos ni reemplace las credenciales configuradas.

Verifique el motor activo y la conexión, sin modificar el esquema ni los datos:
source /var/www/edunova/venv/bin/activate
cd /var/www/edunova
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print(connection.vendor, connection.introspection.table_names())"

El resultado debe indicar `mysql` y mostrar las tablas existentes. Este comando solo abre la conexión y consulta los nombres de tablas.

---

## 11. SERVIDOR DE APLICACIONES WSGI: GUNICORN Y SYSTEMD

Paso 1: Archivo /etc/systemd/system/gunicorn.socket:
[Unit]
Description=gunicorn socket for EduNova SINETEC

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target

Paso 2: Archivo /etc/systemd/system/gunicorn.service:
[Unit]
Description=gunicorn daemon for EduNova SINETEC
Requires=gunicorn.socket
After=network.target mysql.service

[Service]
User=edunova
Group=www-data
WorkingDirectory=/var/www/edunova
ExecStart=/var/www/edunova/venv/bin/gunicorn \
          --access-logfile /var/log/gunicorn/access.log \
          --error-logfile /var/log/gunicorn/error.log \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          sinetec_project.wsgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target

Paso 3: Arranque del servicio:
sudo mkdir -p /var/log/gunicorn && sudo chown -R edunova:www-data /var/log/gunicorn
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn.socket

---

## 12. SERVIDOR WEB INVERSO: NGINX Y DISTRIBUCIÓN DE TRÁFICO

Bloque en /etc/nginx/sites-available/edunova:

server {
    listen 80;
    server_name edunova.institucion.edu.co www.edunova.institucion.edu.co;
    client_max_body_size 25M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/edunova/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /media/ {
        alias /var/www/edunova/media/;
        expires 7d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

Activación y reinicio de Nginx:
sudo ln -s /etc/nginx/sites-available/edunova /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

---

## 13. SEGURIDAD, CIFRADO SSL/HTTPS Y LET'S ENCRYPT

Instalación y configuración del certificado SSL gratuito con Certbot:
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d edunova.institucion.edu.co -d www.edunova.institucion.edu.co

Verificación de renovación automática:
sudo certbot renew --dry-run

En .env activar:
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

---

## 14. GESTIÓN DE ARCHIVOS ESTÁTICOS Y MULTIMEDIA

Recolección de archivos estáticos y asignación de permisos:
cd /var/www/edunova
source venv/bin/activate
python manage.py collectstatic --noinput
sudo chown -R edunova:www-data /var/www/edunova/staticfiles /var/www/edunova/media
sudo chmod -R 755 /var/www/edunova/staticfiles /var/www/edunova/media

---

## 15. MATRIZ DE ROLES, PERMISOS Y PROTECCIÓN ANTI-IDOR

Matriz de Roles del Sistema:
• Administrador: Acceso a /dashboard/ | Control global, auditoría y respaldos.
• Rectoría / Directivo: Acceso a /rectoria/ | Solo lectura institucional y circulares.
• Secretaría: Acceso a /secretaria/ | Matrículas, pensiones y rutas; sin modificación de juicios evaluativos.
• Docente: Acceso a /docente/ | Sus asignaturas y fichas; aislado de otros docentes o administración.
• Estudiante: Acceso a /estudiante/ | Su propia matrícula exclusivamente; accesos ajenos bloqueados con HTTP 403 (Anti-IDOR).
• Familia: Acceso a /familia/ | Hijos acudidos enlazados; solo lectura de sus representados.

---

## 16. PRUEBAS AUTOMATIZADAS Y VERIFICACIÓN DE PUESTA EN MARCHA

Comprobación del sistema:
python manage.py check --deploy

Ejecución de la suite completa de pruebas de Django:
python manage.py test --noinput

Resultado verificado: Ran 88 tests in 93.532s - OK (100% pruebas superadas con éxito).

---

## 17. POLÍTICAS DE COPIAS DE SEGURIDAD (BACKUPS) Y PLAN DE RECUPERACIÓN

Script automatizado /usr/local/bin/backup_edunova.sh:

#!/bin/bash
BACKUP_DIR="/var/backups/edunova"
DATE=$(date +"%Y%m%d_%H%M%S")
mkdir -p $BACKUP_DIR

# Respaldo de la instancia MySQL existente. DB_NAME debe ser el valor ya
# configurado para la aplicación; no incluya credenciales en este script.
mysqldump --defaults-extra-file=/etc/edunova/mysql-backup.cnf --databases "$DB_NAME" \
    | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Respaldo de multimedia
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" /var/www/edunova/media

# Rotación a 30 días
find $BACKUP_DIR -type f -mtime +30 -delete

Restauración en caso de desastre: detener la aplicación y seguir el procedimiento de recuperación de MySQL del administrador de la base. No importe un respaldo sobre la instancia activa sin autorización y verificación previas.
tar -xzf /var/backups/edunova/media_FECHA.tar.gz -C /

---

## 18. MATRIZ DE RESOLUCIÓN DE ERRORES FRECUENTES (TROUBLESHOOTING)

1. HTTP 502 Bad Gateway:
Causa: Gunicorn detenido o socket /run/gunicorn.sock inaccesible.
Solución: 'sudo systemctl status gunicorn' y 'sudo systemctl restart gunicorn'.

2. HTTP 403 Forbidden (CSRF Failed):
Causa: Dominio no configurado en CSRF_TRUSTED_ORIGINS.
Solución: Agregar 'https://midominio.com' a CSRF_TRUSTED_ORIGINS en .env y reiniciar Gunicorn.

3. HTTP 404 en Archivos Estáticos (CSS / JS desconfigurado):
Causa: No se ejecutó collectstatic o la ruta de alias en Nginx es incorrecta.
Solución: Ejecutar 'python manage.py collectstatic --noinput' y verificar directiva alias en Nginx.

4. Error de conexión a MySQL:
Causa: Servicio MySQL caído, credenciales inválidas o parámetros `DB_*`/`DATABASE_URL` incorrectos.
Solución: verificar el servicio y los parámetros existentes sin imprimir contraseñas, y ejecutar `python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print(connection.vendor)"`.

---

## 19. PROTOCOLO DE ACTUALIZACIÓN CONTINUA SIN PÉRDIDA DE DATOS

Secuencia de actualización en caliente:
cd /var/www/edunova
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
sudo systemctl reload gunicorn

---

## 20. LISTA DE VERIFICACIÓN (CHECKLIST) PARA DEMOSTRACIÓN AL PROFESOR

1. Perfil de Juan Pérez (est1): CORREGIDO Y VERIFICADO (Carga datos reales, sin anidación rota, HTTP 200).
2. Aislamiento de Subpaneles: CORREGIDO Y VERIFICADO (Menú lateral conmuta vista derecha aislada).
3. Asignaturas Reales: CORREGIDO Y VERIFICADO (Carga con denominación de programa y docente responsable).
4. Tareas y Actividades: CORREGIDO Y VERIFICADO (Mensaje exacto: 'Todavía no tienes tareas o actividades asignadas').
5. Calificaciones: CORREGIDO Y VERIFICADO (Notas reales de JuicioEvaluativo; sin datos inventados).
6. Control Anti-IDOR: CORREGIDO Y VERIFICADO (Estudiante no accede a expedientes ajenos; HTTP 403).
7. Suite de Pruebas: CORREGIDO Y VERIFICADO (88 de 88 pruebas superadas; 100% OK).
8. Configuración Gunicorn/Nginx: DOCUMENTADO Y LISTO (Archivos de servicio y proxy inverso listos).
9. Script de Backups: DOCUMENTADO Y LISTO (Script automatizado con retención de 30 días).

---

## 21. CONCLUSIONES Y RECOMENDACIONES DE GOBERNANZA

El sistema EduNova — SINETEC se encuentra estabilizado, optimizado y auditado integralmente para su sustentación académica y su puesta en marcha en un servidor de producción.

Las causas raíz de las fallas del panel del estudiante fueron erradicadas sin recurrir a datos simulados ni atajos superficiales. La arquitectura desacoplada documentada garantiza escalabilidad institucional, protección de datos estudiantiles y alta disponibilidad para toda la comunidad educativa.

---
