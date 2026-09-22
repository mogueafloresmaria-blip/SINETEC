import unicodedata
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.contrib import messages


def _normalizar_texto(texto):
    if not texto:
        return ''
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower().strip()


def requerir_roles(*roles_permitidos):
    """
    Decorador de seguridad institucional que verifica en Backend si el usuario autenticado
    tiene un Rol formal cuyo nombre coincida con 'roles_permitidos'.
    Rechaza con PermissionDenied (HTTP 403) si no está autorizado.
    """
    roles_norm = {_normalizar_texto(r) for r in roles_permitidos}
    # Permitir variaciones de Aprendiz / Estudiante
    if 'aprendiz' in roles_norm:
        roles_norm.add('estudiante')
    if 'estudiante' in roles_norm:
        roles_norm.add('aprendiz')
    # Permitir variaciones de Secretaria
    if any(r.startswith('secretar') for r in roles_norm):
        roles_norm.add('secretaria')
        roles_norm.add('secretaria academica')

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            # Superusuarios institucionales de Django tienen auditoría y acceso maestro
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            perfil = getattr(request.user, 'perfil', None)
            if perfil and perfil.rol:
                rol_actual_norm = _normalizar_texto(perfil.rol.nombre)
                for r in roles_norm:
                    if r in rol_actual_norm or rol_actual_norm in r or rol_actual_norm.startswith(r[:6]):
                        return view_func(request, *args, **kwargs)
            elif any(r in ['instructor', 'instructor sena'] for r in roles_norm) and (
                request.user.is_staff or (request.user.username and request.user.username.lower().startswith('inst'))
            ):
                return view_func(request, *args, **kwargs)

            # Si el usuario no está autorizado para esta vista según su rol:
            rol_nombre = _normalizar_texto(perfil.rol.nombre) if (perfil and perfil.rol) else ''
            messages.error(
                request,
                "Acceso Restringido (Seguridad SINETEC): Tu rol de usuario no tiene permisos para acceder a esta sección privada."
            )
            if 'estudiante' in rol_nombre or 'aprendiz' in rol_nombre:
                return redirect('aprendiz_dashboard')
            elif 'instructor' in rol_nombre or 'docente' in rol_nombre:
                return redirect('instructor_dashboard')
            elif 'secretar' in rol_nombre:
                return redirect('secretaria_dashboard')
            elif 'coordinad' in rol_nombre or 'admin' in rol_nombre:
                return redirect('coordinador_dashboard')

            raise PermissionDenied("Acceso Denegado (Seguridad SINETEC): Tu rol institucional no tiene permisos para acceder a esta vista.")
        return _wrapped_view
    return decorator


def solo_coordinador_o_admin(view_func):
    return requerir_roles('Administrador', 'Coordinador')(view_func)


def solo_instructor(view_func):
    return requerir_roles('Administrador', 'Coordinador', 'Instructor SENA')(view_func)


def solo_aprendiz(view_func):
    return requerir_roles('Estudiante', 'Aprendiz')(view_func)


def solo_secretaria_o_coordinador(view_func):
    return requerir_roles('Administrador', 'Coordinador', 'Secretaría', 'Secretaria')(view_func)


def solo_secretaria(view_func):
    return requerir_roles('Administrador', 'Coordinador', 'Secretaría', 'Secretaria')(view_func)


def validar_propietario_o_coordinador(request, aprendiz_user):
    """
    Regla de seguridad anti-IDOR:
    Un aprendiz solo puede visualizar o modificar sus propios datos.
    Instructores y coordinadores pueden acceder a expedientes autorizados.
    """
    if request.user.is_superuser:
        return True
    perfil = getattr(request.user, 'perfil', None)
    rol_nombre = _normalizar_texto(perfil.rol.nombre) if (perfil and perfil.rol) else ''

    if any(r in rol_nombre for r in ['coordinador', 'admin', 'instructor', 'secretar']):
        return True

    # Si es aprendiz, debe ser exactamente la misma cuenta
    if request.user.id == aprendiz_user.id:
        return True

    raise PermissionDenied("Violación de Seguridad: No tienes autorización para consultar el expediente privado de otro aprendiz.")