from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from usuarios.models import Rol, PerfilUsuario
from instituciones.models import InstitucionEducativa
from academico.models import ProgramaFormacion, Competencia, ResultadoAprendizaje, Ficha, Matricula
from seguimiento.models import BitacoraSeguimiento
from evaluaciones.models import JuicioEvaluativo


class Command(BaseCommand):
    help = 'Carga datos demostrativos oficiales de la Media Técnica en el Magdalena para SINETEC'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Iniciando carga de datos demostrativos para SINETEC..."))

        # 1. Crear Roles Institucionales
        roles = [
            ("Administrador", "Control total de seguridad, usuarios y auditoría"),
            ("Coordinador", "Líder de articulación con la Media Técnica"),
            ("Instructor SENA", "Instructor asignado a visitas y evaluaciones"),
            ("Docente I.E.", "Docente enlace del colegio articulado"),
            ("Estudiante", "Aprendiz de grado 10° u 11° en formación técnica"),
        ]
        roles_dict = {}
        for nombre, desc in roles:
            rol, _ = Rol.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
            roles_dict[nombre] = rol

        # 2. Crear Superusuario Administrador si no existe
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                'email': 'admin@sena.edu.co',
                'first_name': 'Administrador',
                'last_name': 'SINETEC',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin1234*')
            admin_user.save()
            admin_perfil = admin_user.perfil
            admin_perfil.rol = roles_dict["Administrador"]
            admin_perfil.numero_documento = "1082000001"
            admin_perfil.save()
            self.stdout.write(self.style.SUCCESS("Superusuario 'admin' creado (Clave: admin1234*)"))

        # 3. Crear Instructor Demo
        instructor, created = User.objects.get_or_create(
            username="instructor_carlos",
            defaults={
                'email': 'cmartinez@sena.edu.co',
                'first_name': 'Carlos',
                'last_name': 'Martínez'
            }
        )
        if created:
            instructor.set_password('Sena2026*')
            instructor.save()
            p = instructor.perfil
            p.rol = roles_dict["Instructor SENA"]
            p.numero_documento = "85441223"
            p.telefono = "3001234567"
            p.save()

        # 4. Crear Instituciones Educativas en el Magdalena
        col1, _ = InstitucionEducativa.objects.get_or_create(
            codigo_dane="147189000123",
            defaults={
                'nombre': 'I.E. Técnica Departamental de Ciénaga',
                'municipio': 'Ciénaga',
                'direccion': 'Calle 12 No. 15-40',
                'telefono': '3157894561',
                'rector_nombre': 'Lic. Alberto Castro',
                'enlace_nombre': 'Prof. Marta Domínguez',
                'enlace_telefono': '3014567890',
                'activa': True
            }
        )

        col2, _ = InstitucionEducativa.objects.get_or_create(
            codigo_dane="147001002456",
            defaults={
                'nombre': 'I.E. Distrital Simón Bolívar',
                'municipio': 'Santa Marta',
                'direccion': 'Avenida del Libertador No. 28-10',
                'telefono': '3009876543',
                'rector_nombre': 'Lic. María Consuelo Vega',
                'enlace_nombre': 'Prof. Jorge Eliécer Ruiz',
                'enlace_telefono': '3123456789',
                'activa': True
            }
        )

        col3, _ = InstitucionEducativa.objects.get_or_create(
            codigo_dane="147053000789",
            defaults={
                'nombre': 'I.E. Departamental Agropecuaria de Aracataca',
                'municipio': 'Aracataca',
                'direccion': 'Carrera 5 No. 8-22',
                'telefono': '3206549871',
                'rector_nombre': 'Lic. Gabriel Polo',
                'enlace_nombre': 'Prof. Sofía Mercado',
                'enlace_telefono': '3109876543',
                'activa': True
            }
        )

        # 5. Crear Programa Formativo
        prog, _ = ProgramaFormacion.objects.get_or_create(
            codigo_programa="228106",
            defaults={
                'denominacion': 'Técnico en Sistemas',
                'version': '102',
                'activo': True
            }
        )

        # 6. Crear Competencias y Resultados de Aprendizaje
        comp1, _ = Competencia.objects.get_or_create(
            programa=prog,
            codigo="220501001",
            defaults={'descripcion': 'Mantenimiento Preventivo y Correctivo de Equipos de Cómputo'}
        )

        rap1, _ = ResultadoAprendizaje.objects.get_or_create(
            competencia=comp1,
            codigo="RAP-01",
            defaults={'descripcion': 'Verificar el estado operativo del hardware y software de acuerdo con manuales del fabricante.'}
        )

        rap2, _ = ResultadoAprendizaje.objects.get_or_create(
            competencia=comp1,
            codigo="RAP-02",
            defaults={'descripcion': 'Ejecutar mantenimiento físico y lógico cumpliendo normas de seguridad y salud en el trabajo.'}
        )

        # 7. Crear Fichas Técnicas
        ficha1, _ = Ficha.objects.get_or_create(
            codigo_ficha="2501234",
            defaults={
                'programa': prog,
                'institucion': col1,
                'instructor_lider': instructor,
                'fecha_inicio': timezone.now().date(),
                'fecha_fin': timezone.now().date().replace(year=timezone.now().year + 1),
                'estado': 'En Ejecucion',
                'periodo_cerrado': False
            }
        )

        ficha2, _ = Ficha.objects.get_or_create(
            codigo_ficha="2501890",
            defaults={
                'programa': prog,
                'institucion': col2,
                'instructor_lider': instructor,
                'fecha_inicio': timezone.now().date(),
                'fecha_fin': timezone.now().date().replace(year=timezone.now().year + 1),
                'estado': 'En Ejecucion',
                'periodo_cerrado': False
            }
        )

        # 8. Crear Aprendices Demo
        aprendices_datos = [
            ("Juan David", "Martínez Gómez", "1082987123", "10"),
            ("Camila", "Ortiz De la Rosa", "1082544991", "10"),
            ("Andrés Felipe", "Pérez Varela", "1082112344", "10"),
            ("Valentina", "Quintero Salas", "1082776510", "11"),
        ]

        for nombres, apellidos, doc, grado in aprendices_datos:
            u, c = User.objects.get_or_create(
                username=f"ap_{doc}",
                defaults={
                    'email': f"{doc}@sena.edu.co",
                    'first_name': nombres,
                    'last_name': apellidos
                }
            )
            if c:
                u.set_password(f"Sena{doc[:4]}*")
                u.save()
                p = u.perfil
                p.rol = roles_dict["Estudiante"]
                p.tipo_documento = "TI"
                p.numero_documento = doc
                p.telefono = "3008889900"
                p.save()

            # Matricular en ficha1
            mat, _ = Matricula.objects.get_or_create(
                ficha=ficha1,
                aprendiz=u,
                defaults={'grado_escolar': grado, 'estado_formacion': 'En Formacion'}
            )

            # Asignar juicios evaluativos de ejemplo
            if doc == "1082112344":
                # Aprendiz con novedad de mejora
                JuicioEvaluativo.objects.get_or_create(
                    matricula=mat,
                    resultado_aprendizaje=rap1,
                    defaults={
                        'instructor': instructor,
                        'juicio_valor': 'D',
                        'observaciones': 'Requiere presentar plan de mejoramiento sobre mantenimiento correctivo.',
                        'fecha_evaluacion': timezone.now().date()
                    }
                )
            else:
                # Aprendices aprobados
                JuicioEvaluativo.objects.get_or_create(
                    matricula=mat,
                    resultado_aprendizaje=rap1,
                    defaults={
                        'instructor': instructor,
                        'juicio_valor': 'A',
                        'observaciones': 'Alcanzó satisfactoriamente los criterios de desempeño.',
                        'fecha_evaluacion': timezone.now().date()
                    }
                )

        # 9. Crear Bitácoras de Seguimiento de Ejemplo
        BitacoraSeguimiento.objects.get_or_create(
            ficha=ficha1,
            fecha_visita=timezone.now().date(),
            tipo_seguimiento='Presencial Aula',
            defaults={
                'instructor': instructor,
                'observaciones': 'Visita técnica de diagnóstico al aula de informática. Se verificó el cumplimiento del cronograma formativo y se revisaron las evidencias de los aprendices de grado 10°.',
                'compromisos': 'El docente enlace coordinará el préstamo de la sala de cómputo los días martes y jueves en jornada contraria.',
                'fecha_verificacion': timezone.now().date()
            }
        )

        self.stdout.write(self.style.SUCCESS("¡Datos demostrativos cargados exitosamente para SINETEC!"))
        self.stdout.write(self.style.SUCCESS("- 3 Colegios del Magdalena"))
        self.stdout.write(self.style.SUCCESS("- 1 Programa Técnico con Competencias y RAP"))
        self.stdout.write(self.style.SUCCESS("- 2 Fichas Técnicas"))
        self.stdout.write(self.style.SUCCESS("- 4 Aprendices matriculados con Juicios Evaluativos"))
        self.stdout.write(self.style.SUCCESS("- 1 Bitácora de seguimiento con compromisos"))
