# GUÍA DE INSTALACIÓN, CONFIGURACIÓN Y CONEXIÓN DE MYSQL SERVER
### SISTEMA SINETEC – PROYECTO FORMATIVO ADSI (228106)
**Centro de Logística y Promoción Ecoturística del Magdalena**

---

## 1. INTRODUCCIÓN PEDAGÓGICA A MYSQL SERVER Y MYSQL WORKBENCH

### ¿Qué es MySQL Server?
Es un Sistema Gestor de Bases de Datos Relacionales (RDBMS) de código abierto, creado por Oracle, que procesa y almacena tablas con relaciones matemáticas estrictas mediante el lenguaje SQL.

### ¿Para qué sirve y por qué lo necesitamos en SINETEC?
1. **Persistencia Profesional:** Permite almacenar de forma permanente y masiva los registros de colegios, aprendices, notas y bitácoras del Magdalena.
2. **Motor InnoDB:** Proporciona transacciones seguras (propiedades ACID) y soporte de llaves foráneas (`FOREIGN KEY`) para evitar que se borren colegios que tienen fichas activas o notas huérfanas.
3. **Requisito del Programa ADSI:** El manejo de MySQL Server y MySQL Workbench es una competencia técnica evaluada obligatoriamente en el proyecto formativo.

### ¿Qué es MySQL Workbench?
Es el entorno visual oficial con ventanas, botones y gráficos para administrar MySQL sin necesidad de memorizar comandos de consola negra.

---

## 2. GUÍA PASO A PASO DE INSTALACIÓN Y PUESTA EN MARCHA

### Opción A: Mediante el Instalador Oficial de MySQL (Recomendada)
1. **Descargar el Instalador:**
   * Ingrese a la web oficial: `https://dev.mysql.com/downloads/installer/`
   * Descargue el archivo `mysql-installer-community-8.0.x.msi` (aproximadamente 400 MB).
2. **Seleccionar Componentes:**
   * En la pantalla *Choosing a Setup Type*, seleccione **Custom** (Personalizado).
   * Añada a la lista de instalación:
     * `MySQL Server 8.0` (El motor de base de datos).
     * `MySQL Workbench 8.0` (La interfaz visual de administración).
3. **Configuración del Servidor:**
   * *Type and Networking:* Deje el puerto por defecto **3306**.
   * *Authentication Method:* Seleccione *Use Strong Password Encryption* (Recomendado).
   * *Accounts and Roles:* Defina una contraseña para el usuario `root` (ejemplo: `admin1234*` o `Sena2026*`). **¡Anote esta contraseña!**
   * *Windows Service:* Deje el nombre del servicio como `MySQL80` y marque la casilla *"Start the MySQL Server at System Startup"*.
4. **Finalizar Instalación:** Presione *Execute* hasta que todos los pasos se marquen en verde.

---

### Opción B: Mediante XAMPP (Alternativa Ligera para Desarrollo)
1. Si ya tiene instalado **XAMPP**, simplemente abra el panel de control de XAMPP.
2. En la fila que dice **MySQL**, haga clic en el botón **Start**.
3. El botón se pondrá en verde y mostrará el puerto **3306**.
4. En XAMPP, el usuario por defecto es `root` y la contraseña está **en blanco** (vacía).

---

## 3. CÓMO EJECUTAR EL SCRIPT SQL EN MYSQL WORKBENCH

1. Abra **MySQL Workbench** desde el menú de inicio de Windows.
2. En la pantalla principal, haga clic en la conexión local: `Local instance MySQL80` (o `localhost:3306`).
3. Digite la contraseña de `root` que definió al instalar.
4. En el menú superior, seleccione: **File -> Open SQL Script...**
5. Busque y abra el archivo de nuestro proyecto ubicado en:  
   `c:\Users\ADMIN\Documents\SENA ADSI\Proyectos\SINETEC\docs\05_base_de_datos\script_creacion_inicial_mysql.sql`
6. En la barra de herramientas, presione el ícono del **Rayo amarillo (Execute)**.
7. En el panel inferior (*Output*), verá cómo se crean una a una las 11 tablas con marcas de verificación verdes.
8. En el panel izquierdo (*Schemas*), haga clic derecho y seleccione **Refresh All**. Aparecerá la base de datos `sinetec_db` con todas sus tablas.

---

## 4. CÓMO ACTIVAR LA CONEXIÓN DE SINETEC CON MYSQL SERVER

Una vez que MySQL esté encendido:

1. Abra el archivo `.env` en la raíz de su proyecto SINETEC y verifique sus credenciales:
   ```properties
   USE_MYSQL=True
   DB_NAME=sinetec_db
   DB_USER=root
   DB_PASSWORD=su_contraseña_aqui
   DB_HOST=localhost
   DB_PORT=3306
   ```
2. Ejecute el script de diagnóstico automático creado en su proyecto:
   ```powershell
   .\venv\Scripts\python.exe verificar_mysql.py
   ```
3. Aplique las migraciones en MySQL:
   ```powershell
   .\venv\Scripts\python.exe manage.py migrate
   ```
4. Cargue los datos demostrativos en MySQL:
   ```powershell
   .\venv\Scripts\python.exe manage.py cargar_datos_demo
   ```

---

## 5. LOS 5 ERRORES MÁS COMUNES Y CÓMO SOLUCIONARLOS

### Error 1: `Can't connect to MySQL server on 'localhost' (10061)`
* **Qué significa:** El servidor MySQL no está encendido o el puerto 3306 está bloqueado.
* **Solución:** Abra el menú de inicio de Windows, escriba `services.msc`, busque el servicio `MySQL80`, haga clic derecho y seleccione **Iniciar**. Si usa XAMPP, presione **Start** en MySQL.

### Error 2: `Access denied for user 'root'@'localhost' (using password: YES)`
* **Qué significa:** La contraseña escrita en el archivo `.env` no coincide con la contraseña asignada al instalar MySQL Server.
* **Solución:** Abra el archivo `.env` y corrija el campo `DB_PASSWORD` colocando la contraseña exacta. Si no recuerda la contraseña, en XAMPP suele ser vacía (`DB_PASSWORD=`).

### Error 3: `Unknown database 'sinetec_db'`
* **Qué significa:** MySQL está funcionando, pero aún no se ha creado la base de datos vacía.
* **Solución:** Ejecute en su terminal `python verificar_mysql.py` (este script la crea automáticamente) o en Workbench ejecute: `CREATE DATABASE sinetec_db;`.

### Error 4: `Error 1451: Cannot delete or update a parent row: a foreign key constraint fails`
* **Qué significa:** Se intenta borrar un registro padre (ejemplo: un colegio) que ya tiene registros hijos asociados (fichas técnicas o aprendices).
* **Solución:** Es el comportamiento correcto de la base de datos para proteger la integridad referencial. Para anular un colegio, use borrado lógico cambiando su estado a `activa = False`.

### Error 5: `ModuleNotFoundError: No module named 'MySQLdb'`
* **Qué significa:** Django no encuentra el conector de base de datos.
* **Solución:** Ya lo dejamos resuelto en SINETEC utilizando **PyMySQL** en `sinetec_project/__init__.py`. Solo asegúrese de tener activo su entorno virtual `venv`.

---

## 6. APORTE A LOS RESULTADOS DE APRENDIZAJE SENA
*Esta actividad contribuye al resultado de aprendizaje relacionado con **administrar y configurar sistemas manejadores de bases de datos de acuerdo con los requerimientos del software**, porque proporciona los procedimientos de instalación, contingencia, scripts DDL y políticas de integridad referencial requeridas para el entorno de producción.*
