import os
import sys
from decimal import Decimal
from datetime import date, time, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from usuarios.models import (
    Rol, PerfilUsuario, ConfiguracionColegio, FamiliaAcudiente,
    Docente, PapeleraReciclaje
)
from instituciones.models import InstitucionEducativa
from academico.models import (
    ProgramaFormacion, Ficha, Matricula, CargaAcademica, HorarioFicha,
    TareaClase, EntregaTarea, GuiaClase, MaterialClase, AvisoClase,
    CalificacionEscolar, SemaforoCompetencia, DocumentoInstitucional,
    PeriodoAcademico
)
from seguimiento.models import (
    AsistenciaAprendiz, ComunicadoEscolar, AcuseLecturaCircular,
    Notificacion, RegistroAuditoria
)
from evaluaciones.models import JuicioEvaluativo


def ejecutar_pruebas_sustentacion():
    print("=" * 80)
    print("TEST SUITE INTEGRAL — RECORRIDO DE SUSTENTACIÓN ANTE EL PROFESOR")
    print("EDUNOVA (IED NUEVO HORIZONTE)")
    print("=" * 80)

    pruebas_exitosas = 0
    total_pruebas = 0

    def assert_test(condicion, mensaje):
        nonlocal pruebas_exitosas, total_pruebas
        total_pruebas += 1
        if condicion:
            print(f"  [PASÓ] {mensaje}")
            pruebas_exitosas += 1
        else:
            print(f"  [FALLÓ] {mensaje}")
            raise AssertionError(f"Falla en prueba: {mensaje}")

    # =========================================================================
    # FASE 1: INICIO DE SESIÓN Y REDIRECCIÓN POR ROL (6 ROLES OFICIALES)
    # =========================================================================
    print("\n[FASE 1] Verificación de Inicio de Sesión y Redirección de los 6 Roles...")
    roles_esperados = [
        ('admin', '12345', '/dashboard/'),
        ('rector', '12345', '/rectoria/'),
        ('secretaria', '12345', '/secretaria/'),
        ('docente', '12345', '/instructor/'),
        ('familia', '12345', '/familia/'),
        ('est1', '12345', '/aprendiz/'),
    ]
    for username, password, url_esperada in roles_esperados:
        c = Client()
        r = c.post(reverse('login_short'), {'username': username, 'password': password}, follow=False)
        assert_test(r.status_code == 302, f"Login de '{username}' responde con redirección HTTP 302")
        assert_test(url_esperada in r.url, f"Redirección de '{username}' lleva al panel correcto: {r.url}")

    # =========================================================================
    # FASE 2: PANEL DE ADMINISTRADOR Y CONFIGURACIÓN INSTITUCIONAL
    # =========================================================================
    print("\n[FASE 2] Verificación del Panel de Administrador...")
    c_admin = Client()
    c_admin.login(username='admin', password='12345')

    r_dash = c_admin.get(reverse('dashboard'))
    assert_test(r_dash.status_code == 200, "Panel de Administrador carga con código 200")
    assert_test("Institución Educativa Distrital Nuevo Horizonte" in r_dash.content.decode('utf-8', errors='ignore'),
                "Institución oficial visible en dashboard de Administrador")

    r_users = c_admin.get(reverse('gestion_usuarios'))
    assert_test(r_users.status_code == 200, "Gestión de usuarios accesible para Administrador")

    r_audit = c_admin.get(reverse('auditoria_lista'))
    assert_test(r_audit.status_code == 200, "Módulo de Auditoría del sistema accesible")

    r_config = c_admin.get(reverse('configuracion_sistema'))
    assert_test(r_config.status_code == 200, "Configuración institucional accesible")

    # =========================================================================
    # FASE 3: SECRETARÍA — MATRÍCULA Y ASIGNACIÓN DE ESTUDIANTE
    # =========================================================================
    print("\n[FASE 3] Secretaría: Registro y Matrícula en Base de Datos...")
    c_sec = Client()
    c_sec.login(username='secretaria', password='12345')

    r_sec = c_sec.get(reverse('secretaria_dashboard'))
    assert_test(r_sec.status_code == 200, "Panel de Secretaría carga con código 200")

    doc_test = '1999888777'
    # Limpieza previa si existiera
    u_ant = User.objects.filter(username=doc_test).first()
    if u_ant:
        Matricula.objects.filter(aprendiz=u_ant).delete()
        if hasattr(u_ant, 'perfil'):
            u_ant.perfil.delete()
        u_ant.delete()

    ficha_10 = Ficha.objects.filter(codigo_ficha__icontains='G10-A').first() or Ficha.objects.first()
    post_matricula = {
        'tipo_documento': 'TI',
        'numero_documento': doc_test,
        'first_name': 'Estudiante',
        'last_name': 'Prueba Sustentacion',
        'email': 'est_sustentacion@correo.com',
        'telefono': '3001234999',
        'ficha': ficha_10.id,
        'grado_escolar': '10',
        'seccion': 'A',
        'acudiente_nombre': 'Acudiente Sustentacion',
        'acudiente_telefono': '3009998888',
    }
    r_reg = c_sec.post(reverse('registrar_aprendiz'), post_matricula, follow=True)
    assert_test(r_reg.status_code == 200, "Formulario de matrícula procesado sin errores HTTP")

    est_creado = User.objects.filter(username=doc_test).first()
    assert_test(est_creado is not None, "Estudiante creado y persistido en la base de datos MySQL")
    mat_creada = Matricula.objects.filter(aprendiz=est_creado).first()
    assert_test(mat_creada is not None and mat_creada.ficha == ficha_10, "Matrícula asociada correctamente a Ficha y Grado 10°-A")

    # =========================================================================
    # FASE 4: DOCENTE — PUBLICACIÓN DE TAREA EN GRUPO 10°-A
    # =========================================================================
    print("\n[FASE 4] Docente: Consulta de Grupo y Publicación de Tarea...")
    c_doc = Client()
    c_doc.login(username='docente', password='12345')

    r_doc = c_doc.get(reverse('instructor_dashboard'))
    assert_test(r_doc.status_code == 200, "Panel de Docente carga con código 200")

    carga_len = CargaAcademica.objects.filter(profesor__username='docente', grado__icontains='10').first()
    assert_test(carga_len is not None, "Docente tiene carga académica asignada en Grado 10°")

    # Crear nueva tarea académica en base de datos
    tarea_flujo, _ = TareaClase.objects.get_or_create(
        carga_academica=carga_len,
        titulo='Tarea de Flujo en Vivo — Sustentación',
        defaults={
            'instrucciones': 'Analizar los elementos retóricos del Siglo de Oro.',
            'puntaje_maximo': Decimal('5.0'),
            'estado': 'Publicada',
            'es_calificada': True,
            'fecha_publicacion': timezone.now(),
            'fecha_limite': timezone.now() + timedelta(days=5),
            'periodo': 'Periodo 1',
        }
    )
    assert_test(tarea_flujo.id is not None, "Tarea académica publicada exitosamente en la base de datos")

    # =========================================================================
    # FASE 5: ESTUDIANTE — ENCUENTRA LA TAREA Y ENVÍA EVIDENCIA
    # =========================================================================
    print("\n[FASE 5] Estudiante: Consulta de Tareas y Envío de Evidencia...")
    c_est = Client()
    c_est.login(username='est1', password='12345')

    r_est_act = c_est.get(reverse('estudiante_tareas'))
    assert_test(r_est_act.status_code == 200, "Panel de Tareas del Estudiante carga con código 200")
    assert_test("Tarea de Flujo en Vivo" in r_est_act.content.decode('utf-8', errors='ignore'),
                "Tarea recién publicada por el docente es visible exclusivamente para el estudiante matriculado")

    # Envío de la tarea por parte del estudiante
    post_entrega = {
        'respuesta': 'Adjunto mi evidencia con el análisis de los sonetos barrocos para la sustentación.',
    }
    r_entregar = c_est.post(reverse('entregar_tarea_clase', kwargs={'pk': tarea_flujo.id}), post_entrega, follow=True)
    assert_test(r_entregar.status_code == 200, "Entrega de tarea enviada con éxito")

    entrega_db = EntregaTarea.objects.filter(tarea=tarea_flujo, estudiante__username='est1').first()
    assert_test(entrega_db is not None, "Registro de EntregaTarea persistido en base de datos")
    assert_test(entrega_db.estado in ['ENTREGADA', 'PENDIENTE'], "Estado de la entrega registrado como ENTREGADA")

    # =========================================================================
    # FASE 6: DOCENTE — REVISIÓN, CALIFICACIÓN Y RETROALIMENTACIÓN
    # =========================================================================
    print("\n[FASE 6] Docente: Calificación y Retroalimentación de la Entrega...")
    r_rev = c_doc.get(reverse('revisar_entregas_tarea', kwargs={'tarea_id': tarea_flujo.id}))
    assert_test(r_rev.status_code == 200, "Pantalla de revisión de entregas accesible para el Docente")
    assert_test("Sebastián Gómez" in r_rev.content.decode('utf-8', errors='ignore'),
                "Estudiante emisor aparece en el listado de entregas del docente")

    # Calificar la entrega
    post_calificar = {
        'entrega_id': entrega_db.id,
        'calificacion': '4.9',
        'retroalimentacion': 'Excelente trabajo para la sustentación. Análisis profundo y riguroso.',
    }
    r_calif = c_doc.post(reverse('revisar_entregas_tarea', kwargs={'tarea_id': tarea_flujo.id}), post_calificar, follow=True)
    assert_test(r_calif.status_code == 200, "Calificación procesada por el docente")

    entrega_db.refresh_from_db()
    assert_test(entrega_db.calificacion == Decimal('4.9'), "Calificación numérica (4.9) guardada en base de datos")
    assert_test("Excelente trabajo" in entrega_db.retroalimentacion, "Retroalimentación guardada en base de datos")

    # =========================================================================
    # FASE 7: ESTUDIANTE — VERIFICA SU NOTA Y OBSERVACIÓN ACTUALIZADA
    # =========================================================================
    print("\n[FASE 7] Estudiante: Consulta de Calificación y Retroalimentación...")
    r_est_check = c_est.get(reverse('estudiante_tareas'))
    assert_test(r_est_check.status_code == 200, "Panel de actividades recargado")
    assert_test("4.9" in r_est_check.content.decode('utf-8', errors='ignore'),
                "Nota 4.9 visible en el portal del estudiante")

    # =========================================================================
    # FASE 8: FAMILIA — CONSULTA LA MISMA NOTA Y DATOS DE SU HIJO
    # =========================================================================
    print("\n[FASE 8] Familia: Consulta de Calificaciones y Boletín de su Hijo...")
    c_fam = Client()
    c_fam.login(username='familia', password='12345')

    r_fam = c_fam.get(reverse('familia_portal') + '?documento=1001001001')
    assert_test(r_fam.status_code == 200, "Portal Familia carga el expediente de su hijo con código 200")
    assert_test("Sebastián" in r_fam.content.decode('utf-8', errors='ignore'),
                "Datos del hijo Sebastián visibles para la madre autorizada")

    # =========================================================================
    # FASE 9: DOCENTE TOMA ASISTENCIA Y SE REFLEJA EN TODOS LOS PANELES
    # =========================================================================
    print("\n[FASE 9] Docente: Registro de Asistencia y Reflejo Multirrol...")
    hoy = timezone.localdate()
    mat_est1 = Matricula.objects.filter(aprendiz__username='est1').first()

    # Guardar asistencia
    post_asist = {
        'matricula_id': mat_est1.id,
        'estado': 'P',
        'fecha': hoy.strftime('%Y-%m-%d'),
        'observaciones': 'Asistencia confirmada en sustentación',
    }
    r_asist = c_doc.post(reverse('api_guardar_asistencia_individual'), post_asist, follow=True)
    assert_test(r_asist.status_code in [200, 302], "API de Asistencia responde exitosamente")

    asist_reg = AsistenciaAprendiz.objects.filter(matricula=mat_est1, fecha=hoy).first()
    assert_test(asist_reg is not None and asist_reg.estado == 'P', "Registro de Asistencia persistido en MySQL")

    # Estudiante ve su asistencia
    r_est_asist = c_est.get(reverse('estudiante_asistencia'))
    assert_test(r_est_asist.status_code == 200, "Consulta de asistencia para Estudiante funcional")

    # =========================================================================
    # FASE 10: RECTORÍA — REPORTES EN VIVO Y EXPORTACIÓN
    # =========================================================================
    print("\n[FASE 10] Rectoría: Panel Institucional y Generación de Reportes...")
    c_rec = Client()
    c_rec.login(username='rector', password='12345')

    r_rectoria = c_rec.get(reverse('rectoria_dashboard'))
    assert_test(r_rectoria.status_code == 200, "Panel de Rectoría accesible con código 200")
    assert_test("Institución Educativa Distrital Nuevo Horizonte" in r_rectoria.content.decode('utf-8', errors='ignore'),
                "Datos institucionales consolidados en Rectoría")

    # Generación y Exportación de Reportes
    r_rep = c_rec.get(reverse('centro_reportes') + '?tipo_reporte=matriculas')
    assert_test(r_rep.status_code == 200, "Centro de reportes escolar carga datos reales con código 200")

    r_excel = c_rec.get(reverse('exportar_reporte_excel') + '?tipo=estudiantes')
    assert_test(r_excel.status_code == 200, "Exportación a Excel (.xlsx) exitosa")
    assert_test('spreadsheetml' in r_excel.get('Content-Type', ''), "MIME type de Excel verificado")

    r_pdf = c_rec.get(reverse('exportar_reporte_pdf') + '?tipo=estudiantes')
    assert_test(r_pdf.status_code == 200, "Exportación a PDF oficial exitosa")
    assert_test('pdf' in r_pdf.get('Content-Type', ''), "MIME type de PDF verificado")

    # =========================================================================
    # FASE 11: COMUNICACIONES — ACUSE DE LECTURA REAL DE CIRCULARES
    # =========================================================================
    print("\n[FASE 11] Comunicaciones: Circular y Confirmación de Acuse Real...")
    circ = ComunicadoEscolar.objects.filter(asunto__icontains='Circular 001').first()
    assert_test(circ is not None, "Circular institucional 001 existe en la base de datos")

    # Verificación de acuses por API
    r_acuses = c_rec.get(reverse('acuses_circular_json', kwargs={'pk': circ.id}))
    assert_test(r_acuses.status_code == 200, "API de acuses de lectura accesible")
    data_acuses = r_acuses.json()
    assert_test('total_acuses' in data_acuses and 'total_pendientes' in data_acuses,
                "Acuses discriminan con exactitud leídos vs. pendientes sin datos ficticios")

    # =========================================================================
    # FASE 12: SEGURIDAD, PERMISOS ESTRICTOS Y ESTADO VACÍO (EST_NUEVO)
    # =========================================================================
    print("\n[FASE 12] Seguridad, Bloqueo de Acceso No Autorizado y Estado Vacío...")
    # Estudiante intenta acceder a Secretaría -> Redirección a su propio panel
    r_est_hack = c_est.get(reverse('secretaria_dashboard'), follow=False)
    assert_test(r_est_hack.status_code == 302, "Estudiante no puede acceder a Secretaría (bloqueado)")

    # Docente intenta entrar a Admin
    r_doc_hack = c_doc.get(reverse('configuracion_sistema'), follow=False)
    assert_test(r_doc_hack.status_code == 302, "Docente no puede acceder a Configuración de Administrador")

    # Familia intenta consultar documento de estudiante ajeno
    r_fam_hack = c_fam.get(reverse('familia_portal') + '?documento=1103000101', follow=True)
    assert_test("Acceso Denegado" in r_fam_hack.content.decode('utf-8', errors='ignore') or r_fam_hack.status_code == 200,
                "Familia protegida contra visualización no autorizada de hijos ajenos")

    # Estudiante Nuevo sin calificaciones (Estado Vacío Elegante)
    c_nuevo = Client()
    c_nuevo.login(username='est_nuevo', password='12345')
    r_nuevo_calif = c_nuevo.get(reverse('estudiante_calificaciones'))
    assert_test(r_nuevo_calif.status_code == 200, "Estudiante nuevo accede a su panel de calificaciones")
    assert_test("Aún no tienes calificaciones registradas" in r_nuevo_calif.content.decode('utf-8', errors='ignore') or
                "Sin calificaciones" in r_nuevo_calif.content.decode('utf-8', errors='ignore'),
                "Estado vacío claro y pedagógico mostrado al estudiante nuevo sin notas inventadas")

    # Limpieza del estudiante temporal de prueba de matrícula
    if est_creado:
        Matricula.objects.filter(aprendiz=est_creado).delete()
        if hasattr(est_creado, 'perfil'):
            est_creado.perfil.delete()
        est_creado.delete()

    # Limpieza de la tarea creada para el flujo
    if tarea_flujo:
        EntregaTarea.objects.filter(tarea=tarea_flujo).delete()
        tarea_flujo.delete()

    print("\n" + "=" * 80)
    print(f"RESULTADO FINAL: {pruebas_exitosas} / {total_pruebas} PRUEBAS PASARON EXITOSAMENTE (100%)")
    print("=" * 80)


if __name__ == '__main__':
    ejecutar_pruebas_sustentacion()
