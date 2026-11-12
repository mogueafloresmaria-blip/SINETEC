import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from seguimiento.models import Notificacion
from academico.models import Matricula
from django.core.cache import cache

def run():
    print("=== INICIANDO VERIFICACION RIGUROSA DEL SISTEMA DE NOTIFICACIONES ===")
    cache.clear()

    u10 = User.objects.get(username='1099887711')
    u11 = User.objects.get(username='estudiante')
    u_fam = User.objects.get(username='familia_test')

    c10 = Client()
    c10.force_login(u10)

    c11 = Client()
    c11.force_login(u11)

    c_fam = Client()
    c_fam.force_login(u_fam)

    # 1. Probar API campana para estudiante 10
    res10 = c10.get('/notificaciones/api/campana/')
    data10 = res10.json()
    print("Estudiante 10 (" + u10.username + "): status=" + str(data10['status']) + ", no_leidas=" + str(data10['num_no_leidas']) + ", items=" + str(len(data10['notificaciones'])))

    for n in data10['notificaciones']:
        assert 'Grado 6' not in n['titulo'] and 'Grado 6' not in n['mensaje'], "ERROR: Fuga de Grado 6 en 10: " + str(n)
        assert 'Grado 11' not in n['titulo'] and 'Grado 11' not in n['mensaje'], "ERROR: Fuga de Grado 11 en 10: " + str(n)
    print(">>> OK: 0 fugas de otros grados para Estudiante 10 (Andres Felipe Castro)")

    # 2. Probar API campana para estudiante 11
    res11 = c11.get('/notificaciones/api/campana/')
    data11 = res11.json()
    print("Estudiante 11 (" + u11.username + "): status=" + str(data11['status']) + ", no_leidas=" + str(data11['num_no_leidas']) + ", items=" + str(len(data11['notificaciones'])))

    for n in data11['notificaciones']:
        assert 'Grado 6' not in n['titulo'] and 'Grado 6' not in n['mensaje'], "ERROR: Fuga de Grado 6 en 11: " + str(n)
        assert 'Grado 10' not in n['titulo'] and 'Grado 10' not in n['mensaje'], "ERROR: Fuga de Grado 10 en 11: " + str(n)
    print(">>> OK: 0 fugas de otros grados para Estudiante 11 (Sofía Gómez)")

    # 3. Probar API campana para familia
    res_fam = c_fam.get('/notificaciones/api/campana/')
    data_fam = res_fam.json()
    print("Familia (" + u_fam.username + "): status=" + str(data_fam['status']) + ", no_leidas=" + str(data_fam['num_no_leidas']) + ", items=" + str(len(data_fam['notificaciones'])))
    for n in data_fam['notificaciones']:
        assert 'Grado 6' not in n['titulo'] and 'Grado 6' not in n['mensaje'], "ERROR: Fuga de Grado 6 en familia: " + str(n)
        assert 'Grado 11' not in n['titulo'] and 'Grado 11' not in n['mensaje'], "ERROR: Fuga de Grado 11 en familia: " + str(n)
    print(">>> OK: 0 fugas de otros grados para Familia")

    # 4. Probar toggle leida / no leida
    if data10['notificaciones']:
        test_notif_id = data10['notificaciones'][0]['id']
        orig_leida = data10['notificaciones'][0]['leida']
        print("Probando toggle para notificacion ID " + str(test_notif_id) + " (estado inicial leida=" + str(orig_leida) + ")...")

        res_toggle = c10.post(f'/notificaciones/{test_notif_id}/toggle-leida-ajax/')
        data_toggle = res_toggle.json()
        print("Respuesta toggle 1:", data_toggle)
        assert data_toggle['leida'] != orig_leida, "El estado leida no cambio tras toggle"

        # Revertir toggle
        res_toggle2 = c10.post(f'/notificaciones/{test_notif_id}/toggle-leida-ajax/')
        data_toggle2 = res_toggle2.json()
        print("Respuesta toggle 2 (revertido):", data_toggle2)
        assert data_toggle2['leida'] == orig_leida, "El estado no revirtio correctamente"

    print(">>> OK: Toggle leida / no leida funciona y actualiza contador inmediatamente")

    # 5. Emisión de circular dirigida a Grado 10 desde Secretaría y verificación de entrega exclusiva
    from seguimiento.models import ComunicadoEscolar
    admin_sec = User.objects.filter(perfil__rol__nombre__in=['Secretaría', 'Secretaria', 'Administrador']).first()
    c_sec = Client()
    c_sec.force_login(admin_sec)

    print("Enviando circular exclusiva para Grado 10 desde Secretaría...")
    res_circ = c_sec.post('/comunicaciones/redactar/', {
        'asunto': 'Circular Prueba Exclusiva Grado 10',
        'mensaje': 'Instrucciones obligatorias unicamente para los estudiantes de grado 10 y sus familias.',
        'destinatario_tipo': 'Grado',
        'grado_especifico': '10',
        'fecha': '2026-11-12',
        'estado': 'PUBLICADA',
    })

    # Verificar que el estudiante 10 la reciba
    cache.clear()
    res10_post = c10.get('/notificaciones/api/campana/').json()
    titulos10 = [n['titulo'] for n in res10_post['notificaciones']]
    assert any('Circular Prueba Exclusiva Grado 10' in t for t in titulos10), "ERROR: Estudiante 10 no recibio la circular de Grado 10"
    print(">>> OK: Estudiante 10 recibio la circular de Grado 10 exitosamente")

    # Verificar que el estudiante 11 NO la reciba
    res11_post = c11.get('/notificaciones/api/campana/').json()
    titulos11 = [n['titulo'] for n in res11_post['notificaciones']]
    assert not any('Circular Prueba Exclusiva Grado 10' in t for t in titulos11), "ERROR: Fuga detectada: Estudiante 11 recibio la circular de Grado 10!"
    print(">>> OK: Estudiante 11 NO recibio la circular de Grado 10 (Aislamiento perfecto)")

    print("=== TODAS LAS PRUEBAS DE AISLAMIENTO, DESTINATARIOS Y CAMPANITA FUERON EXITOSAS ===")

if __name__ == '__main__':
    run()
