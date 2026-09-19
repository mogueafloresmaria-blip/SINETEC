import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date

from usuarios.models import Rol, PerfilUsuario, EvidenciaTaller, CalificacionEvidencia
from instituciones.models import InstitucionEducativa
from academico.models import (
    ProgramaFormacion, Competencia, Ficha, Matricula, HorarioFicha,
    ProyectoInnovacion, LogroAprendiz, DocumentoInstitucional,
    ResultadoAprendizaje as RapCurricular
)
from seguimiento.models import (
    BitacoraSeguimiento, AsistenciaAprendiz, SolicitudSecretaria,
    CompromisoFormativo, CasoAlertaTemprana, EmpresaConvenio,
    EtapaProductiva, BitacoraEtapaProductiva
)
from evaluaciones.models import JuicioEvaluativo


def poblar():
    print("=== POBLANDO DATOS DEMO OFICIALES SINETEC ===")

    # 1. Asegurar Roles
    roles_def = [
        ("Administrador", "Control total del sistema"),
        ("Coordinador", "Coordinación académica"),
        ("Instructor SENA", "Instructor técnico de articulación"),
        ("Docente I.E.", "Docente enlace del colegio"),
        ("Estudiante", "Aprendiz en formación técnica"),
        ("Secretaría", "Ventanilla única y registro institucional"),
    ]
    roles_map = {}
    for nombre, desc in roles_def:
        rol, _ = Rol.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
        roles_map[nombre] = rol

    # 2. Los 4 Usuarios Demo con contraseña Sena2026*
    PASSWORD_DEMO = "Sena2026*"

    usuarios_demo = [
        {
            "username": "coordinador_demo",
            "first_name": "Roberto",
            "last_name": "Cañas",
            "email": "coordinador@sena.edu.co",
            "rol": roles_map["Coordinador"],
            "doc": "1082990001",
            "cargo": "Coordinador de Articulación",
            "is_staff": True,
        },
        {
            "username": "instructor_demo",
            "first_name": "Claudia",
            "last_name": "Morales",
            "email": "instructor@sena.edu.co",
            "rol": roles_map["Instructor SENA"],
            "doc": "1082990002",
            "cargo": "Instructora Técnica ADSI",
            "is_staff": False,
        },
        {
            "username": "secretaria_demo",
            "first_name": "Marcela",
            "last_name": "Mendoza",
            "email": "secretaria@sena.edu.co",
            "rol": roles_map["Secretaría"],
            "doc": "1082990003",
            "cargo": "Secretaría Académica",
            "is_staff": False,
        },
        {
            "username": "aprendiz_demo",
            "first_name": "Mateo",
            "last_name": "Gómez Silva",
            "email": "aprendiz@sena.edu.co",
            "rol": roles_map["Estudiante"],
            "doc": "1082990004",
            "cargo": "Aprendiz ADSI",
            "is_staff": False,
        },
    ]

    for udata in usuarios_demo:
        user, created = User.objects.get_or_create(
            username=udata["username"],
            defaults={
                "first_name": udata["first_name"],
                "last_name": udata["last_name"],
                "email": udata["email"],
                "is_staff": udata["is_staff"],
            }
        )
        user.set_password(PASSWORD_DEMO)
        user.first_name = udata["first_name"]
        user.last_name = udata["last_name"]
        user.email = udata["email"]
        user.save()

        perfil = user.perfil
        perfil.rol = udata["rol"]
        perfil.numero_documento = udata["doc"]
        perfil.cargo = udata["cargo"]
        perfil.telefono = "3001234567"
        perfil.save()
        print(f" -> Usuario '{user.username}' configurado con rol '{udata['rol'].nombre}' (Clave: {PASSWORD_DEMO})")

    coord_user = User.objects.get(username="coordinador_demo")
    inst_user = User.objects.get(username="instructor_demo")
    sec_user = User.objects.get(username="secretaria_demo")
    apr_user = User.objects.get(username="aprendiz_demo")

    # 3. Ficha y Matrícula para Aprendiz Demo
    ficha_demo = Ficha.objects.first()
    if not ficha_demo:
        inst_educativa, _ = InstitucionEducativa.objects.get_or_create(
            codigo_dane="147001000001",
            defaults={"nombre": "I.E.D. Normal Superior San Pedro Alejandrino", "municipio": "Santa Marta"}
        )
        prog, _ = ProgramaFormacion.objects.get_or_create(
            codigo="228106",
            defaults={"denominacion": "Análisis y Desarrollo de Sistemas de Información", "version": 1}
        )
        ficha_demo = Ficha.objects.create(
            codigo_ficha="3173430",
            programa=prog,
            institucion=inst_educativa,
            instructor_lider=inst_user,
            fecha_inicio=date(2025, 2, 1),
            fecha_fin=date(2026, 11, 30),
            estado="En Ejecucion"
        )

    # Asignar instructor_demo como líder de ficha
    ficha_demo.instructor_lider = inst_user
    ficha_demo.save()

    mat_demo, _ = Matricula.objects.get_or_create(
        ficha=ficha_demo,
        aprendiz=apr_user,
        defaults={
            "estado_formacion": "En Formacion",
            "grado_escolar": "11"
        }
    )

    # 4. Asistencias para Aprendiz Demo
    hoy = timezone.localdate()
    for i in range(1, 15):
        f_asist = hoy - timedelta(days=i)
        if f_asist.weekday() < 5:
            AsistenciaAprendiz.objects.get_or_create(
                matricula=mat_demo,
                fecha=f_asist,
                defaults={
                    "estado": "P",
                    "observaciones": "Asistencia regular en aula",
                    "registrado_por": inst_user,
                }
            )

    # 5. RAPs y Juicios Evaluativos
    comp = Competencia.objects.first()
    if comp:
        rap_cur, _ = RapCurricular.objects.get_or_create(
            competencia=comp,
            codigo="RAP-228106-01",
            defaults={"descripcion": "Especificar requisitos del sistema según estándares pedagógicos SENA"}
        )
        JuicioEvaluativo.objects.get_or_create(
            matricula=mat_demo,
            resultado_aprendizaje=rap_cur,
            defaults={
                "juicio_valor": "A",
                "instructor": inst_user,
                "fecha_evaluacion": hoy - timedelta(days=5),
                "observaciones": "Excelente desempeño técnico y entrega oportuna."
            }
        )

    # 6. Convenio y Etapa Productiva
    empresa, _ = EmpresaConvenio.objects.get_or_create(
        nit="900889977-1",
        defaults={
            "razon_social": "Soluciones Digitales del Caribe S.A.S.",
            "contacto_nombre": "Ing. Andrés Palomino",
            "contacto_cargo": "Director de Desarrollo",
            "contacto_email": "contacto@solucionescaribe.com",
            "contacto_telefono": "3015551234",
            "direccion": "Cra 5 # 22-45",
            "municipio": "Santa Marta",
            "activa": True,
        }
    )

    ep_demo, _ = EtapaProductiva.objects.get_or_create(
        matricula=mat_demo,
        defaults={
            "modalidad": "Contrato de Aprendizaje",
            "empresa": empresa,
            "instructor_seguimiento": inst_user,
            "tutor_empresarial": "Ing. Andrés Palomino",
            "tutor_cargo": "Líder de Desarrollo",
            "tutor_email": "andres@solucionescaribe.com",
            "tutor_telefono": "3015551234",
            "fecha_inicio": hoy - timedelta(days=60),
            "estado": "EN_DESARROLLO",
        }
    )

    BitacoraEtapaProductiva.objects.get_or_create(
        etapa_productiva=ep_demo,
        numero_visita=1,
        defaults={
            "fecha_visita": hoy - timedelta(days=25),
            "instructor": inst_user,
            "actividades_desarrolladas": "Concertación del plan de trabajo, inducción al repositorio y configuración de ambientes de desarrollo.",
            "concepto_evaluativo": "SATISFACTORIO",
            "observaciones_tutor": "El aprendiz demuestra alto compromiso y conocimientos en bases de datos.",
            "observaciones_instructor": "Cumple a cabalidad con los lineamientos del Formato F023 SENA.",
        }
    )

    # 7. Compromiso Formativo
    CompromisoFormativo.objects.get_or_create(
        matricula=mat_demo,
        titulo="Nivelación en modelado entidad-relación",
        defaults={
            "instructor": inst_user,
            "descripcion": "El aprendiz presentará el diagrama ER normalizado hasta 3FN del proyecto formativo.",
            "fecha_limite": hoy + timedelta(days=5),
            "estado": "PENDIENTE",
        }
    )

    # 8. Alerta Temprana Formal
    CasoAlertaTemprana.objects.get_or_create(
        matricula=mat_demo,
        tipo_alerta="academica",
        defaults={
            "nivel_riesgo": "MEDIO",
            "puntuacion_riesgo": 45.0,
            "factores_detectados": "Ajuste de evidencias de taller de programación modular.",
            "estado": "INTERVENCION",
            "responsable": inst_user,
            "plan_accion": "Acompañamiento tutorial en el ambiente de formación y seguimiento de compromisos.",
        }
    )

    # 9. Solicitud a Secretaría
    SolicitudSecretaria.objects.get_or_create(
        aprendiz=apr_user,
        asunto="Solicitud de constancia de matrícula con promedio para subsidio",
        defaults={
            "ficha": ficha_demo,
            "categoria": "Certificacion",
            "mensaje": "Requiero constancia formal de matrícula activa en el programa ADSI para trámite ante Jóvenes en Acción.",
            "prioridad": "Media",
            "estado": "RECIBIDA",
        }
    )

    # 10. Proyectos de Innovación SENNOVA
    ProyectoInnovacion.objects.get_or_create(
        titulo="SINETEC: Ecosistema Digital de Seguimiento para la Media Técnica",
        defaults={
            "descripcion": "Plataforma de alta disponibilidad para la trazabilidad formativa, control criptográfico de carné QR y acompañamiento integral en colegios articulados del Magdalena.",
            "lider": apr_user,
            "ficha": ficha_demo,
            "instructor_asesor": inst_user,
            "categoria": "Software TIC",
            "estado": "DESARROLLO",
        }
    )

    ProyectoInnovacion.objects.get_or_create(
        titulo="Sistema IoT de Monitoreo Agrometeorológico para Cultivos del Magdalena",
        defaults={
            "descripcion": "Red de sensores de bajo costo para medición de humedad de suelo, temperatura y pluviometría con telemetría LoRaWAN.",
            "lider": inst_user,
            "ficha": ficha_demo,
            "instructor_asesor": inst_user,
            "categoria": "Agroecologia",
            "estado": "FINALIZADO",
        }
    )

    # 11. Documentos Institucionales
    DocumentoInstitucional.objects.get_or_create(
        titulo="Formato Oficial F023 - Bitácora de Etapa Productiva",
        defaults={
            "categoria": "Formato Oficial SENA",
            "descripcion": "Plantilla oficial institucional para el registro y concertación de actividades en empresa o proyecto productivo.",
            "version": "2.0",
            "subido_por": sec_user,
            "roles_permitidos": "Todos",
        }
    )

    DocumentoInstitucional.objects.get_or_create(
        titulo="Resolución de Apertura de Fichas de Articulación con la Educación Media 2026",
        defaults={
            "categoria": "Normativa Institucional",
            "descripcion": "Acto administrativo formal que avala las cohortes técnicas en instituciones educativas de Santa Marta y Magdalena.",
            "version": "1.0",
            "subido_por": coord_user,
            "roles_permitidos": "Todos",
        }
    )

    # 12. Logros e Insignias para Aprendiz Demo
    LogroAprendiz.objects.get_or_create(
        aprendiz=apr_user,
        titulo="Puntualidad Impecable",
        defaults={
            "icono": "bi-clock-check-fill",
            "color": "success",
            "descripcion": "Más de 30 sesiones consecutivas con asistencia puntual sin inasistencias injustificadas.",
            "categoria": "Puntualidad y Asistencia",
        }
    )

    LogroAprendiz.objects.get_or_create(
        aprendiz=apr_user,
        titulo="Innovador SENNOVA",
        defaults={
            "icono": "bi-lightbulb-fill",
            "color": "primary",
            "descripcion": "Participación activa en el semillero de investigación institucional.",
            "categoria": "Investigación Formativa",
        }
    )

    print("=== POBLACIÓN DE DATOS DEMO EXITOSA ===")


if __name__ == '__main__':
    poblar()

