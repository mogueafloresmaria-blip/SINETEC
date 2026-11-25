from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from usuarios.decorators import _obtener_categorias_rol, solo_aprendiz, solo_instructor
from .models import CargaAcademica, HorarioFicha, Matricula, ProgramaFormacion, Competencia, ResultadoAprendizaje, TareaClase, EntregaTarea, GuiaClase, ActividadClase, AvisoClase, CalificacionEscolar
from django.contrib.auth.models import User


def _cargas_para_aprendiz(usuario):
    cargas_por_matricula = Q()
    hay_matriculas = False
    matriculas = Matricula.objects.filter(
        aprendiz=usuario,
        estado_formacion='En Formacion',
    ).only('grado_escolar', 'seccion')

    for matricula in matriculas:
        grado = ''.join(caracter for caracter in matricula.grado_escolar if caracter.isdigit())
        if not grado:
            continue
        seccion = Q(seccion__iexact=matricula.seccion) | Q(seccion__isnull=True) | Q(seccion='')
        cargas_por_matricula |= Q(grado__icontains=grado) & seccion
        hay_matriculas = True

    if not hay_matriculas:
        return CargaAcademica.objects.none()
    return CargaAcademica.objects.filter(cargas_por_matricula).distinct()


@login_required
@solo_instructor
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
@solo_instructor
def detalle_clase(request, carga_id):
    carga = get_object_or_404(CargaAcademica, id=carga_id)
    
    # Permitir al profesor de la carga o al personal directivo/superusuario
    if request.user != carga.profesor and not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, "No tienes permiso para ver esta clase.")
        return redirect('horarios_tablero')

    # Procesar registro de asistencia docente
    if request.method == 'POST' and request.POST.get('action') == 'guardar_asistencia':
        fecha_str = request.POST.get('fecha')
        from django.utils import timezone
        import datetime
        from seguimiento.models import AsistenciaAprendiz
        
        fecha = timezone.localdate()
        if fecha_str:
            try:
                fecha = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except Exception:
                pass
                
        for key, val in request.POST.items():
            if key.startswith('asistencia_'):
                mat_id = key.replace('asistencia_', '')
                try:
                    mat_obj = Matricula.objects.get(id=mat_id)
                    AsistenciaAprendiz.objects.update_or_create(
                        matricula=mat_obj,
                        fecha=fecha,
                        defaults={
                            'estado': val,
                            'observaciones': request.POST.get(f'obs_{mat_id}', ''),
                            'registrado_por': request.user,
                            'carga_academica': carga
                        }
                    )
                except Exception:
                    pass
        messages.success(request, "Asistencia registrada correctamente.")
        return redirect(f'/academico/clase/{carga.id}/?tab=asistencia')

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
    
    # Matriculas de estudiantes en formación para el grado y sección de la carga (grados 1° a 11°)
    grado_num = ''.join(filter(str.isdigit, str(carga.grado)))
    matriculas = Matricula.objects.filter(estado_formacion='En Formacion')
    if grado_num:
        matriculas = matriculas.filter(Q(grado_escolar=grado_num) | Q(grado_escolar__icontains=grado_num))
    if carga.seccion:
        matriculas = matriculas.filter(seccion__iexact=carga.seccion)
    
    context['matriculas'] = matriculas
    
    return render(request, 'academico/detalle_clase.html', context)

@login_required
@solo_instructor
def crear_tarea(request, carga_id):
    carga = get_object_or_404(CargaAcademica, id=carga_id)
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        instrucciones = request.POST.get('instrucciones') or request.POST.get('descripcion')
        fecha_limite = request.POST.get('fecha_limite') or request.POST.get('fecha_entrega')
        
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
@solo_instructor
def detalle_tarea_docente(request, tarea_id):
    tarea = get_object_or_404(TareaClase, id=tarea_id)
    entregas = tarea.entregas.all()
    return render(request, 'academico/detalle_tarea_docente.html', {
        'tarea': tarea,
        'entregas': entregas
    })

