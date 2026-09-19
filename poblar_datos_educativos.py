import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from datetime import date, time
from django.contrib.auth.models import User
from usuarios.models import Rol, PerfilUsuario
from academico.models import ProgramaFormacion, Competencia, ResultadoAprendizaje, Ficha, Matricula, HorarioFicha, NovedadHorario
from evaluaciones.models import JuicioEvaluativo
from instituciones.models import InstitucionEducativa

def sembrar():
    print("Iniciando sembrado de datos educativos...")

    # 1. Asegurar Roles
    roles = {
        'Administrador': 'Administrador global del sistema',
        'Coordinador': 'Coordinador de Media Técnica SENA',
        'Instructor SENA': 'Instructor técnico responsable de fichas',
        'Docente I.E.': 'Docente enlace de la Institución Educativa',
        'Estudiante': 'Aprendiz SENA matriculado en formación',
    }
    roles_objs = {}
    for nombre, desc in roles.items():
        obj, _ = Rol.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
        roles_objs[nombre] = obj

    # 2. Configurar usuarios clave
    # Laura (Coordinadora)
    laura = User.objects.filter(username='laura').first()
    if laura:
        laura.first_name = 'Laura'
        laura.last_name = 'Valencia'
        laura.email = 'coordinacion.magdalena@sena.edu.co'
        laura.set_password('sena1234*')
        laura.save()
        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=laura)
        perfil.rol = roles_objs['Coordinador']
        perfil.numero_documento = 'CC-108200001'
        perfil.save()
        print("Usuario 'laura' configurado como Coordinadora.")

    # Admin
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        admin_user.first_name = 'Administrador'
        admin_user.last_name = 'SINETEC'
        admin_user.set_password('admin1234*')
        admin_user.save()
        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=admin_user)
        perfil.rol = roles_objs['Administrador']
        perfil.numero_documento = 'CC-100000000'
        perfil.save()

    # Instructor Carlos
    instructor_carlos = User.objects.filter(username='instructor_carlos').first()
    if not instructor_carlos:
        instructor_carlos = User.objects.create_user(
            username='instructor_carlos',
            email='carlos.martinez@sena.edu.co',
            first_name='Carlos',
            last_name='Martínez',
            password='sena1234*'
        )
    else:
        instructor_carlos.set_password('sena1234*')
        instructor_carlos.save()
    perfil_carlos, _ = PerfilUsuario.objects.get_or_create(usuario=instructor_carlos)
    perfil_carlos.rol = roles_objs['Instructor SENA']
    perfil_carlos.numero_documento = 'CC-85472190'
    perfil_carlos.save()

    # Docente I.E. Profe Mendoza
    docente_mendoza, creado = User.objects.get_or_create(
        username='profesor_mendoza',
        defaults={
            'first_name': 'Javier',
            'last_name': 'Mendoza',
            'email': 'jmendoza@iedciena.edu.co',
        }
    )
    docente_mendoza.set_password('sena1234*')
    docente_mendoza.save()
    perfil_mendoza, _ = PerfilUsuario.objects.get_or_create(usuario=docente_mendoza)
    perfil_mendoza.rol = roles_objs['Docente I.E.']
    perfil_mendoza.numero_documento = 'CC-12589632'
    perfil_mendoza.save()
    print("Usuario 'profesor_mendoza' configurado como Docente I.E.")

    # Instructor Andrea (segundo instructor para permutas)
    instructor_andrea, _ = User.objects.get_or_create(
        username='instructora_andrea',
        defaults={
            'first_name': 'Andrea',
            'last_name': 'Gómez',
            'email': 'andrea.gomez@sena.edu.co',
        }
    )
    instructor_andrea.set_password('sena1234*')
    instructor_andrea.save()
    perfil_andrea, _ = PerfilUsuario.objects.get_or_create(usuario=instructor_andrea)
    perfil_andrea.rol = roles_objs['Instructor SENA']
    perfil_andrea.numero_documento = 'CC-57894123'
    perfil_andrea.save()

    # 3. Fichas y Programas
    programa = ProgramaFormacion.objects.first()
    if not programa:
        programa = ProgramaFormacion.objects.create(
            codigo_programa='228106',
            denominacion='Técnico en Programación de Software',
            version='1',
            activo=True
        )

    institucion = InstitucionEducativa.objects.first()
    if not institucion:
        institucion = InstitucionEducativa.objects.create(
            dane='147189000123',
            nombre='I.E. Técnica Departamental de Ciénaga',
            municipio='Ciénaga',
            rector_nombre='Lic. Roberto Fuentes',
            enlace_nombre='Lic. Javier Mendoza'
        )

    ficha1 = Ficha.objects.filter(codigo_ficha='2501234').first()
    if not ficha1:
        ficha1 = Ficha.objects.create(
            codigo_ficha='2501234',
            programa=programa,
            institucion=institucion,
            instructor_lider=instructor_carlos,
            fecha_inicio=date(2026, 2, 1),
            fecha_fin=date(2026, 11, 30),
            estado='En Ejecucion'
        )

    # 4. Competencias y RAPs
    competencias_data = [
        {
            'codigo': '220501096',
            'descripcion': 'Desarrollar la solución de software de acuerdo con el diseño y metodologías de desarrollo.',
            'raps': [
                ('RAP-01', 'Construir la interfaz de usuario web aplicando estándares HTML5, CSS3 y principios de diseño responsivo.'),
                ('RAP-02', 'Implementar la lógica del modelo de datos relacional y consultas SQL utilizando motores de bases de datos.'),
                ('RAP-03', 'Codificar los módulos backend del aplicativo web integrando controladores, vistas y seguridad según requerimientos.'),
                ('RAP-04', 'Ejecutar pruebas unitarias e integrales para verificar el correcto funcionamiento del software.')
            ]
        },
        {
            'codigo': '240201500',
            'descripcion': 'Promover la interacción idónea consigo mismo, con los demás y con la naturaleza en los contextos laboral y social.',
            'raps': [
                ('RAP-ET01', 'Interactuar en los contextos Productivos y Comunitarios a partir del reconocimiento de los principios y valores universales.'),
                ('RAP-ET02', 'Asumir actitudes críticas y propositivas en función de la resolución de problemas de carácter productivo y social.')
            ]
        },
        {
            'codigo': '240202501',
            'descripcion': 'Interactuar en lengua inglesa de forma oral y escrita en contextos laborales y académicos.',
            'raps': [
                ('RAP-ING01', 'Comprender vocabulario técnico en inglés relacionado con tecnologías de la información y software.'),
            ]
        }
    ]

    raps_creados = []
    for c_data in competencias_data:
        comp, _ = Competencia.objects.get_or_create(
            programa=programa,
            codigo=c_data['codigo'],
            defaults={'descripcion': c_data['descripcion']}
        )
        for r_cod, r_desc in c_data['raps']:
            rap_obj, _ = ResultadoAprendizaje.objects.get_or_create(
                competencia=comp,
                codigo=r_cod,
                defaults={'descripcion': r_desc}
            )
            raps_creados.append(rap_obj)

    print(f"Competencias y {len(raps_creados)} RAPs verificados.")

    # 5. Aprendices y Juicios Evaluativos
    aprendices = User.objects.filter(perfil__rol__nombre='Estudiante')
    matriculas = Matricula.objects.filter(ficha=ficha1)
    if not matriculas.exists() and aprendices.exists():
        for ap in aprendices:
            Matricula.objects.get_or_create(ficha=ficha1, aprendiz=ap, defaults={'grado_escolar': '10'})
        matriculas = Matricula.objects.filter(ficha=ficha1)

    for mat in matriculas:
        # Asignar juicios en los primeros 3 RAPs
        for idx, rap in enumerate(raps_creados[:3]):
            juicio_val = 'A' if (mat.id + idx) % 4 != 0 else 'D'
            obs = 'Desempeño satisfactorio en los talleres y evidencias de clase.' if juicio_val == 'A' else 'Pendiente entrega del plan de mejoramiento del taller práctico.'
            JuicioEvaluativo.objects.update_or_create(
                matricula=mat,
                resultado_aprendizaje=rap,
                defaults={
                    'instructor': instructor_carlos,
                    'juicio_valor': juicio_val,
                    'observaciones': obs,
                    'fecha_evaluacion': date(2026, 9, 10),
                }
            )

    # Asegurar QR diario para todos los aprendices
    for ap in aprendices:
        perfil = ap.perfil
        perfil.asegurar_qr()

    # 6. Horarios y Novedades de Horario
    bloques = [
        ('1', time(7, 0), time(10, 0), 'Lunes', instructor_carlos, 'Sala de Cómputo 1 (IED Ciénaga)', 'Presencial', 'Algoritmia y Maquetación Web'),
        ('1', time(10, 0), time(12, 30), 'Lunes', docente_mendoza, 'Sala de Cómputo 1', 'Presencial', 'Acompañamiento Técnico Institucional'),
        ('2', time(7, 0), time(11, 0), 'Martes', instructor_andrea, 'Ambiente Virtual Teams / Sala 2', 'Mixta', 'Bases de Datos Relacionales MySQL'),
        ('3', time(13, 0), time(17, 0), 'Miércoles', instructor_carlos, 'Sala de Cómputo 1', 'Presencial', 'Programación Backend Django'),
        ('4', time(8, 0), time(11, 0), 'Jueves', docente_mendoza, 'Aula de Clases 10A', 'Presencial', 'Lógica y Matemáticas Aplicadas'),
        ('5', time(7, 0), time(11, 0), 'Viernes', instructor_carlos, 'Sala de Cómputo 1', 'Presencial', 'Taller Integrador de Evidencias'),
    ]

    for dia_idx, h_ini, h_fin, dia_nombre, inst, amb, mod, tema in bloques:
        horario_obj, _ = HorarioFicha.objects.get_or_create(
            ficha=ficha1,
            dia=dia_idx,
            hora_inicio=h_ini,
            defaults={
                'hora_fin': h_fin,
                'instructor': inst,
                'ambiente': amb,
                'modalidad': mod,
                'tema': tema,
                'activo': True
            }
        )

    # Crear una novedad histórica de cambio docente/instructor
    horario_muestra = HorarioFicha.objects.filter(ficha=ficha1).first()
    if horario_muestra and not NovedadHorario.objects.exists():
        NovedadHorario.objects.create(
            horario=horario_muestra,
            instructor_anterior=instructor_andrea,
            instructor_nuevo=instructor_carlos,
            motivo='Permuta',
            observacion='Permuta acordada para cubrir sesión presencial de evaluación de software.',
            registrado_por=laura
        )

    print("Sembrado completado exitosamente.")

if __name__ == '__main__':
    sembrar()
