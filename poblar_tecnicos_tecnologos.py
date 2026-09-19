import os
import sys
import uuid
from datetime import date, timedelta

sys.path.insert(0, r'c:\SINETEC\SINETEC')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')

import django
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from usuarios.models import Rol, PerfilUsuario, FichaSena, ResultadoAprendizaje as RapUsuario, EvidenciaTaller, CalificacionEvidencia
from instituciones.models import InstitucionEducativa
from academico.models import (
    ProgramaFormacion, Ficha, Competencia, ResultadoAprendizaje as RapCurricular,
    Matricula, RecursoBiblioteca, DocumentoInstitucional, ProyectoInnovacion
)
from seguimiento.models import (
    BitacoraSeguimiento, AsistenciaAprendiz, CasoAlertaTemprana, CompromisoFormativo,
    EmpresaConvenio, EtapaProductiva, BitacoraEtapaProductiva, MensajeSeguimiento
)

print("Iniciando carga de Técnicos, Tecnólogos y módulos de SINETEC...")

# 1. Asegurar Roles
rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador', defaults={'descripcion': 'Administrador general'})
rol_coord, _ = Rol.objects.get_or_create(nombre='Coordinador', defaults={'descripcion': 'Coordinador Académico Media Técnica'})
rol_inst, _ = Rol.objects.get_or_create(nombre='Instructor', defaults={'descripcion': 'Instructor SENA Líder'})
rol_est, _ = Rol.objects.get_or_create(nombre='Estudiante', defaults={'descripcion': 'Aprendiz de Media Técnica'})
rol_sec, _ = Rol.objects.get_or_create(nombre='Secretaria', defaults={'descripcion': 'Personal de Secretaría Técnica'})

# 2. Instituciones Educativas en el Magdalena
colegios_data = [
    {"dane": "147001000123", "nombre": "I.E.D. Escuela Normal Superior San Pedro Alejandrino", "muni": "Santa Marta", "dir": "Av. del Libertador No. 39-105"},
    {"dane": "147001000456", "nombre": "I.E.D. INEM Simón Bolívar", "muni": "Santa Marta", "dir": "Troncal del Caribe Km 3"},
    {"dane": "147001000789", "nombre": "I.E.D. Liceo Samario", "muni": "Santa Marta", "dir": "Calle 16 No. 18-40"},
    {"dane": "147001001012", "nombre": "I.E.D. Rodrigo de Bastidas", "muni": "Santa Marta", "dir": "Calle 10 No. 55-20"},
    {"dane": "147001001345", "nombre": "I.E.D. Técnico Industrial de Santa Marta", "muni": "Santa Marta", "dir": "Av. Libertador No. 25-10"},
    {"dane": "147189000111", "nombre": "I.E.T. Departamental de Ciénaga", "muni": "Ciénaga", "dir": "Calle 17 No. 12-30"},
]
colegios = {}
for c in colegios_data:
    obj, _ = InstitucionEducativa.objects.get_or_create(
        codigo_dane=c["dane"],
        defaults={"nombre": c["nombre"], "municipio": c["muni"], "direccion": c["dir"], "telefono": "3001234567"}
    )
    colegios[c["dane"]] = obj

# 3. Programas: Técnicos y Tecnólogos
programas_data = [
    # Técnicos
    {"codigo": "228118", "nombre": "Técnico en Programación de Software", "version": "1"},
    {"codigo": "233101", "nombre": "Técnico en Sistemas", "version": "2"},
    {"codigo": "133100", "nombre": "Técnico en Contabilización de Operaciones Comerciales y Financieras", "version": "1"},
    {"codigo": "134101", "nombre": "Técnico en Asistencia Administrativa", "version": "2"},
    {"codigo": "839312", "nombre": "Técnico en Mantenimiento de Equipos de Cómputo", "version": "1"},
    {"codigo": "524100", "nombre": "Técnico en Integración de Contenidos Digitales", "version": "1"},
    # Tecnólogos
    {"codigo": "228106", "nombre": "Tecnólogo en Análisis y Desarrollo de Software (ADSO)", "version": "1"},
    {"codigo": "228101", "nombre": "Tecnólogo en Gestión de Redes de Datos", "version": "1"},
    {"codigo": "112005", "nombre": "Tecnólogo en Gestión del Talento Humano", "version": "2"},
    {"codigo": "122115", "nombre": "Tecnólogo en Gestión Administrativa", "version": "1"},
]
programas = {}
for p in programas_data:
    obj, _ = ProgramaFormacion.objects.get_or_create(
        codigo_programa=p["codigo"],
        defaults={"denominacion": p["nombre"], "version": p["version"], "activo": True}
    )
    programas[p["codigo"]] = obj

