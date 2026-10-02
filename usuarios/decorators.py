import unicodedata
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Q


def _normalizar_texto(texto):
    if not texto:
        return ''
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower().strip()


def obtener_url_redireccion_por_rol(user):
    """
    Determina la URL de destino según el rol institucional real del usuario en MySQL.
    """
    if not user or not user.is_authenticated:
        return 'login'
    if user.is_superuser:
        return 'dashboard'

    perfil = getattr(user, 'perfil', None)
    if not perfil or not perfil.rol:
        return 'dashboard'

    rol_nombre = _normalizar_texto(perfil.rol.nombre)

    if 'estudiante' in rol_nombre or 'aprendiz' in rol_nombre or 'alumno' in rol_nombre:
        return 'aprendiz_dashboard'
    elif 'famili' in rol_nombre or 'acudiente' in rol_nombre:
        return 'familia_portal'
    elif any(r in rol_nombre for r in ['docente', 'instructor', 'profesor']):
        return 'instructor_dashboard'
    elif 'secretar' in rol_nombre:
        return 'secretaria_dashboard'
    elif 'rector' in rol_nombre or 'coordinad' in rol_nombre:
        return 'rectoria_dashboard'
    else:
        return 'dashboard'


def _obtener_categorias_rol(texto):
    """
    Retorna el conjunto de categorías institucionales a las que pertenece un rol o texto:
    - 'ADMIN': Administrador, Superusuario
    - 'DIRECTIVO': Rector, Rectoría, Coordinador, Directivo
    - 'SECRETARIA': Secretaría, Secretaria, Auxiliar
    - 'DOCENTE': Docente, Profesor, Instructor, Maestro, Tutor
    - 'ESTUDIANTE': Estudiante, Aprendiz, Alumno
    - 'FAMILIA': Familia, Acudiente, Padre, Madre, Tutor Legal
    """
    t = _normalizar_texto(texto)
    cats = set()
    if not t:
        return cats

    if any(k in t for k in ['admin', 'super']):
        cats.add('ADMIN')
    if any(k in t for k in ['rector', 'coordinad', 'directiv']):
        cats.add('DIRECTIVO')
    if any(k in t for k in ['secretar']):
        cats.add('SECRETARIA')
    if any(k in t for k in ['docent', 'profesor', 'instructor', 'maestr']):
        cats.add('DOCENTE')
    if any(k in t for k in ['estudiant', 'aprendiz', 'alumno']):
        cats.add('ESTUDIANTE')
    if any(k in t for k in ['famili', 'acudient', 'padre', 'madre']):
        cats.add('FAMILIA')

    return cats


def requerir_roles(*roles_permitidos):
    """
    Decorador de seguridad institucional que verifica en Backend si el usuario autenticado
    tiene un Rol formal compatible con 'roles_permitidos'.
    Reconoce sinónimos escolares (Profesor / Docente, Docente I.E., Instructor, etc.).
    """
    categorias_permitidas = set()
    roles_norm_set = set()
    for r in roles_permitidos:
        r_norm = _normalizar_texto(r)
        roles_norm_set.add(r_norm)
        categorias_permitidas.update(_obtener_categorias_rol(r))

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            # Superusuarios de Django tienen acceso maestro total
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            perfil = getattr(request.user, 'perfil', None)
            if perfil and perfil.rol:
                rol_nombre = perfil.rol.nombre
                user_norm = _normalizar_texto(rol_nombre)
                user_cats = _obtener_categorias_rol(rol_nombre)

                # Administradores institucionales tienen acceso a vistas de gestión
                if 'ADMIN' in user_cats:
                    return view_func(request, *args, **kwargs)

                # Coincidencia por categoría institucional (e.g. DOCENTE, DIRECTIVO, SECRETARIA, etc.)
                if bool(user_cats & categorias_permitidas):
                    return view_func(request, *args, **kwargs)

                # Directivos (Rector / Coordinador) tienen acceso a vistas de gestión académica y reportes
                if 'DIRECTIVO' in user_cats and bool(categorias_permitidas & {'DOCENTE', 'SECRETARIA', 'ADMIN'}):
                    return view_func(request, *args, **kwargs)

                # Coincidencia por subcadena o coincidencia de prefijo
                for r in roles_norm_set:
                    if r in user_norm or user_norm in r or (len(r) >= 4 and user_norm.startswith(r[:4])):
                        return view_func(request, *args, **kwargs)

            # Si el usuario no está autorizado para esta vista según su rol:
            messages.error(
                request,
                "Acceso Restringido (Seguridad SINETEC): Tu rol de usuario no tiene permisos para acceder a esta sección."
            )
            return redirect(obtener_url_redireccion_por_rol(request.user))
        return _wrapped_view
    return decorator


