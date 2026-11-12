import os, sys, django
sys.path.insert(0, r'c:\EDUNOVA\EDUNOVA')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from academico.models import Matricula

def test_carla_matricula():
    print("=" * 80)
    print("TEST: VERIFICACIÓN DE CARLA Y SELECCIÓN DE ESTUDIANTES EN MATRÍCULA")
    print("=" * 80)

    client = Client()
    # Login como Secretaría
    client.login(username='test_sec_mat', password='12345')

    # 1. Cargar el formulario de matrícula
    resp = client.get('/academico/matriculas/nueva/')
    assert resp.status_code == 200, f"Error al cargar nueva_matricula: {resp.status_code}"
    html = resp.content.decode('utf-8')

    # 2. Verificar que Carla aparece en el HTML y en la lista de estudiantes
    assert 'carla flores' in html.lower(), "Carla Flores NO aparece en el HTML del formulario de matrícula"
    assert '1745637476' in html, "El documento de Carla (1745637476) NO aparece en el formulario"
    print("  [OK] Carla Flores encontrada en la lista de estudiantes (Nombre y Documento presentes)")

    # 3. Verificar que los demás estudiantes también aparecen
    carla_user = User.objects.filter(username='1745637476').first()
    assert carla_user is not None, "Carla no existe en la base de datos MySQL"
    print(f"  [OK] Usuario de Carla en MySQL: ID={carla_user.id}, Nombre={carla_user.get_full_name()}, Doc={carla_user.username}")

    total_filas = html.count('alumno-fila-item')
    assert total_filas >= 20, f"Número bajo de estudiantes en la lista: {total_filas}"
    print(f"  [OK] Total de estudiantes renderizados en el selector: {total_filas}")

    # 4. Probar matriculación seleccionando a Carla (alumno_id=378) en un grado nuevo (ej. Grado 5° Sección B)
    # Limpiar matrícula previa en Grado 5 si existe
    Matricula.objects.filter(aprendiz=carla_user, grado_escolar='5').delete()

    resp_post = client.post('/academico/matriculas/nueva/', {
        'alumno_id': carla_user.id,
        'grado_escolar': '5',
        'seccion': 'B',
        'jornada': 'Mañana'
    }, follow=True)

    assert resp_post.status_code == 200, f"Error al procesar matrícula de Carla: {resp_post.status_code}"
    
    # 5. Comprobar que la matrícula de Carla se guardó en MySQL
    mat_carla = Matricula.objects.filter(aprendiz=carla_user, grado_escolar='5', seccion='B', estado_formacion='En Formacion').first()
    assert mat_carla is not None, "La matrícula de Carla en Grado 5° Sección B NO se guardó en MySQL"
    print(f"  [OK] Matrícula de Carla guardada exitosamente en MySQL: ID #{mat_carla.id}, Grado {mat_carla.grado_escolar}°-{mat_carla.seccion}")

    # 6. Consultar la lista de matrículas y verificar que Carla aparece
    resp_lista = client.get('/estudiantes/matriculas/?q=Carla')
    assert resp_lista.status_code == 200, "Error al consultar lista de matrículas"
    assert 'carla' in resp_lista.content.decode('utf-8').lower(), "Carla no aparece en la lista general de matrículas"
    print("  [OK] Carla visible y filtrable en el listado general de matrículas de Secretaría")

    print("\n" + "=" * 80)
    print("TODAS LAS PRUEBAS DE CARLA Y SELECCIÓN DE ESTUDIANTES PASARON EXITOSAMENTE (100% OK)")
    print("=" * 80)

if __name__ == '__main__':
    test_carla_matricula()