# Competencias y RAPs
for p_cod, prog in programas.items():
    comp, _ = Competencia.objects.get_or_create(
        programa=prog,
        codigo=f"COMP-{p_cod[:4]}",
        defaults={"descripcion": f"Desarrollar competencias técnicas principales de {prog.denominacion}."}
    )
    RapCurricular.objects.get_or_create(
        competencia=comp,
        codigo=f"RAP-01-{p_cod[:4]}",
        defaults={"descripcion": f"Apropiar fundamentos teóricos y conceptuales de {prog.denominacion}."}
    )
    RapCurricular.objects.get_or_create(
        competencia=comp,
        codigo=f"RAP-02-{p_cod[:4]}",
        defaults={"descripcion": f"Aplicar metodologías prácticas y talleres de simulación en {prog.denominacion}."}
    )
    RapCurricular.objects.get_or_create(
        competencia=comp,
        codigo=f"RAP-03-{p_cod[:4]}",
        defaults={"descripcion": f"Construir producto técnico final y sustentar ante el comité evaluador."}
    )

# 4. Instructores
instructores_data = [
    {"username": "instructor_adso", "nombre": "Carlos", "apellido": "Mendoza Polo", "doc": "85441230", "email": "cmendoza@sena.edu.co"},
    {"username": "instructor_sistemas", "nombre": "Patricia", "apellido": "Vargas Cotes", "doc": "57231450", "email": "pvargas@sena.edu.co"},
    {"username": "instructor_contable", "nombre": "Hernán", "apellido": "Gutiérrez Díaz", "doc": "12654320", "email": "hgutierrez@sena.edu.co"},
    {"username": "instructor_admin", "nombre": "Luz Marina", "apellido": "Pérez Rivas", "doc": "36987120", "email": "lperez@sena.edu.co"},
]
instructores = {}
for i in instructores_data:
    user, created = User.objects.get_or_create(
        username=i["username"],
        defaults={"first_name": i["nombre"], "last_name": i["apellido"], "email": i["email"]}
    )
    if created:
        user.set_password("Sena2026*")
        user.save()
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user)
    perfil.rol = rol_inst
    perfil.numero_documento = i["doc"]
    perfil.telefono = "3158901234"
    perfil.save()
    instructores[i["username"]] = user

# 5. Fichas de Media Técnica
hoy = timezone.localdate()
fecha_inicio = hoy - timedelta(days=200)
fecha_fin = hoy + timedelta(days=165)

fichas_config = [
    {"codigo": "3173430", "prog": "228118", "dane": "147001000123", "inst": "instructor_adso"},
    {"codigo": "2824910", "prog": "228106", "dane": "147001000456", "inst": "instructor_adso"},
    {"codigo": "2694120", "prog": "233101", "dane": "147001000789", "inst": "instructor_sistemas"},
    {"codigo": "2791820", "prog": "228101", "dane": "147001001012", "inst": "instructor_sistemas"},
    {"codigo": "2718340", "prog": "133100", "dane": "147001001345", "inst": "instructor_contable"},
    {"codigo": "2683900", "prog": "112005", "dane": "147189000111", "inst": "instructor_admin"},
]
fichas = {}
for f in fichas_config:
    obj, _ = Ficha.objects.get_or_create(
        codigo_ficha=f["codigo"],
        defaults={
            "programa": programas[f["prog"]],
            "institucion": colegios[f["dane"]],
            "instructor_lider": instructores[f["inst"]],
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "estado": "En Ejecucion"
        }
    )
    fichas[f["codigo"]] = obj

# 6. Aprendices por Ficha
nombres_base = [
    ("Andrés Felipe", "Caicedo Blanco", "TI", "1082991001"),
    ("Valeria Sofía", "Torres Manjarrés", "TI", "1082991002"),
    ("Juan Camilo", "Herrera Daza", "CC", "1082991003"),
    ("Mariana Lucía", "Ospina Rangel", "TI", "1082991004"),
    ("Santiago José", "Martínez Cantillo", "CC", "1082991005"),
]

