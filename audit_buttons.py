import django, os, re
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()
from django.test import Client
from django.contrib.auth.models import User
from academico.models import Matricula

def check_page(client, url, label):
    r = client.get(url)
    if r.status_code != 200:
        print(f"[{r.status_code}] {label}: {url}")
        return
    
    html = r.content.decode('utf-8', errors='replace')
    
    # Find hrefs that look broken
    broken_urls = re.findall(r'href="([^"]*(?:None|undefined|//#|javascript:void)[^"]*)"', html)
    
    # Find buttons with onclick functions referencing undefined functions
    onclick_fns = re.findall(r"onclick=\"([^\"]+)\"", html)
    
    # Find modals and triggers
    modal_ids = set(re.findall(r'id="(modal[^"]+)"', html))
    targets = {t.lstrip('#') for t in re.findall(r'data-bs-target="([^"]+)"', html)}
    missing = targets - modal_ids
    
    issues = []
    if broken_urls:
        issues.append(f"BROKEN HREFS: {broken_urls[:3]}")
    if missing:
        issues.append(f"MISSING MODALS (triggers without modal HTML): {list(missing)[:5]}")
    
    if issues:
        print(f"[ISSUES] {label} ({url}):")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"[OK] {label}: HTTP {r.status_code}, Modals OK ({len(modal_ids)} modals, {len(targets)} triggers)")

print("=== AUDITORÍA DE BOTONES Y MODALES ===\n")

# Admin user pages
admin_client = Client()
admin_user = User.objects.filter(username='admin').first()
admin_client.force_login(admin_user)

check_page(admin_client, '/dashboard/', 'Admin > Dashboard')
check_page(admin_client, '/matriculas/', 'Admin > Matrículas')
check_page(admin_client, '/estudiantes/', 'Admin > Lista Estudiantes')

m = Matricula.objects.first()
check_page(admin_client, '/estudiantes/%d/' % m.aprendiz.id, 'Admin > Detalle Estudiante')

check_page(admin_client, '/academico/horarios/', 'Admin > Horarios')
check_page(admin_client, '/academico/fichas/', 'Admin > Fichas')
check_page(admin_client, '/academico/programas/', 'Admin > Programas')
check_page(admin_client, '/calificaciones/', 'Admin > Calificaciones')
check_page(admin_client, '/familias/', 'Admin > Familias')

# Docente user pages
doc_client = Client()
doc_user = User.objects.filter(username='docente').first()
doc_client.force_login(doc_user)

check_page(doc_client, '/instructor/', 'Docente > Dashboard Inicio')
check_page(doc_client, '/actividades-y-tareas/', 'Docente > Actividades')
check_page(doc_client, '/asistencia/', 'Docente > Asistencia')
check_page(doc_client, '/calificaciones-docente/', 'Docente > Calificaciones')
check_page(doc_client, '/horario-escolar/', 'Docente > Horario')
check_page(doc_client, '/mis-estudiantes/', 'Docente > Mis Estudiantes')
check_page(doc_client, '/mis-estudiantes/?estudiante_id=%d&tab=info' % m.aprendiz.id, 'Docente > Ficha Estudiante')
check_page(doc_client, '/comunicaciones-docente/', 'Docente > Comunicaciones')
check_page(doc_client, '/notificaciones-docente/', 'Docente > Notificaciones')

print("\n=== FIN DE AUDITORÍA ===")
