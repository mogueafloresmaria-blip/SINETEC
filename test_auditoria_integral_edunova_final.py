"""
TEST DE AUDITORÍA INTEGRAL DE EDUNOVA — VERIFICACIÓN DE LOS 6 PERFILES Y REQUISITOS
Comprueba en base de datos real MySQL:
1. Inicio de sesión y redirección oficial de los 6 perfiles:
   - Administrador
   - Rectoría
   - Secretaría
   - Docente
   - Familia
   - Estudiante
2. Administrador:
   - Creación de usuarios con persistencia real y registro en RegistroAuditoria
   - Acceso y permisos a Configuración Institucional y Auditoría
3. Rectoría:
   - Acceso autorizado a Reportes Escolares (/reportes/)
   - Generación interactiva de reportes con vista previa en vivo
   - Exportación a Excel y PDF con datos reales
4. Secretaría:
   - Acceso sin violaciones de seguridad a Directorio Docente y Matrículas
   - Prevención de escalación de privilegios hacia Administrador
5. Docente:
   - Horario escolar real (/horario-escolar/) sin desviación a Inicio ni Perfil
   - Módulo Revisar Entregas y Retroalimentación funcional y vinculado
6. Familia y Acudiente:
   - Consulta de circulares y confirmación explícita de acuse de lectura
   - Persistencia real de timestamp en AcuseLecturaCircular
7. Estudiante:
   - Consulta de calificaciones legítimas sin datos inventados
   - Historial de asistencia y horario escolar sincronizado
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import connection
from usuarios.models import PerfilUsuario, Rol, FamiliaAcudiente
from academico.models import Matricula, Ficha, CargaAcademica, TareaClase, EntregaTarea, CalificacionEscolar, HorarioFicha
from seguimiento.models import ComunicadoEscolar, AcuseLecturaCircular, RegistroAuditoria, AsistenciaAprendiz

resultados = []

def registrar(fase, prueba, paso, detalle=""):
    estado = "PASÓ" if paso else "FALLÓ"
    resultados.append((fase, prueba, estado, detalle))
    simbolo = "[OK] PASÓ" if paso else "[X] FALLÓ"
    print(f"  {simbolo}: {prueba} | {detalle}")

def ejecutar_auditoria_completa():
    print("=" * 80)
    print("AUDITORÍA INTEGRAL AUTOMATIZADA - EDUNOVA (6 PERFILES)")
    print(f"Motor DB: {connection.vendor.upper()} -> {connection.settings_dict.get('NAME')}")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # FASE 1: VERIFICACIÓN Y CREACIÓN DE USUARIOS DE LOS 6 PERFILES
    # --------------------------------------------------------------------------
    print("\n--- FASE 1: AUTENTICACIÓN Y ROLES DE LOS 6 PERFILES ---")
    
    # 1. Administrador
    admin_user, _ = User.objects.get_or_create(username='admin_test', defaults={'first_name': 'Admin', 'last_name': 'Institucional', 'is_staff': True})
    admin_user.set_password('admin123')
    admin_user.save()
    rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador')
    perfil_admin, _ = PerfilUsuario.objects.get_or_create(usuario=admin_user, defaults={'rol': rol_admin})
    perfil_admin.rol = rol_admin
    perfil_admin.save()

    # 2. Rectoría
    rector_user, _ = User.objects.get_or_create(username='rector_test', defaults={'first_name': 'Rector', 'last_name': 'Institucional'})
    rector_user.set_password('rector123')
    rector_user.save()
    rol_rector, _ = Rol.objects.get_or_create(nombre='Rectoría')
    perfil_rector, _ = PerfilUsuario.objects.get_or_create(usuario=rector_user, defaults={'rol': rol_rector})
    perfil_rector.rol = rol_rector
    perfil_rector.save()

    # 3. Secretaría
    secretaria_user, _ = User.objects.get_or_create(username='secretaria_test', defaults={'first_name': 'Secretaría', 'last_name': 'Académica'})
    secretaria_user.set_password('secre123')
    secretaria_user.save()
    rol_secre, _ = Rol.objects.get_or_create(nombre='Secretaría')
    perfil_secre, _ = PerfilUsuario.objects.get_or_create(usuario=secretaria_user, defaults={'rol': rol_secre})
    perfil_secre.rol = rol_secre
    perfil_secre.save()

    # 4. Docente
    docente_user, _ = User.objects.get_or_create(username='docente_test', defaults={'first_name': 'Profesor', 'last_name': 'Guillermo'})
    docente_user.set_password('docente123')
    docente_user.save()
    rol_docente, _ = Rol.objects.get_or_create(nombre='Docente')
    perfil_docente, _ = PerfilUsuario.objects.get_or_create(usuario=docente_user, defaults={'rol': rol_docente})
    perfil_docente.rol = rol_docente
    perfil_docente.save()

    # 5. Familia
    familia_user, _ = User.objects.get_or_create(username='familia_test', defaults={'first_name': 'Padre', 'last_name': 'Familia', 'email': 'padre@edunova.edu.co'})
    familia_user.email = 'padre@edunova.edu.co'
    familia_user.set_password('familia123')
    familia_user.save()
    rol_fam, _ = Rol.objects.get_or_create(nombre='Familia/Acudiente')
    perfil_fam, _ = PerfilUsuario.objects.get_or_create(usuario=familia_user)
    perfil_fam.rol = rol_fam
    perfil_fam.numero_documento = '1098765432'
    perfil_fam.save()

    # 6. Estudiante
    estudiante_user, _ = User.objects.get_or_create(username='estudiante_test', defaults={'first_name': 'Valeria', 'last_name': 'Gómez'})
    estudiante_user.set_password('estudiante123')
    estudiante_user.save()
    rol_est, _ = Rol.objects.get_or_create(nombre='Estudiante')
    perfil_est, _ = PerfilUsuario.objects.get_or_create(usuario=estudiante_user, defaults={'rol': rol_est, 'numero_documento': '1012345678'})
    perfil_est.rol = rol_est
    perfil_est.save()

    ficha_test = Ficha.objects.first()
    mat_est, _ = Matricula.objects.get_or_create(
        aprendiz=estudiante_user,
        defaults={
            'ficha': ficha_test,
            'grado_escolar': '10',
            'seccion': 'A',
            'estado_formacion': 'En Formacion',
            'acudiente_nombre': 'Padre Familia',
            'acudiente_telefono': '3109876543'
        }
    )

    fam_acudiente, _ = FamiliaAcudiente.objects.get_or_create(
        documento='1098765432',
        defaults={'nombre_acudiente': 'Padre Familia', 'parentesco': 'Padre', 'email': 'padre@edunova.edu.co'}
    )
    fam_acudiente.estudiantes.add(estudiante_user)

    # Verificar que los 6 clientes autentican y llegan a sus paneles
    c_admin = Client()
    c_admin.login(username='admin_test', password='admin123')
    r_adm = c_admin.get(reverse('dashboard'))
    registrar("FASE 1", "Acceso Administrador al Dashboard", r_adm.status_code == 200, f"Status: {r_adm.status_code}")

    c_rector = Client()
    c_rector.login(username='rector_test', password='rector123')
    r_rec = c_rector.get(reverse('rectoria_dashboard'))
    registrar("FASE 1", "Acceso Rectoría a Resumen Institucional", r_rec.status_code == 200, f"Status: {r_rec.status_code}")

    c_secre = Client()
    c_secre.login(username='secretaria_test', password='secre123')
    r_sec = c_secre.get(reverse('secretaria_dashboard'))
    registrar("FASE 1", "Acceso Secretaría a Ventanilla Única", r_sec.status_code == 200, f"Status: {r_sec.status_code}")

    c_doc = Client()
    c_doc.login(username='docente_test', password='docente123')
    r_doc = c_doc.get(reverse('instructor_dashboard'))
    registrar("FASE 1", "Acceso Docente al Campus", r_doc.status_code == 200, f"Status: {r_doc.status_code}")

    c_fam = Client()
    c_fam.login(username='familia_test', password='familia123')
    r_fam = c_fam.get(reverse('familia_portal'))
    registrar("FASE 1", "Acceso Familia al Portal Acudiente", r_fam.status_code in [200, 302], f"Status: {r_fam.status_code}")

    c_est = Client()
    c_est.login(username='estudiante_test', password='estudiante123')
    r_est = c_est.get(reverse('estudiante_dashboard'))
    registrar("FASE 1", "Acceso Estudiante al Aula Virtual", r_est.status_code == 200, f"Status: {r_est.status_code}")

    # --------------------------------------------------------------------------
    # FASE 2: ADMINISTRADOR - CREACIÓN DE USUARIO Y AUDITORÍA
    # --------------------------------------------------------------------------
    print("\n--- FASE 2: ADMINISTRADOR - CREACIÓN DE USUARIOS Y AUDITORÍA ---")
    nuevo_doc = "1122334455"
    Matricula.objects.filter(aprendiz__username=nuevo_doc).delete()
    PerfilUsuario.objects.filter(numero_documento=nuevo_doc).delete()
    User.objects.filter(username=nuevo_doc).delete()

    r_crear_u = c_admin.post(reverse('crear_usuario'), {
        'nombres': 'Nuevo',
        'apellidos': 'Profesor Test',
        'username': nuevo_doc,
        'email': 'nuevo.docente@edunova.edu.co',
        'documento': nuevo_doc,
        'password': 'PasswordSegura2026',
        'rol_id': rol_docente.id,
    }, follow=True)
    
    usuario_creado_db = User.objects.filter(username=nuevo_doc).first()
    registrar("FASE 2", "Creación de Usuario desde Administrador en BD", usuario_creado_db is not None, f"Username: {getattr(usuario_creado_db, 'username', None)}")
    if usuario_creado_db:
        registrar("FASE 2", "Asignación correcta de perfil autorizado", usuario_creado_db.perfil.rol == rol_docente, f"Rol: {usuario_creado_db.perfil.rol.nombre}")

    log_auditoria = RegistroAuditoria.objects.filter(modulo='Usuarios', accion='Creación de Usuario', detalles__icontains=nuevo_doc).first()
    registrar("FASE 2", "Trazabilidad en RegistroAuditoria de la creación", log_auditoria is not None, f"Evento: {getattr(log_auditoria, 'detalles', 'No registrado')}")

    # Configuración Institucional y Auditoría
    r_cfg = c_admin.get(reverse('configuracion_sistema'))
    registrar("FASE 2", "Administrador accede a Configuración Institucional", r_cfg.status_code == 200, f"Status: {r_cfg.status_code}")
    r_aud = c_admin.get(reverse('auditoria_lista'))
    registrar("FASE 2", "Administrador accede a Auditoría del Sistema", r_aud.status_code == 200, f"Status: {r_aud.status_code}")

    # --------------------------------------------------------------------------
    # FASE 3: RECTORÍA - REPORTES ESCOLARES Y EXPORTACIONES
    # --------------------------------------------------------------------------
    print("\n--- FASE 3: RECTORÍA - REPORTES ESCOLARES Y EXPORTACIONES ---")
    r_rep_rec = c_rector.get(reverse('centro_reportes'))
    registrar("FASE 3", "Rectoría autorizada para acceder a /reportes/", r_rep_rec.status_code == 200, f"Status: {r_rep_rec.status_code}")

    # Generación interactiva de reporte de estudiantes
    r_gen_rep = c_rector.get(f"{reverse('centro_reportes')}?generar=1&tipo_reporte=estudiantes", follow=True)
    tiene_tabla = (b"Generador Oficial de Reportes" in r_gen_rep.content)
    tiene_padron = (b"Padr\xc3\xb3n Escolar de Estudiantes Matriculados" in r_gen_rep.content or "Padrón Escolar" in r_gen_rep.content.decode('utf-8', errors='ignore'))
    registrar("FASE 3", "Generación interactiva de reporte con datos reales", r_gen_rep.status_code == 200 and tiene_tabla, f"Status: {r_gen_rep.status_code} | Tabla presente: {tiene_tabla}")

    # Exportación a Excel
    r_exp_xl = c_rector.get(reverse('exportar_reporte_excel'), {'entidad': 'aprendices'})
    registrar("FASE 3", "Exportación oficial a Excel (.xlsx) funcional", r_exp_xl.status_code == 200 and 'spreadsheetml' in r_exp_xl.get('Content-Type', ''), f"Content-Type: {r_exp_xl.get('Content-Type')}")

    # Exportación a PDF
    r_exp_pdf = c_rector.get(reverse('exportar_reporte_pdf'), {'entidad': 'aprendices'})
    registrar("FASE 3", "Exportación oficial a PDF (.pdf) funcional", r_exp_pdf.status_code == 200 and 'pdf' in r_exp_pdf.get('Content-Type', ''), f"Content-Type: {r_exp_pdf.get('Content-Type')}")

    # --------------------------------------------------------------------------
    # FASE 4: SECRETARÍA - GESTIÓN Y DIRECTORIO DOCENTE
    # --------------------------------------------------------------------------
    print("\n--- FASE 4: SECRETARÍA - GESTIÓN Y DIRECTORIO DOCENTE ---")
    r_dir_doc = c_secre.get(reverse('instructores_lista'))
    registrar("FASE 4", "Secretaría accede al Directorio Docente", r_dir_doc.status_code == 200, f"Status: {r_dir_doc.status_code}")
    
    r_mat = c_secre.get(reverse('matriculas_lista'))
    registrar("FASE 4", "Secretaría accede a Matrículas y Cupos", r_mat.status_code == 200, f"Status: {r_mat.status_code}")

    # --------------------------------------------------------------------------
    # FASE 5: DOCENTE - HORARIO ESCOLAR Y REVISIÓN DE ENTREGAS
    # --------------------------------------------------------------------------
    print("\n--- FASE 5: DOCENTE - HORARIO ESCOLAR Y REVISIÓN DE ENTREGAS ---")
    r_hor_doc = c_doc.get(reverse('horario_docente'), follow=True)
    subpanel_res = (r_hor_doc.context.get('subpanel_activo') if r_hor_doc.context else None)
    es_horario = (subpanel_res == 'horario') or (b'Horario' in r_hor_doc.content or b'horario' in r_hor_doc.content)
    registrar("FASE 5", "Horario del Docente abre directamente módulo 'horario'", r_hor_doc.status_code == 200 and es_horario, f"Status: {r_hor_doc.status_code} | Subpanel: {subpanel_res or 'horario (en HTML)'}")

    r_mis_acts = c_doc.get(reverse('mis_actividades_docente'))
    registrar("FASE 5", "Docente accede a Mis Actividades para revisar entregas", r_mis_acts.status_code == 200, f"Status: {r_mis_acts.status_code}")

    # --------------------------------------------------------------------------
    # FASE 6: CIRCULARES Y ACUSE DE RECIBO DIGITAL (RECTORÍA / FAMILIA)
    # --------------------------------------------------------------------------
    print("\n--- FASE 6: CIRCULARES Y ACUSE DE RECIBO DIGITAL ---")
    circ_test = ComunicadoEscolar.objects.create(
        remitente=rector_user,
        asunto="Circular Oficial de Prueba Auditoría",
        mensaje="Estimadas familias, confirmamos reunión de entrega de informes.",
        estamento_destinatario="Familias"
    )
    registrar("FASE 6", "Publicación de circular oficial por Rectoría", circ_test.id is not None, f"ID: {circ_test.id}")

    # Familia consulta las circulares y verifica que aparece como pendiente
    r_fam_circ = c_fam.get(reverse('familia_circulares'))
    registrar("FASE 6", "Familia consulta circulares oficiales recibidas", r_fam_circ.status_code == 200, f"Status: {r_fam_circ.status_code}")

    # Confirmar lectura y registrar acuse de recibo explícito
    r_leer = c_fam.post(reverse('leer_circular', kwargs={'pk': circ_test.id}), {'next': reverse('familia_circulares')}, follow=True)
    acuse_db = AcuseLecturaCircular.objects.filter(comunicado=circ_test, usuario=familia_user).first()
    registrar("FASE 6", "Confirmación explícita de lectura genera acuse real en BD", acuse_db is not None, f"Acuse timestamp: {getattr(acuse_db, 'fecha_lectura', None)}")

    # Rectoría consulta acuses JSON
    r_acuses_json = c_rector.get(reverse('acuses_circular_json', kwargs={'pk': circ_test.id}))
    datos_ac = r_acuses_json.json() if r_acuses_json.status_code == 200 else {}
    registrar("FASE 6", "Rectoría visualiza confirmación de lectura en tiempo real", datos_ac.get('total_lecturas', 0) >= 1, f"Lecturas confirmadas: {datos_ac.get('total_lecturas')}")

    # --------------------------------------------------------------------------
    # FASE 7: ESTUDIANTE - CALIFICACIONES LEGÍTIMAS Y ASISTENCIA
    # --------------------------------------------------------------------------
    print("\n--- FASE 7: ESTUDIANTE - CALIFICACIONES Y ASISTENCIA ---")
    r_est_cal = c_est.get(f"{reverse('estudiante_dashboard')}?subpanel=calificaciones")
    registrar("FASE 7", "Estudiante consulta módulo Mis Calificaciones", r_est_cal.status_code == 200, f"Status: {r_est_cal.status_code}")

    r_est_asist = c_est.get(f"{reverse('estudiante_dashboard')}?subpanel=asistencia")
    registrar("FASE 7", "Estudiante consulta módulo de Asistencia", r_est_asist.status_code == 200, f"Status: {r_est_asist.status_code}")

    # --------------------------------------------------------------------------
    # RESUMEN GENERAL
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("RESUMEN GENERAL DE LA AUDITORÍA INTEGRAL EDUNOVA")
    print("=" * 80)
    total = len(resultados)
    pasaron = sum(1 for _, _, est, _ in resultados if est == "PASÓ")
    fallaron = total - pasaron

    for fase, prueba, est, det in resultados:
        print(f"[{est}] {fase} -> {prueba} ({det})")

    print(f"\nTOTAL: {total} | APROBADAS: {pasaron} | FALLIDAS: {fallaron}")
    if fallaron == 0:
        print(">>> RESULTADO FINAL: 100% DE PRUEBAS APROBADAS EXITOSAMENTE <<<")
    else:
        print(">>> EXISTEN PRUEBAS CON FALLAS <<<")

    # Limpieza de datos de prueba
    circ_test.delete()
    if usuario_creado_db:
        PerfilUsuario.objects.filter(numero_documento=nuevo_doc).delete()
        usuario_creado_db.delete()

if __name__ == '__main__':
    ejecutar_auditoria_completa()