aprendices_creados = []
for f_cod, ficha_obj in fichas.items():
    # Asociar FichaSena para compatibilidad con módulo de evidencias taller
    ficha_sena, _ = FichaSena.objects.get_or_create(
        numero_ficha=f_cod,
        defaults={"programa": ficha_obj.programa.denominacion, "jornada": "Diurna"}
    )
    rap_usuario, _ = RapUsuario.objects.get_or_create(
        ficha=ficha_sena,
        codigo=f"RAP-{f_cod[:4]}",
        defaults={"descripcion": f"Desarrollar productos del programa {ficha_obj.programa.denominacion}"}
    )

    # Crear evidencia de taller
    evidencia, _ = EvidenciaTaller.objects.get_or_create(
        ficha=ficha_obj,
        titulo=f"Taller Práctico de {ficha_obj.programa.denominacion}",
        defaults={
            "rap": rap_usuario,
            "instructor": ficha_obj.instructor_lider,
            "descripcion": "Desarrollar el caso de estudio propuesto con documentación técnica completa.",
            "fecha_limite": timezone.now() + timedelta(days=15)
        }
    )

    # Crear bitácora de visita
    BitacoraSeguimiento.objects.get_or_create(
        ficha=ficha_obj,
        fecha_visita=hoy - timedelta(days=10),
        defaults={
            "instructor": ficha_obj.instructor_lider,
            "tipo_seguimiento": "Presencial Aula",
            "observaciones": f"Acompañamiento presencial a la ficha {f_cod}. Verificación de equipos en sala de informática y avance en talleres.",
            "compromisos": "Los aprendices deben subir la evidencia de taller antes del viernes.",
            "fecha_verificacion": hoy + timedelta(days=5)
        }
    )

    for idx, (nom, ape, tdoc, base_doc) in enumerate(nombres_base, start=1):
        uname = f"apr_{f_cod}_{idx}"
        doc_num = f"108{f_cod[-3:]}{idx:04d}"
        user_apr, created = User.objects.get_or_create(
            username=uname,
            defaults={"first_name": nom, "last_name": ape, "email": f"{uname}@misena.edu.co"}
        )
        if created:
            user_apr.set_password("Sena2026*")
            user_apr.save()

        perfil_apr, _ = PerfilUsuario.objects.get_or_create(usuario=user_apr)
        perfil_apr.rol = rol_est
        perfil_apr.tipo_documento = tdoc
        perfil_apr.numero_documento = doc_num
        perfil_apr.qr_token = uuid.uuid4()
        perfil_apr.qr_rotacion = hoy
        perfil_apr.save()

        # Matrícula
        mat, _ = Matricula.objects.get_or_create(
            ficha=ficha_obj,
            aprendiz=user_apr,
            defaults={"grado_escolar": "11" if idx % 2 == 0 else "10", "estado_formacion": "En Formacion"}
        )
        aprendices_creados.append((mat, user_apr))

        # Calificación de evidencia
        CalificacionEvidencia.objects.get_or_create(
            evidencia=evidencia,
            aprendiz=user_apr,
            defaults={
                "juicio_evaluativo": "A" if idx <= 3 else "PENDIENTE",
                "observaciones": "Excelente trabajo, cumple con las normas técnicas de calidad." if idx <= 3 else "Pendiente de revisión final."
            }
        )

        # Asistencia para hoy y días anteriores
        for d in [0, 2, 5, 8]:
            fecha_asist = hoy - timedelta(days=d)
            AsistenciaAprendiz.objects.get_or_create(
                matricula=mat,
                fecha=fecha_asist,
                defaults={
                    "estado": "P" if (idx + d) % 4 != 0 else "A",
                    "observaciones": "Sesión presencial normal en ambiente de aprendizaje.",
                    "registrado_por": ficha_obj.instructor_lider
                }
            )