@login_required
@solo_instructor
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
                mat_obj = Matricula.objects.filter(aprendiz=entrega.estudiante).first()
                if mat_obj:
                    CalificacionEscolar.objects.update_or_create(
                        matricula=mat_obj,
                        carga_academica=entrega.tarea.carga_academica,
                        periodo=entrega.tarea.periodo or 'Periodo 1',
                        defaults={
                            'nota': float(str(calificacion).replace(',', '.')),
                            'profesor': request.user,
                            'observaciones': retroalimentacion
                        }
                    )
            except Exception as e:
                pass

            messages.success(request, 'Calificación guardada correctamente.')
            if request.POST.get('guardar_continuar'):
                siguiente = EntregaTarea.objects.filter(tarea=entrega.tarea, estado__in=['PENDIENTE', 'ENTREGADA', 'ENTREGADA_TARDE']).exclude(id=entrega.id).first()
                if not siguiente:
                    cargas_doc = CargaAcademica.objects.filter(profesor=request.user)
                    siguiente = EntregaTarea.objects.filter(tarea__carga_academica__in=cargas_doc, estado__in=['PENDIENTE', 'ENTREGADA', 'ENTREGADA_TARDE']).exclude(id=entrega.id).first()
                if siguiente:
                    return redirect('revision_entrega', entrega_id=siguiente.id)
                else:
                    messages.info(request, '¡Has calificado todas las actividades y entregas pendientes!')
            return redirect('panel_calificaciones')

    return render(request, 'academico/revision_entrega.html', {'entrega': entrega})

@login_required
@solo_instructor
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
@solo_instructor
def mis_actividades_docente(request):
    cargas = CargaAcademica.objects.filter(profesor=request.user)
    tareas_qs = TareaClase.objects.filter(
        Q(carga_academica__in=cargas) | Q(tema__profesor=request.user)
    ).exclude(estado='Papelera').distinct().select_related(
        'carga_academica', 'carga_academica__programa', 'tema'
    ).annotate(
        total_entregas=Count('entregas', distinct=True),
        pendientes=Count('entregas', filter=Q(entregas__estado__in=['ENTREGADA', 'ENTREGADA_TARDE']), distinct=True)
    ).order_by('-fecha_publicacion', '-id')

    total_actividades = tareas_qs.count()
    page_number = request.GET.get('page', 1)
    paginator = Paginator(tareas_qs, 6)
    page_obj = paginator.get_page(page_number)

    return render(request, 'academico/mis_actividades_docente.html', {
        'tareas': page_obj,
        'page_obj': page_obj,
        'total_actividades': total_actividades,
        'subpanel_activo': 'mis_actividades',
    })

