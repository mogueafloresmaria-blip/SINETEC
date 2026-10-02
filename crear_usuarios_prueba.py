from django.contrib.auth.models import User
from academico.models import Matricula, Ficha
from usuarios.models import PerfilUsuario, Rol

rol_estudiante, _ = Rol.objects.get_or_create(nombre='Estudiante')
ficha_base = Ficha.objects.first()

data = [
    ("andres10", "Andrés", "Gómez", "10"),
    ("aprendiz2_10", "Segundo", "Estudiante", "10"),
    ("aprendiz3_11", "Tercer", "Estudiante", "11"),
    ("aprendiz4_11", "Cuarto", "Estudiante", "11")
]

User.objects.filter(username__in=[d[0] for d in data]).delete()

for username, fname, lname, grado in data:
    u = User.objects.create_user(
        username=username,
        first_name=fname,
        last_name=lname,
        email=f"{username}@prueba.com",
        password="Password123*"
    )
    
    p, _ = PerfilUsuario.objects.get_or_create(usuario=u, defaults={
        'rol': rol_estudiante,
        'numero_documento': f"{username}"
    })
    
    Matricula.objects.create(
        aprendiz=u,
        ficha=ficha_base,
        grado_escolar=grado,
        seccion='A',
        estado_formacion='En Formacion'
    )

print("4 Estudiantes creados exitosamente.")