# 7. Alertas Tempranas
if aprendices_creados:
    mat_alerta = aprendices_creados[0][0]
    alerta, _ = CasoAlertaTemprana.objects.get_or_create(
        matricula=mat_alerta,
        defaults={
            "tipo_alerta": "inasistencia",
            "nivel_riesgo": "MEDIO",
            "puntuacion_riesgo": 55.0,
            "factores_detectados": "El aprendiz acumuló inasistencias consecutivas en el periodo.",
            "estado": "SEGUIMIENTO",
            "responsable": mat_alerta.ficha.instructor_lider,
            "plan_accion": "Llamada al acudiente y citación a coordinación pedagógica."
        }
    )
    CompromisoFormativo.objects.get_or_create(
        matricula=mat_alerta,
        instructor=mat_alerta.ficha.instructor_lider,
        titulo="Ponerse al día con talleres prácticos pendientes",
        defaults={
            "descripcion": "El aprendiz se compromete a entregar las evidencias pendientes.",
            "fecha_limite": hoy + timedelta(days=7),
            "estado": "PENDIENTE"
        }
    )

# 8. Empresas en Convenio & Etapa Productiva
empresas_data = [
    {"nit": "891700123-1", "nombre": "Daabon Group", "sec": "Agroindustria y Exportación", "contacto": "Recursos Humanos Daabon"},
    {"nit": "860002456-4", "nombre": "Drummond Ltd. Colombia", "sec": "Minería y Logística Portuaria", "contacto": "Gestión Humana Drummond"},
    {"nit": "800145789-2", "nombre": "Sociedad Portuaria Regional de Santa Marta", "sec": "Logística y Transporte Marítimo", "contacto": "Talento Humano SPRSM"},
    {"nit": "900321654-8", "nombre": "Clínica del Prado Santa Marta", "sec": "Salud y Gestión Administrativa", "contacto": "Administración Clínica"},
]
for emp in empresas_data:
    emp_obj, _ = EmpresaConvenio.objects.get_or_create(
        nit=emp["nit"],
        defaults={"razon_social": emp["nombre"], "contacto_nombre": emp["contacto"], "contacto_telefono": "3004567890", "contacto_email": "convenios@empresa.com", "direccion": "Zona Industrial"}
    )

if aprendices_creados:
    mat_ep = aprendices_creados[len(empresas_data)][0]
    ep_obj, _ = EtapaProductiva.objects.get_or_create(
        matricula=mat_ep,
        defaults={
            "empresa": EmpresaConvenio.objects.first(),
            "modalidad": "Contrato de Aprendizaje",
            "estado": "EN_DESARROLLO",
            "fecha_inicio": hoy - timedelta(days=60),
            "fecha_fin": hoy + timedelta(days=120),
            "tutor_empresarial": "Ing. Carlos Restrepo",
            "instructor_seguimiento": mat_ep.ficha.instructor_lider
        }
    )
    BitacoraEtapaProductiva.objects.get_or_create(
        etapa_productiva=ep_obj,
        numero_visita=1,
        defaults={
            "fecha_visita": hoy - timedelta(days=30),
            "instructor": mat_ep.ficha.instructor_lider,
            "actividades_desarrolladas": "Inducción técnica, configuración de ambientes y soporte a base de datos institucional.",
            "concepto_evaluativo": "SATISFACTORIO"
        }
    )

# 9. Proyectos SENNOVA (Innovación)
admin_user = User.objects.filter(is_superuser=True).first() or instructores["instructor_adso"]
ficha_sample = Ficha.objects.first()

proyectos_sennova = [
    {
        "titulo": "Sistema IoT para Monitoreo Ecoturístico de la Sierra Nevada",
        "cat": "Software TIC",
        "desc": "Red de sensores IoT interconectados con Django y LoRaWAN para medición ambiental en senderos turísticos del Magdalena."
    },
    {
        "titulo": "Plataforma Inteligente de Trazabilidad Agroindustrial para el Banano Magdalena",
        "cat": "Software TIC",
        "desc": "Sistema de gestión integral para la trazabilidad de fincas bananeras en Zona Bananera articulado con aprendices ADSO."
    },
    {
        "titulo": "Dron Autónomo con Visión Artificial para Levantamiento Topográfico Rural",
        "cat": "Software TIC",
        "desc": "Prototipo de aeronave no tripulada con procesamiento de imágenes satelitales para colegios agropecuarios articulados."
    }
]
for ps in proyectos_sennova:
    ProyectoInnovacion.objects.get_or_create(
        titulo=ps["titulo"],
        defaults={
            "descripcion": ps["desc"],
            "lider": admin_user,
            "instructor_asesor": instructores["instructor_adso"],
            "categoria": ps["cat"],
            "estado": "EN_DESARROLLO",
            "ficha": ficha_sample
        }
    )

