"""
Servicio Unificado de Papelera de Reciclaje Institucional - EDUNOVA
Permite el resguardo lógico (Soft Delete), consulta por rol, restauración
fidedigna y eliminación definitiva autorizada de cualquier elemento del sistema.
Compatible con los 6 roles actuales (Admin, Rectoría, Secretaría, Docente,
Estudiante, Familia) y cualquier rol futuro.
"""

import json
from datetime import datetime, date
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q
from usuarios.models import PapeleraReciclaje
try:
    from seguimiento.models import RegistroAuditoria
except ImportError:
    RegistroAuditoria = None


class PapeleraService:
    """Servicio central reutilizable para gestión de papelera y soft-delete."""

    @staticmethod
    def _serializar_valor(val):
        """Convierte valores de modelos a formatos serializables en JSON."""
        if val is None:
            return None
        if isinstance(val, (datetime, date)):
            return val.isoformat()
        if hasattr(val, 'pk'):
            return val.pk
        if hasattr(val, 'url'):
            return str(val)
        return str(val) if not isinstance(val, (int, float, bool, str, list, dict)) else val

    @classmethod
    def snapshot_objeto(cls, obj):
        """Genera un diccionario completo con los datos del objeto para su posterior recuperación."""
        datos = {}
        if not obj:
            return datos
        try:
            for field in obj._meta.fields:
                val = getattr(obj, field.name, None)
                datos[field.name] = cls._serializar_valor(val)
        except Exception:
            pass
        return datos

    @classmethod
    def clasificar_objeto(cls, obj):
        """Determina el tipo_objeto y nombres de presentación según el modelo del elemento."""
        nombre_modelo = obj.__class__.__name__
        tipo = 'Otro'
        modulo_defecto = 'Módulo General'
        titulo = str(obj)
        subtitulo = ''

        if nombre_modelo == 'User':
            perfil = getattr(obj, 'perfil', None)
            rol_nombre = perfil.rol.nombre if (perfil and perfil.rol) else ''
            if any(r in rol_nombre for r in ['Estudiante', 'Aprendiz', 'Alumno']):
                tipo = 'Estudiante'
                modulo_defecto = 'Gestión Escolar'
            elif any(r in rol_nombre for r in ['Docente', 'Profesor', 'Instructor']):
                tipo = 'Docente'
                modulo_defecto = 'Directorio Docente'
            else:
                tipo = 'Usuario'
                modulo_defecto = 'Administración de Usuarios'
            titulo = obj.get_full_name() or obj.username
            doc = getattr(perfil, 'numero_documento', '') or obj.username
            subtitulo = f"Documento: {doc} · Rol: {rol_nombre or 'Usuario'}"

        elif nombre_modelo in ['Matricula', 'MatriculaAcademica']:
            tipo = 'Matricula'
            modulo_defecto = 'Matrículas y Cupos'
            est = getattr(obj, 'aprendiz', None)
            nom_est = est.get_full_name() or est.username if est else 'Sin estudiante'
            titulo = f"Matrícula de {nom_est}"
            subtitulo = f"Grado {getattr(obj, 'grado_escolar', '')}°{getattr(obj, 'seccion', '')}"

        elif nombre_modelo == 'HorarioFicha':
            tipo = 'Horario'
            modulo_defecto = 'Horarios Escolares'
            materia = getattr(obj, 'nombre_materia', '') or (obj.programa.denominacion if getattr(obj, 'programa', None) else 'Clase')
            titulo = f"Clase: {materia}"
            subtitulo = f"Día {getattr(obj, 'dia', '')} · {getattr(obj, 'hora_inicio', '')} - {getattr(obj, 'hora_fin', '')}"

        elif nombre_modelo == 'TareaClase':
            tipo = 'TareaClase'
            modulo_defecto = 'Actividades y Tareas'
            titulo = getattr(obj, 'titulo', 'Actividad')
            subtitulo = f"Tipo: {getattr(obj, 'tipo_actividad', 'Tarea')} · Puntos: {getattr(obj, 'puntos_maximos', 5.0)}"

        elif nombre_modelo == 'EntregaTarea':
            tipo = 'EntregaTarea'
            modulo_defecto = 'Entregas de Actividades'
            est = getattr(obj, 'aprendiz', None)
            nom_est = est.get_full_name() if est else 'Estudiante'
            titulo = f"Entrega de {nom_est}"
            subtitulo = f"Tarea: {getattr(getattr(obj, 'tarea', None), 'titulo', 'Actividad')}"

        elif nombre_modelo == 'GuiaClase':
            tipo = 'GuiaClase'
            modulo_defecto = 'Gestión Documental y Guías'
            titulo = getattr(obj, 'titulo', 'Guía Pedagógica')
            subtitulo = f"Publicada: {getattr(obj, 'fecha_publicacion', '')}"

        elif nombre_modelo in ['MaterialClase', 'Documento']:
            tipo = 'Documento'
            modulo_defecto = 'Documentos Institucionales'
            titulo = getattr(obj, 'titulo', getattr(obj, 'nombre', 'Documento'))
            subtitulo = f"Tipo: {getattr(obj, 'tipo_documento', 'Archivo')}"

        elif nombre_modelo == 'ComunicadoEscolar':
            tipo = 'Comunicado'
            modulo_defecto = 'Canal Oficial de Circulares'
            titulo = getattr(obj, 'asunto', 'Circular Oficial')
            subtitulo = f"Destinatario: {getattr(obj, 'estamento_destinatario', 'General')}"

        elif nombre_modelo == 'ComunicacionMensaje':
            tipo = 'Mensaje'
            modulo_defecto = 'Mensajería Directa'
            titulo = f"Mensaje: {getattr(obj, 'asunto', 'Comunicación')}"
            rem = getattr(obj, 'remitente', None)
            dest = getattr(obj, 'destinatario', None)
            subtitulo = f"De: {rem.get_full_name() if rem else ''} → Para: {dest.get_full_name() if dest else 'Grupo'}"

        elif nombre_modelo == 'CalificacionEscolar':
            tipo = 'Calificacion'
            modulo_defecto = 'Registro de Calificaciones'
            mat = getattr(obj, 'matricula', None)
            nom_est = mat.aprendiz.get_full_name() if (mat and mat.aprendiz) else 'Estudiante'
            titulo = f"Calificación de {nom_est}"
            subtitulo = f"Nota: {getattr(obj, 'nota', 0.0)} · {getattr(obj, 'periodo', '')}"

        elif nombre_modelo in ['CargaAcademica', 'AsignacionAcademica']:
            tipo = 'CargaAcademica'
            modulo_defecto = 'Asignación Académica'
            prof = getattr(obj, 'profesor', None)
            nom_p = prof.get_full_name() if prof else 'Docente'
            titulo = f"Carga de {nom_p}"
            subtitulo = f"Grado {getattr(obj, 'grado', '')}°{getattr(obj, 'seccion', '')}"

        elif nombre_modelo in ['Ficha', 'FichaSena']:
            tipo = 'Ficha'
            modulo_defecto = 'Cursos y Fichas'
            titulo = f"Ficha {getattr(obj, 'codigo_ficha', getattr(obj, 'codigo', ''))}"
            subtitulo = f"Programa: {getattr(getattr(obj, 'programa', None), 'denominacion', '')}"

        elif nombre_modelo == 'TransporteRuta':
            tipo = 'Transporte'
            modulo_defecto = 'Rutas de Transporte'
            titulo = f"Ruta: {getattr(obj, 'nombre_ruta', 'Ruta')}"
            subtitulo = f"Conductor: {getattr(obj, 'conductor_nombre', '')}"

        elif nombre_modelo == 'BitacoraSeguimiento':
            tipo = 'Bitacora'
            modulo_defecto = 'Seguimiento y Convivencia'
            titulo = f"Bitácora #{obj.id}"
            subtitulo = getattr(obj, 'observaciones', '')[:80]

        return tipo, titulo[:200], subtitulo[:255], modulo_defecto

    @classmethod
    def enviar_a_papelera(cls, obj, usuario=None, motivo='', modulo_origen=''):
        """
        Envía un objeto a la papelera mediante Soft-Delete.
        Conserva su información, relaciones y genera el snapshot en PapeleraReciclaje.
        """
        if not obj:
            return None

        tipo, titulo, subtitulo, mod_auto = cls.clasificar_objeto(obj)
        mod_final = modulo_origen or mod_auto
        snapshot = cls.snapshot_objeto(obj)
        orig_id = getattr(obj, 'id', None) or getattr(obj, 'pk', 0) or 0

        # 1. Ejecutar soft delete según el tipo de elemento
        try:
            nombre_modelo = obj.__class__.__name__

            if nombre_modelo == 'User':
                obj.is_active = False
                obj.save(update_fields=['is_active'])
                if hasattr(obj, 'perfil') and obj.perfil:
                    obj.perfil.esta_activo = False
                    obj.perfil.save(update_fields=['esta_activo'])
                from academico.models import Matricula
                Matricula.objects.filter(aprendiz=obj).update(estado_formacion='Inactivo')

            elif nombre_modelo in ['Matricula', 'MatriculaAcademica']:
                obj.estado_formacion = 'Inactivo'
                obj.save(update_fields=['estado_formacion'])

            elif nombre_modelo == 'HorarioFicha':
                obj.activo = False
                obj.save(update_fields=['activo'])

            elif nombre_modelo == 'TareaClase':
                obj.estado = 'PAPELERA'
                obj.save(update_fields=['estado'])

            elif nombre_modelo == 'GuiaClase':
                obj.estado = 'PAPELERA'
                obj.save(update_fields=['estado'])

            elif nombre_modelo == 'ComunicacionMensaje':
                if usuario and usuario == obj.remitente:
                    obj.eliminado_por_remitente = True
                if usuario and usuario == obj.destinatario:
                    obj.eliminado_por_destinatario = True
                if not usuario:
                    obj.eliminado_por_remitente = True
                    obj.eliminado_por_destinatario = True
                obj.save()

            elif nombre_modelo == 'ComunicadoEscolar':
                # Si no tiene campo booleano de soft-delete, se borra el registro activo
                # pero queda su snapshot completo registrado en Papelera para reconstrucción exacta.
                obj.delete()

            elif nombre_modelo == 'CalificacionEscolar':
                obj.delete()

            elif nombre_modelo == 'TransporteRuta':
                obj.delete()

            elif nombre_modelo in ['CargaAcademica', 'AsignacionAcademica']:
                obj.delete()

            elif nombre_modelo in ['Ficha', 'FichaSena']:
                obj.estado = 'Cancelada'
                obj.save(update_fields=['estado'])

        except Exception:
            pass

        # 2. Registrar en la tabla central PapeleraReciclaje
        registro = PapeleraReciclaje.objects.create(
            tipo_objeto=tipo,
            objeto_id=orig_id,
            titulo=titulo,
            subtitulo=subtitulo,
            modulo_origen=mod_final,
            datos_recuperacion=snapshot,
            eliminado_por=usuario,
            motivo=motivo or f"Eliminado desde {mod_final}",
            restaurado=False
        )

        # 3. Trazabilidad de Auditoría
        if usuario:
            try:
                RegistroAuditoria.registrar(
                    usuario=usuario,
                    modulo='Papelera',
                    accion='Envío a Papelera de Reciclaje',
                    detalles=f"Se envió a la papelera '{titulo}' ({tipo}) desde {mod_final}."
                )
            except Exception:
                pass

        return registro

    @classmethod
    def obtener_items_para_usuario(cls, usuario, tipo_sel='Todos', q=''):
        """
        Devuelve el queryset de elementos en papelera filtrado estrictamente por rol y permisos.
        - Administrador: Visión global de toda la institución.
        - Rectoría / Secretaría: Supervisión y elementos institucionales.
        - Docente: Elementos propios o de sus asignaturas / tareas.
        - Estudiante: Únicamente elementos eliminados por él mismo.
        - Familia: Únicamente elementos eliminados por la cuenta familiar.
        - Rol futuro: Por defecto estricto solo sus propios elementos.
        """
        if not usuario or not usuario.is_authenticated:
            return PapeleraReciclaje.objects.none()

        perfil = getattr(usuario, 'perfil', None)
        rol_nombre = perfil.rol.nombre if (perfil and perfil.rol) else ''

        es_admin = usuario.is_superuser or any(r in rol_nombre for r in ['Admin', 'Administrador'])
        es_directivo = any(r in rol_nombre for r in ['Rector', 'Rectoría', 'Coordinador'])
        es_secretaria = any(r in rol_nombre for r in ['Secretar', 'Secretaría'])
        es_docente = any(r in rol_nombre for r in ['Docente', 'Profesor', 'Instructor'])
        es_estudiante = any(r in rol_nombre for r in ['Estudiante', 'Aprendiz', 'Alumno'])
        es_familia = any(r in rol_nombre for r in ['Familia', 'Acudiente', 'Padre', 'Madre'])

        items = PapeleraReciclaje.objects.filter(restaurado=False).select_related('eliminado_por')

        if es_admin or es_directivo or es_secretaria:
            # Vista institucional completa
            pass
        elif es_docente:
            # Docente ve lo que él eliminó o actividades/entregas de su labor
            items = items.filter(
                Q(eliminado_por=usuario) |
                Q(tipo_objeto__in=['TareaClase', 'EntregaTarea', 'GuiaClase', 'MaterialClase', 'Documento', 'Horario', 'Mensaje'])
            )
        elif es_estudiante:
            # Estudiante ve EXCLUSIVAMENTE lo que él eliminó
            items = items.filter(eliminado_por=usuario)
        elif es_familia:
            # Familia ve EXCLUSIVAMENTE lo que eliminó
            items = items.filter(eliminado_por=usuario)
        else:
            # Cualquier nuevo rol futuro: acceso seguro por defecto a sus propios registros
            items = items.filter(eliminado_por=usuario)

        # Filtro por tipo de elemento
        if tipo_sel and tipo_sel != 'Todos':
            items = items.filter(tipo_objeto=tipo_sel)

        # Búsqueda por término
        if q:
            items = items.filter(
                Q(titulo__icontains=q) |
                Q(subtitulo__icontains=q) |
                Q(modulo_origen__icontains=q) |
                Q(motivo__icontains=q)
            )

        return items.order_by('-fecha_eliminacion')

    @classmethod
    def puede_restaurar(cls, elem, usuario):
        """Verifica si el usuario tiene autorización para restaurar el elemento."""
        if not usuario or not usuario.is_authenticated or not elem:
            return False

        if usuario.is_superuser:
            return True

        perfil = getattr(usuario, 'perfil', None)
        rol_nombre = perfil.rol.nombre if (perfil and perfil.rol) else ''

        if any(r in rol_nombre for r in ['Admin', 'Administrador', 'Rector', 'Rectoría', 'Coordinador', 'Secretar']):
            return True

        # El creador / eliminador siempre puede restaurar sus propios elementos
        if elem.eliminado_por_id == usuario.id:
            return True

        # Docentes pueden restaurar recursos pedagógicos o actividades de su área
        if any(r in rol_nombre for r in ['Docente', 'Profesor', 'Instructor']):
            if elem.tipo_objeto in ['TareaClase', 'EntregaTarea', 'GuiaClase', 'MaterialClase', 'Horario', 'Mensaje']:
                return True

        return False

    @classmethod
    def puede_eliminar_definitivo(cls, elem, usuario):
        """
        Verifica autorización para borrado permanente.
        Protege especialmente expedientes de estudiantes, calificaciones y directivas.
        """
        if not usuario or not usuario.is_authenticated or not elem:
            return False

        if usuario.is_superuser:
            return True

        perfil = getattr(usuario, 'perfil', None)
        rol_nombre = perfil.rol.nombre if (perfil and perfil.rol) else ''

        if any(r in rol_nombre for r in ['Admin', 'Administrador']):
            return True

        if any(r in rol_nombre for r in ['Rector', 'Rectoría']):
            return True

        # Elementos institucionales sensibles (Estudiantes, Calificaciones, Matrículas)
        # solo pueden ser borrados definitivamente por Administrador o Rectoría
        if elem.tipo_objeto in ['Estudiante', 'Usuario', 'Docente', 'Matricula', 'Calificacion', 'CargaAcademica', 'Ficha']:
            return False

        # Secretaría puede eliminar borradores o registros administrativos que ella eliminó
        if any(r in rol_nombre for r in ['Secretar']) and elem.eliminado_por_id == usuario.id:
            return True

        # Docentes, estudiantes y familias solo pueden depurar permanentemente
        # elementos propios que ellos hayan enviado a la papelera (p. ej. mensajes, borradores)
        if elem.eliminado_por_id == usuario.id and elem.tipo_objeto in ['Mensaje', 'TareaClase', 'GuiaClase', 'Documento']:
            return True

        return False

    @classmethod
    def restaurar_elemento(cls, elem, usuario=None):
        """
        Restaura el elemento a su módulo y ubicación original con sus relaciones.
        Evita registros duplicados y deja constancia en auditoría.
        """
        if not elem:
            return False, "Elemento no encontrado."

        if usuario and not cls.puede_restaurar(elem, usuario):
            return False, "No tienes autorización para restaurar este elemento."

        datos = elem.datos_recuperacion or {}
        tipo = elem.tipo_objeto
        obj_id = elem.objeto_id

        try:
            if tipo in ['Estudiante', 'Docente', 'Usuario']:
                user_obj = User.objects.filter(pk=obj_id).first()
                if user_obj:
                    user_obj.is_active = True
                    user_obj.save(update_fields=['is_active'])
                    if hasattr(user_obj, 'perfil') and user_obj.perfil:
                        user_obj.perfil.esta_activo = True
                        user_obj.perfil.save(update_fields=['esta_activo'])
                    from academico.models import Matricula
                    Matricula.objects.filter(aprendiz=user_obj).update(estado_formacion='En Formacion')

            elif tipo == 'Matricula':
                from academico.models import Matricula
                Matricula.objects.filter(pk=obj_id).update(estado_formacion='En Formacion')

            elif tipo == 'Horario':
                from academico.models import HorarioFicha
                HorarioFicha.objects.filter(pk=obj_id).update(activo=True)

            elif tipo == 'TareaClase':
                from academico.models import TareaClase
                tarea = TareaClase.objects.filter(pk=obj_id).first()
                if tarea:
                    tarea.estado = 'Publicada'
                    tarea.save(update_fields=['estado'])
                elif datos and datos.get('carga_academica'):
                    TareaClase.objects.get_or_create(
                        id=obj_id,
                        defaults={
                            'carga_academica_id': datos.get('carga_academica'),
                            'titulo': datos.get('titulo', elem.titulo),
                            'instrucciones': datos.get('instrucciones', ''),
                            'tipo_actividad': datos.get('tipo_actividad', 'Tarea'),
                            'estado': 'Publicada'
                        }
                    )

            elif tipo == 'EntregaTarea':
                from academico.models import EntregaTarea
                EntregaTarea.objects.filter(pk=obj_id).update(estado='ENTREGADA')

            elif tipo == 'GuiaClase':
                from academico.models import GuiaClase
                guia = GuiaClase.objects.filter(pk=obj_id).first()
                if guia:
                    guia.estado = 'PUBLICADA'
                    guia.save(update_fields=['estado'])
                elif datos and datos.get('titulo'):
                    GuiaClase.objects.get_or_create(
                        id=obj_id,
                        defaults={
                            'titulo': datos.get('titulo'),
                            'instrucciones': datos.get('instrucciones', ''),
                            'estado': 'PUBLICADA'
                        }
                    )

            elif tipo == 'Comunicado':
                from seguimiento.models import ComunicadoEscolar
                com = ComunicadoEscolar.objects.filter(pk=obj_id).first()
                if not com and datos:
                    ComunicadoEscolar.objects.get_or_create(
                        id=obj_id,
                        defaults={
                            'asunto': datos.get('asunto', elem.titulo),
                            'mensaje': datos.get('mensaje', ''),
                            'estamento_destinatario': datos.get('estamento_destinatario', 'Toda'),
                            'remitente_id': datos.get('remitente') or (usuario.id if usuario else 1),
                            'curso_id': datos.get('curso'),
                            'estudiante_destinatario_id': datos.get('estudiante_destinatario'),
                            'urgente': bool(datos.get('urgente')),
                        }
                    )

            elif tipo == 'Mensaje':
                from academico.models import ComunicacionMensaje
                msg = ComunicacionMensaje.objects.filter(pk=obj_id).first()
                if msg:
                    msg.eliminado_por_remitente = False
                    msg.eliminado_por_destinatario = False
                    msg.save(update_fields=['eliminado_por_remitente', 'eliminado_por_destinatario'])
                elif datos:
                    ComunicacionMensaje.objects.get_or_create(
                        id=obj_id,
                        defaults={
                            'remitente_id': datos.get('remitente'),
                            'destinatario_id': datos.get('destinatario'),
                            'asunto': datos.get('asunto', elem.titulo),
                            'mensaje': datos.get('mensaje', ''),
                            'eliminado_por_remitente': False,
                            'eliminado_por_destinatario': False,
                        }
                    )

            elif tipo == 'Calificacion':
                from academico.models import CalificacionEscolar
                cal = CalificacionEscolar.objects.filter(pk=obj_id).first()
                if not cal and datos and datos.get('matricula'):
                    CalificacionEscolar.objects.get_or_create(
                        id=obj_id,
                        defaults={
                            'matricula_id': datos.get('matricula'),
                            'carga_academica_id': datos.get('carga_academica'),
                            'profesor_id': datos.get('profesor'),
                            'periodo': datos.get('periodo', 'Periodo 1'),
                            'nota': float(datos.get('nota', 0.0)),
                            'desempeno': datos.get('desempeno', 'Básico'),
                            'observaciones': datos.get('observaciones', ''),
                        }
                    )

            elif tipo == 'CargaAcademica':
                from academico.models import CargaAcademica
                if datos:
                    CargaAcademica.objects.get_or_create(
                        profesor_id=datos.get('profesor'),
                        programa_id=datos.get('programa'),
                        grado=datos.get('grado'),
                        seccion=datos.get('seccion')
                    )

            elif tipo == 'Transporte':
                from usuarios.models import TransporteRuta
                if datos and datos.get('nombre_ruta'):
                    TransporteRuta.objects.get_or_create(
                        id=obj_id,
                        defaults={
                            'nombre_ruta': datos.get('nombre_ruta'),
                            'placa_vehiculo': datos.get('placa_vehiculo', ''),
                            'conductor_nombre': datos.get('conductor_nombre', ''),
                            'conductor_telefono': datos.get('conductor_telefono', ''),
                            'cupos_totales': int(datos.get('cupos_totales', 20)),
                        }
                    )

            elif tipo == 'Ficha':
                from academico.models import FichaSena
                FichaSena.objects.filter(pk=obj_id).update(estado='En Ejecución')

            elif tipo == 'Bitacora':
                from seguimiento.models import BitacoraSeguimiento
                if datos and datos.get('ficha'):
                    BitacoraSeguimiento.objects.get_or_create(
                        id=obj_id,
                        defaults={'ficha_id': datos.get('ficha'), 'observaciones': datos.get('observaciones', '')}
                    )

            elem.restaurado = True
            elem.save(update_fields=['restaurado'])

            if usuario:
                try:
                    RegistroAuditoria.registrar(
                        usuario=usuario,
                        modulo='Papelera',
                        accion='Restauración de Elemento',
                        detalles=f"Restauró con éxito '{elem.titulo}' ({tipo}) al estado activo original."
                    )
                except Exception:
                    pass

            return True, f"¡El elemento '{elem.titulo}' ha sido restaurado exitosamente a su módulo original!"

        except Exception as e:
            return False, f"Error al restaurar '{elem.titulo}': {str(e)}"

    @classmethod
    def eliminar_definitivo(cls, elem, usuario=None):
        """
        Eliminación física definitiva e irreversible de la base de datos.
        Requiere autorización estricta según el rol.
        """
        if not elem:
            return False, "Elemento no encontrado."

        if usuario and not cls.puede_eliminar_definitivo(elem, usuario):
            return False, "No tienes autorización para eliminar definitivamente este elemento institucional."

        titulo = elem.titulo
        tipo = elem.tipo_objeto
        obj_id = elem.objeto_id

        try:
            if tipo in ['Estudiante', 'Docente', 'Usuario']:
                user_obj = User.objects.filter(pk=obj_id).first()
                if user_obj:
                    from academico.models import Matricula
                    Matricula.objects.filter(aprendiz=user_obj).delete()
                    user_obj.delete()

            elif tipo == 'Matricula':
                from academico.models import Matricula
                Matricula.objects.filter(pk=obj_id).delete()

            elif tipo == 'Horario':
                from academico.models import HorarioFicha
                HorarioFicha.objects.filter(pk=obj_id).delete()

            elif tipo == 'TareaClase':
                from academico.models import TareaClase
                TareaClase.objects.filter(pk=obj_id).delete()

            elif tipo == 'EntregaTarea':
                from academico.models import EntregaTarea
                EntregaTarea.objects.filter(pk=obj_id).delete()

            elif tipo == 'GuiaClase':
                from academico.models import GuiaClase
                GuiaClase.objects.filter(pk=obj_id).delete()

            elif tipo == 'Comunicado':
                from seguimiento.models import ComunicadoEscolar
                ComunicadoEscolar.objects.filter(pk=obj_id).delete()

            elif tipo == 'Mensaje':
                from academico.models import ComunicacionMensaje
                ComunicacionMensaje.objects.filter(pk=obj_id).delete()

            elif tipo == 'Calificacion':
                from academico.models import CalificacionEscolar
                CalificacionEscolar.objects.filter(pk=obj_id).delete()

            elif tipo == 'CargaAcademica':
                from academico.models import CargaAcademica
                CargaAcademica.objects.filter(pk=obj_id).delete()

            elif tipo == 'Transporte':
                from usuarios.models import TransporteRuta
                TransporteRuta.objects.filter(pk=obj_id).delete()

            elif tipo == 'Ficha':
                from academico.models import FichaSena
                FichaSena.objects.filter(pk=obj_id).delete()

            elif tipo == 'Bitacora':
                from seguimiento.models import BitacoraSeguimiento
                BitacoraSeguimiento.objects.filter(pk=obj_id).delete()

            elem.delete()

            if usuario:
                try:
                    RegistroAuditoria.registrar(
                        usuario=usuario,
                        modulo='Papelera',
                        accion='Eliminación Definitiva',
                        detalles=f"Depuración permanente de '{titulo}' ({tipo}) de la base de datos."
                    )
                except Exception:
                    pass

            return True, f"El registro '{titulo}' fue eliminado definitivamente de la base de datos."

        except Exception as e:
            return False, f"Error al eliminar definitivamente '{titulo}': {str(e)}"
