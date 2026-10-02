from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import CargaAcademica, HorarioFicha, Matricula, ProgramaFormacion, Competencia, ResultadoAprendizaje, TareaClase, EntregaTarea, GuiaClase, ActividadClase, AvisoClase, CalificacionEscolar
from django.contrib.auth.models import User

@login_required
def buscar_carga_desde_horario(request, horario_id):
    horario = get_object_or_404(HorarioFicha, id=horario_id)
    # Get or create CargaAcademica matching this HorarioFicha
    carga = CargaAcademica.objects.filter(
        profesor=horario.instructor,
        programa=horario.programa,
        grado=horario.grado,
        seccion=horario.seccion,
    ).first()
    
    if not carga and horario.programa:
        carga = CargaAcademica.objects.create(
            profesor=horario.instructor,
            programa=horario.programa,
            nivel=horario.nivel or 'Secundaria',
            grado=horario.grado,
            seccion=horario.seccion or 'A',
            anio_lectivo=2026
        )
    
    if carga:
        return redirect('detalle_clase', carga_id=carga.id)
    else:
        messages.error(request, "No se pudo encontrar ni crear el detalle de la clase porque no tiene programa asociado.")
        return redirect('horarios_tablero')

@login_required
def detalle_clase(request, carga_id):
    carga = get_object_or_404(CargaAcademica, id=carga_id)
    
    # Restrict to 10 and 11
    if request.user == carga.profesor and not (request.user.is_superuser):
        if carga.grado not in ['10', '11', '10mo Grado', '11mo Grado', '10°', '11°']:
            messages.error(request, "Solo tienes acceso a los grados 10° y 11°.")
            return redirect('horarios_tablero')

    tab = request.GET.get('tab', 'informacion')
    
    context = {
        'carga': carga,
        'tab': tab,
        'competencias': Competencia.objects.filter(programa=carga.programa),
        'guias': GuiaClase.objects.filter(carga_academica=carga),
        'actividades': ActividadClase.objects.filter(carga_academica=carga),
        'tareas': TareaClase.objects.filter(carga_academica=carga),
        'avisos': AvisoClase.objects.filter(carga_academica=carga),
        'calificaciones': CalificacionEscolar.objects.filter(carga_academica=carga),
    }
    
    # Matriculas (Students)
    matriculas = Matricula.objects.filter(
        estado_formacion='En Formacion',
        grado_escolar__in=['10', '11']
    )
    # further filter by seccion and grado to match carga if needed
    grado_num = ''.join(filter(str.isdigit, carga.grado))
    if grado_num:
        matriculas = matriculas.filter(grado_escolar=grado_num, seccion=carga.seccion)
    
    context['matriculas'] = matriculas
    
    return render(request, 'academico/detalle_clase.html', context)

@login_required
def crear_tarea(request, carga_id):
    carga = get_object_or_404(CargaAcademica, id=carga_id)
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        instrucciones = request.POST.get('instrucciones')
        fecha_limite = request.POST.get('fecha_limite')
        
        if titulo and instrucciones:
            TareaClase.objects.create(
                carga_academica=carga,
                titulo=titulo,
                instrucciones=instrucciones,
                fecha_limite=fecha_limite if fecha_limite else None
            )
            messages.success(request, 'Tarea creada exitosamente.')
            return redirect(f'/academico/clase/{carga.id}/?tab=tareas')
        else:
            messages.error(request, 'Título e instrucciones son requeridos.')
            
    return render(request, 'academico/crear_tarea.html', {'carga': carga})

@login_required
def detalle_tarea_docente(request, tarea_id):
    tarea = get_object_or_404(TareaClase, id=tarea_id)
    entregas = tarea.entregas.all()
    return render(request, 'academico/detalle_tarea_docente.html', {
        'tarea': tarea,
        'entregas': entregas
    })

