"""
==============================================================================
PROYECTO FORMATIVO: SISTEMAS DE INFORMACIÓN Y DESARROLLO DE SOFTWARE EN EL MAGDALENA
SOFTWARE: SINETEC (Sistema de Integración Técnica Education)
CENTRO: Centro de Logística y Promoción Ecoturística del Magdalena - ADSI 228106
ARCHIVO: verificar_mysql.py
DESCRIPCIÓN: Script pedagógico para verificar el estado de MySQL Server,
             probar la conexión en el puerto 3306, crear la base de datos
             'sinetec_db' y activar la conexión en Django.
==============================================================================
"""

import sys
from pathlib import Path
from decouple import config

try:
    import pymysql
except ImportError:
    print("[-] Error: PyMySQL no está instalado en el entorno virtual.")
    print("    Ejecute: pip install PyMySQL")
    sys.exit(1)


def diagnosticar_mysql():
    print("=" * 70)
    print("  DIAGNÓSTICO DE CONEXIÓN MYSQL SERVER - PROYECTO SINETEC")
    print("=" * 70)

    # Leer credenciales desde el archivo .env
    db_host = config('DB_HOST', default='localhost')
    db_port = config('DB_PORT', default=3306, cast=int)
    db_user = config('DB_USER', default='root')
    db_password = config('DB_PASSWORD', default='')
    db_name = config('DB_NAME', default='sinetec_db')

    print(f"[*] Parámetros configurados en .env:")
    print(f"    - Host: {db_host}")
    print(f"    - Puerto: {db_port}")
    print(f"    - Usuario: {db_user}")
    print(f"    - Contraseña: {'[Configurada]' if db_password else '[En blanco]'}")
    print(f"    - Base de Datos Objetivo: {db_name}")
    print("-" * 70)

    # Paso 1: Probar conexión básica al servidor MySQL
    print(f"[*] Intentando conectar con el servidor MySQL en {db_host}:{db_port}...")
    try:
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            charset='utf8mb4',
            connect_timeout=5
        )
        print("[+] ¡ÉXITO! Conexión establecida correctamente con MySQL Server.")
    except pymysql.MySQLError as e:
        print("\n[-] NO SE PUDO CONECTAR CON MYSQL SERVER.")
        print(f"    Detalle del error: {e}")
        print("\n[?] POSIBLES CAUSAS Y SOLUCIONES:")
        print("    1. MySQL Server no está encendido:")
        print("       - Si usa MySQL Server nativo: Abra Servicios de Windows (services.msc) y verifique que 'MySQL80' esté 'En ejecución'.")
        print("       - Si usa XAMPP: Abra el panel de XAMPP y presione 'Start' en el módulo MySQL.")
        print("    2. La contraseña de 'root' es diferente:")
        print("       - Si definió una contraseña durante la instalación, escríbala en el archivo .env en: DB_PASSWORD=su_clave")
        print("    3. El puerto 3306 está ocupado por otro servicio:")
        print("       - Verifique con netstat -ano | findstr 3306")
        print("-" * 70)
        print("[i] SINETEC continúa funcionando de manera segura con la base de datos local SQLite.")
        return False

    # Paso 2: Verificar o crear la base de datos sinetec_db
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES;")
            bases_datos = [row[0] for row in cursor.fetchall()]

            if db_name in bases_datos:
                print(f"[+] La base de datos '{db_name}' ya existe en el servidor.")
            else:
                print(f"[*] Creando la base de datos '{db_name}' con cotejamiento utf8mb4...")
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                print(f"[+] ¡Base de datos '{db_name}' creada exitosamente!")

        connection.close()

        # Paso 3: Ofrecer activar USE_MYSQL=True en .env
        env_path = Path(__file__).resolve().parent / '.env'
        if env_path.exists():
            contenido = env_path.read_text(encoding='utf-8')
            if 'USE_MYSQL=False' in contenido:
                print("\n[!] ¿Desea activar MySQL como la base de datos activa para Django? (s/n): ", end="")
                opcion = input().strip().lower()
                if opcion == 's':
                    nuevo_contenido = contenido.replace('USE_MYSQL=False', 'USE_MYSQL=True')
                    env_path.write_text(nuevo_contenido, encoding='utf-8')
                    print("[+] Configuración actualizada: USE_MYSQL=True en archivo .env.")
                    print("[*] Ejecute ahora: python manage.py migrate")
            elif 'USE_MYSQL=True' in contenido:
                print("[+] Django ya está configurado para usar MySQL (USE_MYSQL=True).")

        print("=" * 70)
        print("  DIAGNÓSTICO FINALIZADO CON ÉXITO")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"[-] Ocurrió un error durante la creación de la base de datos: {e}")
        connection.close()
        return False


if __name__ == '__main__':
    diagnosticar_mysql()
