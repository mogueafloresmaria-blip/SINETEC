import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SINETEC.settings")
django.setup()

from django.contrib.auth.models import User
from academico.models import Matricula, Ficha, ProgramaFormacion
from usuarios.models import PerfilUsuario, RolSistema

# Asegurar roles
rol_estudiante, _ = RolSistema.objects.get_or_create(nombre='Estudiante')

# Asegurar Fichas/Programa
prog, _ = ProgramaFormacion.objects.get_or_create(
    codigo_programa="PROG-01",
    defaults={'denominacion': "Programa de Prueba"}
)
ficha10, _ = Ficha.objects.get_or_create(
    codigo_ficha="FICHA-10",
    defaults={'programa': prog, 'jornada': 'Manana'}
)
ficha11, _ = Ficha.objects.get_or_create(
    codigo_ficha="FICHA-11",
    defaults={'programa': prog, 'jornada': 'Manana'}
)

data = [
    ("andres10", "Andrés", "Gómez", "10", ficha10),
    ("aprendiz2_10", "Segundo", "Estudiante", "10", ficha10),
    ("aprendiz3_11", "Tercer", "Estudiante", "11", ficha11),
    ("aprendiz4_11", "Cuarto", "Estudiante", "11", ficha11)
]

for username, fname, lname, grado, ficha in data:
    u, created = User.objects.get_or_create(username=username, defaults={
        'first_name': fname,
        'last_name': lname,
        'email': f"{username}@prueba.com"
    })
    if created:
        u.set_password("Sena12345*")
        u.save()

    p, _ = PerfilUsuario.objects.get_or_create(user=u, defaults={
        'rol': rol_estudiante,
        'numero_documento': f"DOC-{username}"
    })
    
    # Crear matricula
    Matricula.objects.get_or_create(aprendiz=u, defaults={
        'ficha': ficha,
        'grado_escolar': grado,
        'seccion': 'A',
        'estado_formacion': 'En Formacion',
        'programa': prog
    })

# Ahora limpiar otros aprendices (dejar solo estos 4 para no amontonar)
keep_usernames = ["andres10", "aprendiz2_10", "aprendiz3_11", "aprendiz4_11"]
Matricula.objects.exclude(aprendiz__username__in=keep_usernames).delete()

print("Limpieza y creación completada.")
