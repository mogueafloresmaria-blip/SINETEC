import os
import sys
import django
from io import BytesIO

sys.path.insert(0, r'c:\SINETEC\SINETEC')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse
from usuarios.models import Rol, PerfilUsuario
from academico.models import Ficha, Matricula, ComunicacionMensaje

User = get_user_model()

def test_student_and_secretaria_system():
    print("======================================================================")
    print(" AUDITORÍA Y VERIFICACIÓN COMPLETA - ESTUDIANTE Y SECRETARÍA EDUNOVA")
    print("======================================================================")
    
    client = Client()
    
    # 1. Check Secretaría enrollment page permissions
    sec_user, _ = User.objects.get_or_create(username='sec_test_user', defaults={'email': 'sec@edunova.edu'})
    sec_user.set_password('secpass123')
    sec_user.save()
    
    sec_role, _ = Rol.objects.get_or_create(nombre='Secretaría')
    if hasattr(sec_user, 'perfil'):
        sec_user.perfil.rol = sec_role
        sec_user.perfil.save()
    else:
        PerfilUsuario.objects.create(usuario=sec_user, rol=sec_role)
        
    client.login(username='sec_test_user', password='secpass123')
    
    # Check Nueva Matricula page access
    url_nueva_matricula = reverse('nueva_matricula')
    res = client.get(url_nueva_matricula)
    print(f"[TEST 1] Acceso Secretaría a {url_nueva_matricula}: HTTP {res.status_code}")
    assert res.status_code == 200, f"Error: Secretaría returned {res.status_code} on {url_nueva_matricula}"
    print("  -> OK: Secretaría tiene acceso concedido a la vista de nueva matrícula")
    
    # Check menu HTML for Registrar Cobro absence
    sec_dashboard_res = client.get('/secretaria/')
    print(f"[TEST 2] Verificando panel de Secretaría (/secretaria/): HTTP {sec_dashboard_res.status_code}")
    html_content = sec_dashboard_res.content.decode('utf-8')
    assert "Registrar cobro" not in html_content, "Error: 'Registrar cobro' still present in Secretaria panel"
    print("  -> OK: 'Registrar cobro' eliminado exitosamente del panel de Secretaría")
    
    # 3. Test Student Creation from Secretaría & Automatic Account Linking with Document as username/password
    doc_num = '1098765432'
    Matricula.objects.filter(aprendiz__username=doc_num).delete()
    User.objects.filter(username=doc_num).delete()
    
    ficha10 = Ficha.objects.first()
    
    post_data = {
        'nombre': 'Estudiante',
        'apellido': 'Prueba AutoAccount',
        'documento': doc_num,
        'tipo_documento': 'TI',
        'email': 'estudiante.test@edunova.edu',
        'ficha': ficha10.id if ficha10 else 1,
        'jornada': 'MAÑANA',
        'sede': 'SEDE PRINCIPAL',
        'estado_matricula': 'MATRICULADO',
    }
    
    enroll_res = client.post(url_nueva_matricula, post_data, follow=True)
    print(f"[TEST 3] Registro de matricula desde Secretaría: HTTP {enroll_res.status_code}")
    
    student_user = User.objects.filter(username=doc_num).first()
    assert student_user is not None, "Error: Django User account was not auto-created with document number"
    print(f"  -> OK: Estudiante {student_user.get_full_name()} creado exitosamente con usuario BD '{student_user.username}'")
    
    # 4. Test Student Login with Document Number as initial credentials
    client.logout()
    login_success = client.login(username=doc_num, password=doc_num)
    assert login_success, f"Error: Student login failed using document number '{doc_num}' as username and password"
    print(f"  -> OK: Inicio de sesión exitoso del estudiante usando su cédula/documento '{doc_num}'")
    
    # 5. Verify Student Panel Modules
    student_urls = [
        ('/aprendiz/', 'Inicio'),
        ('/aprendiz/?tab=calificaciones', 'Calificaciones'),
        ('/aprendiz/?tab=horario', 'Mi horario'),
        ('/aprendiz/?tab=actividades', 'Tareas'),
        ('/aprendiz/?tab=asistencia', 'Asistencia'),
        ('/aprendiz/?tab=comunicados', 'Comunicados'),
        ('/aprendiz/?tab=mensajeria', 'Mensajería'),
        ('/portafolio/', 'Portafolio'),
        ('/aprendiz/?tab=perfil', 'Perfil del estudiante'),
    ]
    
    print("[TEST 4] Verificando acceso a los 9 módulos del Panel del Estudiante:")
    for url, label in student_urls:
        res = client.get(url)
        assert res.status_code == 200, f"Error: Module {label} ({url}) returned HTTP {res.status_code}"
        print(f"  -> Modulo '{label}' ({url}): HTTP 200 OK")
        
    # 6. Test Photo Upload in Student Profile
    print("[TEST 5] Probando carga segura de fotografía de perfil del estudiante:")
    fake_img = SimpleUploadedFile("avatar_prueba.jpg", b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xFF\xDB\x00C", content_type="image/jpeg")
    photo_res = client.post('/aprendiz/', {
        'action': 'actualizar_foto_perfil',
        'foto': fake_img,
    }, follow=True)
    assert photo_res.status_code == 200
    
    student_user.refresh_from_db()
    assert student_user.perfil.foto_perfil is not None and bool(student_user.perfil.foto_perfil), "Error: Profile photo was not saved in DB"
    print(f"  -> OK: Fotografía guardada correctamente en BD ({student_user.perfil.foto_perfil.name})")
    
    # Check persistence after re-login
    client.logout()
    client.login(username=doc_num, password=doc_num)
    dashboard_res = client.get('/aprendiz/')
    assert student_user.perfil.foto_perfil.url in dashboard_res.content.decode('utf-8')
    print("  -> OK: La fotografía persiste tras cerrar sesión y volver a entrar")
    
    # 7. Test Direct Messaging to Teacher
    print("[TEST 6] Probando módulo de Mensajería directa entre Estudiante y Docente:")
    docente_user = User.objects.filter(perfil__rol__nombre__icontains='Docente').first()
    if not docente_user:
        docente_user, _ = User.objects.get_or_create(username='docente_prueba', defaults={'first_name': 'Profesor', 'last_name': 'Titular'})
        doc_role, _ = Rol.objects.get_or_create(nombre='Docente')
        PerfilUsuario.objects.get_or_create(usuario=docente_user, defaults={'rol': doc_role, 'numero_documento': '11223344'})
        
    msg_texto = "Estimado profesor, le escribo para consultar el material de clase."
    msg_res = client.post('/aprendiz/', {
        'action': 'enviar_mensaje_docente',
        'docente_id': docente_user.id,
        'asunto': 'Duda sobre actividad',
        'mensaje': msg_texto
    }, follow=True)
    assert msg_res.status_code == 200
    
    # Verify in DB
    msg_db = ComunicacionMensaje.objects.filter(remitente=student_user, destinatario=docente_user, mensaje=msg_texto).first()
    assert msg_db is not None, "Error: Message was not saved in DB"
    print("  -> OK: Mensaje privado guardado y persistido en BD correctamente")
    
    # 8. Test Admin Auto Student Account Creation
    print("[TEST 7] Verificando creación automática de cuenta desde Administrador:")
    admin_user, _ = User.objects.get_or_create(username='admin_test_auto', defaults={'is_superuser': True})
    admin_user.set_password('adminpass123')
    admin_user.save()
    client.login(username='admin_test_auto', password='adminpass123')
    
    doc_num_admin = '1098765433'
    Matricula.objects.filter(aprendiz__username=doc_num_admin).delete()
    User.objects.filter(username=doc_num_admin).delete()
    
    post_admin_data = {
        'nombre': 'Estudiante Admin',
        'apellido': 'Creado Automatico',
        'documento': doc_num_admin,
        'tipo_documento': 'TI',
        'email': 'estudiante_admin@edunova.edu',
        'ficha': ficha10.id if ficha10 else 1,
        'jornada': 'MAÑANA',
        'sede': 'SEDE PRINCIPAL',
        'estado_matricula': 'MATRICULADO',
    }
    enroll_admin_res = client.post(url_nueva_matricula, post_admin_data, follow=True)
    assert enroll_admin_res.status_code == 200
    student_admin_user = User.objects.filter(username=doc_num_admin).first()
    assert student_admin_user is not None, "Error: Student account created from Admin failed"
    print(f"  -> OK: Estudiante registrado desde Administrador generó automáticamente usuario BD '{student_admin_user.username}'")
    
    # Verify Admin Student login with document credentials
    client.logout()
    login_admin_student = client.login(username=doc_num_admin, password=doc_num_admin)
    assert login_admin_student, f"Error: Student created by admin failed login with document '{doc_num_admin}'"
    print("  -> OK: Estudiante creado desde Admin inicia sesión exitosamente con su documento")

    print("======================================================================")
    print(" TODAS LAS PRUEBAS DEL PANEL DEL ESTUDIANTE Y SECRETARÍA PASARON CON ÉXITO (100% OK)")
    print("======================================================================")

if __name__ == '__main__':
    test_student_and_secretaria_system()