def solo_admin(view_func):
    return requerir_roles('Administrador')(view_func)


def solo_rectoria_o_admin(view_func):
    return requerir_roles('Administrador', 'Rectoría', 'Rector', 'Coordinador')(view_func)


def solo_coordinador_o_admin(view_func):
    return requerir_roles('Administrador', 'Rectoría', 'Rector', 'Coordinador')(view_func)


def solo_secretaria_o_coordinador(view_func):
    return requerir_roles('Administrador', 'Rectoría', 'Rector', 'Coordinador', 'Secretaría', 'Secretaria')(view_func)


def solo_secretaria(view_func):
    return requerir_roles('Administrador', 'Rectoría', 'Rector', 'Coordinador', 'Secretaría', 'Secretaria')(view_func)


def solo_instructor(view_func):
    return requerir_roles('Administrador', 'Rectoría', 'Rector', 'Coordinador', 'Docente', 'Docente I.E.', 'Instructor', 'Instructor SENA', 'Profesor / Docente')(view_func)


def solo_docente(view_func):
    return requerir_roles('Administrador', 'Rectoría', 'Rector', 'Coordinador', 'Docente', 'Docente I.E.', 'Instructor', 'Instructor SENA', 'Profesor / Docente')(view_func)


def solo_aprendiz(view_func):
    return requerir_roles('Estudiante', 'Aprendiz', 'Alumno')(view_func)


def solo_familia(view_func):
    return requerir_roles('Familia/Acudiente', 'Familia', 'Acudiente', 'Familia / Acudiente')(view_func)


def validar_propietario_o_coordinador(request, estudiante_user):
    """
    Regla de seguridad anti-IDOR estricta:
    - Superusuarios, Administradores, Rectoría y Secretaría tienen acceso institucional.
    - Docentes pueden acceder a los estudiantes de sus cursos/fichas.
    - Estudiantes solo pueden consultar su propio expediente.
    - Familias/Acudientes solo pueden consultar los estudiantes asignados a su núcleo familiar.
    Cualquier intento no autorizado lanza PermissionDenied (HTTP 403).
    """
    if request.user.is_superuser:
        return True

    perfil = getattr(request.user, 'perfil', None)
    rol_nombre = _normalizar_texto(perfil.rol.nombre) if (perfil and perfil.rol) else ''

    # 1. Autoridad institucional
    if any(r in rol_nombre for r in ['admin', 'rector', 'coordinad', 'secretar']):
        return True

    # 2. Docentes (verificar si el estudiante está en alguna de sus fichas o cursos)
    if any(r in rol_nombre for r in ['docente', 'instructor', 'profesor']):
        from academico.models import Matricula
        fichas_docente = request.user.fichas_asignadas.all()
        esta_en_ficha = Matricula.objects.filter(aprendiz=estudiante_user, ficha__in=fichas_docente).exists()
        if esta_en_ficha or request.user.is_staff:
            return True
        raise PermissionDenied("Violación de Seguridad: Como docente, este estudiante no pertenece a ninguno de tus cursos asignados.")

    # 3. Familias y Acudientes (verificar asociación con el estudiante)
    if any(r in rol_nombre for r in ['famili', 'acudiente']):
        from usuarios.models import FamiliaAcudiente
        doc_acudiente = perfil.numero_documento if perfil else ''
        es_hijo = FamiliaAcudiente.objects.filter(
            (Q(documento=doc_acudiente) | Q(email__iexact=request.user.email) | Q(nombre_acudiente__icontains=request.user.last_name)) &
            Q(estudiantes=estudiante_user)
        ).exists()
        if es_hijo:
            return True
        raise PermissionDenied("Violación de Seguridad: No tienes autorización para consultar la información privada de este estudiante.")

    # 4. Estudiantes (únicamente su propio expediente)
    if any(r in rol_nombre for r in ['estudiante', 'aprendiz', 'alumno']):
        if request.user.id == estudiante_user.id:
            return True
        raise PermissionDenied("Violación de Seguridad: Como estudiante, solo tienes autorización para consultar tu propio expediente.")

    raise PermissionDenied("Violación de Seguridad SINETEC: No estás autorizado para acceder a este expediente estudiantil.")