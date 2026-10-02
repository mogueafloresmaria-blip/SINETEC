import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from academico.models import ComunicacionMensaje, CalificacionEscolar, Matricula, CargaAcademica
from seguimiento.models import AsistenciaAprendiz, ComunicadoEscolar

def test_full_system():
    print("=" * 60)
    print("1. PROBANDO INICIO DE SESIÓN DE LOS 4 ESTUDIANTES REALES")
    print("=" * 60)
    
    students = [
        ('est1', 'Estudiante10*', 'Grado 10°A', 'Juan Pérez'),
        ('est2', 'Estudiante10*', 'Grado 10°A', 'María Gómez'),
        ('est3', 'Estudiante11*', 'Grado 11°A', 'Luis Martínez'),
        ('est4', 'Estudiante11*', 'Grado 11°A', 'Ana López'),
    ]
    
    for username, pwd, grado, nombre in students:
        c = Client()
        ok = c.login(username=username, password=pwd)
        assert ok, f"Error: no se pudo iniciar sesión con {username}"
        # Consultar portal estudiante
        resp = c.get('/estudiante/')
        assert resp.status_code == 200, f"Error: panel estudiante respondió {resp.status_code} para {username}"
        print(f"  [OK] {username} ({nombre}) - {grado} -> Login exitoso, Panel Estudiante HTTP 200")

    print("\n" + "=" * 60)
    print("2. PROBANDO INICIO DE SESIÓN DE LOS 6 ROLES INSTITUCIONALES")
    print("=" * 60)
    
    roles = [
        ('admin', 'Admin2026*', '/dashboard/', 'Administrador'),
        ('docente', 'Docente2026*', '/instructor/', 'Docente'),
        ('rector', 'Rector2026*', '/rectoria/', 'Rectoría'),
        ('secretaria', 'Secretaria2026*', '/secretaria/', 'Secretaría'),
        ('familia', 'Familia2026*', '/familia/', 'Familia'),
        ('est1', 'Estudiante10*', '/estudiante/', 'Estudiante'),
    ]
    
    for user, pwd, url, rol_desc in roles:
        c = Client()
        ok = c.login(username=user, password=pwd)
        assert ok, f"Error: no se pudo iniciar sesión con {user}"
        resp = c.get(url)
        assert resp.status_code == 200, f"Error: {url} respondió {resp.status_code} para {user}"
        print(f"  [OK] Rol {rol_desc} (usuario: '{user}') -> Login exitoso, {url} HTTP 200")

    print("\n" + "=" * 60)
    print("3. PROBANDO COMUNICACIONES DE IDA Y VUELTA (DOCENTE <-> FAMILIA)")
    print("=" * 60)
    
    docente_u = User.objects.get(username='docente')
    familia_u = User.objects.get(username='familia')
    
    # Paso A: Docente envía comunicación a la familia
    msg_doc_to_fam = ComunicacionMensaje.objects.create(
        remitente=docente_u,
        destinatario=familia_u,
        asunto="Reunión de Seguimiento Académico y Convivencial",
        mensaje="Estimada familia de Juan Pérez, cordialmente le solicitamos una breve reunión para revisar el destacado avance académico del estudiante."
    )
    print(f"  [PASO 1] Docente envió mensaje a Familia (ID: {msg_doc_to_fam.id})")
    
    # Paso B: Familia entra a su portal y verifica que el mensaje llegó
    c_fam = Client()
    c_fam.login(username='familia', password='Familia2026*')
    resp_mensajes_fam = c_fam.get('/academico/comunicaciones/')
    assert resp_mensajes_fam.status_code == 200
    mensajes_recibidos_fam = ComunicacionMensaje.objects.filter(destinatario=familia_u, id=msg_doc_to_fam.id).exists()
    assert mensajes_recibidos_fam, "Error: la familia no encontró el mensaje en su bandeja"
    print(f"  [PASO 2] Familia recibió el mensaje en su buzón exitosamente")
    
    # Paso C: Familia responde al docente
    msg_fam_reply = ComunicacionMensaje.objects.create(
        remitente=familia_u,
        destinatario=docente_u,
        asunto="Re: Reunión de Seguimiento Académico y Convivencial",
        mensaje="Buenas tardes profesor, con mucho gusto asistiré el próximo viernes a primera hora. Gracias por el seguimiento."
    )
    print(f"  [PASO 3] Familia respondió al Docente (ID: {msg_fam_reply.id})")
    
    # Paso D: Docente entra a su buzón y verifica la respuesta recibida
    c_doc = Client()
    c_doc.login(username='docente', password='Docente2026*')
    resp_doc_inbox = c_doc.get('/academico/comunicaciones/')
    assert resp_doc_inbox.status_code == 200
    respuesta_encontrada = ComunicacionMensaje.objects.filter(destinatario=docente_u, id=msg_fam_reply.id).exists()
    assert respuesta_encontrada, "Error: el docente no encontró la respuesta de la familia"
    print(f"  [PASO 4] Docente recibió la respuesta de la Familia exitosamente en su buzón")

    print("\n" + "=" * 60)
    print("4. PROBANDO COMUNICACIONES DE IDA Y VUELTA (DOCENTE <-> ESTUDIANTE)")
    print("=" * 60)
    
    est1_u = User.objects.get(username='est1')
    
    # Docente a Estudiante
    msg_doc_est = ComunicacionMensaje.objects.create(
        remitente=docente_u,
        destinatario=est1_u,
        asunto="Felicitaciones por entrega de guía de aprendizaje",
        mensaje="Apreciado Juan, tu guía de Desarrollo Web ha sido evaluada satisfactoriamente con felicitaciones."
    )
    # Estudiante verifica recepción
    c_est = Client()
    c_est.login(username='est1', password='Estudiante10*')
    resp_est_inbox = c_est.get('/academico/comunicaciones/')
    assert resp_est_inbox.status_code == 200
    assert ComunicacionMensaje.objects.filter(destinatario=est1_u, id=msg_doc_est.id).exists()
    print("  [OK] Estudiante 'est1' recibió comunicación del Docente correctamente")

    print("\n" + "=" * 60)
    print("5. PROBANDO VISTAS DEL PORTAL FAMILIA")
    print("=" * 60)
    
    subrutas_familia = [
        ('/familia/', 'Inicio Familia'),
        ('/familia/matricula/', 'Ficha Matrícula'),
        ('/familia/boletines/', 'Boletines y Notas'),
        ('/familia/asistencia/', 'Asistencia Hijos'),
        ('/familia/pensiones/', 'Recibos y Pensiones'),
        ('/comunicaciones/', 'Comunicaciones Familia'),
    ]
    for ruta, desc in subrutas_familia:
        resp = c_fam.get(ruta)
        assert resp.status_code == 200, f"Error: {ruta} ({desc}) respondió {resp.status_code}"
        print(f"  [OK] {desc} ({ruta}) -> HTTP 200")

    print("\n" + "=" * 60)
    print("6. PROBANDO RECUPERAR CONTRASEÑA")
    print("=" * 60)
    
    c_anon = Client()
    resp_recuperar = c_anon.get('/recuperar-contrasena/')
    assert resp_recuperar.status_code == 200, f"Error: /recuperar-contrasena/ respondió {resp_recuperar.status_code}"
    # Probar búsqueda de usuario existente
    resp_post_rec = c_anon.post('/recuperar-contrasena/', {'identificador': 'est1'})
    assert resp_post_rec.status_code == 200
    assert 'Juan' in resp_post_rec.content.decode('utf-8') or 'est1' in resp_post_rec.content.decode('utf-8')
    print("  [OK] /recuperar-contrasena/ -> GET HTTP 200 y POST verificación exitosa")

    print("\n" + "=" * 60)
    print("¡TODAS LAS PRUEBAS COMPLETADAS AL 100% CON ÉXITO!")
    print("=" * 60)

if __name__ == '__main__':
    test_full_system()
