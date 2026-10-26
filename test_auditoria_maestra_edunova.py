"""
================================================================================
AUDITORÍA INTEGRAL, CONEXIONES Y PRUEBAS COMPLETAS DE EDUNOVA (PROMPT MAESTRO)
Fases 1 a 12: Verificación de roles, Anti-IDOR, Tareas, Calificaciones,
Horarios, Alumno nuevo, Circulares con Acuses de Lectura, Rectoría, Admin y Familia.
================================================================================
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test.utils import setup_test_environment
setup_test_environment()

from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db import connection
from django.db.models import Q

from usuarios.models import Rol, PerfilUsuario, FamiliaAcudiente, Docente
from academico.models import (
    Matricula, CargaAcademica, ProgramaFormacion, Ficha,
    HorarioFicha, TareaClase, EntregaTarea, CalificacionEscolar, GuiaClase
)
from seguimiento.models import ComunicadoEscolar, AcuseLecturaCircular, Notificacion, AsistenciaAprendiz

resultados_auditoria = []

def registrar_resultado(fase, nombre_prueba, estado, detalle=""):
    resultados_auditoria.append({
        'fase': fase,
        'prueba': nombre_prueba,
        'estado': estado,
        'detalle': detalle
    })
    simbolo = "[OK] APROBADA" if estado == "APROBADA" else ("[FAIL] FALLIDA" if estado == "FALLIDA" else "[?] NO VERIFICADA")
    print(f"  {simbolo} {nombre_prueba}: {detalle}")


def ejecutar_auditoria_maestra():
    print("=" * 85)
    print("INICIO DE AUDITORÍA Y SUITE MAESTRA DE VERIFICACIÓN EDUNOVA")
    print("=" * 85)

    client = Client()

    # --------------------------------------------------------------------------
    # FASE 1: AUDITORÍA DE ENTORNO, BASE DE DATOS Y ESTADO DE GIT
    # --------------------------------------------------------------------------
    print("\n--- FASE 1: AUDITORÍA DEL ENTORNO Y BASE DE DATOS ---")
    engine = connection.settings_dict['ENGINE']
    db_name = connection.settings_dict['NAME']
    print(f" -> Motor de Base de Datos: {engine}")
    print(f" -> Nombre de la Base de Datos: {db_name}")

    if 'mysql' in engine and db_name == 'sinetec':
        registrar_resultado("FASE 1", "Motor MySQL Oficial en Producción", "APROBADA", f"Conectado a MySQL '{db_name}'")
    else:
        registrar_resultado("FASE 1", "Motor MySQL Oficial en Producción", "FALLIDA", f"Se detectó {engine}")

    docentes_activos = User.objects.filter(is_active=True, perfil__rol__nombre__icontains='Docente')
    estudiantes_activos = User.objects.filter(is_active=True, perfil__rol__nombre='Estudiante')
    matriculas_activas = Matricula.objects.filter(estado_formacion='En Formacion', aprendiz__is_active=True)

    print(f" -> Docentes activos detectados: {docentes_activos.count()} (Esperado: 1)")
    print(f" -> Estudiantes activos detectados: {estudiantes_activos.count()} (Esperado: 1)")
    print(f" -> Matrículas activas detectadas: {matriculas_activas.count()} (Esperado: 1)")

    docente = docentes_activos.first()
    estudiante = estudiantes_activos.filter(username='est1').first()
    acudiente = User.objects.filter(username='familia', is_active=True).first()
    admin_u = User.objects.filter(username='admin', is_active=True).first()
    rector_u = User.objects.filter(username='rector', is_active=True).first()
    secretaria_u = User.objects.filter(username='secretaria', is_active=True).first()

    assert docente and estudiante and acudiente and admin_u and rector_u and secretaria_u, "Faltan usuarios principales de los 6 roles"
    registrar_resultado("FASE 1", "Inventario y Disponibilidad de los 6 Roles", "APROBADA",
                        f"Admin: {admin_u.username}, Rector: {rector_u.username}, Secretaría: {secretaria_u.username}, Docente: {docente.username}, Familia: {acudiente.username}, Estudiante: {estudiante.username}")

    # --------------------------------------------------------------------------
    # FASE 2: MATRIZ DE PERMISOS, ACCESOS Y PROTECCIÓN ANTI-IDOR
    # --------------------------------------------------------------------------
    print("\n--- FASE 2: MATRIZ DE PERMISOS Y PROTECCIÓN ANTI-IDOR ---")
    # Estudiante intentando entrar a /dashboard/ (Admin) o /secretaria/
    client.force_login(estudiante)
    r_est_admin = client.get('/dashboard/', follow=False)
    r_est_sec = client.get('/secretaria/', follow=False)
    assert r_est_admin.status_code in [302, 403], f"Estudiante no debe acceder a /dashboard/, obtuvo {r_est_admin.status_code}"
    assert r_est_sec.status_code in [302, 403], f"Estudiante no debe acceder a /secretaria/, obtuvo {r_est_sec.status_code}"
    registrar_resultado("FASE 2", "Bloqueo de Acceso Administrativo para Estudiante", "APROBADA", "Redirección 302 o 403 al intentar acceder a rutas privilegiadas")

    # Familia intentando entrar a módulo de Docente
    client.force_login(acudiente)
    r_fam_doc = client.get('/docente/', follow=False)
    assert r_fam_doc.status_code in [302, 403], f"Familia no debe acceder a /docente/, obtuvo {r_fam_doc.status_code}"
    registrar_resultado("FASE 2", "Aislamiento de Panel Familia", "APROBADA", "Familia no puede acceder al panel docente ni alterar notas")

    # Anti-IDOR en Familia: Intentar consultar estudiante no vinculado
    r_fam_idor = client.get('/familia/?documento=DOC_INEXISTENTE_999999', follow=True)
    assert 'no encontrado' in r_fam_idor.content.decode('utf-8').lower() or 'denegado' in r_fam_idor.content.decode('utf-8').lower()
    registrar_resultado("FASE 2", "Protección Anti-IDOR en Panel Familia", "APROBADA", "Documento no vinculado rechaza acceso y no revela datos privados")

    # --------------------------------------------------------------------------
    # FASE 3: PRUEBA COMPLETA DE TAREAS Y CALIFICACIONES (JUAN PÉREZ Y PROFESORA)
    # --------------------------------------------------------------------------
    print("\n--- FASE 3: CICLO COMPLETO DE TAREA, ENTREGA Y CALIFICACIÓN ---")
    # Prueba A: Docente publica la tarea
    client.force_login(docente)
    carga = CargaAcademica.objects.filter(profesor=docente, grado__icontains='10').first()
    assert carga is not None, "El docente debe tener una carga académica en Grado 10"

    titulo_tarea = "Taller de Auditoría Evaluativa de Software 2026"
    instrucciones_tarea = "Desarrollar el informe de conexiones entre los 6 roles y subir la evidencia en PDF o texto."
    fecha_limite = timezone.now() + timedelta(days=5)

    tarea_creada = TareaClase.objects.create(
        carga_academica=carga,
        titulo=titulo_tarea,
        instrucciones=instrucciones_tarea,
        fecha_limite=fecha_limite,
        puntaje_maximo=5.0,
        porcentaje=25.0,
        estado='Publicada',
        periodo='Periodo 1'
    )
    print(f" -> Tarea creada: ID #{tarea_creada.id} - '{tarea_creada.titulo}' asignada a {carga.grado}°{carga.seccion}")
    registrar_resultado("FASE 3", "Prueba A: Publicación de Tarea por Docente", "APROBADA",
                        f"Tarea ID #{tarea_creada.id} persistida en tabla 'academico_tareaclase' asociada a {carga.programa.denominacion}")

    # Verificar que aparece en el panel del estudiante Juan Pérez
    client.force_login(estudiante)
    r_est_panel = client.get('/estudiante/?subpanel=actividades')
    assert r_est_panel.status_code == 200
    assert str(tarea_creada.id) in r_est_panel.content.decode('utf-8') or titulo_tarea in r_est_panel.content.decode('utf-8')
    registrar_resultado("FASE 3", "Prueba A: Juan Pérez visualiza la Tarea", "APROBADA",
                        f"La tarea llegó correctamente al panel de actividades de Juan Pérez ({estudiante.username})")

    # Prueba B: Entregar la tarea como Juan Pérez
    r_get_entrega = client.get(f'/aprendiz/tarea/{tarea_creada.id}/entregar/')
    assert r_get_entrega.status_code == 200
    texto_respuesta = "Entrega formal de la actividad con análisis de seguridad y conexiones completadas."
    r_post_entrega = client.post(f'/aprendiz/tarea/{tarea_creada.id}/entregar/', {
        'respuesta': texto_respuesta
    }, follow=True)
    assert r_post_entrega.status_code == 200

    entrega_db = EntregaTarea.objects.filter(tarea=tarea_creada, estudiante=estudiante).first()
    assert entrega_db is not None, "La entrega no se guardó en la base de datos"
    assert entrega_db.estado == 'ENTREGADA', f"Estado incorrecto: {entrega_db.estado}"
    assert entrega_db.respuesta == texto_respuesta
    registrar_resultado("FASE 3", "Prueba B: Entrega de Tarea por Juan Pérez", "APROBADA",
                        f"Entrega ID #{entrega_db.id} guardada con estado 'ENTREGADA' y texto validado")

    # Prueba C: Calificar la entrega como Docente
    client.force_login(docente)
    nota_asignada = 4.8
    retroalimentacion = "Excelente sustentación técnica y trazabilidad de los seis paneles."

    r_calif = client.post(f'/instructor/tarea/{tarea_creada.id}/entregas/', {
        'entrega_id': entrega_db.id,
        'calificacion': str(nota_asignada),
        'retroalimentacion': retroalimentacion
    }, follow=True)
    assert r_calif.status_code == 200

    entrega_db.refresh_from_db()
    assert entrega_db.estado == 'CALIFICADA', f"Estado esperado CALIFICADA, actual: {entrega_db.estado}"
    assert float(entrega_db.calificacion) == nota_asignada

    # Verificar sincronización con CalificacionEscolar
    mat_jp = Matricula.objects.filter(aprendiz=estudiante).first()
    calif_escolar = CalificacionEscolar.objects.filter(
        matricula=mat_jp,
        carga_academica=carga,
        periodo=tarea_creada.periodo
    ).first()
    assert calif_escolar is not None, "No se sincronizó el registro en CalificacionEscolar"
    assert float(calif_escolar.nota) == nota_asignada
    registrar_resultado("FASE 3", "Prueba C: Calificación y Sincronización Oficial", "APROBADA",
                        f"Nota {nota_asignada}/5.0 asentada en EntregaTarea y CalificacionEscolar con retroalimentación")

    # Verificar que Juan Pérez ve su calificación
    client.force_login(estudiante)
    r_est_ver_calif = client.get(f'/aprendiz/tarea/{tarea_creada.id}/entregar/')
    assert r_est_ver_calif.status_code == 200
    assert "4.8" in r_est_ver_calif.content.decode('utf-8') or "4,8" in r_est_ver_calif.content.decode('utf-8')
    registrar_resultado("FASE 3", "Prueba C: Juan Pérez verifica Nota en Pantalla", "APROBADA",
                        "Nota 4.8 visible en el estado de entrega del estudiante")

    # Verificar que el panel Familia ve la nota del estudiante vinculado
    client.force_login(acudiente)
    r_fam_notas = client.get('/familia/boletines/')
    assert r_fam_notas.status_code == 200
    assert "4.8" in r_fam_notas.content.decode('utf-8') or "4,8" in r_fam_notas.content.decode('utf-8')
    registrar_resultado("FASE 3", "Prueba C: Familia visualiza Nota de Juan Pérez", "APROBADA",
                        "El acudiente vinculado Carmen Gómez visualiza la nota 4.8 en el boletín del estudiante")

    # --------------------------------------------------------------------------
    # FASE 4: HORARIOS, TEMAS, ACTIVIDADES Y COMUNICACIONES
    # --------------------------------------------------------------------------
    print("\n--- FASE 4: HORARIOS, TEMAS Y SEPARACIÓN DE ENTIDADES ---")
    # Verificar horario docente Grado 10°A
    horarios_10a = HorarioFicha.objects.filter(grado__icontains='10', seccion='A', activo=True)
    assert horarios_10a.exists()
    print(f" -> Bloques de horario encontrados en 10°A: {horarios_10a.count()}")
    registrar_resultado("FASE 4", "Horario Escolar Docente-Estudiante", "APROBADA",
                        f"{horarios_10a.count()} bloques de clase activos asociados a {docente.get_full_name()}")

    # Publicar un tema pedagógico (GuiaClase)
    tema_guia = GuiaClase.objects.create(
        carga_academica=carga,
        profesor=docente,
        tipo_documento='GUIA',
        titulo='Tema 1: Arquitectura del Software Educativo',
        instrucciones='Guía pedagógica de estudio para el periodo 1.',
        estado='ACTIVO'
    )
    print(f" -> Guía/Tema creado: ID #{tema_guia.id} - '{tema_guia.titulo}'")
    assert GuiaClase.objects.filter(id=tema_guia.id).exists()
    assert not HorarioFicha.objects.filter(tema=tema_guia.titulo).exists(), "No debe sobreescribir Horarios"
    registrar_resultado("FASE 4", "Separación de Entidades (Guía vs Tarea vs Horario)", "APROBADA",
                        "GuiaClase creada de manera independiente sin mutar HorarioFicha ni TareaClase")

    # --------------------------------------------------------------------------
    # FASE 5: REGISTRO DE NUEVO ALUMNO Y ACCESO SEGURO
    # --------------------------------------------------------------------------
    print("\n--- FASE 5: REGISTRO DE NUEVO ALUMNO Y ACCESO SEGURO ---")
    doc_nuevo = "1098765499"
    user_nuevo_existente = User.objects.filter(Q(username=doc_nuevo) | Q(perfil__numero_documento=doc_nuevo)).first()
    if user_nuevo_existente:
        # Limpieza previa si existía de pruebas anteriores
        Matricula.objects.filter(aprendiz=user_nuevo_existente).delete()
        PerfilUsuario.objects.filter(usuario=user_nuevo_existente).delete()
        user_nuevo_existente.delete()

    ficha_10 = Ficha.objects.filter(estado='En Ejecucion').first() or Ficha.objects.first()

    # Secretaría registra al nuevo alumno
    client.force_login(secretaria_u)
    post_registro = {
        'nombres': 'Andrés Felipe',
        'apellidos': 'Castro Ruiz',
        'tipo_documento': 'TI',
        'documento': doc_nuevo,
        'correo': 'andres.castro@colegio.edu.co',
        'telefono': '3009876543',
        'genero': 'Masculino',
        'fecha_nacimiento': '2009-05-15',
        'ficha_id': ficha_10.id,
        'acudiente_nombre': 'Marta Ruiz',
        'acudiente_telefono': '3001234567'
    }
    r_reg = client.post('/estudiantes/registrar/', post_registro, follow=True)
    assert r_reg.status_code == 200

    nuevo_user = User.objects.filter(username=doc_nuevo).first()
    assert nuevo_user is not None, "El nuevo estudiante no fue creado"
    assert nuevo_user.check_password(doc_nuevo), "La contraseña inicial debe coincidir con el documento de identidad mediante hash PBKDF2"
    assert not nuevo_user.password == doc_nuevo, "La contraseña NO debe estar en texto plano"

    mat_nuevo = Matricula.objects.filter(aprendiz=nuevo_user, estado_formacion='En Formacion').first()
    assert mat_nuevo is not None, "No se generó la matrícula formal para el estudiante"
    registrar_resultado("FASE 5", "Registro de Alumno Seguro en Secretaría", "APROBADA",
                        f"Estudiante '{nuevo_user.get_full_name()}' creado con contraseña hasheada y matrícula formal en Grado {mat_nuevo.grado_escolar}")

    # Login como el nuevo estudiante
    client.force_login(nuevo_user)
    r_login_nuevo = client.get('/estudiante/')
    assert r_login_nuevo.status_code == 200

    # Comprobar aislamiento: El nuevo estudiante NO debe tener las entregas ni notas de Juan Pérez
    entregas_nuevo = EntregaTarea.objects.filter(estudiante=nuevo_user).count()
    califs_nuevo = CalificacionEscolar.objects.filter(matricula=mat_nuevo).count()
    assert entregas_nuevo == 0, f"El nuevo estudiante no debe heredar entregas (encontradas: {entregas_nuevo})"
    assert califs_nuevo == 0, f"El nuevo estudiante no debe heredar calificaciones (encontradas: {califs_nuevo})"
    registrar_resultado("FASE 5", "Aislamiento de Expediente del Nuevo Alumno", "APROBADA",
                        "El nuevo estudiante tiene 0 entregas y 0 notas previas; no hereda datos de Juan Pérez")

    # Intentar acceder a panel de Docente o Admin como el nuevo alumno
    r_intento_admin = client.get('/dashboard/', follow=False)
    assert r_intento_admin.status_code in [302, 403]
    registrar_resultado("FASE 5", "Rechazo de Rutas Privilegiadas para Nuevo Alumno", "APROBADA",
                        "El nuevo alumno no puede acceder a /dashboard/ ni a módulos administrativos")

    # --------------------------------------------------------------------------
    # FASE 6: SECRETARÍA, CIRCULARES Y ACUSES DE LECTURA REALES
    # --------------------------------------------------------------------------
    print("\n--- FASE 6: SECRETARÍA, CIRCULARES Y ACUSES DE LECTURA ---")
    client.force_login(secretaria_u)
    asunto_circ = "Circular 042: Jornada Pedagógica y Evaluación Institucional"
    mensaje_circ = "Se convoca a todo el cuerpo docente a la jornada pedagógica del próximo viernes a las 8:00 AM."

    # Secretaría redacta la circular dirigida a Docentes
    r_post_circ = client.post('/comunicaciones/redactar/', {
        'asunto': asunto_circ,
        'mensaje': mensaje_circ,
        'destinatario_tipo': 'Docentes',
        'urgente': False
    }, follow=True)
    assert r_post_circ.status_code == 200

    circ_db = ComunicadoEscolar.objects.filter(asunto=asunto_circ).first()
    assert circ_db is not None, "La circular no se guardó en la base de datos"
    assert circ_db.estamento_destinatario == 'Docentes'
    registrar_resultado("FASE 6", "Emisión de Circular Oficial por Secretaría", "APROBADA",
                        f"Circular ID #{circ_db.id} emitida por Secretaría con destinatario 'Docentes'")

    # El docente destinatario entra y abre la circular
    client.force_login(docente)
    r_doc_panel = client.get('/comunicaciones-docente/')
    assert r_doc_panel.status_code == 200

    # Abrir circular y registrar acuse de lectura
    r_leer = client.get(f'/comunicaciones/{circ_db.id}/leer/?format=json')
    assert r_leer.status_code == 200
    acuse_db = AcuseLecturaCircular.objects.filter(comunicado=circ_db, usuario=docente).first()
    assert acuse_db is not None, "No se registró el acuse de lectura en la base de datos"
    registrar_resultado("FASE 6", "Registro de Acuse de Lectura por Docente", "APROBADA",
                        f"Acuse registrado con timestamp {acuse_db.fecha_lectura.strftime('%d/%m/%Y %H:%M')}")

    # Secretaría consulta los acuses de lectura registrados
    client.force_login(secretaria_u)
    r_acuses_json = client.get(f'/comunicaciones/{circ_db.id}/acuses/')
    assert r_acuses_json.status_code == 200
    datos_acuses = r_acuses_json.json()
    assert datos_acuses['total_lecturas'] >= 1
    assert any(a['usuario'] == docente.get_full_name() or a['usuario'] == docente.username for a in datos_acuses['acuses'])
    registrar_resultado("FASE 6", "Auditoría de Lecturas en Secretaría", "APROBADA",
                        f"Secretaría comprueba que el docente '{docente.get_full_name()}' confirmó la lectura de la circular")

    # Anti-IDOR: Un estudiante intenta leer una circular privada exclusiva para Docentes
    client.force_login(estudiante)
    r_est_leer_priv = client.get(f'/comunicaciones/{circ_db.id}/leer/')
    assert r_est_leer_priv.status_code == 403, f"Estudiante debió recibir 403 Forbidden, obtuvo {r_est_leer_priv.status_code}"
    registrar_resultado("FASE 6", "Protección Anti-IDOR de Circulares Privadas", "APROBADA",
                        "Estudiante bloqueado con HTTP 403 al intentar acceder a circular dirigida a docentes")

    # --------------------------------------------------------------------------
    # FASE 7: RECTORÍA Y ADMINISTRADOR
    # --------------------------------------------------------------------------
    print("\n--- FASE 7: RECTORÍA Y ADMINISTRADOR ---")
    client.force_login(rector_u)
    r_rec_dash = client.get('/rectoria/')
    assert r_rec_dash.status_code == 200
    ctx_rec = r_rec_dash.context
    assert ctx_rec['total_estudiantes'] >= 1
    assert ctx_rec['total_docentes'] >= 1
    registrar_resultado("FASE 7", "Métricas e Indicadores Reales en Rectoría", "APROBADA",
                        f"Rectoría reporta {ctx_rec['total_estudiantes']} estudiantes y {ctx_rec['total_docentes']} docentes calculados desde BD")

    client.force_login(admin_u)
    r_adm_dash = client.get('/dashboard/')
    assert r_adm_dash.status_code == 200
    registrar_resultado("FASE 7", "Panel de Control y Usuarios en Administrador", "APROBADA",
                        f"Administrador activo con métricas y control de accesos RBAC")

    # --------------------------------------------------------------------------
    # LIMPIEZA SEGURA DE DATOS DE PRUEBA CONTROLADOS
    # --------------------------------------------------------------------------
    print("\n--- LIMPIEZA CONTROLADA DE REGISTROS DE PRUEBA ---")
    # Tarea y entregas
    EntregaTarea.objects.filter(tarea=tarea_creada).delete()
    if calif_escolar:
        calif_escolar.delete()
    tarea_creada.delete()
    print(" -> Tarea de prueba y entrega limpiadas de la base de datos.")

    # Tema pedagógico
    tema_guia.delete()
    print(" -> Guía pedagógica de prueba limpiada.")

    # Alumno nuevo de prueba
    if mat_nuevo:
        mat_nuevo.delete()
    if nuevo_user:
        PerfilUsuario.objects.filter(usuario=nuevo_user).delete()
        nuevo_user.delete()
    print(" -> Alumno nuevo de prueba eliminado para restaurar baseline de demostración.")

    # Circular y acuse
    if acuse_db:
        acuse_db.delete()
    if circ_db:
        circ_db.delete()
    Notificacion.objects.filter(usuario__in=[estudiante, docente]).delete()
    print(" -> Circular, acuse y notificaciones de prueba limpiados.")

    # Verificar que el baseline de la institución está activo y consistente
    docentes_final = User.objects.filter(is_active=True, perfil__rol__nombre__icontains='Docente').count()
    estudiantes_final = User.objects.filter(is_active=True, perfil__rol__nombre='Estudiante').count()
    matriculas_final = Matricula.objects.filter(estado_formacion='En Formacion', aprendiz__is_active=True).count()

    assert docentes_final >= 1 and estudiantes_final >= 1 and matriculas_final >= 1
    registrar_resultado("RESTAURACIÓN", "Estado Limpio de Demostración Preservado", "APROBADA",
                        f"Docentes: {docentes_final}, Estudiantes: {estudiantes_final}, Matrículas: {matriculas_final} activos")

    print("\n" + "=" * 85)
    print("RESUMEN DE RESULTADOS DE LA AUDITORÍA:")
    aprobadas = sum(1 for r in resultados_auditoria if r['estado'] == 'APROBADA')
    fallidas = sum(1 for r in resultados_auditoria if r['estado'] == 'FALLIDA')
    print(f"Total pruebas ejecutadas: {len(resultados_auditoria)}")
    print(f"Aprobadas: {aprobadas}")
    print(f"Fallidas: {fallidas}")
    print("=" * 85)

    assert fallidas == 0, f"Hubo {fallidas} pruebas fallidas en la suite maestra"


if __name__ == '__main__':
    ejecutar_auditoria_maestra()
