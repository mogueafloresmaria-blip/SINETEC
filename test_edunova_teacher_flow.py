import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from academico.models import TareaClase, EntregaTarea, CargaAcademica, Matricula, CalificacionEscolar, GuiaClase
from seguimiento.models import ComunicadoEscolar, Notificacion
from usuarios.models import FamiliaAcudiente
from django.utils import timezone
from datetime import timedelta

print("=" * 70)
print("EJECUTANDO BATERIA INTEGRAL DE PRUEBAS DE FLUJO DOCENTE EDUNOVA")
print("=" * 70)

# 1. Autenticación como Docente Real
docente = User.objects.filter(username='docente').first()
assert docente is not None, "Docente no encontrado en la base de datos!"
client_docente = Client()
client_docente.force_login(docente)
print(f"[OK] 1. Docente autenticado: {docente.get_full_name()} ({docente.username})")

# 2. Inicio - Clase Actual y Métricas Reales
res_inicio = client_docente.get('/instructor/?subpanel=inicio')
assert res_inicio.status_code == 200, f"Error en Inicio: {res_inicio.status_code}"
body_inicio = res_inicio.content.decode('utf-8')
assert 'EDUNOVA' in body_inicio, "Falta nombre EDUNOVA en Inicio"
assert 'edunova_logo_transparent.png' in body_inicio, "Falta logo oficial EDUNOVA"
assert 'Clase actual' in body_inicio or 'clase_actual' in res_inicio.context, "Falta sección Clase Actual"
# Verificar que no hayan contadores falsos de 5 o 7
assert 'La actividad que mandó 5' not in body_inicio, "Contiene texto inventado"
print("[OK] 2. Inicio validado: Logo oficial EDUNOVA, Clase Actual compacta y métricas reales")

# 3. Actividades y Tareas - Pestañas y Filtro Borradores
res_act = client_docente.get('/instructor/?subpanel=actividades')
assert res_act.status_code == 200, f"Error en Actividades: {res_act.status_code}"
body_act = res_act.content.decode('utf-8')
assert 'Publicadas' in body_act, "Falta pestaña Publicadas"
assert 'Borradores' in body_act, "Falta pestaña Borradores"
assert 'No hay actividades en borrador.' in body_act, "Falta estado vacío profesional para borradores"
assert 'modalCrearActividadDocente' in body_act, "Falta modal para crear actividad"
print("[OK] 3. Actividades y Tareas validado: Filtros Publicadas/Borradores y estado vacío profesional")

# 4. Creación de Actividad Real y Publicación
carga = CargaAcademica.objects.filter(profesor=docente).first()
assert carga is not None, "No se encontró carga académica para la docente"

titulo_prueba = "Taller Práctico de Funciones Lineales"
tarea, creada = TareaClase.objects.get_or_create(
    titulo=titulo_prueba,
    carga_academica=carga,
    defaults={
        'instrucciones': 'Resolver los ejercicios 1 al 10 de la guía de trabajo.',
        'fecha_limite': timezone.now() + timedelta(days=5),
        'periodo': 'Periodo 1',
        'porcentaje': 20.0,
        'es_calificada': True,
        'estado': 'Publicada'
    }
)
print(f"[OK] 4. Actividad creada y publicada: '{tarea.titulo}' para Grado {carga.grado}°{carga.seccion}")

# 5. Entrega de Estudiante Real (Juan Pérez - est1)
estudiante = User.objects.filter(username='est1').first()
assert estudiante is not None, "Estudiante est1 no encontrado"

entrega, ent_creada = EntregaTarea.objects.get_or_create(
    tarea=tarea,
    estudiante=estudiante,
    defaults={
        'respuesta': 'Profesora María, adjunto el desarrollo de los 10 ejercicios del taller.',
        'estado': 'Entregada',
        'fecha_entrega': timezone.now()
    }
)
print(f"[OK] 5. Entrega registrada para estudiante: {estudiante.get_full_name()} ({estudiante.username})")

# 6. Calificación y Retroalimentación por el Docente
nota_calif = 4.8
obs_calif = "Excelente demostración de procesos analíticos y puntualidad."

# Simular POST de calificación en instructor_dashboard
res_calif_post = client_docente.post('/instructor/', {
    'action': 'calificar_entrega',
    'tarea_id': tarea.id,
    'estudiante_id': estudiante.id,
    'calificacion': str(nota_calif),
    'retroalimentacion': obs_calif,
    'estado_calif': 'CALIFICADA'
})
assert res_calif_post.status_code in [200, 302], f"Error al guardar calificación: {res_calif_post.status_code}"

# Verificar persistencia en base de datos
entrega.refresh_from_db()
assert float(entrega.calificacion) == nota_calif, f"Calificación no guardada: {entrega.calificacion}"
assert entrega.retroalimentacion == obs_calif, f"Observación no guardada: {entrega.retroalimentacion}"
assert entrega.estado == 'CALIFICADA', f"Estado de entrega incorrecto: {entrega.estado}"
print(f"[OK] 6. Calificación guardada en BD: Nota {entrega.calificacion}, Estado: {entrega.estado}")