@login_required
@solo_instructor
def crear_actividad_digital(request):
    guias = GuiaClase.objects.filter(Q(carga_academica__profesor=request.user) | Q(profesor=request.user)).distinct()
    if not guias.exists() and request.user.is_superuser:
        guias = GuiaClase.objects.all().distinct()
        
    cargas = CargaAcademica.objects.filter(profesor=request.user).select_related('programa').order_by('grado', 'programa__denominacion')
    if not cargas.exists() and request.user.is_superuser:
        cargas = CargaAcademica.objects.all().select_related('programa').order_by('grado', 'programa__denominacion')

    grados_cargas = sorted(list(set(''.join(ch for ch in str(c.grado) if ch.isdigit()) for c in cargas if c.grado)), key=lambda x: int(x) if x.isdigit() else 0)

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

            # Notificar y crear entregas pendientes para los estudiantes del grado y curso correspondiente
            from seguimiento.models import Notificacion
            from django.urls import reverse
            from usuarios.models import FamiliaAcudiente
            
            g_num = ''.join(ch for ch in str(c_obj.grado) if ch.isdigit()) or str(c_obj.grado).strip()
            sec_val = str(c_obj.seccion or '').strip()

            if destinatario_tipo == 'individual' and estudiante_id:
                target_users = list(User.objects.filter(id=estudiante_id))
            else:
                mats = [
                    m for m in matriculas_qs 
                    if str(m.grado_escolar).strip() == g_num 
                    and (not sec_val or not m.seccion or str(m.seccion).strip().upper() == sec_val.upper())
                ]
                if not mats:
                    mats = [m for m in matriculas_qs if str(m.grado_escolar).strip() == g_num]
                target_users = [m.aprendiz for m in mats if m.aprendiz]

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

            # Notificar también a los acudientes de los estudiantes vinculados
            try:
                for u in target_users:
                    doc_u = getattr(getattr(u, 'perfil', None), 'numero_documento', None) or u.username
                    familias = FamiliaAcudiente.objects.filter(
                        Q(estudiantes=u) | Q(documento=doc_u) | Q(email__iexact=u.email)
                    ).distinct()
                    for fam in familias:
                        fam_user = User.objects.filter(Q(username=fam.documento) | Q(email__iexact=fam.email)).first()
                        if fam_user:
                            Notificacion.objects.create(
                                usuario=fam_user,
                                titulo=f"Nueva Actividad Asignada: {tarea.titulo}",
                                mensaje=f"Se ha asignado la actividad '{tarea.titulo}' a tu acudido(a) {u.get_full_name() or u.username} en {c_obj.programa.denominacion if c_obj.programa else 'Clase'}.",
                                enlace=reverse('entregar_tarea_clase', kwargs={'pk': tarea.id}),
                                tipo='info'
                            )
            except Exception:
                pass

            messages.success(request, f'¡Actividad "{tarea.titulo}" publicada y enviada a los estudiantes con éxito!')
            return redirect(f"{reverse('actividades_tareas')}?tarea_id={tarea.id}")
        else:
            messages.error(request, 'No se pudo asociar la actividad a ninguna carga académica docente.')

    return render(request, 'academico/crear_actividad_digital.html', {
        'guias': guias,
        'cargas': cargas,
        'grados_cargas': grados_cargas,
        'resultados': resultados,
        'estudiantes': matriculas_qs,
    })

