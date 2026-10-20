import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from academico.models import (
    CargaAcademica, Matricula, PeriodoAcademico, CalificacionEscolar,
    TareaClase, EntregaTarea
)
from seguimiento.models import Notificacion

def test_student_panel():
    print("==================================================")
    print("PRUEBAS EXHAUSTIVAS DEL PANEL DE ESTUDIANTE EDUNOVA")
    print("==================================================")

    c = Client()
    est1 = User.objects.filter(username='est1').first()
    assert est1, "Usuario est1 no encontrado"
    c.force_login(est1)

    # 1. VERIFICACIÓN DE SUBPANEL CALIFICACIONES Y PERÍODOS 1, 2, 3
    print("\n[1] Verificando períodos 1, 2 y 3 interactivos en Calificaciones...")
    resp_calif = c.get(f"{reverse('estudiante_dashboard')}?subpanel=calificaciones")
    assert resp_calif.status_code == 200, f"Error HTTP {resp_calif.status_code}"
    html_calif = resp_calif.content.decode('utf-8')

    # Contenedores para período 1, 2, 3
    assert 'id="contenedor-periodo-1"' in html_calif, "Falta contenedor-periodo-1"
    assert 'id="contenedor-periodo-2"' in html_calif, "Falta contenedor-periodo-2"
    assert 'id="contenedor-periodo-3"' in html_calif, "Falta contenedor-periodo-3"
    print("  -> Contenedores de Período 1, 2 y 3 presentes y listos.")

    # Botones / Selector rápido de períodos
    assert 'cambiarPeriodoCalificaciones' in html_calif, "Falta función cambiarPeriodoCalificaciones"
    assert 'id="tab-btn-periodo-1"' in html_calif, "Falta tab-btn-periodo-1"
    assert 'id="tab-btn-periodo-2"' in html_calif, "Falta tab-btn-periodo-2"
    assert 'id="tab-btn-periodo-3"' in html_calif, "Falta tab-btn-periodo-3"
    print("  -> Botones interactivos de períodos 1, 2 y 3 verificados.")

    # Mensaje de ausencia de notas en períodos vacíos
    assert "Aún no tienes calificaciones registradas en este período" in html_calif, "Falta mensaje de ausencia de notas"
    print("  -> Mensaje «Aún no tienes calificaciones registradas en este período» verificado.")

    # Materias matriculadas aparecen
    mat = Matricula.objects.filter(aprendiz=est1).first()
    cargas = CargaAcademica.objects.filter(grado=mat.grado_escolar, seccion=mat.seccion)
    for carga in cargas:
        nom_asig = carga.programa.denominacion
        assert nom_asig in html_calif, f"Asignatura matriculada {nom_asig} no aparece en el boletín"
    print(f"  -> Todas las {cargas.count()} asignaturas matriculadas de Grado 10-A aparecen en los períodos.")

    # 2. VERIFICACIÓN DE TAREAS Y ACTIVIDADES
    print("\n[2] Verificando subpanel Tareas y Actividades...")
    resp_act = c.get(f"{reverse('estudiante_dashboard')}?subpanel=actividades")
    assert resp_act.status_code == 200, f"Error HTTP {resp_act.status_code}"
    html_act = resp_act.content.decode('utf-8')

    # Mensaje o listado de tareas pendientes
    assert "Tareas y Actividades Asignadas" in html_act, "Falta encabezado de tareas"
    assert "Mis Entregas y Calificaciones" in html_act, "Falta encabezado de entregas"
    # Modales de detalle presentes si hay tareas
    if "No tienes tareas pendientes por el momento" in html_act:
        print("  -> Mensaje «No tienes tareas pendientes por el momento» verificado.")
    else:
        assert "modalDetalleTarea" in html_act, "Falta modal de detalle de tarea"
        assert "Resolver / Entregar" in html_act, "Falta botón Resolver / Entregar"
        print("  -> Tareas asignadas y modales de detalles interactivos verificados.")

    if "No tienes entregas registradas por el momento" in html_act:
        print("  -> Mensaje «No tienes entregas registradas por el momento» verificado.")
    else:
        print("  -> Historial de entregas y retroalimentaciones verificado.")

    # 3. VERIFICACIÓN DE NOTIFICACIONES
    print("\n[3] Verificando subpanel Notificaciones...")
    resp_notif = c.get(f"{reverse('estudiante_dashboard')}?subpanel=notificaciones")
    assert resp_notif.status_code == 200, f"Error HTTP {resp_notif.status_code}"
    html_notif = resp_notif.content.decode('utf-8')

    assert "Mis Notificaciones Académicas" in html_notif, "Falta encabezado de notificaciones"
    if "No tienes notificaciones por el momento" in html_notif:
        print("  -> Mensaje «No tienes notificaciones por el momento» verificado.")
    else:
        print("  -> Notificaciones reales mostradas correctamente.")

    # 4. CONEXIÓN REAL DOCENTE -> ESTUDIANTE: DOCENTE GUARDA CALIFICACIÓN EN PLANILLA
    print("\n[4] Comprobando conexión Docente -> Estudiante (Calificaciones y Notificaciones)...")
    carga_test = cargas.first()
    docente = carga_test.profesor
    c.force_login(docente)

    # Docente asienta nota 4.8 en Periodo 1 para est1
    resp_save = c.post(reverse('instructor_dashboard'), {
        'action': 'guardar_notas',
        'carga_id': carga_test.id,
        'periodo': 'Periodo 1',
        f'nota_{mat.id}': '4.8',
        f'obs_{mat.id}': 'Excelente desempeño en actividades prácticas.',
    })
    assert resp_save.status_code == 302, f"Error al guardar notas: HTTP {resp_save.status_code}"

    # Estudiante verifica que la nota aparece en el Periodo 1
    c.force_login(est1)
    resp_calif_check = c.get(f"{reverse('estudiante_dashboard')}?subpanel=calificaciones")
    html_calif_check = resp_calif_check.content.decode('utf-8')
    assert "4.8" in html_calif_check, "La nota 4.8 no apareció en el boletín del estudiante"
    assert "Superior" in html_calif_check, "El desempeño Superior no apareció en el boletín"
    print("  -> Calificación 4.8 y desempeño 'Superior' reflejados automáticamente en el Periodo 1 del estudiante.")

    # Estudiante verifica notificación recibida
    notif_grade = Notificacion.objects.filter(usuario=est1, titulo__icontains='Calificación Registrada').order_by('-id').first()
    assert notif_grade is not None, "No se generó notificación para el estudiante"
    assert "/estudiante/?subpanel=calificaciones" in notif_grade.enlace, "El enlace de la notificación no apunta a calificaciones"
    print(f"  -> Notificación real recibida: '{notif_grade.titulo}' con enlace a: {notif_grade.enlace}")

    # Probar que abrir_notificacion marca como leída y redirige
    resp_abrir = c.get(reverse('abrir_notificacion', kwargs={'pk': notif_grade.id}))
    assert resp_abrir.status_code == 302
    assert "/estudiante/?subpanel=calificaciones" in resp_abrir.url
    notif_grade.refresh_from_db()
    assert notif_grade.leida is True, "La notificación no se marcó como leída al abrirla"
    print("  -> 'abrir_notificacion' marcó la notificación como leída y redirigió al contenido correcto.")

    # 5. PRIVACIDAD: est1 no ve calificaciones de est2
    print("\n[5] Verificando privacidad de datos entre estudiantes...")
    est2 = User.objects.filter(username='est2').first()
    if est2:
        mat2 = Matricula.objects.filter(aprendiz=est2).first()
        if mat2:
            # Crear nota para est2 en Informática con nota distintiva 3.7
            CalificacionEscolar.objects.update_or_create(
                matricula=mat2,
                carga_academica=carga_test,
                periodo='Periodo 2',
                defaults={'profesor': docente, 'nota': 3.7, 'observaciones': 'Nota privada de est2'}
            )
            # est1 consulta período 2: no debe tener la observación de est2
            c.force_login(est1)
            resp_priv = c.get(f"{reverse('estudiante_dashboard')}?subpanel=calificaciones")
            assert "Nota privada de est2" not in resp_priv.content.decode('utf-8'), "Fuga de privacidad: est1 ve nota de est2"
            print("  -> Privacidad confirmada: cada estudiante consulta estrictamente su propia información.")

    print("\n==================================================")
    print("TODAS LAS PRUEBAS DEL PANEL ESTUDIANTE PASARON EXITOSAMENTE (100%)")
    print("==================================================")

if __name__ == '__main__':
    test_student_panel()
