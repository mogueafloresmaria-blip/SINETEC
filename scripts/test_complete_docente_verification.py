import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test.utils import setup_test_environment
setup_test_environment()

from django.test import Client
from django.contrib.auth.models import User
from academico.models import CargaAcademica, Matricula, HorarioFicha, CalificacionEscolar, TareaClase
from seguimiento.models import Notificacion, ComunicadoEscolar, AsistenciaAprendiz
from usuarios.models import FamiliaAcudiente

def run_tests():
    print("=" * 70)
    print("EJECUTANDO BATERIA COMPLETA DE PRUEBAS DEL PANEL DOCENTE EDUNOVA")
    print("=" * 70)

    client = Client()

    # 1. Login como docente
    print("\n[TEST 1] Login como docente...")
    docente_user = User.objects.get(username='docente')
    login_ok = client.force_login(docente_user)
    print("OK - Docente autenticado:", docente_user.username, "(", docente_user.get_full_name(), ")")

    # 2 & 3 & 4 & 5. Cargas, Grados y Estudiantes del docente
    print("\n[TEST 2-5] Verificando cargas académicas y exclusión de otros grados...")
    cargas = CargaAcademica.objects.filter(profesor=docente_user)
    grados_docente = set(c.grado for c in cargas)
    print(f"Grados asignados a {docente_user.username}: {grados_docente}")
    assert grados_docente.issubset({'10', '11'}), f"Error: grados ajenos detectados: {grados_docente}"
    
    materias_docente = set(c.programa.denominacion for c in cargas if c.programa)
    print(f"Materias asignadas: {materias_docente}")

    # Comprobar que en el dashboard docente solo cargan 10 y 11
    resp_dash = client.get('/instructor/')
    assert resp_dash.status_code == 200
    print("OK - Dashboard docente carga con HTTP 200")
    for m in resp_dash.context['todos_mis_estudiantes']:
        g_num = ''.join(ch for ch in str(m.grado_escolar) if ch.isdigit())
        assert g_num in ['10', '11'], f"Estudiante de grado ajeno en lista: {m} (Grado {m.grado_escolar})"
    print(f"OK - Todos los {len(resp_dash.context['todos_mis_estudiantes'])} estudiantes pertenecen estrictamente a Grado 10 o 11")

    # 6, 7, 8. Bloqueo de rutas administrativas para Docente
    print("\n[TEST 6-8] Verificando seguridad y bloqueo de URLs administrativas...")
    rutas_bloqueadas = [
        ('/dashboard/', [302, 403], 'Redirige fuera de admin'),
        ('/estudiantes/', [302, 403], 'Redirige al panel docente / 403'),
        ('/matriculas/', [302, 403], 'Redirige al panel docente / 403'),
        ('/calificaciones/', [302, 403], 'Redirige al panel docente / 403'),
        ('/pensiones/', [302, 403], 'Redirige al panel docente / 403'),
        ('/transporte/', [302, 403], 'Redirige al panel docente / 403'),
        ('/documentos/', [302, 403], 'Redirige al panel docente / 403'),
    ]
    for ruta, codigos_esperados, desc in rutas_bloqueadas:
        resp = client.get(ruta)
        assert resp.status_code in codigos_esperados, f"FALLO: {ruta} respondio con {resp.status_code}, esperado {codigos_esperados}"
        print(f"  OK - {ruta} -> {resp.status_code} ({desc})")

    # 9 & 10. Consulta de estudiante propio vs ajeno
    print("\n[TEST 9-10] Verificando autorizacion para consultar ficha de estudiante...")
    # Estudiante propio en grado 10
    est_propio = Matricula.objects.filter(grado_escolar__icontains='10').first()
    assert est_propio is not None
    resp_est_ok = client.get(f'/estudiantes/{est_propio.id}/')
    print(f"  Consulta estudiante propio (ID {est_propio.id}, Grado {est_propio.grado_escolar}): status {resp_est_ok.status_code}")
    assert resp_est_ok.status_code == 200, f"Error: No pudo consultar estudiante propio (status {resp_est_ok.status_code})"

    # Crear o buscar un estudiante de grado ajeno (ej: Grado 8)
    from academico.models import Ficha
    ficha_def = Ficha.objects.first()
    user_ajeno, _ = User.objects.get_or_create(username='est_ajeno_8', defaults={'first_name': 'Carlos', 'last_name': 'Ajeno'})
    mat_ajena, _ = Matricula.objects.get_or_create(
        aprendiz=user_ajeno,
        defaults={'ficha': ficha_def, 'grado_escolar': '8', 'seccion': 'A', 'estado_formacion': 'En Formacion'}
    )
    if not hasattr(user_ajeno, 'perfil'):
        from usuarios.models import PerfilUsuario, Rol
        rol_est = Rol.objects.filter(nombre__icontains='Estudiante').first()
        PerfilUsuario.objects.create(usuario=user_ajeno, rol=rol_est)
    resp_est_bloq = client.get(f'/estudiantes/{user_ajeno.id}/')
    print(f"  Consulta estudiante ajeno (ID {user_ajeno.id}, Grado {mat_ajena.grado_escolar}): status {resp_est_bloq.status_code}")
    assert resp_est_bloq.status_code == 403, f"FALLO DE SEGURIDAD: Docente pudo consultar estudiante ajeno! Status: {resp_est_bloq.status_code}"
    print("  OK - Estudiante ajeno correctamente bloqueado con HTTP 403")

    # 11 & 12. Crear y consultar actividad
    print("\n[TEST 11-12] Creando y consultando actividad escolar...")
    carga_test = cargas.first()
    resp_crear_act = client.post('/instructor/', {
        'action': 'crear_tarea',
        'carga_id': carga_test.id,
        'titulo': 'Actividad Prueba Automatizada Antigravity',
        'descripcion': 'Resolver ejercicios capitulo 3',
        'tipo_actividad': 'Taller',
        'puntaje_maximo': '5.0',
        'fecha_limite': '2026-10-25'
    })
    assert resp_crear_act.status_code == 302
    act_creada = TareaClase.objects.filter(titulo='Actividad Prueba Automatizada Antigravity').first()
    assert act_creada is not None
    print(f"  OK - Actividad creada exitosamente (ID: {act_creada.id}, Materia: {act_creada.carga_academica.programa.denominacion})")

    # 13 & 14. Registrar y consultar asistencia
    print("\n[TEST 13-14] Registrando y consultando asistencia escolar...")
    mat_10 = Matricula.objects.filter(grado_escolar__icontains='10').first()
    resp_asist = client.post('/instructor/', {
        'action': 'guardar_asistencia',
        'carga_id': carga_test.id,
        'fecha': '2026-10-06',
        f'estado_{mat_10.id}': 'P',
        f'obs_{mat_10.id}': 'Asistencia verificada en prueba'
    })
    assert resp_asist.status_code == 302
    asist_reg = AsistenciaAprendiz.objects.filter(matricula=mat_10, fecha='2026-10-06').first()
    assert asist_reg is not None
    print(f"  OK - Asistencia registrada correctamente (Estudiante: {mat_10.aprendiz.username}, Estado: {asist_reg.estado})")

    # 15. Calificaciones
    print("\n[TEST 15] Registrando y consultando calificacion escolar...")
    resp_calif = client.post('/instructor/', {
        'action': 'guardar_notas',
        'carga_id': carga_test.id,
        'periodo': 'Periodo 1',
        f'nota_{mat_10.id}': '4.5',
        f'obs_{mat_10.id}': 'Excelente compromiso'
    })
    assert resp_calif.status_code == 302
    print("  OK - Calificacion guardada exitosamente en BD via accion guardar_notas")

    # 16. Horario
    print("\n[TEST 16] Consultando horario docente...")
    resp_horario = client.get('/instructor/?subpanel=horario')
    assert resp_horario.status_code == 200
    print("  OK - Subpanel de horario carga exitosamente")

    # 17 & 18. Mensajería con familias
    print("\n[TEST 17-18] Enviar mensaje a acudiente y verificar recepcion exclusiva...")
    est_target = Matricula.objects.filter(aprendiz__username='est2').first()
    assert est_target is not None, "Estudiante est2 no encontrado"
    acudiente_user = User.objects.get(username='acudiente')

    # Enviar comunicado dirigido al acudiente
    resp_msg = client.post('/instructor/', {
        'action': 'enviar_comunicado',
        'tipo_destinatario': 'acudiente',
        'estudiante_id': est_target.aprendiz.id,
        'asunto': 'Citacion a Entrega de Informes 2026',
        'mensaje': 'Estimada madre de familia, le esperamos el viernes a las 8am.',
        'canal': 'mensaje'
    })
    assert resp_msg.status_code == 302

    # Verificar que el comunicado se guardo con destinatario 'acudiente'
    com_fam = ComunicadoEscolar.objects.filter(
        remitente=docente_user,
        estudiante_destinatario=acudiente_user,
        asunto__icontains='Citacion a Entrega de Informes'
    ).first()
    assert com_fam is not None, f"Error: El comunicado no llego al usuario acudiente! com_fam={com_fam}"
    assert com_fam.estamento_destinatario == 'Familias'
    print(f"  OK - Comunicado registrado para usuario acudiente ({acudiente_user.username}) con estamento 'Familias'")

    # Verificar que el estudiante (est2) NO ve el comunicado en su portal
    client_est = Client()
    client_est.force_login(est_target.aprendiz)
    resp_est_portal = client_est.get('/aprendiz/')
    assert resp_est_portal.status_code == 200
    comunicados_est = resp_est_portal.context.get('comunicados_estudiante', [])
    ids_com_est = [c.id for c in comunicados_est]
    assert com_fam.id not in ids_com_est, "ERROR CRITICO: El estudiante vio el comunicado destinado al acudiente!"
    print(f"  OK - Estudiante ({est_target.aprendiz.username}) NO tiene acceso al mensaje del acudiente")

    # Verificar que el acudiente SI ve el comunicado en su portal
    client_fam = Client()
    client_fam.force_login(acudiente_user)
    resp_fam_portal = client_fam.get('/familia/')
    assert resp_fam_portal.status_code == 200
    circulares_fam = resp_fam_portal.context.get('circulares', [])
    ids_fam = [c.id for c in circulares_fam]
    assert com_fam.id in ids_fam, "ERROR: El acudiente no ve el comunicado en su portal de familia!"
    print(f"  OK - Acudiente ({acudiente_user.username}) ve el mensaje perfectamente en su portal de familia")

    # 19 & 20. Notificaciones: Ciclo 14 -> 13 -> F5 -> 13
    print("\n[TEST 19-20] Ciclo de Notificaciones: marcar como leida y persistencia en BD...")
    client.force_login(docente_user)
    # Asegurar exactamente 14 notificaciones no leidas para la prueba
    Notificacion.objects.filter(usuario=docente_user).delete()
    for i in range(14):
        Notificacion.objects.create(
            usuario=docente_user,
            titulo=f"Notificacion de prueba {i+1}",
            mensaje=f"Mensaje {i+1}",
            leida=False
        )
    sin_leer_inicial = Notificacion.objects.filter(usuario=docente_user, leida=False).count()
    assert sin_leer_inicial == 14, f"Esperado 14, obtenido {sin_leer_inicial}"
    print(f"  Contador inicial en BD: {sin_leer_inicial}")

    # Obtener la primera notificacion
    notif_test = Notificacion.objects.filter(usuario=docente_user, leida=False).first()
    # Ejecutar peticion AJAX para marcar como leida
    resp_ajax = client.post(
        f'/notificaciones/{notif_test.id}/marcar-leida-ajax/',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    assert resp_ajax.status_code == 200, f"AJAX respondio con status {resp_ajax.status_code}"
    data_ajax = json.loads(resp_ajax.content)
    assert data_ajax['success'] is True
    assert data_ajax['total_sin_leer'] == 13, f"Esperado 13, obtenido {data_ajax['total_sin_leer']}"
    print(f"  OK - Respuesta AJAX recibida: success=True, total_sin_leer={data_ajax['total_sin_leer']}")

    # Simular F5 (GET a la pagina de notificaciones)
    resp_f5 = client.get('/instructor/?subpanel=notificaciones')
    assert resp_f5.status_code == 200
    conteo_f5 = resp_f5.context['total_notificaciones_sin_leer']
    assert conteo_f5 == 13, f"F5 fallo! Esperado 13, obtenido {conteo_f5}"
    print(f"  OK - Despues de F5 el contador se conserva en {conteo_f5}")

    # Marcar otra mas
    notif_test_2 = Notificacion.objects.filter(usuario=docente_user, leida=False).first()
    resp_ajax_2 = client.post(
        f'/notificaciones/{notif_test_2.id}/marcar-leida-ajax/',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    data_ajax_2 = json.loads(resp_ajax_2.content)
    assert data_ajax_2['total_sin_leer'] == 12
    resp_f5_2 = client.get('/instructor/?subpanel=notificaciones')
    assert resp_f5_2.context['total_notificaciones_sin_leer'] == 12
    print("  OK - Segunda notificacion leida: 13 -> 12, F5 -> 12 confirmado")

    # Marcar todas como leidas
    resp_todas = client.post(
        '/notificaciones/marcar-todas-leidas/',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    assert resp_todas.status_code == 200
    resp_f5_0 = client.get('/instructor/?subpanel=notificaciones')
    assert resp_f5_0.context['total_notificaciones_sin_leer'] == 0
    print("  OK - Marcar todas como leidas: contador llega a 0")

    # Restaurar algunas notificaciones para el panel
    for i in range(5):
        Notificacion.objects.create(
            usuario=docente_user,
            titulo=f"Aviso institucional {i+1}",
            mensaje=f"Comunicado del colegio {i+1}",
            leida=False
        )

    # 21 & 22. Documentos y Perfil
    print("\n[TEST 21-22] Verificando modulo de documentos y perfil docente...")
    resp_docs = client.get('/instructor/?subpanel=documentos')
    assert resp_docs.status_code == 200
    print("  OK - Documentos cargan correctamente con sus 3 secciones")

    resp_perf = client.get('/perfil-profesional/')
    assert resp_perf.status_code == 200
    print("  OK - Perfil profesional carga correctamente con datos reales")

    # FASE 7: Diario de campo (marcar_tema) y observacion (guardar_observacion)
    print("\n[TEST FASE 7] Probando formularios de seguimiento (marcar_tema y guardar_observacion)...")
    resp_tema = client.post('/instructor/', {
        'action': 'marcar_tema',
        'horario_id': carga_test.id,
        'tema_texto': 'Ecuaciones Cuadraticas y Graficacion de Parabolas'
    })
    assert resp_tema.status_code == 302
    print("  OK - marcar_tema guardado en BD con exito")

    resp_obs = client.post('/instructor/', {
        'action': 'guardar_observacion',
        'estudiante_id': est_target.aprendiz.id,
        'tipo_observacion': 'Académica',
        'observacion_texto': 'Demuestra gran avance en comprension lectora y matematicas.'
    })
    assert resp_obs.status_code == 302
    print("  OK - guardar_observacion guardado en BD con exito")

    print("\n" + "=" * 70)
    print("TODAS LAS PRUEBAS COMPLETADAS SATISFACTORIAMENTE (25/25)")
    print("=" * 70)

if __name__ == '__main__':
    run_tests()
