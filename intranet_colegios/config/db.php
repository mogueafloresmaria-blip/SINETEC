<?php
// config/db.php - Conexión de Base de Datos para DYL SCHOOL
// Soporta MySQL con creación automática de esquema y fallback transparente a SQLite

class Database {
    private static ?PDO $instance = null;
    private static string $driver = 'mysql';

    public static function getConnection(): PDO {
        if (self::$instance !== null) {
            return self::$instance;
        }

        $host = 'localhost';
        $port = '3306';
        $dbname = 'dyl_school_db';
        $user = 'root';
        $pass = '12345';

        // Intento 1: Conexión a MySQL
        try {
            // Conectar primero sin DB para crearla si no existe
            $pdoInit = new PDO("mysql:host={$host};port={$port};charset=utf8mb4", $user, $pass, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_TIMEOUT => 3
            ]);
            $pdoInit->exec("CREATE DATABASE IF NOT EXISTS `{$dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
            unset($pdoInit);

            // Conectar a la base de datos
            self::$instance = new PDO("mysql:host={$host};port={$port};dbname={$dbname};charset=utf8mb4", $user, $pass, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_EMULATE_PREPARES => false,
            ]);
            self::$driver = 'mysql';
        } catch (Throwable $e) {
            // Fallback: SQLite local en caso de que MySQL no esté disponible
            $dbPath = __DIR__ . '/../data/dyl_school.sqlite';
            if (!file_exists(dirname($dbPath))) {
                @mkdir(dirname($dbPath), 0777, true);
            }
            self::$instance = new PDO("sqlite:" . $dbPath, null, null, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            ]);
            self::$driver = 'sqlite';
        }

        return self::$instance;
    }

    public static function getDriver(): string {
        return self::$driver;
    }
}
