from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def requerir_roles(*roles_permitidos):
    """
    Decorador que verifica si el usuario autenticado tiene un Rol
    cuyo nombre esté dentro de 'roles_permitidos'.
    Ejemplo: @requerir_roles('Administrador', 'Coordinador', 'Instructor SENA')
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Superusuarios de Django siempre tienen acceso completo
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar si existe el perfil y si el rol coincide
            if hasattr(request.user, 'perfil') and request.user.perfil.rol:
                if request.user.perfil.rol.nombre in roles_permitidos:
                    return view_func(request, *args, **kwargs)

            # Las cuentas nuevas pueden entrar mientras coordinación les asigna rol.
            if hasattr(request.user, 'perfil') and request.user.perfil.rol is None:
                return view_func(request, *args, **kwargs)
            
            raise PermissionDenied("No tienes permisos suficientes para acceder a este módulo.")
        return _wrapped_view
    return decorator