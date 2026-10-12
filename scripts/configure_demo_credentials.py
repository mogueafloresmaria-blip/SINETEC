import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
import django
django.setup()

from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario, Rol

def configurar_credenciales():
    print("=" * 70)
    print("CONFIGURANDO CREDENCIALES DE DEMOSTRACIÓN — EDUNOVA")
    print("=" * 70)

    # 1. Roles con clave '12345'
    cuentas_12345 = ['admin', 'rector', 'secretaria', 'docente', 'familia', 'acudiente']
    for username in cuentas_12345:
        u = User.objects.filter(username=username).first()
        if u:
            u.set_password('12345')
            u.save()
            rol = u.perfil.rol.nombre if (hasattr(u, 'perfil') and u.perfil.rol) else 'Sin Rol'
            print(f"[OK] Usuario: {u.username:12s} | Rol: {rol:20s} | Contraseña configurada: 12345")
        else:
            print(f"[ALERTA] Usuario no encontrado: {username}")

    # 2. Estudiantes con clave = numero_documento
    estudiantes = PerfilUsuario.objects.filter(rol__nombre__icontains='estudiante').select_related('usuario', 'rol')
    for perfil in estudiantes:
        u = perfil.usuario
        doc = (perfil.numero_documento or '').strip()
        if u and doc:
            u.set_password(doc)
            u.save()
            print(f"[OK] Estudiante: {u.username:12s} | Nombre: {u.get_full_name():20s} | Doc / Clave: {doc}")
        else:
            print(f"[ALERTA] Estudiante sin documento o sin usuario: {u}")

    print("\n" + "=" * 70)
    print("¡CREDENCIALES DE DEMOSTRACIÓN CONFIGURADAS EXITOSAMENTE!")
    print("=" * 70)

if __name__ == '__main__':
    configurar_credenciales()
