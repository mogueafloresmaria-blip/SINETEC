from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from .models import Docente, ExperienciaAcademica, EstudioRealizado, PerfilUsuario, Rol

def docentes_lista(request):
    docentes = Docente.objects.all().select_related('usuario')
    return render(request, 'usuarios/docentes/lista.html', {'docentes': docentes})

def docente_editar(request, pk=None):
    docente = get_object_or_404(Docente, pk=pk) if pk else None
    user = docente.usuario if docente else None
    perfil = user.perfil if user and hasattr(user, 'perfil') else None

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Extract simple POST data
                nombres = request.POST.get('nombres', '')
                apellidos = request.POST.get('apellidos', '')
                tipo_documento = request.POST.get('tipo_documento', 'CC')
                numero_documento = request.POST.get('numero_documento', '')
                email = request.POST.get('email', '')
                telefono = request.POST.get('telefono', '')
                direccion = request.POST.get('direccion', '')
                barrio = request.POST.get('barrio', '')
                fecha_nacimiento = request.POST.get('fecha_nacimiento') or None
                edad = request.POST.get('edad', '')

                # Información Académica Institucional
                area = request.POST.get('area', '')
                escalafon = request.POST.get('escalafon', '')
                estado_docente = request.POST.get('estado_docente', 'ACTIVO')
                nro_resolucion = request.POST.get('nro_resolucion', '')
                profesion = request.POST.get('profesion', '')
                fecha_ingreso = request.POST.get('fecha_ingreso') or None
                fecha_retiro = request.POST.get('fecha_retiro') or None

                if not user:
                    # Create new user
                    username = numero_documento
                    if User.objects.filter(username=username).exists():
                        messages.error(request, "Ya existe un usuario con ese número de documento.")
                        return redirect(request.path)
                    
                    user = User.objects.create_user(
                        username=username,
                        first_name=nombres,
                        last_name=apellidos,
                        email=email,
                        password=numero_documento # Default password
                    )
                    rol, _ = Rol.objects.get_or_create(nombre='Docente')
                    perfil = PerfilUsuario.objects.create(
                        usuario=user,
                        numero_documento=numero_documento,
                        tipo_documento=tipo_documento,
                        telefono=telefono,
                        fecha_nacimiento=fecha_nacimiento,
                        rol=rol
                    )
                    docente = Docente.objects.create(
                        usuario=user,
                        direccion=direccion,
                        barrio=barrio,
                        area=area,
                        escalafon=escalafon,
                        estado_docente=estado_docente,
                        nro_resolucion=nro_resolucion,
                        profesion=profesion,
                        fecha_ingreso=fecha_ingreso,
                        fecha_retiro=fecha_retiro
                    )
                else:
                    user.first_name = nombres
                    user.last_name = apellidos
                    user.email = email
                    user.save()

                    if perfil:
                        perfil.numero_documento = numero_documento
                        perfil.tipo_documento = tipo_documento
                        perfil.telefono = telefono
                        perfil.fecha_nacimiento = fecha_nacimiento
                        perfil.save()
                    
                    docente.direccion = direccion
                    docente.barrio = barrio
                    docente.area = area
                    docente.escalafon = escalafon
                    docente.estado_docente = estado_docente
                    docente.nro_resolucion = nro_resolucion
                    docente.profesion = profesion
                    docente.fecha_ingreso = fecha_ingreso
                    docente.fecha_retiro = fecha_retiro
                    docente.save()

                # Process Experiencia Academica
                ExperienciaAcademica.objects.filter(docente=docente).delete()
                instituciones_exp = request.POST.getlist('exp_institucion[]')
                anos_exp = request.POST.getlist('exp_anos[]')
                for inst, an in zip(instituciones_exp, anos_exp):
                    if inst and an:
                        ExperienciaAcademica.objects.create(docente=docente, institucion=inst, anos=int(an))

                # Process Estudios Realizados
                EstudioRealizado.objects.filter(docente=docente).delete()
                estudio_titulos = request.POST.getlist('estudio_titulo[]')
                estudio_insts = request.POST.getlist('estudio_institucion[]')
                estudio_anos = request.POST.getlist('estudio_ano[]')
                for tit, inst, an in zip(estudio_titulos, estudio_insts, estudio_anos):
                    if tit and inst and an:
                        EstudioRealizado.objects.create(docente=docente, titulo=tit, institucion=inst, ano=int(an))
                
                messages.success(request, "Docente guardado exitosamente.")
                return redirect('docentes_lista')
                
        except Exception as e:
            messages.error(request, f"Error al guardar: {e}")

    # Prepare context
    context = {
        'docente': docente,
        'user': user,
        'perfil': perfil,
        'experiencias': docente.experiencias.all() if docente else [],
        'estudios': docente.estudios.all() if docente else []
    }
    return render(request, 'usuarios/docentes/form.html', context)

def docente_eliminar(request, pk):
    docente = get_object_or_404(Docente, pk=pk)
    if request.method == 'POST':
        # Soft delete or hard delete depending on requirement
        user = docente.usuario
        if hasattr(user, 'perfil'):
            user.perfil.esta_activo = False
            user.perfil.save()
        user.is_active = False
        user.save()
        docente.estado_docente = 'INACTIVO'
        docente.save()
        messages.success(request, "Docente inhabilitado exitosamente.")
        return redirect('docentes_lista')
    return render(request, 'usuarios/docentes/eliminar.html', {'docente': docente})
