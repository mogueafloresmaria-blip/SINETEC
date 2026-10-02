import django, os, re
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()
from django.test import Client
from django.contrib.auth.models import User
from academico.models import Matricula

def check_page(client, url, label):
    try:
        r = client.get(url)
        status = r.status_code
        loc = r.get('Location', '')
        if status == 200:
            print(f"[OK-200] {label}: {url}")
        elif status in (301, 302):
            print(f"[REDIRECT-{status}] {label}: {url} -> {loc}")
        else:
            print(f"[ERROR-{status}] {label}: {url}")
    except Exception as e:
        print(f"[CRASH] {label}: {url} => {e}")

print("=== FULL ROUTE AUDIT - ADMIN ===\n")
admin_client = Client()
admin_user = User.objects.filter(username='admin').first()
admin_client.force_login(admin_user)

routes_admin = [
    ('/dashboard/', 'Dashboard'),
    ('/matriculas/', 'Matrículas'),
    ('/estudiantes/', 'Lista Estudiantes'),
    ('/academico/horarios/', 'Horarios'),
    ('/academico/fichas/', 'Fichas'),
    ('/academico/programas/', 'Programas'),
    ('/calificaciones/', 'Calificaciones'),
    ('/familias/', 'Familias'),
    ('/comunicaciones/', 'Comunicaciones'),
    ('/alertas/', 'Alertas Tempranas'),
    ('/instructores/', 'Instructores'),
    ('/pensiones/', 'Caja Pensiones'),
    ('/transporte/', 'Transporte Escolar'),
    ('/rectoria/', 'Rectoría'),
    ('/secretaria/', 'Secretaría'),
    ('/coordinacion/', 'Coordinación'),
    ('/documentos/', 'Documentos'),
    ('/biblioteca/', 'Biblioteca'),
    ('/academico/cursos/', 'Cursos'),
]

m = Matricula.objects.first()
routes_admin += [
    ('/estudiantes/%d/' % m.aprendiz.id, 'Detalle Estudiante'),
    ('/instructores/1/', 'Detalle Instructor'),
]

for url, label in routes_admin:
    check_page(admin_client, url, label)

print("\n=== FULL ROUTE AUDIT - DOCENTE ===\n")
doc_client = Client()
doc_user = User.objects.filter(username='docente').first()
doc_client.force_login(doc_user)

routes_docente = [
    ('/instructor/', 'Panel Docente'),
    ('/actividades-y-tareas/', 'Actividades'),
    ('/asistencia/', 'Asistencia'),
    ('/calificaciones-docente/', 'Calificaciones'),
    ('/horario-escolar/', 'Horario'),
    ('/mis-estudiantes/', 'Mis Estudiantes'),
    ('/mis-asignaturas/', 'Mis Asignaturas'),
    ('/mis-grupos/', 'Mis Grupos'),
    ('/comunicaciones-docente/', 'Comunicaciones'),
    ('/notificaciones-docente/', 'Notificaciones'),
    ('/recursos-docente/', 'Recursos'),
    ('/documentos-docente/', 'Documentos'),
    ('/eventos-docente/', 'Eventos'),
    ('/reportes-docente/', 'Reportes'),
    ('/perfil-profesional/', 'Perfil'),
    ('/manual-docente/', 'Manual'),
    ('/papelera-docente/', 'Papelera'),
]

for url, label in routes_docente:
    check_page(doc_client, url, label)

print("\n=== FIN ===")