# 10. Gestión Documental
documentos_institucionales = [
    {
        "tit": "Convenio Marco de Articulación con la Educación Media Técnica Magdalena 2026",
        "cat": "Formato Oficial SENA",
        "desc": "Acuerdo oficial suscrito entre la Dirección Regional del SENA Magdalena y las Secretarías de Educación Departamental y Distrital de Santa Marta."
    },
    {
        "tit": "Manual de Convivencia y Reglamento del Aprendiz SENA",
        "cat": "Normativa Institucional",
        "desc": "Reglamento oficial vigente de deberes, derechos, comités de evaluación y régimen disciplinario de los aprendices."
    },
    {
        "tit": "Guía Integrada de Aprendizaje N° 04: Arquitectura de Software MVC y Django",
        "cat": "Guia Pedagogica",
        "desc": "Orientación pedagógica oficial para el desarrollo del componente técnico en el Tecnólogo en ADSO."
    },
    {
        "tit": "Formato Institucional F-023: Registro de Visita y Bitácora de Media Técnica",
        "cat": "Formato Oficial SENA",
        "desc": "Plantilla oficial aprobada por el Sistema Integrado de Gestión para la formalización de acuerdos en colegios."
    }
]
for doc in documentos_institucionales:
    DocumentoInstitucional.objects.get_or_create(
        titulo=doc["tit"],
        defaults={
            "categoria": doc["cat"],
            "descripcion": doc["desc"],
            "subido_por": admin_user,
            "version": "1.0",
            "roles_permitidos": "Todos"
        }
    )

# 11. Biblioteca Digital
recursos_biblioteca = [
    {"tit": "Manual de Referencia Oficial de Python 3 y Django 5", "cat": "Guia de Aprendizaje", "desc": "Documentación curricular para el desarrollo web en Media Técnica."},
    {"tit": "Fundamentos de Redes de Datos y Modelo OSI (Cisco CCNA)", "cat": "Documento Tecnico", "desc": "Material de apoyo para la competencia de redes y telecomunicaciones."},
    {"tit": "Plan Único de Cuentas (PUC) para Comerciantes en Colombia", "cat": "Libro Tecnico", "desc": "Guía técnica para el programa de Contabilización de Operaciones."},
    {"tit": "Metodología de Gestión Ágil de Proyectos con Scrum SENA", "cat": "Manual SENA", "desc": "Marco de trabajo colaborativo para el desarrollo de evidencias de taller."}
]
for rb in recursos_biblioteca:
    RecursoBiblioteca.objects.get_or_create(
        titulo=rb["tit"],
        defaults={
            "autor": "SENA Regional Magdalena",
            "categoria": rb["cat"],
            "descripcion": rb["desc"],
            "ano_publicacion": 2026,
            "disponible": True
        }
    )

# 12. Mensajería de Seguimiento
primera_bitacora = BitacoraSeguimiento.objects.first()
if primera_bitacora:
    MensajeSeguimiento.objects.get_or_create(
        bitacora=primera_bitacora,
        remitente=admin_user,
        defaults={
            "mensaje": "Se informa que la evidencia de taller y avances de bitácora han sido verificados satisfactoriamente por el equipo de articulación SENA."
        }
    )

print("\n=== CARGA COMPLETA EXITOSA ===")
print(f"Programas totales: {ProgramaFormacion.objects.count()} (Técnicos y Tecnólogos)")
print(f"Fichas activas: {Ficha.objects.count()}")
print(f"Matrículas de aprendices: {Matricula.objects.count()}")
print(f"Bitácoras de seguimiento: {BitacoraSeguimiento.objects.count()}")
print(f"Asistencias registradas: {AsistenciaAprendiz.objects.count()}")
print(f"Casos de alerta temprana: {CasoAlertaTemprana.objects.count()}")
print(f"Empresas en convenio: {EmpresaConvenio.objects.count()}")
print(f"Aprendices en etapa productiva: {EtapaProductiva.objects.count()}")
print(f"Proyectos SENNOVA: {ProyectoInnovacion.objects.count()}")
print(f"Documentos en gestión documental: {DocumentoInstitucional.objects.count()}")
print(f"Recursos en biblioteca: {RecursoBiblioteca.objects.count()}")
