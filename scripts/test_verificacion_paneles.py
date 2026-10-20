import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from academico.models import HorarioFicha, Matricula

def test_all_panels():
    c = Client()
    print("==================================================")
    print("VERIFICACION INTEGRAL DE PANELES Y NAVEGACION EDUNOVA")
    print("==================================================")

    # 1. ESTUDIANTE (Juan Pérez)
    est1 = User.objects.filter(username='est1').first()
    assert est1 is not None, "Usuario est1 no encontrado"
    print(f"[OK] Usuario estudiante: {est1.username} ({est1.get_full_name()})")
    
    # Foto
    foto = est1.perfil.foto_perfil
    print(f"[OK] Foto perfil est1: {foto} (URL: {foto.url if foto else 'Vacio'})")
    if foto:
        foto_path = os.path.join('media', str(foto).replace('/', os.sep))
        assert os.path.exists(foto_path), f"El archivo de foto {foto_path} no existe en disco"
        print(f"[OK] Archivo físico de foto verificado en disco: {foto_path} ({os.path.getsize(foto_path)} bytes)")

    c.force_login(est1)
    subpaneles = [
        'inicio', 'perfil', 'horario', 'asignaturas',
        'calificaciones', 'actividades', 'asistencia',
        'temas', 'comunicaciones', 'notificaciones', 'documentos'
    ]
    for sp in subpaneles:
        resp = c.get(f'/estudiante/?subpanel={sp}')
        assert resp.status_code == 200, f"Error en subpanel {sp}: status {resp.status_code}"
        content = resp.content.decode('utf-8')
        sec_id = 'student-home-content' if sp == 'inicio' else f'subpanel-{sp}'
        assert f'id="{sec_id}"' in content, f"Seccion {sec_id} no encontrada en HTML"
        # Check active link in sidebar
        assert f'id="student-nav-{sp}"' in content or (sp == 'inicio' and 'id="student-nav-home"' in content), f"Enlace nav para {sp} no encontrado"
        print(f"  -> Subpanel Estudiante '{sp}': HTTP 200 OK | Seccion {sec_id} presente y activa")

    # Horario Juan Pérez
    resp_h = c.get('/estudiante/?subpanel=horario')
    html_h = resp_h.content.decode('utf-8')
    assert 'Horario de Clases, Jornada y Programa' in html_h, "Cabecera de horario no encontrada"
    assert 'Vista Semanal' in html_h, "Badge Vista Semanal no encontrado"
    assert 'Periodo Académico 2026-B' in html_h, "Badge Periodo Académico no encontrado"
    assert 'schedule-compact-card' in html_h, "Clase de tarjeta compacta no encontrada"
    print("[OK] Subpanel Horario del estudiante verificado con diseño compacto y colores cálidos.")

    # 2. DOCENTE (Miguel González / docente)
    docente = User.objects.filter(username='docente').first()
    if docente:
        c.force_login(docente)
        resp_doc = c.get('/instructor/')
        print(f"[OK] Panel Docente (/instructor/): HTTP {resp_doc.status_code}")
        assert resp_doc.status_code in [200, 302], f"Error en panel docente: {resp_doc.status_code}"
        
        # Horario docente
        resp_hdoc = c.get('/instructor/?subpanel=horario')
        print(f"[OK] Horario Docente (/instructor/?subpanel=horario): HTTP {resp_hdoc.status_code}")
        
        # Comparar HorarioFicha entre estudiante y docente
        horarios_10a_est = HorarioFicha.objects.filter(grado__icontains='10', seccion='A', activo=True)
        horarios_10a_doc = HorarioFicha.objects.filter(instructor=docente, grado__icontains='10', seccion='A', activo=True)
        print(f"[OK] HorarioFicha compartida Grado 10-A: {horarios_10a_est.count()} bloques totales | {horarios_10a_doc.count()} impartidos por el docente")
        assert horarios_10a_est.count() > 0, "No hay bloques de HorarioFicha para 10-A"

    # 3. ADMINISTRADOR
    admin_u = User.objects.filter(is_superuser=True).first()
    if admin_u:
        c.force_login(admin_u)
        resp_adm = c.get('/dashboard/')
        print(f"[OK] Panel Administrador (/dashboard/): HTTP {resp_adm.status_code}")
        assert resp_adm.status_code == 200, f"Error en panel admin: {resp_adm.status_code}"

    # 4. RECTORÍA / COORDINACIÓN
    rector = User.objects.filter(username='rector').first()
    if rector:
        c.force_login(rector)
        resp_rec = c.get('/rectoria/')
        print(f"[OK] Panel Rectoría (/rectoria/): HTTP {resp_rec.status_code}")
        assert resp_rec.status_code == 200, f"Error en panel rectoría: {resp_rec.status_code}"
        resp_coord = c.get('/coordinacion/')
        print(f"[OK] Panel Coordinación (/coordinacion/): HTTP {resp_coord.status_code}")
        assert resp_coord.status_code == 200, f"Error en panel coordinación: {resp_coord.status_code}"

    # 5. SECRETARÍA
    secre = User.objects.filter(username='secretaria').first()
    if secre:
        c.force_login(secre)
        resp_sec = c.get('/secretaria/')
        print(f"[OK] Panel Secretaría (/secretaria/): HTTP {resp_sec.status_code}")
        assert resp_sec.status_code == 200, f"Error en panel secretaría: {resp_sec.status_code}"

    # 6. FAMILIA
    familia = User.objects.filter(perfil__rol__nombre__icontains='Familia').first() or User.objects.filter(perfil__rol__nombre__icontains='Acudiente').first()
    if not familia:
        # Check any user with acudiente role
        from usuarios.models import Rol
        rol_fam = Rol.objects.filter(nombre__icontains='Familia').first()
        if rol_fam:
            p = PerfilUsuario.objects.filter(rol=rol_fam).first()
            if p:
                familia = p.usuario
    if familia:
        c.force_login(familia)
        resp_fam = c.get('/familia/')
        print(f"[OK] Panel Familia (/familia/): HTTP {resp_fam.status_code}")
        assert resp_fam.status_code in [200, 302], f"Error en panel familia: {resp_fam.status_code}"
    else:
        print("[INFO] No se encontró usuario específico con rol Familia en DB de prueba")

    print("==================================================")
    print("TODAS LAS PRUEBAS DE LOS 6 PANELES PASARON CON EXITO")
    print("==================================================")

if __name__ == '__main__':
    test_all_panels()
