import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.contrib.auth.models import User
from academico.models import CargaAcademica, Matricula, TareaClase, HorarioFicha, DocumentoInstitucional, GuiaClase, CalificacionEscolar
from seguimiento.models import Notificacion, ComunicadoEscolar, AsistenciaAprendiz
from usuarios.models import FamiliaAcudiente, PerfilUsuario

print("=== DOCENTE INFO ===")
docente = User.objects.filter(username='docente').first()
if docente:
    print(f"Docente: {docente.username} - {docente.get_full_name()} (email: {docente.email})")
    print("\n--- Cargas Académicas ---")
    for c in CargaAcademica.objects.filter(profesor=docente):
        prog = c.programa.denominacion if c.programa else "N/A"
        print(f"  Carga #{c.id}: Grado {c.grado}°{c.seccion} | Asignatura: {prog} | Nivel: {c.nivel}")

    print("\n--- Horarios ---")
    for h in HorarioFicha.objects.filter(instructor=docente, activo=True):
        print(f"  Horario #{h.id}: Dia {h.dia} {h.hora_inicio}-{h.hora_fin} | Grado {h.grado}°{h.seccion} | {h.nombre_materia} | {h.ambiente}")

    print("\n--- Notificaciones ---")
    notifs = Notificacion.objects.filter(usuario=docente)
    print(f"  Total notificaciones: {notifs.count()}, No leidas: {notifs.filter(leida=False).count()}")
    for n in notifs:
        print(f"    ID {n.id}: leida={n.leida} | {n.titulo} | {n.fecha_creacion}")

print("\n=== MATRICULAS (TODAS) ===")
for m in Matricula.objects.all():
    print(f"  Mat #{m.id}: {m.aprendiz.username} ({m.aprendiz.get_full_name()}) | Grado: {m.grado_escolar}°{m.seccion} | Estado: {m.estado_formacion} | Acudiente: {m.acudiente_nombre}")

print("\n=== FAMILIAS ===")
for f in FamiliaAcudiente.objects.all():
    ests = [f"{e.username} ({e.get_full_name()})" for e in f.estudiantes.all()]
    print(f"  Familia #{f.id}: Acudiente: {f.nombre_acudiente} (User: {f.usuario.username if f.usuario else 'None'}) | Estudiantes: {ests}")

print("\n=== DOCUMENTOS INSTITUCIONALES ===")
for d in DocumentoInstitucional.objects.all():
    print(f"  Doc #{d.id}: {d.titulo} | Tipo: {d.tipo} | Creado por: {d.creado_por}")

print("\n=== GUIAS CLASE ===")
for g in GuiaClase.objects.all():
    print(f"  Guia #{g.id}: {g.titulo} | Carga: {g.carga_academica}")