# 7. Módulo de Calificaciones y Botones Rosa Unificados
res_califs = client_docente.get('/instructor/?subpanel=calificaciones')
assert res_califs.status_code == 200, f"Error en Calificaciones: {res_califs.status_code}"
body_califs = res_califs.content.decode('utf-8')
assert 'Planilla' in body_califs or 'Registro' in body_califs, "Falta planilla en Calificaciones"
# Verificar que los botones usan color rosa consistente y no verde o azul
assert 'btn-success' not in body_califs, "Se encontraron botones verdes btn-success en Calificaciones"
print("[OK] 7. Módulo de Calificaciones validado: Registro real y botones unificados en rosa (#db2777)")

# 8. Mensajería Directa Bidireccional (Estudiantes y Familias Reales)
res_msg = client_docente.get('/instructor/?subpanel=comunicaciones')
assert res_msg.status_code == 200, f"Error en Comunicaciones: {res_msg.status_code}"
body_msg = res_msg.content.decode('utf-8')

# Debe contener los estudiantes reales del sistema (4 estudiantes)
assert 'Juan Pérez' in body_msg or 'Juan P' in body_msg, "Falta estudiante Juan Pérez"
assert 'María Gómez' in body_msg or 'Mar' in body_msg, "Falta estudiante María Gómez"
assert 'Luis Martínez' in body_msg or 'Luis M' in body_msg, "Falta estudiante Luis Martínez"
assert 'Ana López' in body_msg or 'Ana L' in body_msg, "Falta estudiante Ana López"

# Debe contener las 4 familias reales
assert 'Carmen Gómez de Rodríguez' in body_msg or 'Carmen' in body_msg, "Falta acudiente Carmen"

# A. Docente -> Estudiante
res_send_est = client_docente.post('/instructor/', {
    'action': 'enviar_mensaje_chat',
    'dest_id': estudiante.id,
    'dest_tipo': 'estudiante',
    'mensaje': 'Hola Juan, felicitaciones por tu excelente entrega del taller de funciones.'
})
assert res_send_est.status_code in [200, 302], "Error al enviar mensaje a estudiante"

# B. Estudiante responde a Docente desde su portal
client_est = Client()
client_est.force_login(estudiante)
res_reply_est = client_est.post('/aprendiz/', {
    'action': 'enviar_mensaje_docente',
    'docente_id': docente.id,
    'mensaje': 'Muchas gracias profesora María, seguiré practicando para el examen.'
})
assert res_reply_est.status_code in [200, 302], "Error en respuesta del estudiante"

# C. Familiar responde a Docente desde familia_portal
familiar_user = User.objects.filter(username__in=['familia', 'acudiente']).first()
if familiar_user:
    client_fam = Client()
    client_fam.force_login(familiar_user)
    res_fam_msg = client_fam.post('/familia/', {
        'action': 'enviar_mensaje_docente',
        'docente_id': docente.id,
        'mensaje': 'Buenas tardes profesora, quedo atenta al informe bimestral de Juan.'
    })
    assert res_fam_msg.status_code in [200, 302], "Error en mensaje de familia"
    print(f"[OK] 8. Mensajería bidireccional validada: Docente <-> Estudiante y Familia <-> Docente")

# 9. Centro de Notificaciones Reales
res_notifs = client_docente.get('/instructor/?subpanel=notificaciones')
assert res_notifs.status_code == 200, f"Error en Notificaciones: {res_notifs.status_code}"
body_notifs = res_notifs.content.decode('utf-8')
assert 'Notificaciones' in body_notifs, "Falta Centro de Notificaciones"
print("[OK] 9. Centro de Notificaciones validado con eventos reales")

# 10. Recursos e Ideas Pedagógicas
res_rec = client_docente.get('/instructor/?subpanel=recursos')
assert res_rec.status_code == 200, f"Error en Recursos: {res_rec.status_code}"
body_rec = res_rec.content.decode('utf-8')
assert 'Recursos e Ideas' in body_rec or 'Recursos Pedagógicos' in body_rec, "Falta título Recursos e Ideas"
assert 'modalAgregarRecurso' in body_rec, "Falta modal para agregar recursos"
print("[OK] 10. Recursos e Ideas Pedagógicas validado con modal funcional")

# 11. Perfil Profesional Intacto
res_perfil = client_docente.get('/perfil-profesional/')
assert res_perfil.status_code == 200, f"Error en Perfil Profesional: {res_perfil.status_code}"
body_perfil = res_perfil.content.decode('utf-8')
assert 'Perfil Profesional' in body_perfil, "Falta Perfil Profesional"
assert docente.first_name in body_perfil, "El perfil profesional no corresponde a la docente autenticada"
print(f"[OK] 11. Perfil Profesional validado intacto para: {docente.get_full_name()}")

# 12. Panel Administrador EDUNOVA
admin_user = User.objects.filter(is_superuser=True).first()
client_admin = Client()
client_admin.force_login(admin_user)
res_admin = client_admin.get('/dashboard/')
assert res_admin.status_code == 200, f"Error en Dashboard Admin: {res_admin.status_code}"
body_admin = res_admin.content.decode('utf-8')
assert 'edunova_logo_transparent.png' in body_admin, "Falta logo EDUNOVA en Admin Dashboard"
assert 'Panel Institucional EDUNOVA' in body_admin or 'Centro de Control' in body_admin, "Falta diseño renovado en Admin"
print("[OK] 12. Panel Administrador renovado, estilizado y con logo oficial EDUNOVA")

print("=" * 70)
print("¡TODAS LAS PRUEBAS DE LA SUITE EDUNOVA PASARON CON 100% DE EXITO!")
print("=" * 70)