@login_required
def comunicaciones(request):
    from .models import ComunicacionMensaje
    perfil = getattr(request.user, 'perfil', None)
    rol_nombre = perfil.rol.nombre if perfil and perfil.rol else ''
    es_aprendiz = 'ESTUDIANTE' in _obtener_categorias_rol(rol_nombre)

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
        mensajes_del_usuario = ComunicacionMensaje.objects.filter(
            Q(remitente=request.user) | Q(destinatario=request.user)
        )
        
        if action == 'eliminar':
            msg_id = request.POST.get('msg_id')
            msg = get_object_or_404(mensajes_del_usuario, id=msg_id)
            if msg.remitente == request.user:
                msg.eliminado_por_remitente = True
            if msg.destinatario == request.user:
                msg.eliminado_por_destinatario = True
            msg.save()
            try:
                from usuarios.papelera_service import PapeleraService
                PapeleraService.enviar_a_papelera(
                    msg,
                    usuario=request.user,
                    motivo='Eliminado desde Mensajería Directa',
                    modulo_origen='Mensajería Directa'
                )
            except Exception:
                pass
            messages.success(request, 'Mensaje movido a la papelera de reciclaje.')
            next_url = request.POST.get('next_url') or 'comunicaciones'
            return redirect(next_url)
            
        elif action == 'restaurar':
            msg_id = request.POST.get('msg_id')
            msg = get_object_or_404(mensajes_del_usuario, id=msg_id)
            if msg.remitente == request.user:
                msg.eliminado_por_remitente = False
            if msg.destinatario == request.user:
                msg.eliminado_por_destinatario = False
            msg.save()
            try:
                from usuarios.models import PapeleraReciclaje
                PapeleraReciclaje.objects.filter(tipo_objeto='Mensaje', objeto_id=msg.id).update(restaurado=True)
            except Exception:
                pass
            messages.success(request, 'Mensaje restaurado exitosamente.')
            next_url = request.POST.get('next_url') or 'comunicaciones'
            return redirect(next_url)
            
        elif action == 'eliminar_definitivo':
            msg_id = request.POST.get('msg_id')
            msg = get_object_or_404(mensajes_del_usuario, id=msg_id)
            if msg.remitente == request.user or msg.destinatario == request.user:
                try:
                    from usuarios.models import PapeleraReciclaje
                    PapeleraReciclaje.objects.filter(tipo_objeto='Mensaje', objeto_id=msg.id).delete()
                except Exception:
                    pass
                msg.delete()
                messages.success(request, 'Mensaje eliminado definitivamente de la base de datos.')
            next_url = request.POST.get('next_url') or 'comunicaciones'
            return redirect(next_url)

        # Enviar mensaje directo a uno o múltiples destinatarios
        enviar_a_todos = request.POST.get('enviar_a_todos', '').strip() in ['1', 'true', 'True'] or request.POST.get('destinatarios_ids_csv', '').strip() == 'TODOS'
        dest_single = request.POST.get('destinatario_id', '').strip()
        dest_ids_raw = request.POST.getlist('destinatarios_ids')
        csv_ids = request.POST.get('destinatarios_ids_csv', '').strip()
        if csv_ids and csv_ids != 'TODOS':
            dest_ids_raw.extend([x.strip() for x in csv_ids.split(',') if x.strip()])
        if dest_single and dest_single != 'TODOS':
            dest_ids_raw.append(dest_single)

        grupo_destino = request.POST.get('grupo_destino', '').strip()
        roles_seleccionados = request.POST.getlist('roles_seleccionados')
        asunto = request.POST.get('asunto', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()

        next_url = request.POST.get('next_url', '').strip() or 'comunicaciones'

        if not asunto or not mensaje:
            messages.error(request, 'Por favor completa el asunto y el contenido del mensaje.')
            return redirect(next_url)

        destinatarios_finales = set()
        if enviar_a_todos:
            destinatarios_finales = set(User.objects.filter(is_active=True).exclude(pk=request.user.pk))
        else:
            ids_a_enviar = set()
            for r_id in dest_ids_raw:
                if str(r_id).isdigit():
                    ids_a_enviar.add(int(r_id))

            if ids_a_enviar:
                destinatarios_finales.update(User.objects.filter(is_active=True, id__in=ids_a_enviar).exclude(pk=request.user.pk))

            from usuarios.views import obtener_usuarios_destinatarios_autorizados
            for rol_cod in roles_seleccionados:
                destinatarios_finales.update(obtener_usuarios_destinatarios_autorizados(request.user, rol=rol_cod))

            if grupo_destino:
                destinatarios_finales.update(obtener_usuarios_destinatarios_autorizados(request.user, grado=grupo_destino))

        if not destinatarios_finales:
            messages.error(request, 'Debes seleccionar una persona del directorio institucional para enviarle el mensaje.')
            return redirect(next_url)

        from seguimiento.models import Notificacion

        mensaje_padre_id = request.POST.get('mensaje_padre_id', '').strip()
        padre_obj = None
        if mensaje_padre_id and mensaje_padre_id.isdigit():
            padre_obj = ComunicacionMensaje.objects.filter(pk=int(mensaje_padre_id)).first()

        total_enviados = 0
        ultimo_msg = None
        for dest_u in destinatarios_finales:
            msg = ComunicacionMensaje.objects.create(
                remitente=request.user,
                destinatario=dest_u,
                grupo_destino=grupo_destino or None,
                asunto=asunto,
                mensaje=mensaje,
                mensaje_padre=padre_obj
            )
            ultimo_msg = msg
            total_enviados += 1

            # Notificación institucional en tiempo real
            perfil_d = getattr(dest_u, 'perfil', None)
            rol_nom_d = perfil_d.rol.nombre if (perfil_d and perfil_d.rol) else ''
            if any(r in rol_nom_d for r in ['Docente', 'Instructor', 'Profesor']):
                enlace_dest = f"/instructor/?subpanel=comunicaciones&chat_user={request.user.id}&chat_tipo=estudiante"
            elif any(r in rol_nom_d for r in ['Estudiante', 'Aprendiz']):
                enlace_dest = "/estudiante/?subpanel=comunicaciones"
            elif 'Familia' in rol_nom_d:
                enlace_dest = "/familia/comunicaciones/"
            else:
                enlace_dest = "/comunicaciones/"

            Notificacion.objects.create(
                usuario=dest_u,
                titulo=f"Mensaje de {request.user.get_full_name() or request.user.username}: {asunto[:60]}",
                mensaje=f"{mensaje[:150]}",
                tipo='info',
                enlace=enlace_dest
            )
            total_enviados += 1

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1':
            return JsonResponse({
                'success': True,
                'total_enviados': total_enviados,
                'asunto': asunto,
                'mensaje': mensaje,
                'fecha': ultimo_msg.fecha_envio.strftime('%d/%m/%Y %I:%M %p') if ultimo_msg else '',
                'remitente_nombre': request.user.get_full_name() or request.user.username,
            })

        if total_enviados == 1:
            u_unico = list(destinatarios_finales)[0]
            messages.success(request, f'¡Mensaje directo enviado exitosamente a {u_unico.get_full_name() or u_unico.username}!')
        else:
            messages.success(request, f'¡Comunicado general enviado exitosamente a toda la plataforma ({total_enviados} usuarios)!')
        return redirect(next_url)

    # Directorio visible completo con TODOS los usuarios registrados activos (excepto el propio usuario)
    usuarios_todos = User.objects.filter(is_active=True).exclude(pk=request.user.pk).select_related('perfil', 'perfil__rol').order_by('perfil__rol__nombre', 'first_name', 'last_name', 'username')

    directorio_usuarios = []
    for u in usuarios_todos:
        p = getattr(u, 'perfil', None)
        r_nom = p.rol.nombre if (p and p.rol) else ('Administrador' if u.is_superuser else 'Usuario')
        r_lower = r_nom.lower()

        if 'rector' in r_lower:
            badge_style = 'background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA;'
            avatar_bg = '#DC2626'
            cat = 'directivos'
        elif 'admin' in r_lower:
            badge_style = 'background: #E0E7FF; color: #3730A3; border: 1px solid #C7D2FE;'
            avatar_bg = '#4F46E5'
            cat = 'admin'
        elif any(d in r_lower for d in ['docente', 'profesor', 'instructor']):
            badge_style = 'background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0;'
            avatar_bg = '#059669'
            cat = 'docentes'
        elif 'secretar' in r_lower:
            badge_style = 'background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A;'
            avatar_bg = '#D97706'
            cat = 'secretaria'
        elif any(e in r_lower for e in ['estudiante', 'aprendiz', 'alumno']):
            badge_style = 'background: #E0F2FE; color: #075985; border: 1px solid #BAE6FD;'
            avatar_bg = '#0284C7'
            cat = 'estudiantes'
        elif 'familia' in r_lower:
            badge_style = 'background: #F3E8FF; color: #6B21A8; border: 1px solid #E9D5FF;'
            avatar_bg = '#9333EA'
            cat = 'familias'
        else:
            badge_style = 'background: #F1F5F9; color: #475569; border: 1px solid #CBD5E1;'
            avatar_bg = '#64748B'
            cat = 'otros'

        full_name = u.get_full_name() or u.username
        parts = full_name.split()
        iniciales = (parts[0][0] + (parts[1][0] if len(parts) > 1 else ''))[:2].upper() if parts else u.username[:2].upper()

        m = u.matriculas_academicas.first() if hasattr(u, 'matriculas_academicas') else None
        grado_str = f"Grado {m.grado_escolar}°{m.seccion}" if (m and m.grado_escolar) else ""
        doc_str = p.numero_documento if (p and p.numero_documento) else ""

        directorio_usuarios.append({
            'id': u.id,
            'nombre': full_name,
            'username': u.username,
            'rol': r_nom,
            'categoria': cat,
            'badge_style': badge_style,
            'avatar_bg': avatar_bg,
            'iniciales': iniciales,
            'grado': grado_str,
            'documento': doc_str,
        })

    from usuarios.views import obtener_usuarios_destinatarios_autorizados
    usuarios_disponibles = obtener_usuarios_destinatarios_autorizados(request.user)

    roles_institucionales = [
        {'codigo': 'Docente', 'nombre': '👨‍🏫 Docentes e Instructores'},
        {'codigo': 'Estudiante', 'nombre': '🎒 Estudiantes y Aprendices'},
        {'codigo': 'Familia', 'nombre': '👨‍👩‍👧‍👦 Familias y Acudientes'},
        {'codigo': 'Admin', 'nombre': '🏛️ Directivos y Secretaría'},
    ]
    grados_catalogo = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']

    return render(request, 'academico/comunicaciones.html', {
        'recibidos': recibidos,
        'enviados': enviados,
        'papelera': papelera,
        'usuarios': usuarios_disponibles,
        'directorio_usuarios': directorio_usuarios,
        'total_directorio': len(directorio_usuarios),
        'destinatarios_muestra': directorio_usuarios[:60],
        'roles_institucionales': roles_institucionales,
        'grados_catalogo': grados_catalogo,
        'total_recibidos': recibidos.count(),
        'total_enviados': enviados.count(),
        'total_papelera': papelera.count(),
    })


@login_required
def api_conversacion_historial(request, otro_usuario_id):
    """
    Retorna el historial completo cronológico (antiguo a reciente) de la conversación
    entre el usuario autenticado y otro_usuario_id.
    """
    from django.contrib.auth.models import User
    from academico.models import ComunicacionMensaje
    from django.db.models import Q
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404

    otro_usuario = get_object_or_404(User, pk=otro_usuario_id)
    mensajes_qs = ComunicacionMensaje.objects.filter(
        (Q(remitente=request.user, destinatario=otro_usuario, eliminado_por_remitente=False) |
         Q(remitente=otro_usuario, destinatario=request.user, eliminado_por_destinatario=False))
    ).select_related('remitente', 'remitente__perfil', 'remitente__perfil__rol').order_by('fecha_envio')

    # Marcar como leídos los mensajes recibidos del otro usuario
    ComunicacionMensaje.objects.filter(
        remitente=otro_usuario,
        destinatario=request.user,
        leido=False
    ).update(leido=True)

    items = []
    for m in mensajes_qs:
        perf = getattr(m.remitente, 'perfil', None)
        rol_nom = perf.rol.nombre if (perf and perf.rol) else ('Administrador' if m.remitente.is_superuser else 'Usuario')
        items.append({
            'id': m.id,
            'es_mio': m.remitente_id == request.user.id,
            'remitente_id': m.remitente_id,
            'remitente_nombre': m.remitente.get_full_name() or m.remitente.username,
            'remitente_rol': rol_nom,
            'asunto': m.asunto,
            'mensaje': m.mensaje,
            'fecha': m.fecha_envio.strftime('%d/%m/%Y %I:%M %p'),
            'hora': m.fecha_envio.strftime('%I:%M %p'),
            'leido': m.leido,
        })

    perf_otro = getattr(otro_usuario, 'perfil', None)
    rol_otro = perf_otro.rol.nombre if (perf_otro and perf_otro.rol) else ('Administrador' if otro_usuario.is_superuser else 'Usuario')
    return JsonResponse({
        'success': True,
        'otro_usuario': {
            'id': otro_usuario.id,
            'nombre': otro_usuario.get_full_name() or otro_usuario.username,
            'rol': rol_otro,
            'username': otro_usuario.username,
        },
        'total': len(items),
        'mensajes': items
    })


@login_required
@solo_aprendiz
def actividades_estudiante(request):
    tareas = []
    tareas_qs = TareaClase.objects.filter(
        carga_academica__in=_cargas_para_aprendiz(request.user),
        estado='Publicada',
    ).select_related('carga_academica', 'carga_academica__programa').distinct()
    for tarea in tareas_qs:
        entrega = EntregaTarea.objects.filter(tarea=tarea, estudiante=request.user).first()
        tareas.append({'tarea': tarea, 'entrega': entrega})
    
    return render(request, 'academico/actividades_estudiante.html', {'tareas': tareas})

@login_required
@solo_aprendiz
def entregar_tarea(request, tarea_id):
    tarea = get_object_or_404(
        TareaClase.objects.filter(
            carga_academica__in=_cargas_para_aprendiz(request.user),
            estado='Publicada',
        ),
        id=tarea_id,
    )
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
