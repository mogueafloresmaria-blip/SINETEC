import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'sinetec_project.settings'
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from usuarios.models import PerfilUsuario, Rol
from academico.models import ProgramaFormacion, Ficha, Matricula
from instituciones.models import InstitucionEducativa

# 1. Asegurar roles
rol_estudiante, _ = Rol.objects.get_or_create(nombre='Estudiante')
rol_instructor, _ = Rol.objects.get_or_create(nombre='Instructor SENA')

# 2. Instructores de referencia
inst_carlos = User.objects.filter(username='instructor_carlos').first()
inst_adso = User.objects.filter(username='instructor_adso').first()
inst_default = inst_carlos or inst_adso or User.objects.filter(is_superuser=True).first()

# 3. Instituciones
colegios = list(InstitucionEducativa.objects.all())
if not colegios:
    ied_inem, _ = InstitucionEducativa.objects.get_or_create(
        nombre='I.E.D. INEM Simón Bolívar',
        municipio='Santa Marta',
        departamento='Magdalena',
        sector='Oficial'
    )
    colegios = [ied_inem]

# 4. Datos para completar los 10 programas
programas_a_completar = [
    {
        'codigo': '134101',
        'denominacion': 'Técnico en Asistencia Administrativa',
        'ficha_codigo': '2891101',
        'aprendices': [
            ('1082991001', 'Valentina Sofia', 'Mendoza Perez', 'ap_1082991001'),
            ('1082991002', 'Mateo Jose', 'Castillo Rangel', 'ap_1082991002'),
            ('1082991003', 'Daniela Maria', 'Vargas Polo', 'ap_1082991003'),
        ]
    },
    {
        'codigo': '524100',
        'denominacion': 'Técnico en Integración de Contenidos Digitales',
        'ficha_codigo': '2891202',
        'aprendices': [
            ('1082992001', 'Santiago Andres', 'Gomez Navarro', 'ap_1082992001'),
            ('1082992002', 'Mariana Lucia', 'Suarez Diaz', 'ap_1082992002'),
            ('1082992003', 'Carlos Eduardo', 'Pineda Castro', 'ap_1082992003'),
        ]
    },
    {
        'codigo': '839312',
        'denominacion': 'Técnico en Mantenimiento de Equipos de Cómputo',
        'ficha_codigo': '2891303',
        'aprendices': [
            ('1082993001', 'David Alejandro', 'Romero Ruiz', 'ap_1082993001'),
            ('1082993002', 'Gabriela Elena', 'Ortega Morales', 'ap_1082993002'),
            ('1082993003', 'Andres Felipe', 'Silva Cotes', 'ap_1082993003'),
        ]
    },
    {
        'codigo': '122115',
        'denominacion': 'Tecnólogo en Gestión Administrativa',
        'ficha_codigo': '2891404',
        'aprendices': [
            ('1082994001', 'Isabella Maria', 'Torres Jimenez', 'ap_1082994001'),
            ('1082994002', 'Juan Camilo', 'Herrera Santos', 'ap_1082994002'),
            ('1082994003', 'Laura Vanessa', 'Peña Gutierrez', 'ap_1082994003'),
        ]
    },
]

pw_hash = make_password('Sena2026*')

for p_data in programas_a_completar:
    prog, _ = ProgramaFormacion.objects.get_or_create(
        codigo_programa=p_data['codigo'],
        defaults={'denominacion': p_data['denominacion'], 'version': '1', 'activo': True}
    )

    ied = colegios[0] if colegios else None
    ficha, f_created = Ficha.objects.get_or_create(
        codigo_ficha=p_data['ficha_codigo'],
        defaults={
            'programa': prog,
            'institucion': ied,
            'instructor_lider': inst_default,
            'fecha_inicio': '2026-02-01',
            'fecha_fin': '2026-11-30',
            'estado': 'En Ejecucion',
        }
    )

    for doc, nombre, apellido, usr in p_data['aprendices']:
        user, u_created = User.objects.get_or_create(
            username=usr,
            defaults={
                'first_name': nombre,
                'last_name': apellido,
                'email': f"{usr}@soy.sena.edu.co",
                'password': pw_hash,
            }
        )
        if not u_created:
            user.password = pw_hash
            user.save()

        perfil, _ = PerfilUsuario.objects.get_or_create(
            usuario=user,
            defaults={
                'rol': rol_estudiante,
                'tipo_documento': 'CC',
                'numero_documento': doc,
                'telefono': '3001234567',
                'direccion': 'Santa Marta, Magdalena',
            }
        )

        Matricula.objects.get_or_create(
            aprendiz=user,
            ficha=ficha,
            defaults={
                'estado_formacion': 'En Formacion',
                'grado_escolar': '10'
            }
        )

print('Población de los 10 programas completada con éxito.')