@login_required
def revision_entrega(request, entrega_id):
    entrega = get_object_or_404(EntregaTarea, id=entrega_id)
    if request.method == 'POST':
        calificacion = request.POST.get('calificacion')
        retroalimentacion = request.POST.get('retroalimentacion')
        if calificacion:
            entrega.calificacion = calificacion
            entrega.retroalimentacion = retroalimentacion
            entrega.estado = 'CALIFICADA'
            entrega.save()
            
            # Registrar en CalificacionEscolar si es requerido
            try:
                CalificacionEscolar.objects.update_or_create(
                    matricula__aprendiz=entrega.estudiante,
                    carga_academica=entrega.tarea.carga_academica,
                    periodo=entrega.tarea.periodo,
                    defaults={
                        'nota': calificacion,
                        'profesor': request.user,
                        'observaciones': retroalimentacion
                    }
                )
            except Exception as e:
                pass

            messages.success(request, 'Calificación guardada correctamente.')
            if request.POST.get('guardar_continuar'):
                siguiente = EntregaTarea.objects.filter(tarea=entrega.tarea, estado__in=['PENDIENTE', 'ENTREGADA', 'ENTREGADA_TARDE']).exclude(id=entrega.id).first()
                if siguiente:
                    return redirect('revision_entrega', entrega_id=siguiente.id)
            return redirect('panel_calificaciones')

    return render(request, 'academico/revision_entrega.html', {'entrega': entrega})

@login_required
def panel_calificaciones(request):
    cargas = CargaAcademica.objects.filter(profesor=request.user)
    tareas = TareaClase.objects.filter(carga_academica__in=cargas)
    # Limitar a unos pocos aprendices si el requerimiento exige "no 68, sino los reales de prueba". 
    # El filtro de carga academica y tarea ya restringe.
    entregas_pendientes = EntregaTarea.objects.filter(
        tarea__in=tareas, 
        estado__in=['ENTREGADA', 'ENTREGADA_TARDE', 'PENDIENTE']
    ).exclude(estado='CALIFICADA').exclude(respuesta__isnull=True, archivo__isnull=True).select_related('tarea', 'estudiante')

    return render(request, 'academico/panel_calificaciones.html', {'entregas_pendientes': entregas_pendientes})

@login_required
def mis_actividades_docente(request):
    cargas = CargaAcademica.objects.filter(profesor=request.user)
    tareas = TareaClase.objects.filter(carga_academica__in=cargas).annotate(
        total_entregas=Count('entregas'),
        pendientes=Count('entregas', filter=Q(entregas__estado__in=['ENTREGADA', 'ENTREGADA_TARDE']))
    )
    return render(request, 'academico/mis_actividades_docente.html', {'tareas': tareas})

