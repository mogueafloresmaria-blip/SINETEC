from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario, Rol, FamiliaAcudiente
from academico.models import Matricula, Ficha, CargaAcademica, HorarioFicha

print("=== INVENTARIO COMPLETO EDUNOVA ===")
total_users = User.objects.count()
total_perfiles = PerfilUsuario.objects.count()
users_sin_perfil = User.objects.filter(perfil__isnull=True).count()
print(f"Total Usuarios Django: {total_users}")
print(f"Total Perfiles: {total_perfiles}")
print(f"Usuarios sin Perfil: {users_sin_perfil}")

roles = Rol.objects.all()
for r in roles:
    c = PerfilUsuario.objects.filter(rol=r).count()
    print(f"  Rol {r.nombre}: {c} perfiles")

estudiante_users = (
    User.objects.filter(perfil__rol__nombre__icontains='estudiante') |
    User.objects.filter(perfil__rol__nombre__icontains='aprendiz')
).distinct()
print(f"\nTotal Usuarios con rol Estudiante/Aprendiz: {estudiante_users.count()}")

total_mat = Matricula.objects.count()
print(f"Total Matriculas: {total_mat}")
mat_activas = Matricula.objects.filter(estado_formacion='En Formacion').count()
mat_retiradas = Matricula.objects.filter(estado_formacion='Retirado').count()
mat_trasladadas = Matricula.objects.filter(estado_formacion='Trasladado').count()
mat_certificadas = Matricula.objects.filter(estado_formacion='Certificado').count()
mat_desertadas = Matricula.objects.filter(estado_formacion='Desertado').count()
print(f"  Matriculas Activas ('En Formacion'): {mat_activas}")
print(f"  Matriculas Retiradas: {mat_retiradas}")
print(f"  Matriculas Trasladadas: {mat_trasladadas}")
print(f"  Matriculas Certificadas: {mat_certificadas}")
print(f"  Matriculas Desertadas: {mat_desertadas}")

print("\n--- DETALLE DE MATRICULAS REGISTRADAS ---")
for m in Matricula.objects.select_related('aprendiz', 'aprendiz__perfil', 'ficha').all():
    p = getattr(m.aprendiz, 'perfil', None)
    doc = p.numero_documento if p else 'SIN_PERFIL'
    rol = p.rol.nombre if p and p.rol else 'SIN_ROL'
    acudientes = FamiliaAcudiente.objects.filter(estudiantes=m.aprendiz).count()
    print(f"Matricula ID={m.id} | User={m.aprendiz.username} | Nombre={m.aprendiz.get_full_name()} | Doc={doc} | Rol={rol} | Ficha={m.ficha} | Grado={m.grado_escolar}{m.seccion} | Estado={m.estado_formacion} | Acudientes={acudientes}")

print("\n--- USUARIOS CON ROL ESTUDIANTE SIN MATRICULA ---")
for u in estudiante_users:
    if not Matricula.objects.filter(aprendiz=u).exists():
        p = getattr(u, 'perfil', None)
        doc = p.numero_documento if p else 'SIN_PERFIL'
        print(f"User={u.username} | Doc={doc} | Nombre={u.get_full_name()}")

print("\n--- ACUDIENTES / FAMILIAS ---")
for fa in FamiliaAcudiente.objects.all():
    ests = list(fa.estudiantes.values_list('username', flat=True))
    print(f"Acudiente={fa.nombre_acudiente} | Doc={fa.documento} | Parentesco={fa.parentesco} | Estudiantes a cargo: {ests}")
