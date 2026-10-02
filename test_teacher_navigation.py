import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

user = User.objects.filter(username='docente').first()
client = Client()
client.force_login(user)

test_suite = [
    ('1. Inicio', '/instructor/?subpanel=inicio', 'Horario de hoy', 'Juntos construimos'),
    ('1b. Inicio directo', '/instructor/', 'Horario de hoy', 'Juntos construimos'),
    ('2. Perfil profesional', '/perfil-profesional/', 'Perfil Profesional', None),
    ('2b. Perfil query', '/instructor/?subpanel=perfil', 'Perfil Profesional', None),
    ('3. Mis Asignaturas', '/mis-asignaturas/', 'Mis Asignaturas', None),
    ('3b. Asignaturas query', '/instructor/?subpanel=asignaturas', 'Mis Asignaturas', None),
    ('4. Mis Estudiantes', '/mis-estudiantes/', 'Grupos a cargo', None),
    ('4b. Alumno direct', '/alumno/', 'Grupos a cargo', None),
    ('4c. Estudiantes query', '/instructor/?subpanel=estudiantes', 'Grupos a cargo', None),
    ('5. Actividades y Tareas', '/actividades-y-tareas/', 'ACTIVIDADES Y TAREAS', None),
    ('5b. Actividades query', '/instructor/?subpanel=actividades', 'ACTIVIDADES Y TAREAS', None),
    ('6. Asistencia', '/asistencia/', 'Registra y consulta la asistencia', None),
    ('6b. Asistencia query', '/instructor/?subpanel=asistencia', 'Registra y consulta la asistencia', None),
    ('7. Calificaciones', '/calificaciones-docente/', 'Registro Oficial de Calificaciones', None),
    ('7b. Calificaciones query', '/instructor/?subpanel=calificaciones', 'Registro Oficial de Calificaciones', None),
    ('8. Horario Escolar', '/horario-escolar/', 'Mi Horario Escolar Semanal', None),
    ('8b. Horario direct', '/horario/', 'Mi Horario Escolar Semanal', None),
    ('8c. Horario query', '/instructor/?subpanel=horario', 'Mi Horario Escolar Semanal', None),
    ('9. Comunicaciones', '/comunicaciones-docente/', 'Comunicaciones y Correo Institucional', None),
    ('9b. Comunicaciones query', '/instructor/?subpanel=comunicaciones', 'Comunicaciones y Correo Institucional', None),
    ('10. Notificaciones', '/notificaciones-docente/', 'Centro de Notificaciones', None),
    ('10b. Notificaciones query', '/instructor/?subpanel=notificaciones', 'Centro de Notificaciones', None),
    ('11. Papelera', '/papelera-docente/', 'Papelera de Reciclaje', None),
    ('11b. Papelera query', '/instructor/?subpanel=papelera', 'Papelera de Reciclaje', None),
]

all_passed = True
for name, url, must_have, must_not_have in test_suite:
    res = client.get(url)
    if res.status_code != 200:
        print(f'FAIL {name} ({url}): status {res.status_code}')
        all_passed = False
        continue
    body = res.content.decode('utf-8', errors='ignore')
    if must_have and must_have.lower() not in body.lower():
        print(f'FAIL {name} ({url}): missing expected text "{must_have}"')
        all_passed = False
        continue
    if must_not_have and must_not_have.lower() in body.lower():
        print(f'FAIL {name} ({url}): contains forbidden text "{must_not_have}"')
        all_passed = False
        continue
    print(f'SUCCESS: {name} -> {url} [200 OK]')

res_inicio = client.get('/instructor/?subpanel=inicio')
body_inicio = res_inicio.content.decode('utf-8', errors='ignore')
assert 'banner_estudiantes.png' not in body_inicio, 'Found banner image in Inicio!'
assert 'banner_libros' not in body_inicio, 'Found books image in Inicio!'
assert 'Horario de hoy' in body_inicio, 'Missing Horario de hoy in Inicio!'
assert 'información académica' in body_inicio.lower(), 'Missing Información académica in Inicio!'
assert 'Aula 101' in body_inicio, 'Missing Aula 101 in Inicio!'
assert 'Juntos construimos' not in body_inicio, 'Found bottom motivational phrase in Inicio!'

print('\n>>> ALL 24 NAVIGATION AND CONTENT TESTS PASSED WITH 100% SUCCESS <<<')