@login_required
def crear_actividad_digital(request):
    guias = GuiaClase.objects.filter(Q(carga_academica__profesor=request.user) | Q(carga_academica__isnull=True)).distinct()
    if not guias.exists():
        guias = GuiaClase.objects.all().distinct()
        
    cargas = CargaAcademica.objects.filter(profesor=request.user).select_related('programa').order_by('grado', 'programa__denominacion')
    if not cargas.exists():
        cargas = CargaAcademica.objects.all().select_related('programa').order_by('grado', 'programa__denominacion')

    resultados = ResultadoAprendizaje.objects.all().order_by('codigo')

    matriculas_qs = list(Matricula.objects.filter(
        estado_formacion__in=['En Formacion', 'Activo']
    ).select_related('aprendiz', 'aprendiz__perfil').order_by('grado_escolar', 'aprendiz__last_name', 'aprendiz__first_name'))

    if request.method == 'POST':
        guia_id = request.POST.get('guia_id')
        carga_id = request.POST.get('carga_id')
        grado = request.POST.get('grado')
        titulo = request.POST.get('titulo', '').strip()
        instrucciones = request.POST.get('instrucciones', '').strip()
        evidencia = request.POST.get('evidencia', 'Tarea').strip()
        rap_id = request.POST.get('resultado_aprendizaje_id')
        destinatario_tipo = request.POST.get('destinatario_tipo', 'todos')
        estudiante_id = request.POST.get('estudiante_id')
        fecha_limite = request.POST.get('fecha_limite')
        hora_limite = request.POST.get('hora_limite')
        puntaje_maximo = request.POST.get('puntaje_maximo', '5.0')
        porcentaje = request.POST.get('porcentaje', '20.0')
        archivo = request.FILES.get('archivo')

        guia = GuiaClase.objects.filter(id=guia_id).first() if guia_id else None
        rap = ResultadoAprendizaje.objects.filter(id=rap_id).first() if rap_id else None

        if not titulo and guia:
            titulo = guia.titulo
        elif not titulo:
            titulo = f"Actividad Pedagógica - {evidencia}"

        if not instrucciones and guia:
            instrucciones = guia.instrucciones
        elif not instrucciones:
            instrucciones = "Siga las instrucciones detalladas y entregue su desarrollo antes de la fecha límite establecida."

        from datetime import datetime
        dt_obj = None
        if fecha_limite and hora_limite:
            try:
                dt_obj = datetime.strptime(f"{fecha_limite} {hora_limite}", "%Y-%m-%d %H:%M")
            except Exception:
                dt_obj = None
        elif fecha_limite:
            try:
                dt_obj = datetime.strptime(f"{fecha_limite} 23:59", "%Y-%m-%d %H:%M")
            except Exception:
                dt_obj = None

        # Determinar carga académica
        c_obj = None
        if carga_id:
            c_obj = CargaAcademica.objects.filter(id=carga_id, profesor=request.user).first()
            if not c_obj:
                c_obj = CargaAcademica.objects.filter(id=carga_id).first()
        if not c_obj and grado:
            c_obj = CargaAcademica.objects.filter(profesor=request.user, grado__icontains=str(grado)).first()
        if not c_obj:
            c_obj = cargas.first()

        if c_obj:
            tarea = TareaClase.objects.create(
                carga_academica=c_obj,
                titulo=titulo,
                instrucciones=instrucciones,
                tipo_actividad=evidencia if evidencia else 'Tarea',
                resultado_aprendizaje=rap,
                fecha_limite=dt_obj,
                puntaje_maximo=float(puntaje_maximo or 5.0),
                porcentaje=float(porcentaje or 20.0),
                archivo=archivo or (guia.archivo if guia and guia.archivo else None),
                estado='Publicada'
            )

            # Notificar y crear entregas pendientes para los estudiantes
            from seguimiento.models import Notificacion
            from django.urls import reverse
            
            g_num = ''.join(ch for ch in str(c_obj.grado) if ch.isdigit()) or '10'
            if destinatario_tipo == 'individual' and estudiante_id:
                target_users = User.objects.filter(id=estudiante_id)
            else:
                mats = [m for m in matriculas_qs if g_num in str(m.grado_escolar)]
                target_users = [m.aprendiz for m in mats] if mats else [m.aprendiz for m in matriculas_qs[:2]]

            for u in target_users:
                EntregaTarea.objects.get_or_create(
                    tarea=tarea,
                    estudiante=u,
                    defaults={'estado': 'PENDIENTE'}
                )
                Notificacion.objects.create(
                    usuario=u,
                    titulo=f"Nueva Actividad: {tarea.titulo}",
                    mensaje=f"Tienes una nueva actividad en {c_obj.programa.denominacion if c_obj.programa else 'Clase'} (Fecha límite: {dt_obj.strftime('%d/%m/%Y %H:%M') if dt_obj else 'Sin límite'}).",
                    enlace=reverse('entregar_tarea_clase', kwargs={'pk': tarea.id}),
                    tipo='info'
                )

            messages.success(request, f'¡Actividad "{tarea.titulo}" publicada y enviada a los estudiantes con éxito!')
            return redirect(f"{reverse('actividades_tareas')}?tarea_id={tarea.id}")
        else:
            messages.error(request, 'No se pudo asociar la actividad a ninguna carga académica docente.')

    return render(request, 'academico/crear_actividad_digital.html', {
        'guias': guias,
        'cargas': cargas,
        'resultados': resultados,
        'estudiantes': matriculas_qs,
    })

