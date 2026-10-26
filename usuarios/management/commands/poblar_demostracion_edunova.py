import os
from datetime import date, time, timedelta, datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from usuarios.models import (
    Rol, PerfilUsuario, ConfiguracionColegio, FamiliaAcudiente,
    Docente, PapeleraReciclaje, PagoPension
)
from instituciones.models import InstitucionEducativa
from academico.models import (
    ProgramaFormacion, Competencia, ResultadoAprendizaje, Ficha, Matricula,
    CargaAcademica, HorarioFicha, TareaClase, EntregaTarea, GuiaClase,
    MaterialClase, AvisoClase, CalificacionEscolar, SemaforoCompetencia,
    DocumentoInstitucional, PeriodoAcademico
)
from seguimiento.models import (
    AsistenciaAprendiz, ComunicadoEscolar, AcuseLecturaCircular,
    Notificacion, RegistroAuditoria, DocumentoAdministrativo, SolicitudSecretaria
)
from evaluaciones.models import JuicioEvaluativo


class Command(BaseCommand):
    help = 'Puebla la base de datos MySQL con la demostración oficial e integral de EduNova (IED Nuevo Horizonte) de forma idempotente.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=" * 70))
        self.stdout.write(self.style.NOTICE("INICIANDO POBLAMIENTO DE DEMOSTRACIÓN — EDUNOVA (IED NUEVO HORIZONTE)"))
        self.stdout.write(self.style.NOTICE("=" * 70))

        with transaction.atomic():
            roles = self._crear_roles()
            colegio, institucion = self._crear_institucion()
            usuarios_demo = self._crear_usuarios_principales(roles, institucion)
            periodos = self._asegurar_periodos()
            programas = self._crear_programas_asignaturas(institucion)
            fichas = self._crear_grados_y_fichas(institucion, programas, usuarios_demo['docente'])
            cargas = self._crear_cargas_academicas(programas, usuarios_demo)
            alumnos_matriculados = self._crear_estudiantes_y_matriculas(roles['Estudiante'], fichas, usuarios_demo)
            self._vincular_familias(usuarios_demo, alumnos_matriculados)
            self._crear_horarios_escolares(fichas, programas, usuarios_demo)
            tareas_dict = self._crear_recursos_academicos_y_tareas(cargas, usuarios_demo)
            self._crear_entregas_y_calificaciones(tareas_dict, cargas, usuarios_demo, periodos)
            self._crear_asistencias(fichas, usuarios_demo)
            self._crear_comunicaciones_y_circulares(usuarios_demo, fichas)
            self._crear_documentos_y_notificaciones(usuarios_demo, institucion)
            self._crear_auditoria_y_papelera(usuarios_demo)

        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("¡POBLAMIENTO DE DEMOSTRACIÓN COMPLETADO EXITOSAMENTE!"))
        self.stdout.write(self.style.SUCCESS("Los 6 paneles de EduNova cuentan con datos reales interconectados."))
        self.stdout.write(self.style.SUCCESS("=" * 70))

    def _crear_roles(self):
        roles_data = [
            ("Administrador", "Control maestro de usuarios, seguridad y auditoría"),
            ("Rectoría", "Dirección institucional, supervisión académica y reportes"),
            ("Secretaría", "Gestión de matrículas, admisiones y expedientes escolares"),
            ("Docente", "Gestión de aula, actividades, tareas, calificaciones y asistencia"),
            ("Familia", "Seguimiento académico y disciplinario de hijos a cargo"),
            ("Estudiante", "Acceso a aula virtual, tareas, calificaciones y horarios"),
        ]
        roles = {}
        for nombre, desc in roles_data:
            rol, _ = Rol.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
            roles[nombre] = rol
        return roles

    def _crear_institucion(self):
        colegio = ConfiguracionColegio.get_solo()
        colegio.nombre = 'Institución Educativa Distrital Nuevo Horizonte'
        colegio.lema = 'Ciencia, Innovación y Liderazgo para el Futuro'
        colegio.codigo_dane = '147001000234'
        colegio.nit = '900.456.789-1'
        colegio.direccion = 'Carrera 12 # 18-40, Santa Marta'
        colegio.telefono = '+57 605 421 9988'
        colegio.email = 'contacto@nuevahorizonte.edu.co'
        colegio.save()

        institucion, _ = InstitucionEducativa.objects.get_or_create(
            codigo_dane='147001000234',
            defaults={
                'nombre': 'I.E.D. Nuevo Horizonte',
                'municipio': 'Santa Marta',
                'direccion': 'Carrera 12 # 18-40',
                'telefono': '+57 605 421 9988',
                'rector_nombre': 'Dra. María Fernanda Gómez',
                'enlace_nombre': 'Prof. Carlos Mendoza',
                'enlace_telefono': '3005550100',
                'activa': True,
            }
        )
        return colegio, institucion

    def _crear_usuarios_principales(self, roles, institucion):
        usuarios_data = [
            ('admin', 'Administrador', 'General', 'admin@nuevahorizonte.edu.co', '1082000001', roles['Administrador'], True),
            ('rector', 'María Fernanda', 'Gómez', 'rectoria@nuevahorizonte.edu.co', '1082000002', roles['Rectoría'], False),
            ('secretaria', 'Rosario', 'Torres', 'secretaria@nuevahorizonte.edu.co', '1082000003', roles['Secretaría'], False),
            ('docente', 'Carlos', 'Mendoza Pérez', 'cmendoza@nuevahorizonte.edu.co', '1002000002', roles['Docente'], False),
            ('docente_laura', 'Laura', 'Martínez Rojas', 'lmartinez@nuevahorizonte.edu.co', '1002000001', roles['Docente'], False),
            ('docente_patricia', 'Patricia', 'Vargas Cotes', 'pvargas@nuevahorizonte.edu.co', '1002000004', roles['Docente'], False),
            ('docente_andres', 'Andrés', 'Torres Díaz', 'atorres@nuevahorizonte.edu.co', '1002000005', roles['Docente'], False),
            ('docente_diana', 'Diana', 'Herrera López', 'dherrera@nuevahorizonte.edu.co', '1002000006', roles['Docente'], False),
            ('docente_felipe', 'Felipe', 'Gómez Ruiz', 'fgomez@nuevahorizonte.edu.co', '1002000007', roles['Docente'], False),
            ('familia', 'Patricia', 'Gómez Castro', 'familia@nuevahorizonte.edu.co', '32889001', roles['Familia'], False),
            ('est1', 'Sebastián', 'Gómez Martínez', 'sgomez@nuevahorizonte.edu.co', '1001001001', roles['Estudiante'], False),
            ('estudiante', 'Sofía', 'Gómez Martínez', 'sofiag@nuevahorizonte.edu.co', '1002002002', roles['Estudiante'], False),
            ('est_nuevo', 'Mateo', 'Castro Ríos', 'mcastro@nuevahorizonte.edu.co', '1003003003', roles['Estudiante'], False),
        ]

        usuarios = {}
        for username, first, last, email, doc, rol, is_super in usuarios_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': email,
                    'is_staff': is_super or rol.nombre in ['Administrador', 'Rectoría', 'Secretaría'],
                    'is_superuser': is_super,
                    'is_active': True,
                }
            )
            # Asegurar contraseña demo estándar: '12345'
            user.set_password('12345')
            user.first_name = first
            user.last_name = last
            user.email = email
            user.is_active = True
            user.save()

            perfil = user.perfil
            perfil.rol = rol
            perfil.numero_documento = doc
            perfil.tipo_documento = 'TI' if rol.nombre == 'Estudiante' else 'CC'
            perfil.telefono = '3005550100'
            perfil.esta_activo = True
            perfil.save()

            usuarios[username] = user

            # Si es docente, vincular con perfil profesional Docente
            if 'Docente' in rol.nombre:
                Docente.objects.get_or_create(
                    usuario=user,
                    defaults={
                        'area': 'Humanidades y Lengua' if username == 'docente' else ('Matemáticas' if username == 'docente_laura' else 'Ciencias'),
                        'escalafon': 'Grado 14 - Decreto 1278',
                        'estado_docente': 'ACTIVO',
                        'profesion': 'Licenciado en Educación',
                        'fecha_ingreso': date(2020, 1, 15),
                        'nro_resolucion': f'RES-2020-{doc[-4:]}',
                    }
                )

        return usuarios

    def _asegurar_periodos(self):
        periodos = []
        datos_p = [
            (1, 'Período 1', date(2026, 1, 15), date(2026, 3, 27), True, Decimal('25.00')),
            (2, 'Período 2', date(2026, 4, 6), date(2026, 6, 12), False, Decimal('25.00')),
            (3, 'Período 3', date(2026, 7, 6), date(2026, 9, 11), False, Decimal('25.00')),
            (4, 'Período 4', date(2026, 9, 14), date(2026, 11, 27), False, Decimal('25.00')),
        ]
        for num, nom, f_ini, f_fin, cerrado, porc in datos_p:
            p, _ = PeriodoAcademico.objects.get_or_create(
                anio_lectivo='2026',
                numero=num,
                defaults={
                    'nombre': nom,
                    'fecha_inicio': f_ini,
                    'fecha_fin': f_fin,
                    'cerrado': cerrado,
                    'porcentaje': porc,
                }
            )
            periodos.append(p)
        return periodos

    def _crear_programas_asignaturas(self, institucion):
        asignaturas = [
            ('COL-LEN-01', 'Lengua Castellana y Literatura', 'Humanidades y Comunicación'),
            ('COL-MAT-01', 'Matemáticas y Geometría', 'Pensamiento Lógico y Matemático'),
            ('COL-CIE-01', 'Ciencias Naturales y Química', 'Investigación Científica'),
            ('COL-SOC-01', 'Ciencias Sociales e Historia', 'Ciencias Sociales y Ciudadanía'),
            ('COL-ING-01', 'Inglés y Lengua Extranjera', 'Bilingüismo y Competencias Globales'),
            ('COL-TEC-01', 'Tecnología e Informática', 'Tecnología y Desarrollo Digital'),
            ('COL-EFI-01', 'Educación Física y Deportes', 'Bienestar y Cultura Física'),
            ('COL-ART-01', 'Educación Artística y Cultural', 'Expresión Creativa y Arte'),
            ('COL-ETI-01', 'Ética y Valores Ciudadanos', 'Formación Ética y Cátedra de Paz'),
        ]
        programas = {}
        for codigo, nombre, desc in asignaturas:
            prog, _ = ProgramaFormacion.objects.get_or_create(
                codigo_programa=codigo,
                defaults={
                    'denominacion': nombre,
                    'version': '1.0',
                    'tipo_programa': 'Colegio',
                    'duracion_meses': 10,
                    'duracion_horas': 160,
                    'institucion': institucion,
                    'observaciones': desc,
                    'fecha_inicio': date(2026, 1, 15),
                    'fecha_fin': date(2026, 11, 30),
                    'activo': True,
                }
            )
            comp, _ = Competencia.objects.get_or_create(
                programa=prog,
                codigo=f'COMP-{codigo[-6:]}',
                defaults={'descripcion': f'Competencias fundamentales en {nombre}.'}
            )
            ResultadoAprendizaje.objects.get_or_create(
                competencia=comp,
                codigo=f'RAP-{codigo[-6:]}',
                defaults={'descripcion': f'Evidencia dominio en los estándares básicos de {nombre}.'}
            )
            programas[codigo] = prog
        return programas

    def _crear_grados_y_fichas(self, institucion, programas, lider_docente):
        prog_base = programas['COL-LEN-01']
        fichas = {}
        # Crear grupos del grado 1° al 11°
        for grado in range(1, 12):
            g_str = f"{grado}"
            codigo_ficha = f"COL-2026-G{grado:02d}-A"
            f, _ = Ficha.objects.get_or_create(
                codigo_ficha=codigo_ficha,
                defaults={
                    'programa': prog_base,
                    'institucion': institucion,
                    'instructor_lider': lider_docente,
                    'fecha_inicio': date(2026, 1, 15),
                    'fecha_fin': date(2026, 11, 30),
                    'estado': 'En Ejecucion',
                }
            )
            fichas[g_str] = f

        # Grupo adicional 10°-B y 11°-B
        for g_extra in [10, 11]:
            f_b, _ = Ficha.objects.get_or_create(
                codigo_ficha=f"COL-2026-G{g_extra:02d}-B",
                defaults={
                    'programa': prog_base,
                    'institucion': institucion,
                    'instructor_lider': lider_docente,
                    'fecha_inicio': date(2026, 1, 15),
                    'fecha_fin': date(2026, 11, 30),
                    'estado': 'En Ejecucion',
                }
            )
            fichas[f"{g_extra}-B"] = f_b

        return fichas

    def _crear_cargas_academicas(self, programas, usuarios):
        # Asignaciones para Carlos Mendoza (Docente principal)
        cargas = {}
        asignaciones = [
            (usuarios['docente'], programas['COL-LEN-01'], 'Secundaria', '10°', 'A', '10-A-LEN'),
            (usuarios['docente'], programas['COL-LEN-01'], 'Media', '11°', 'A', '11-A-LEN'),
            (usuarios['docente_laura'], programas['COL-MAT-01'], 'Secundaria', '10°', 'A', '10-A-MAT'),
            (usuarios['docente_laura'], programas['COL-MAT-01'], 'Media', '11°', 'A', '11-A-MAT'),
            (usuarios['docente_patricia'], programas['COL-CIE-01'], 'Secundaria', '10°', 'A', '10-A-CIE'),
            (usuarios['docente_andres'], programas['COL-SOC-01'], 'Secundaria', '10°', 'A', '10-A-SOC'),
            (usuarios['docente_diana'], programas['COL-ING-01'], 'Secundaria', '10°', 'A', '10-A-ING'),
            (usuarios['docente_felipe'], programas['COL-TEC-01'], 'Secundaria', '10°', 'A', '10-A-TEC'),
        ]
        for profe, prog, nivel, grado, secc, clave in asignaciones:
            c, _ = CargaAcademica.objects.get_or_create(
                profesor=profe,
                programa=prog,
                grado=grado,
                seccion=secc,
                anio_lectivo=2026,
                defaults={'nivel': nivel}
            )
            cargas[clave] = c
        return cargas

    def _crear_estudiantes_y_matriculas(self, rol_estudiante, fichas, usuarios):
        alumnos = []

        # 1. Estudiantes fijos de demostración
        # Sebastián Gómez (est1) en Grado 10°-A
        m_est1, _ = Matricula.objects.get_or_create(
            aprendiz=usuarios['est1'],
            defaults={
                'ficha': fichas['10'],
                'grado_escolar': '10',
                'seccion': 'A',
                'estado_formacion': 'En Formacion',
                'acudiente_nombre': 'Patricia Gómez Castro',
                'acudiente_telefono': '3015551234',
                'fecha_matricula': date(2026, 1, 15),
            }
        )
        alumnos.append(usuarios['est1'])

        # Sofía Gómez (estudiante) en Grado 11°-A
        m_est2, _ = Matricula.objects.get_or_create(
            aprendiz=usuarios['estudiante'],
            defaults={
                'ficha': fichas['11'],
                'grado_escolar': '11',
                'seccion': 'A',
                'estado_formacion': 'En Formacion',
                'acudiente_nombre': 'Patricia Gómez Castro',
                'acudiente_telefono': '3015551234',
                'fecha_matricula': date(2026, 1, 15),
            }
        )
        alumnos.append(usuarios['estudiante'])

        # Mateo Castro (est_nuevo) en Grado 6°-A (demuestra estado limpio/sin calificaciones)
        m_nuevo, _ = Matricula.objects.get_or_create(
            aprendiz=usuarios['est_nuevo'],
            defaults={
                'ficha': fichas['6'],
                'grado_escolar': '6',
                'seccion': 'A',
                'estado_formacion': 'En Formacion',
                'acudiente_nombre': 'Luis Castro Méndez',
                'acudiente_telefono': '3009998877',
                'fecha_matricula': date(2026, 2, 1),
            }
        )
        alumnos.append(usuarios['est_nuevo'])

        # 2. Estudiantes compañeros para Grado 10°-A y 11°-A
        companeros_10 = [
            ('alumno_10_02', 'Valeria', 'Hernández Silva', '1103001002'),
            ('alumno_10_03', 'Juan Camilo', 'Pérez López', '1103001003'),
            ('alumno_10_04', 'Mariana', 'Castro Ruiz', '1103001004'),
        ]
        for username, first, last, doc in companeros_10:
            u, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': f'{username}@nuevahorizonte.edu.co',
                    'is_active': True,
                }
            )
            u.set_password('12345')
            u.save()
            p = u.perfil
            p.rol = rol_estudiante
            p.numero_documento = doc
            p.tipo_documento = 'TI'
            p.telefono = '3005550000'
            p.save()
            Matricula.objects.get_or_create(
                aprendiz=u,
                defaults={
                    'ficha': fichas['10'],
                    'grado_escolar': '10',
                    'seccion': 'A',
                    'estado_formacion': 'En Formacion',
                    'acudiente_nombre': f'Acudiente de {first}',
                    'acudiente_telefono': '3015550000',
                    'fecha_matricula': date(2026, 1, 15),
                }
            )
            alumnos.append(u)

        # 3. Alumnos para poblar cada grado escolar del 1° al 9°
        nombres_grados = [
            (1, 'Lucas', 'Navarro Gil', '1103000101'),
            (2, 'Sara', 'Mejía Torres', '1103000201'),
            (3, 'Martín', 'Fuentes Castro', '1103000301'),
            (4, 'Emma', 'Peña Silva', '1103000401'),
            (5, 'Alejandro', 'Bermúdez Rojas', '1103000501'),
            (7, 'Antonella', 'Mora Gómez', '1103000701'),
            (8, 'Santiago', 'León Vargas', '1103000801'),
            (9, 'Juliana', 'Ospina Díaz', '1103000901'),
        ]
        for g_num, first, last, doc in nombres_grados:
            username = f'alumno_g{g_num:02d}'
            u, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': f'{username}@nuevahorizonte.edu.co',
                    'is_active': True,
                }
            )
            u.set_password('12345')
            u.save()
            p = u.perfil
            p.rol = rol_estudiante
            p.numero_documento = doc
            p.tipo_documento = 'TI'
            p.save()
            Matricula.objects.get_or_create(
                aprendiz=u,
                defaults={
                    'ficha': fichas[str(g_num)],
                    'grado_escolar': str(g_num),
                    'seccion': 'A',
                    'estado_formacion': 'En Formacion',
                    'acudiente_nombre': f'Acudiente de {first}',
                    'acudiente_telefono': '3005550000',
                    'fecha_matricula': date(2026, 1, 15),
                }
            )
            alumnos.append(u)

        return alumnos

    def _vincular_familias(self, usuarios, alumnos):
        # Núcleo familiar oficial de demostración: Patricia Gómez Castro
        fam_rec, _ = FamiliaAcudiente.objects.get_or_create(
            documento='32889001',
            defaults={
                'nombre_acudiente': 'Patricia Gómez Castro',
                'parentesco': 'Madre',
                'telefono': '3015551234',
                'email': 'familia@nuevahorizonte.edu.co',
                'direccion': 'Carrera 14 # 22-50, Santa Marta',
                'ocupacion': 'Contadora Pública',
            }
        )
        # Vincular a Sebastián Gómez (est1) y Sofía Gómez (estudiante)
        fam_rec.estudiantes.add(usuarios['est1'], usuarios['estudiante'])

    def _crear_horarios_escolares(self, fichas, programas, usuarios):
        # Horario semanal completo para Grado 10°-A
        f_10 = fichas['10']
        bloques = [
            # Lunes (Dia 1)
            ('1', time(7, 0), time(8, 30), usuarios['docente_laura'], programas['COL-MAT-01'], 'Aula 101', 'Matemáticas y Geometría'),
            ('1', time(8, 30), time(10, 0), usuarios['docente'], programas['COL-LEN-01'], 'Aula 101', 'Lengua Castellana y Literatura'),
            ('1', time(10, 30), time(12, 0), usuarios['docente_patricia'], programas['COL-CIE-01'], 'Laboratorio 1', 'Ciencias Naturales y Química'),
            # Martes (Dia 2)
            ('2', time(7, 0), time(8, 30), usuarios['docente_diana'], programas['COL-ING-01'], 'Aula 101', 'Inglés y Lengua Extranjera'),
            ('2', time(8, 30), time(10, 0), usuarios['docente_felipe'], programas['COL-TEC-01'], 'Sala de Sistemas', 'Tecnología e Informática'),
            ('2', time(10, 30), time(12, 0), usuarios['docente_andres'], programas['COL-SOC-01'], 'Aula 101', 'Ciencias Sociales e Historia'),
            # Miércoles (Dia 3)
            ('3', time(7, 0), time(8, 30), usuarios['docente'], programas['COL-LEN-01'], 'Aula 101', 'Lengua Castellana y Literatura'),
            ('3', time(8, 30), time(10, 0), usuarios['docente_laura'], programas['COL-MAT-01'], 'Aula 101', 'Matemáticas y Geometría'),
            ('3', time(10, 30), time(12, 0), usuarios['docente_patricia'], programas['COL-CIE-01'], 'Laboratorio 1', 'Ciencias Naturales y Química'),
            # Jueves (Dia 4)
            ('4', time(7, 0), time(8, 30), usuarios['docente_felipe'], programas['COL-TEC-01'], 'Sala de Sistemas', 'Tecnología e Informática'),
            ('4', time(8, 30), time(10, 0), usuarios['docente_diana'], programas['COL-ING-01'], 'Aula 101', 'Inglés y Lengua Extranjera'),
            ('4', time(10, 30), time(12, 0), usuarios['docente_andres'], programas['COL-SOC-01'], 'Aula 101', 'Ciencias Sociales e Historia'),
            # Viernes (Dia 5)
            ('5', time(7, 0), time(8, 30), usuarios['docente'], programas['COL-LEN-01'], 'Aula 101', 'Lengua Castellana y Literatura'),
            ('5', time(8, 30), time(10, 0), usuarios['docente_laura'], programas['COL-MAT-01'], 'Aula 101', 'Matemáticas y Geometría'),
        ]
        for dia, h_ini, h_fin, profe, prog, amb, tema in bloques:
            HorarioFicha.objects.get_or_create(
                ficha=f_10,
                dia=dia,
                hora_inicio=h_ini,
                defaults={
                    'hora_fin': h_fin,
                    'instructor': profe,
                    'programa': prog,
                    'ambiente': amb,
                    'tema': tema,
                    'grado': '10°',
                    'seccion': 'A',
                    'nivel': 'Secundaria',
                    'activo': True,
                }
            )

    def _crear_recursos_academicos_y_tareas(self, cargas, usuarios):
        c_len = cargas['10-A-LEN']
        c_mat = cargas['10-A-MAT']

        # 1. Guías de Clase
        GuiaClase.objects.get_or_create(
            carga_academica=c_len,
            titulo='Guía 01: El Siglo de Oro Español y la Novela Picaresca',
            defaults={
                'profesor': usuarios['docente'],
                'instrucciones': 'Leer los capítulos I y II del Lazarillo de Tormes y responder el cuestionario de análisis narrativo.',
                'tipo_documento': 'GUIA',
                'estado': 'ACTIVO',
            }
        )
        GuiaClase.objects.get_or_create(
            carga_academica=c_mat,
            titulo='Guía 01: Razones Trigonométricas y el Teorema de Pitágoras',
            defaults={
                'profesor': usuarios['docente_laura'],
                'instrucciones': 'Desarrollar los 10 ejercicios prácticos del taller de triángulos rectángulos.',
                'tipo_documento': 'GUIA',
                'estado': 'ACTIVO',
            }
        )

        # 2. Materiales y Avisos
        MaterialClase.objects.get_or_create(
            carga_academica=c_len,
            titulo='Lectura Digital: Contexto Histórico del Renacimiento',
            defaults={
                'descripcion': 'Material de lectura obligatoria para la sustentación del ensayo argumentativo.',
                'enlace': 'https://biblioteca.nuevahorizonte.edu.co/recursos/renacimiento.pdf',
            }
        )
        AvisoClase.objects.get_or_create(
            carga_academica=c_len,
            titulo='Recordatorio: Entrega de Borrador de Ensayo',
            defaults={
                'mensaje': 'Estimados estudiantes, recuerden que este viernes vence el plazo para cargar el borrador de su ensayo.',
            }
        )

        # 3. Tareas
        # Tarea 1: Calificada (para Sebastián Gómez - est1)
        t1, _ = TareaClase.objects.get_or_create(
            carga_academica=c_len,
            titulo='Ensayo Argumentativo: Análisis del Humanismo en el Renacimiento',
            defaults={
                'instrucciones': 'Escribir un ensayo crítico de 600 a 800 palabras analizando la visión humanista y su contraste con la Edad Media.',
                'puntaje_maximo': Decimal('5.0'),
                'estado': 'Publicada',
                'es_calificada': True,
                'fecha_publicacion': timezone.now() - timedelta(days=7),
                'fecha_limite': timezone.now() + timedelta(days=7),
                'periodo': 'Periodo 1',
            }
        )

        # Tarea 2: Pendiente para est1 en Matemáticas
        t2, _ = TareaClase.objects.get_or_create(
            carga_academica=c_mat,
            titulo='Taller Práctico: Aplicación de Funciones Trigonométricas',
            defaults={
                'instrucciones': 'Resolver los problemas de aplicación de ángulos de elevación y depresión en la vida real.',
                'puntaje_maximo': Decimal('5.0'),
                'estado': 'Publicada',
                'es_calificada': True,
                'fecha_publicacion': timezone.now() - timedelta(days=2),
                'fecha_limite': timezone.now() + timedelta(days=4),
                'periodo': 'Periodo 1',
            }
        )

        # Tarea 3: Para calificar en vivo en sustentación (Lengua Castellana)
        t3, _ = TareaClase.objects.get_or_create(
            carga_academica=c_len,
            titulo='Taller de Comprensión Lectora: Figuras Retóricas en la Poesía Barroca',
            defaults={
                'instrucciones': 'Identificar metáforas, hipérboles y antítesis en los sonetos seleccionados de Góngora y Quevedo.',
                'puntaje_maximo': Decimal('5.0'),
                'estado': 'Publicada',
                'es_calificada': True,
                'fecha_publicacion': timezone.now() - timedelta(days=3),
                'fecha_limite': timezone.now() + timedelta(days=5),
                'periodo': 'Periodo 1',
            }
        )

        return {'t1': t1, 't2': t2, 't3': t3}

    def _crear_entregas_y_calificaciones(self, tareas_dict, cargas, usuarios, periodos):
        t1 = tareas_dict['t1']
        t3 = tareas_dict['t3']
        u_est1 = usuarios['est1']
        u_valeria = User.objects.filter(username='alumno_10_02').first()

        # 1. Entrega ya Calificada para Sebastián Gómez (est1)
        EntregaTarea.objects.get_or_create(
            tarea=t1,
            estudiante=u_est1,
            defaults={
                'respuesta': 'Profesor Carlos, adjunto mi ensayo completo con las citas del Renacimiento y su análisis estructurado.',
                'calificacion': Decimal('4.8'),
                'retroalimentacion': 'Excelente desarrollo argumentativo, coherencia impecable y conclusiones muy reflexivas. ¡Felicitaciones!',
                'estado': 'CALIFICADA',
                'fecha_entrega': timezone.now() - timedelta(days=2),
            }
        )

        # 2. Entrega enviada por Valeria Hernández (pendiente por calificar en Docente)
        if u_valeria:
            EntregaTarea.objects.get_or_create(
                tarea=t1,
                estudiante=u_valeria,
                defaults={
                    'respuesta': 'Profesor, envío mi entrega sobre el humanismo para su revisión y comentarios.',
                    'estado': 'ENTREGADA',
                    'fecha_entrega': timezone.now() - timedelta(hours=5),
                }
            )

        # 3. Calificaciones Oficiales en CalificacionEscolar para los 4 períodos
        mat_est1 = Matricula.objects.filter(aprendiz=u_est1).first()
        if mat_est1:
            asignaturas_notas = [
                ('10-A-LEN', usuarios['docente'], Decimal('4.8'), 'Superior', 'Sobresaliente desempeño en expresión escrita y análisis literario.'),
                ('10-A-MAT', usuarios['docente_laura'], Decimal('4.3'), 'Alto', 'Buen dominio de razonamiento lógico y aplicaciones geométricas.'),
                ('10-A-CIE', usuarios['docente_patricia'], Decimal('4.6'), 'Superior', 'Participación ejemplar y rigor en informes de laboratorio.'),
                ('10-A-SOC', usuarios['docente_andres'], Decimal('4.0'), 'Alto', 'Cumplimiento responsable y juicio crítico en debates.'),
                ('10-A-ING', usuarios['docente_diana'], Decimal('4.7'), 'Superior', 'Excelente fluidez verbal y dominio gramatical.'),
                ('10-A-TEC', usuarios['docente_felipe'], Decimal('5.0'), 'Superior', 'Liderazgo destacado en proyectos de innovación tecnológica.'),
            ]
            for clave_carga, profe, nota_val, desemp, obs in asignaturas_notas:
                if clave_carga in cargas:
                    CalificacionEscolar.objects.get_or_create(
                        matricula=mat_est1,
                        carga_academica=cargas[clave_carga],
                        periodo='Periodo 1',
                        defaults={
                            'profesor': profe,
                            'nota': nota_val,
                            'desempeno': desemp,
                            'observaciones': obs,
                            'fecha_registro': timezone.now() - timedelta(days=10),
                        }
                    )

            # Semáforo de competencias para Rectoría y Estudiante
            comp_len = cargas['10-A-LEN'].programa.competencias.first()
            rap_len = comp_len.resultados.first() if comp_len else None
            if comp_len and rap_len:
                SemaforoCompetencia.objects.get_or_create(
                    matricula=mat_est1,
                    competencia=comp_len,
                    resultado_aprendizaje=rap_len,
                    defaults={
                        'profesor': usuarios['docente'],
                        'estado': 'APROBADO',
                        'observaciones': 'Cumple satisfactoriamente con los criterios de evaluación.',
                    }
                )
                JuicioEvaluativo.objects.get_or_create(
                    matricula=mat_est1,
                    resultado_aprendizaje=rap_len,
                    defaults={
                        'instructor': usuarios['docente'],
                        'juicio_valor': 'A',
                        'observaciones': 'Aprobado con distinción académica.',
                        'fecha_evaluacion': date.today() - timedelta(days=10),
                    }
                )

    def _crear_asistencias(self, fichas, usuarios):
        mat_est1 = Matricula.objects.filter(aprendiz=usuarios['est1']).first()
        hoy = timezone.localdate()
        docente = usuarios['docente']

        if mat_est1:
            # Asistencia de hoy: Presente
            AsistenciaAprendiz.objects.get_or_create(
                matricula=mat_est1,
                fecha=hoy,
                defaults={
                    'estado': 'P',
                    'registrado_por': docente,
                    'observaciones': 'Asistencia puntual en clase matutina.',
                }
            )
            # Historial de 5 días atrás
            dias_atras = [(1, 'P'), (2, 'P'), (3, 'J'), (4, 'P'), (5, 'P')]
            for d, est in dias_atras:
                AsistenciaAprendiz.objects.get_or_create(
                    matricula=mat_est1,
                    fecha=hoy - timedelta(days=d),
                    defaults={
                        'estado': est,
                        'registrado_por': docente,
                        'observaciones': 'Registro histórico de control escolar.',
                    }
                )

        # Asistencia para otros compañeros en el día de hoy
        otros = Matricula.objects.filter(ficha=fichas['10']).exclude(aprendiz=usuarios['est1'])
        estados = ['P', 'A', 'T', 'P']
        for idx, m in enumerate(otros):
            AsistenciaAprendiz.objects.get_or_create(
                matricula=m,
                fecha=hoy,
                defaults={
                    'estado': estados[idx % len(estados)],
                    'registrado_por': docente,
                    'observaciones': 'Pase de lista diario oficial.',
                }
            )

    def _crear_comunicaciones_y_circulares(self, usuarios, fichas):
        # Circular 01: Urgente / Institucional General
        c1, _ = ComunicadoEscolar.objects.get_or_create(
            asunto='Circular 001-2026: Inicio del Segundo Período y Entrega de Informes',
            defaults={
                'remitente': usuarios['rector'],
                'estamento_destinatario': 'Todos',
                'mensaje': (
                    'Estimada comunidad de la I.E.D. Nuevo Horizonte: '
                    'Se informa que el próximo viernes 17 de abril se llevará a cabo la entrega oficial '
                    'de boletines correspondientes al Primer Período Académico. Agradecemos puntual asistencia.'
                ),
                'urgente': True,
                'fecha_creacion': timezone.now() - timedelta(days=3),
            }
        )

        # Circular 02: Dirigida a Familias
        c2, _ = ComunicadoEscolar.objects.get_or_create(
            asunto='Circular 002-2026: Convocatoria a Escuela de Padres y Convivencia',
            defaults={
                'remitente': usuarios['secretaria'],
                'estamento_destinatario': 'Familias',
                'mensaje': (
                    'Cordial invitación a todos los padres de familia y acudientes al taller formativo '
                    'de convivencia escolar y apoyo al aprendizaje en el hogar. Lugar: Auditorio Principal.'
                ),
                'urgente': False,
                'fecha_creacion': timezone.now() - timedelta(days=2),
            }
        )

        # Circular 03: Para Docentes
        c3, _ = ComunicadoEscolar.objects.get_or_create(
            asunto='Circular 003-2026: Cronograma de Consolidación de Calificaciones',
            defaults={
                'remitente': usuarios['rector'],
                'estamento_destinatario': 'Docentes',
                'mensaje': (
                    'Señores docentes: Les recordamos que la plataforma permanecerá habilitada para el registro '
                    'de evaluaciones del Primer Período hasta el próximo viernes a las 18:00 horas.'
                ),
                'urgente': False,
                'fecha_creacion': timezone.now() - timedelta(days=1),
            }
        )

        # Acuse de lectura real: Patricia Gómez (familia) ya leyó la Circular 01
        AcuseLecturaCircular.objects.get_or_create(
            comunicado=c1,
            usuario=usuarios['familia'],
            defaults={'fecha_lectura': timezone.now() - timedelta(days=1)}
        )

    def _crear_documentos_y_notificaciones(self, usuarios, institucion):
        # 1. Documentos Institucionales
        docs = [
            ('Manual de Convivencia Escolar 2026', 'Manual de Convivencia', 'Reglamento interno, deberes y derechos de la comunidad educativa.'),
            ('Proyecto Educativo Institucional (PEI)', 'PEI', 'Fundamentos pedagógicos, misión y visión de la I.E.D. Nuevo Horizonte.'),
            ('Calendario Escolar Oficial 2026', 'Calendario', 'Fechas clave de períodos lectivos, recesos y jornadas pedagógicas.'),
        ]
        for tit, cat, desc in docs:
            DocumentoInstitucional.objects.get_or_create(
                titulo=tit,
                defaults={
                    'categoria': cat,
                    'descripcion': desc,
                    'version': '2026.1',
                    'subido_por': usuarios['admin'],
                    'roles_permitidos': 'Administrador, Rectoría, Secretaría, Docente, Familia, Estudiante, Todos',
                }
            )

        # 2. Notificaciones para cada rol
        notificaciones_data = [
            (usuarios['admin'], 'Auditoría del Sistema', 'Se registraron accesos administrativos exitosos en la base de datos.', 'info'),
            (usuarios['rector'], 'Reporte Institucional Listo', 'El consolidado de matrículas y rendimiento académico está actualizado.', 'success'),
            (usuarios['secretaria'], 'Nueva Matrícula Registrada', 'El estudiante Sebastián Gómez Martínez fue asignado al Grado 10°-A.', 'info'),
            (usuarios['docente'], 'Nueva Entrega Recibida', 'Valeria Hernández ha entregado el Taller de Humanismo en Lengua Castellana.', 'warning'),
            (usuarios['familia'], 'Circular 001 Publicada', 'Rectoría publicó la Circular de entrega de informes académicos.', 'info'),
            (usuarios['est1'], 'Calificación Registrada', 'El profesor Carlos Mendoza calificó tu ensayo argumentativo con 4.8.', 'success'),
        ]
        for usr, tit, msg, tipo in notificaciones_data:
            Notificacion.objects.get_or_create(
                usuario=usr,
                titulo=tit,
                defaults={
                    'mensaje': msg,
                    'tipo': tipo,
                    'leida': False,
                    'enlace': '',
                }
            )

    def _crear_auditoria_y_papelera(self, usuarios):
        # Registro de Auditoría Real
        RegistroAuditoria.objects.get_or_create(
            usuario=usuarios['admin'],
            accion='INICIALIZACION_SISTEMA',
            modulo='SISTEMA',
            defaults={
                'detalles': 'Carga y verificación de datos demostrativos oficiales de EduNova (IED Nuevo Horizonte).',
                'ip_address': '127.0.0.1',
            }
        )
        # Elemento demostrativo en Papelera de Reciclaje
        PapeleraReciclaje.objects.get_or_create(
            tipo_objeto='DocumentoAdministrativo',
            objeto_id=999,
            defaults={
                'titulo': 'Borrador Circular Festivos 2025 (Histórico)',
                'subtitulo': 'Documento escolar del año lectivo anterior',
                'modulo_origen': 'Comunicaciones',
                'datos_recuperacion': {'asunto': 'Borrador 2025', 'tipo': 'Circular'},
                'eliminado_por': usuarios['admin'],
                'motivo': 'Depuración anual de borradores no publicados.',
                'restaurado': False,
            }
        )
