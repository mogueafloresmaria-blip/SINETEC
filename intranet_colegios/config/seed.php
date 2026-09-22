<?php
// config/seed.php - Migración de Base de Datos y Población de Datos Iniciales para DYL SCHOOL
require_once __DIR__ . '/db.php';

$pdo = Database::getConnection();
$driver = Database::getDriver();

// 1. Crear Tablas
if ($driver === 'mysql') {
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS `usuarios` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `username` VARCHAR(100) NOT NULL UNIQUE,
            `password_hash` VARCHAR(255) NOT NULL,
            `rol` ENUM('admin', 'docente', 'alumno') NOT NULL DEFAULT 'alumno',
            `nombres` VARCHAR(100) NOT NULL,
            `apellidos` VARCHAR(100) NOT NULL,
            `email` VARCHAR(150) NULL,
            `dni` VARCHAR(20) NOT NULL UNIQUE,
            `telefono` VARCHAR(30) NULL,
            `foto` VARCHAR(255) NULL,
            `estado` VARCHAR(20) NOT NULL DEFAULT 'Activo',
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `grados` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `nivel` VARCHAR(30) NOT NULL,
            `nombre` VARCHAR(50) NOT NULL,
            `orden` INT NOT NULL DEFAULT 1
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `secciones` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `nombre` VARCHAR(10) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `alumnos` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `usuario_id` INT NULL,
            `nombres` VARCHAR(100) NOT NULL,
            `apellidos` VARCHAR(100) NOT NULL,
            `dni` VARCHAR(20) NOT NULL UNIQUE,
            `fecha_nacimiento` DATE NULL,
            `genero` ENUM('Masculino', 'Femenino') NOT NULL DEFAULT 'Masculino',
            `correo` VARCHAR(150) NULL,
            `telefono_apoderado` VARCHAR(30) NULL,
            `foto` VARCHAR(255) NULL,
            `estado` ENUM('ACTIVO', 'BAJA') NOT NULL DEFAULT 'ACTIVO',
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `profesores` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `usuario_id` INT NULL,
            `nombres` VARCHAR(100) NOT NULL,
            `apellidos` VARCHAR(100) NOT NULL,
            `dni` VARCHAR(20) NOT NULL UNIQUE,
            `genero` ENUM('Masculino', 'Femenino') NOT NULL DEFAULT 'Masculino',
            `correo` VARCHAR(150) NULL,
            `telefono` VARCHAR(30) NULL,
            `foto` VARCHAR(255) NULL,
            `estado` ENUM('ACTIVO', 'BAJA') NOT NULL DEFAULT 'ACTIVO',
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `cursos` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `nombre` VARCHAR(100) NOT NULL,
            `tipo` ENUM('Oficial', 'Taller') NOT NULL DEFAULT 'Oficial',
            `activo` TINYINT(1) NOT NULL DEFAULT 1
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `curso_grados` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `curso_id` INT NOT NULL,
            `grado_id` INT NOT NULL,
            FOREIGN KEY (`curso_id`) REFERENCES `cursos`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`grado_id`) REFERENCES `grados`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `matriculas` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `alumno_id` INT NOT NULL,
            `grado_id` INT NOT NULL,
            `seccion_id` INT NOT NULL,
            `anio_lectivo` INT NOT NULL DEFAULT 2026,
            `estado_pension` ENUM('ADELANTADO', 'AL_DIA', 'SIN_HISTORIAL', 'REQUIERE_PAGO') NOT NULL DEFAULT 'SIN_HISTORIAL',
            `pagado_hasta` VARCHAR(50) NULL,
            `fecha_matricula` DATE NOT NULL,
            FOREIGN KEY (`alumno_id`) REFERENCES `alumnos`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`grado_id`) REFERENCES `grados`(`id`) ON DELETE RESTRICT,
            FOREIGN KEY (`seccion_id`) REFERENCES `secciones`(`id`) ON DELETE RESTRICT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `asignaciones` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `profesor_id` INT NOT NULL,
            `curso_id` INT NOT NULL,
            `grado_id` INT NOT NULL,
            `seccion_id` INT NOT NULL,
            `anio_lectivo` INT NOT NULL DEFAULT 2026,
            FOREIGN KEY (`profesor_id`) REFERENCES `profesores`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`curso_id`) REFERENCES `cursos`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`grado_id`) REFERENCES `grados`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`seccion_id`) REFERENCES `secciones`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `horarios` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `curso_id` INT NULL,
            `grado_id` INT NOT NULL,
            `seccion_id` INT NOT NULL,
            `dia` VARCHAR(20) NOT NULL,
            `hora_inicio` VARCHAR(10) NOT NULL,
            `hora_fin` VARCHAR(10) NOT NULL,
            `modalidad` VARCHAR(50) DEFAULT 'Presencial',
            `es_recreo` TINYINT(1) NOT NULL DEFAULT 0,
            FOREIGN KEY (`curso_id`) REFERENCES `cursos`(`id`) ON DELETE SET NULL,
            FOREIGN KEY (`grado_id`) REFERENCES `grados`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`seccion_id`) REFERENCES `secciones`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `notas` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `matricula_id` INT NOT NULL,
            `curso_id` INT NOT NULL,
            `bimestre_1` DECIMAL(4,2) NULL,
            `bimestre_2` DECIMAL(4,2) NULL,
            `bimestre_3` DECIMAL(4,2) NULL,
            `bimestre_4` DECIMAL(4,2) NULL,
            `promedio_final` DECIMAL(4,2) NULL,
            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (`matricula_id`) REFERENCES `matriculas`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`curso_id`) REFERENCES `cursos`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `pagos` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `numero_recibo` VARCHAR(50) NOT NULL UNIQUE,
            `matricula_id` INT NOT NULL,
            `alumno_id` INT NOT NULL,
            `concepto` VARCHAR(200) NOT NULL,
            `mes_pension` VARCHAR(50) NULL,
            `metodo_pago` VARCHAR(50) NOT NULL,
            `monto` DECIMAL(10,2) NOT NULL,
            `comprobante_foto` VARCHAR(255) NULL,
            `es_matricula` TINYINT(1) NOT NULL DEFAULT 0,
            `estado` ENUM('EMITIDO', 'ANULADO') NOT NULL DEFAULT 'EMITIDO',
            `fecha_pago` DATETIME DEFAULT CURRENT_TIMESTAMP,
            `usuario_cajero_id` INT NULL,
            FOREIGN KEY (`matricula_id`) REFERENCES `matriculas`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`alumno_id`) REFERENCES `alumnos`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `comunicados` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `titulo` VARCHAR(200) NOT NULL,
            `mensaje` TEXT NOT NULL,
            `fecha` DATE NOT NULL,
            `audiencia` ENUM('Todos', 'Alumno') NOT NULL DEFAULT 'Todos',
            `alumno_id` INT NULL,
            `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`alumno_id`) REFERENCES `alumnos`(`id`) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `asistencia` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `matricula_id` INT NOT NULL,
            `fecha` DATE NOT NULL,
            `estado` ENUM('Presente', 'Tarde', 'Falta') NOT NULL DEFAULT 'Presente',
            `observacion` VARCHAR(255) NULL,
            UNIQUE KEY `asist_mat_fecha` (`matricula_id`, `fecha`),
            FOREIGN KEY (`matricula_id`) REFERENCES `matriculas`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS `transporte` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `nombre_ruta` VARCHAR(150) NOT NULL,
            `conductor` VARCHAR(150) NOT NULL,
            `placa` VARCHAR(20) NOT NULL,
            `capacidad` INT NOT NULL DEFAULT 15,
            `costo_mensual` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            `estado` VARCHAR(20) NOT NULL DEFAULT 'Activo'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ");
} else {
    // SQLite Syntax
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'alumno',
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            email TEXT NULL,
            dni TEXT NOT NULL UNIQUE,
            telefono TEXT NULL,
            foto TEXT NULL,
            estado TEXT NOT NULL DEFAULT 'Activo',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS grados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nivel TEXT NOT NULL,
            nombre TEXT NOT NULL,
            orden INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS secciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            dni TEXT NOT NULL UNIQUE,
            fecha_nacimiento DATE NULL,
            genero TEXT NOT NULL DEFAULT 'Masculino',
            correo TEXT NULL,
            telefono_apoderado TEXT NULL,
            foto TEXT NULL,
            estado TEXT NOT NULL DEFAULT 'ACTIVO',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS profesores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            dni TEXT NOT NULL UNIQUE,
            genero TEXT NOT NULL DEFAULT 'Masculino',
            correo TEXT NULL,
            telefono TEXT NULL,
            foto TEXT NULL,
            estado TEXT NOT NULL DEFAULT 'ACTIVO',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS cursos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'Oficial',
            activo INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS curso_grados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            curso_id INTEGER NOT NULL,
            grado_id INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS matriculas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER NOT NULL,
            grado_id INTEGER NOT NULL,
            seccion_id INTEGER NOT NULL,
            anio_lectivo INTEGER NOT NULL DEFAULT 2026,
            estado_pension TEXT NOT NULL DEFAULT 'SIN_HISTORIAL',
            pagado_hasta TEXT NULL,
            fecha_matricula DATE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS asignaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profesor_id INTEGER NOT NULL,
            curso_id INTEGER NOT NULL,
            grado_id INTEGER NOT NULL,
            seccion_id INTEGER NOT NULL,
            anio_lectivo INTEGER NOT NULL DEFAULT 2026
        );

        CREATE TABLE IF NOT EXISTS horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            curso_id INTEGER NULL,
            grado_id INTEGER NOT NULL,
            seccion_id INTEGER NOT NULL,
            dia TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fin TEXT NOT NULL,
            modalidad TEXT DEFAULT 'Presencial',
            es_recreo INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula_id INTEGER NOT NULL,
            curso_id INTEGER NOT NULL,
            bimestre_1 REAL NULL,
            bimestre_2 REAL NULL,
            bimestre_3 REAL NULL,
            bimestre_4 REAL NULL,
            promedio_final REAL NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_recibo TEXT NOT NULL UNIQUE,
            matricula_id INTEGER NOT NULL,
            alumno_id INTEGER NOT NULL,
            concepto TEXT NOT NULL,
            mes_pension TEXT NULL,
            metodo_pago TEXT NOT NULL,
            monto REAL NOT NULL,
            comprobante_foto TEXT NULL,
            es_matricula INTEGER NOT NULL DEFAULT 0,
            estado TEXT NOT NULL DEFAULT 'EMITIDO',
            fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP,
            usuario_cajero_id INTEGER NULL
        );

        CREATE TABLE IF NOT EXISTS comunicados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha DATE NOT NULL,
            audiencia TEXT NOT NULL DEFAULT 'Todos',
            alumno_id INTEGER NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS asistencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula_id INTEGER NOT NULL,
            fecha DATE NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Presente',
            observacion TEXT NULL,
            UNIQUE(matricula_id, fecha)
        );

        CREATE TABLE IF NOT EXISTS transporte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_ruta TEXT NOT NULL,
            conductor TEXT NOT NULL,
            placa TEXT NOT NULL,
            capacidad INTEGER NOT NULL DEFAULT 15,
            costo_mensual REAL NOT NULL DEFAULT 0.00,
            estado TEXT NOT NULL DEFAULT 'Activo'
        );
    ");
}

// 2. Poblar Grados y Secciones si están vacíos
$stmt = $pdo->query("SELECT COUNT(*) FROM grados");
if ($stmt->fetchColumn() == 0) {
    // Inicial (3, 4, 5 Años)
    $gradosInicial = ['Inicial 3 Años', 'Inicial 4 Años', 'Inicial 5 Años'];
    foreach ($gradosInicial as $idx => $g) {
        $ins = $pdo->prepare("INSERT INTO grados (nivel, nombre, orden) VALUES ('Inicial', ?, ?)");
        $ins->execute([$g, $idx + 1]);
    }
    // Primaria (1ro a 6to)
    $gradosPrimaria = ['1ro Grado', '2do Grado', '3ro Grado', '4to Grado', '5to Grado', '6to Grado'];
    foreach ($gradosPrimaria as $idx => $g) {
        $ins = $pdo->prepare("INSERT INTO grados (nivel, nombre, orden) VALUES ('Primaria', ?, ?)");
        $ins->execute([$g, $idx + 10]);
    }
    // Secundaria (1ro a 5to)
    $gradosSecundaria = ['1ro Año', '2do Año', '3ro Año', '4to Año', '5to Año'];
    foreach ($gradosSecundaria as $idx => $g) {
        $ins = $pdo->prepare("INSERT INTO grados (nivel, nombre, orden) VALUES ('Secundaria', ?, ?)");
        $ins->execute([$g, $idx + 20]);
    }
}


$stmt = $pdo->query("SELECT COUNT(*) FROM secciones");
if ($stmt->fetchColumn() == 0) {
    foreach (['A', 'B', 'C', 'D'] as $s) {
        $ins = $pdo->prepare("INSERT INTO secciones (nombre) VALUES (?)");
        $ins->execute([$s]);
    }
}

// 3. Poblar Usuario Administrador (Joseph / Admin)
$adminUser = $pdo->query("SELECT * FROM usuarios WHERE username = 'admin@colegio.com' OR username = 'admin'")->fetch();
if (!$adminUser) {
    $passHash = password_hash('admin123', PASSWORD_BCRYPT);
    $ins = $pdo->prepare("INSERT INTO usuarios (username, password_hash, rol, nombres, apellidos, email, dni, telefono, estado) 
                          VALUES (?, ?, 'admin', 'Joseph', 'Alarcón', 'admin@colegio.com', '70891234', '+51 987 654 321', 'Activo')");
    $ins->execute(['admin@colegio.com', $passHash]);
    $adminId = $pdo->lastInsertId();
} else {
    $adminId = $adminUser['id'];
}

// 4. Poblar Plana Docente (2 Profesores Activos)
$profCount = $pdo->query("SELECT COUNT(*) FROM profesores")->fetchColumn();
if ($profCount == 0) {
    $profesoresSeed = [
        [
            'nombres' => 'Carlos Alberto',
            'apellidos' => 'Mendoza Salazar',
            'dni' => '10293847',
            'genero' => 'Masculino',
            'correo' => 'cmendoza@dylschool.edu.pe',
            'telefono' => '+51 912 345 678',
        ],
        [
            'nombres' => 'María Elena',
            'apellidos' => 'Flores Benítez',
            'dni' => '20495867',
            'genero' => 'Femenino',
            'correo' => 'mflores@dylschool.edu.pe',
            'telefono' => '+51 923 456 789',
        ]
    ];

    foreach ($profesoresSeed as $p) {
        $passHash = password_hash($p['dni'], PASSWORD_BCRYPT);
        $insUser = $pdo->prepare("INSERT INTO usuarios (username, password_hash, rol, nombres, apellidos, email, dni, telefono, estado)
                                  VALUES (?, ?, 'docente', ?, ?, ?, ?, ?, 'Activo')");
        $insUser->execute([$p['dni'], $passHash, $p['nombres'], $p['apellidos'], $p['correo'], $p['dni'], $p['telefono']]);
        $uid = $pdo->lastInsertId();

        $insProf = $pdo->prepare("INSERT INTO profesores (usuario_id, nombres, apellidos, dni, genero, correo, telefono, estado)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVO')");
        $insProf->execute([$uid, $p['nombres'], $p['apellidos'], $p['dni'], $p['genero'], $p['correo'], $p['telefono']]);
    }
}

// 5. Poblar 23 Materias y Asignación de Grados (Malla Curricular)
$cursoCount = $pdo->query("SELECT COUNT(*) FROM cursos")->fetchColumn();
if ($cursoCount == 0) {
    $materiasSeed = [
        ['Álgebra', 'Oficial'],
        ['Aritmética', 'Oficial'],
        ['Geometría', 'Oficial'],
        ['Trigonometría', 'Oficial'],
        ['Razonamiento Matemático', 'Oficial'],
        ['Comunicación', 'Oficial'],
        ['Literatura', 'Oficial'],
        ['Razonamiento Verbal', 'Oficial'],
        ['Inglés', 'Oficial'],
        ['Biología', 'Oficial'],
        ['Química', 'Oficial'],
        ['Física', 'Oficial'],
        ['Historia del Perú', 'Oficial'],
        ['Historia Universal', 'Oficial'],
        ['Geografía', 'Oficial'],
        ['Economía', 'Oficial'],
        ['Computación', 'Oficial'],
        ['Educación Física', 'Oficial'],
        ['Arte y Cultura', 'Oficial'],
        ['Música', 'Oficial'],
        ['Tutoría', 'Oficial'],
        ['Robótica Escolar', 'Taller'],
        ['Diseño Gráfico', 'Taller'],
    ];

    foreach ($materiasSeed as $m) {
        $ins = $pdo->prepare("INSERT INTO cursos (nombre, tipo, activo) VALUES (?, ?, 1)");
        $ins->execute([$m[0], $m[1]]);
        $cid = $pdo->lastInsertId();

        // Asignar a Primaria (grados 1 a 6) y Secundaria (grados 7 a 11)
        // Para alcanzar exactamente 65 grupos en primaria y 115 en secundaria
        for ($gid = 1; $gid <= 6; $gid++) {
            $pdo->prepare("INSERT INTO curso_grados (curso_id, grado_id) VALUES (?, ?)")->execute([$cid, $gid]);
        }
        for ($gid = 7; $gid <= 11; $gid++) {
            $pdo->prepare("INSERT INTO curso_grados (curso_id, grado_id) VALUES (?, ?)")->execute([$cid, $gid]);
        }
    }
}

// 6. Poblar 10 Alumnos Activos
$alumnoCount = $pdo->query("SELECT COUNT(*) FROM alumnos")->fetchColumn();
if ($alumnoCount == 0) {
    $alumnosSeed = [
        ['Joseph', 'Mamani Quispe', '73849501', '2010-04-15', 'Masculino', 'jmamani@escuela.edu.pe', '+51 987 111 222'],
        ['Ariana Sofía', 'Grande Morales', '74859602', '2010-06-20', 'Femenino', 'agrande@escuela.edu.pe', '+51 987 222 333'],
        ['Mateo Alejandro', 'Silva Torres', '75960713', '2010-03-12', 'Masculino', 'msilva@escuela.edu.pe', '+51 987 333 444'],
        ['Luciana Paola', 'Paredes Castillo', '76071824', '2010-08-05', 'Femenino', 'lparedes@escuela.edu.pe', '+51 987 444 555'],
        ['Sebastián David', 'Rojas Navarro', '77182935', '2010-01-28', 'Masculino', 'srojas@escuela.edu.pe', '+51 987 555 666'],
        ['Camila Andrea', 'Vargas Mendoza', '78293046', '2010-11-19', 'Femenino', 'cvargas@escuela.edu.pe', '+51 987 666 777'],
        ['Diego Alonso', 'Guerrero Bravo', '79304157', '2010-05-14', 'Masculino', 'dguerrero@escuela.edu.pe', '+51 987 777 888'],
        ['Valeria Nicole', 'Chávez Romero', '70415268', '2010-09-23', 'Femenino', 'vchavez@escuela.edu.pe', '+51 987 888 999'],
        ['Joaquín Manuel', 'Castro Alva', '71526379', '2011-02-17', 'Masculino', 'jcastro@escuela.edu.pe', '+51 987 999 000'],
        ['Mia Isabella', 'Contreras Ramos', '72637480', '2011-07-30', 'Femenino', 'mcontreras@escuela.edu.pe', '+51 987 000 111'],
    ];

    foreach ($alumnosSeed as $al) {
        $passHash = password_hash($al[2], PASSWORD_BCRYPT);
        $insUser = $pdo->prepare("INSERT INTO usuarios (username, password_hash, rol, nombres, apellidos, email, dni, telefono, estado)
                                  VALUES (?, ?, 'alumno', ?, ?, ?, ?, ?, 'Activo')");
        $insUser->execute([$al[2], $passHash, $al[0], $al[1], $al[5], $al[2], $al[6]]);
        $uid = $pdo->lastInsertId();

        $insAlum = $pdo->prepare("INSERT INTO alumnos (usuario_id, nombres, apellidos, dni, fecha_nacimiento, genero, correo, telefono_apoderado, estado)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVO')");
        $insAlum->execute([$uid, $al[0], $al[1], $al[2], $al[3], $al[4], $al[5], $al[6]]);
    }
}

// 7. Poblar Matrículas 2026 (8 Alumnos matriculados en 1ro Año Secundaria - Sec. A y B)
$matCount = $pdo->query("SELECT COUNT(*) FROM matriculas")->fetchColumn();
if ($matCount == 0) {
    // Grado 7 = 1ro Año Secundaria, Seccion 1 = A, Seccion 2 = B
    $grado1Sec = $pdo->query("SELECT id FROM grados WHERE nombre = '1ro Año' LIMIT 1")->fetchColumn() ?: 7;
    $seccA = $pdo->query("SELECT id FROM secciones WHERE nombre = 'A' LIMIT 1")->fetchColumn() ?: 1;
    $seccB = $pdo->query("SELECT id FROM secciones WHERE nombre = 'B' LIMIT 1")->fetchColumn() ?: 2;

    $alumnos = $pdo->query("SELECT id, nombres, apellidos FROM alumnos ORDER BY id ASC LIMIT 8")->fetchAll();
    
    // Asignar pensiones adelantadas o sin historial
    $estados = [
        ['ADELANTADO', 'Mar 2026', $seccA],
        ['ADELANTADO', 'Abr 2026', $seccA],
        ['ADELANTADO', 'Mar 2026', $seccA],
        ['SIN_HISTORIAL', null, $seccA],
        ['ADELANTADO', 'May 2026', $seccB],
        ['ADELANTADO', 'Mar 2026', $seccB],
        ['SIN_HISTORIAL', null, $seccB],
        ['SIN_HISTORIAL', null, $seccB],
    ];

    foreach ($alumnos as $idx => $a) {
        $cfg = $estados[$idx] ?? ['SIN_HISTORIAL', null, $seccA];
        $ins = $pdo->prepare("INSERT INTO matriculas (alumno_id, grado_id, seccion_id, anio_lectivo, estado_pension, pagado_hasta, fecha_matricula)
                              VALUES (?, ?, ?, 2026, ?, ?, '2026-01-05')");
        $ins->execute([$a['id'], $grado1Sec, $cfg[2], $cfg[0], $cfg[1]]);
        $mid = $pdo->lastInsertId();

        // Crear registro de notas para materias principales
        $cursos = $pdo->query("SELECT id FROM cursos LIMIT 6")->fetchAll();
        foreach ($cursos as $c) {
            $b1 = rand(14, 19);
            $b2 = rand(13, 18);
            $prom = round(($b1 + $b2) / 2, 1);
            $insNota = $pdo->prepare("INSERT INTO notas (matricula_id, curso_id, bimestre_1, bimestre_2, promedio_final) VALUES (?, ?, ?, ?, ?)");
            $insNota->execute([$mid, $c['id'], $b1, $b2, $prom]);
        }
    }
}

// 8. Poblar Asignaciones Docentes y Horarios
$asigCount = $pdo->query("SELECT COUNT(*) FROM asignaciones")->fetchColumn();
if ($asigCount == 0) {
    $prof1 = $pdo->query("SELECT id FROM profesores LIMIT 1 OFFSET 0")->fetchColumn();
    $prof2 = $pdo->query("SELECT id FROM profesores LIMIT 1 OFFSET 1")->fetchColumn() ?: $prof1;
    $grado1Sec = $pdo->query("SELECT id FROM grados WHERE nombre = '1ro Año' LIMIT 1")->fetchColumn() ?: 7;
    $seccA = $pdo->query("SELECT id FROM secciones WHERE nombre = 'A' LIMIT 1")->fetchColumn() ?: 1;

    $cAlgebra = $pdo->query("SELECT id FROM cursos WHERE nombre = 'Álgebra' LIMIT 1")->fetchColumn() ?: 1;
    $cComp = $pdo->query("SELECT id FROM cursos WHERE nombre = 'Computación' LIMIT 1")->fetchColumn() ?: 2;
    $cBio = $pdo->query("SELECT id FROM cursos WHERE nombre = 'Biología' LIMIT 1")->fetchColumn() ?: 3;
    $cArte = $pdo->query("SELECT id FROM cursos WHERE nombre = 'Arte y Cultura' LIMIT 1")->fetchColumn() ?: 4;

    // Asignaciones
    $pdo->prepare("INSERT INTO asignaciones (profesor_id, curso_id, grado_id, seccion_id, anio_lectivo) VALUES (?, ?, ?, ?, 2026)")->execute([$prof1, $cAlgebra, $grado1Sec, $seccA]);
    $pdo->prepare("INSERT INTO asignaciones (profesor_id, curso_id, grado_id, seccion_id, anio_lectivo) VALUES (?, ?, ?, ?, 2026)")->execute([$prof1, $cComp, $grado1Sec, $seccA]);
    $pdo->prepare("INSERT INTO asignaciones (profesor_id, curso_id, grado_id, seccion_id, anio_lectivo) VALUES (?, ?, ?, ?, 2026)")->execute([$prof2, $cBio, $grado1Sec, $seccA]);
    $pdo->prepare("INSERT INTO asignaciones (profesor_id, curso_id, grado_id, seccion_id, anio_lectivo) VALUES (?, ?, ?, ?, 2026)")->execute([$prof2, $cArte, $grado1Sec, $seccA]);

    // Horario Lunes para 1ro Año Sección A con Recreo Amarillo
    $horarioBloques = [
        ['curso_id' => $cAlgebra, 'hora_inicio' => '08:00 AM', 'hora_fin' => '09:30 AM', 'es_recreo' => 0],
        ['curso_id' => $cComp, 'hora_inicio' => '09:30 AM', 'hora_fin' => '11:00 AM', 'es_recreo' => 0],
        ['curso_id' => $cBio, 'hora_inicio' => '11:00 AM', 'hora_fin' => '11:30 AM', 'es_recreo' => 0],
        ['curso_id' => null, 'hora_inicio' => '11:30 AM', 'hora_fin' => '12:00 PM', 'es_recreo' => 1], // RECREO
        ['curso_id' => $cArte, 'hora_inicio' => '12:00 PM', 'hora_fin' => '01:30 PM', 'es_recreo' => 0],
    ];

    foreach (['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'] as $dia) {
        foreach ($horarioBloques as $b) {
            $pdo->prepare("INSERT INTO horarios (curso_id, grado_id, seccion_id, dia, hora_inicio, hora_fin, modalidad, es_recreo) 
                           VALUES (?, ?, ?, ?, ?, ?, 'Presencial', ?)")
                ->execute([$b['curso_id'], $grado1Sec, $seccA, $dia, $b['hora_inicio'], $b['hora_fin'], $b['es_recreo']]);
        }
    }
}

// 9. Poblar Pagos en Caja (S/ 750.00 RECAUDADO HOY, 1 MOVIMIENTO)
$pagosCount = $pdo->query("SELECT COUNT(*) FROM pagos")->fetchColumn();
if ($pagosCount == 0) {
    $mat1 = $pdo->query("SELECT id, alumno_id FROM matriculas ORDER BY id ASC LIMIT 1")->fetch();
    if ($mat1) {
        $insPago = $pdo->prepare("INSERT INTO pagos (numero_recibo, matricula_id, alumno_id, concepto, mes_pension, metodo_pago, monto, es_matricula, estado, fecha_pago, usuario_cajero_id)
                                  VALUES ('REC-260107-105121-658', ?, ?, 'Pensión Marzo + Matrícula 2026', 'Marzo 2026', 'Efectivo', 750.00, 1, 'EMITIDO', '2026-01-09 10:51:21', ?)");
        $insPago->execute([$mat1['id'], $mat1['alumno_id'], $adminId]);
    }
}

// 10. Poblar Comunicados
$comCount = $pdo->query("SELECT COUNT(*) FROM comunicados")->fetchColumn();
if ($comCount == 0) {
    $pdo->prepare("INSERT INTO comunicados (titulo, mensaje, fecha, audiencia) 
                   VALUES ('Bienvenida al Año Escolar 2026', 'Estimada comunidad educativa DYL SCHOOL, les damos la más cordial bienvenida al periodo lectivo 2026.', '2026-01-05', 'Todos')")->execute();
    $pdo->prepare("INSERT INTO comunicados (titulo, mensaje, fecha, audiencia) 
                   VALUES ('Cronograma de Evaluaciones Diagnósticas', 'Se informa a los padres de familia que durante la próxima semana se realizarán las pruebas diagnósticas de entrada.', '2026-01-08', 'Todos')")->execute();
}

// 11. Poblar Asistencia del día para 1ro Año Sec. A
$asistCount = $pdo->query("SELECT COUNT(*) FROM asistencia")->fetchColumn();
if ($asistCount == 0) {
    $mats = $pdo->query("SELECT id FROM matriculas ORDER BY id ASC LIMIT 6")->fetchAll();
    foreach ($mats as $idx => $m) {
        $est = ($idx === 4) ? 'Tarde' : (($idx === 5) ? 'Falta' : 'Presente');
        $pdo->prepare("INSERT INTO asistencia (matricula_id, fecha, estado) VALUES (?, '2026-01-09', ?)")->execute([$m['id'], $est]);
    }
}

echo "Base de datos y datos demo de DYL SCHOOL inicializados con éxito.\n";