@login_required
def comunicaciones(request):
    from .models import ComunicacionMensaje
    recibidos = ComunicacionMensaje.objects.filter(destinatario=request.user, eliminado_por_destinatario=False).order_by('-fecha_envio')
    enviados = ComunicacionMensaje.objects.filter(remitente=request.user, eliminado_por_remitente=False).order_by('-fecha_envio')
    
    # Papelera: mensajes borrados por este usuario
    papelera = ComunicacionMensaje.objects.filter(
        destinatario=request.user, eliminado_por_destinatario=True
    ) | ComunicacionMensaje.objects.filter(
        remitente=request.user, eliminado_por_remitente=True
    )
    papelera = papelera.order_by('-fecha_envio')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'eliminar':
            msg_id = request.POST.get('msg_id')
            msg = get_object_or_404(ComunicacionMensaje, id=msg_id)
            if msg.remitente == request.user:
                msg.eliminado_por_remitente = True
            if msg.destinatario == request.user:
                msg.eliminado_por_destinatario = True
            msg.save()
            messages.success(request, 'Mensaje movido a la papelera.')
            return redirect('comunicaciones')
            
        elif action == 'restaurar':
            msg_id = request.POST.get('msg_id')
            msg = get_object_or_404(ComunicacionMensaje, id=msg_id)
            if msg.remitente == request.user:
                msg.eliminado_por_remitente = False
            if msg.destinatario == request.user:
                msg.eliminado_por_destinatario = False
            msg.save()
            messages.success(request, 'Mensaje restaurado.')
            return redirect('comunicaciones')
            
        elif action == 'eliminar_definitivo':
            msg_id = request.POST.get('msg_id')
            msg = get_object_or_404(ComunicacionMensaje, id=msg_id)
            # Solo si el usuario es dueño en alguna parte
            if msg.remitente == request.user or msg.destinatario == request.user:
                msg.delete()
                messages.success(request, 'Mensaje eliminado definitivamente.')
            return redirect('comunicaciones')

        # Si no es ninguna de esas, es enviar mensaje
        destinatario_id = request.POST.get('destinatario_id')
        grupo_destino = request.POST.get('grupo_destino')
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        
        if asunto and mensaje:
            msg = ComunicacionMensaje.objects.create(
                remitente=request.user,
                destinatario_id=destinatario_id if destinatario_id else None,
                grupo_destino=grupo_destino,
                asunto=asunto,
                mensaje=mensaje
            )
            
            from seguimiento.models import Notificacion
            
            if msg.destinatario:
                Notificacion.objects.create(
                    usuario=msg.destinatario,
                    titulo=f"Nuevo mensaje: {asunto}",
                    mensaje=f"Tienes un nuevo mensaje de {request.user.get_full_name()}.",
                    tipo='info',
                    enlace='/academico/comunicaciones/'
                )
            elif msg.grupo_destino:
                estudiantes = User.objects.filter(matriculas_academicas__grado_escolar=msg.grupo_destino)
                for est in estudiantes:
                    Notificacion.objects.create(
                        usuario=est,
                        titulo=f"Nuevo mensaje para grado {msg.grupo_destino}: {asunto}",
                        mensaje=f"Tienes un nuevo mensaje de {request.user.get_full_name()}.",
                        tipo='info',
                        enlace='/academico/comunicaciones/'
                    )
            
            messages.success(request, 'Mensaje enviado.')
            return redirect('comunicaciones')
            
    # Obtener usuarios activos institucionales disponibles para mensajería
    usuarios_disponibles = User.objects.filter(is_active=True).exclude(id=request.user.id).select_related('perfil', 'perfil__rol').order_by('first_name', 'last_name')

    return render(request, 'academico/comunicaciones.html', {
        'recibidos': recibidos,
        'enviados': enviados,
        'papelera': papelera,
        'usuarios': usuarios_disponibles,
        'total_recibidos': recibidos.count(),
        'total_enviados': enviados.count(),
        'total_papelera': papelera.count(),
    })

@login_required
def actividades_estudiante(request):
    matriculas = Matricula.objects.filter(aprendiz=request.user, estado_formacion='En Formacion')
    tareas = []
    for m in matriculas:
        # Get CargaAcademica matching this matricula
        cargas = CargaAcademica.objects.filter(grado=m.grado_escolar, seccion=m.seccion)
        for c in cargas:
            ts = TareaClase.objects.filter(carga_academica=c)
            for t in ts:
                entrega = EntregaTarea.objects.filter(tarea=t, estudiante=request.user).first()
                tareas.append({'tarea': t, 'entrega': entrega})
    
    return render(request, 'academico/actividades_estudiante.html', {'tareas': tareas})

@login_required
def entregar_tarea(request, tarea_id):
    tarea = get_object_or_404(TareaClase, id=tarea_id)
    if request.method == 'POST':
        respuesta = request.POST.get('respuesta')
        archivo = request.FILES.get('archivo')
        
        entrega, created = EntregaTarea.objects.get_or_create(
            tarea=tarea,
            estudiante=request.user,
            defaults={'estado': 'ENTREGADA'}
        )
        if respuesta: entrega.respuesta = respuesta
        if archivo: entrega.archivo = archivo
        entrega.estado = 'ENTREGADA'
        entrega.save()
        messages.success(request, 'Tarea entregada exitosamente.')
        return redirect('actividades_estudiante')
    
    return render(request, 'academico/entregar_tarea.html', {'tarea': tarea})
