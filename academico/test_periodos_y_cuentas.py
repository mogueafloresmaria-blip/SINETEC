from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.urls import reverse

from usuarios.models import Rol, PerfilUsuario
from academico.models import (
    PeriodoAcademico, CalificacionEscolar, InstitucionEducativa,
    ProgramaFormacion, Ficha, Matricula, CargaAcademica
)

class PeriodosAcademicosYCuentasTests(TestCase):
    """
    Pruebas automatizadas de Periodos Académicos, validación de fechas,
    bloqueo por cierre, y creación de cuentas estudiantiles con documento como usuario y clave.
    """

    def setUp(self):
        self.colegio = InstitucionEducativa.objects.create(
            codigo_dane="147001009999",
            nombre="Colegio EduNova",
            municipio="Santa Marta"
        )
        self.programa = ProgramaFormacion.objects.create(
            codigo_programa="1001-A",
            denominacion="Bachillerato"
        )
        self.docente = User.objects.create_user("profesor_ciencias", "doc@edunova.edu", "Clave-123")
        rol_docente, _ = Rol.objects.get_or_create(nombre="Docente")
        self.docente.perfil.rol = rol_docente
        self.docente.perfil.save()

        self.ficha = Ficha.objects.create(
            codigo_ficha="10-A",
            programa=self.programa,
            institucion=self.colegio,
            instructor_lider=self.docente,
            fecha_inicio="2026-02-01",
            fecha_fin="2026-11-30"
        )

        self.carga = CargaAcademica.objects.create(
            profesor=self.docente,
            programa=self.programa,
            nivel="Media Tecnica",
            grado="10",
            seccion="A",
            anio_lectivo=2026
        )

        # Crear roles necesarios
        self.rol_estudiante, _ = Rol.objects.get_or_create(nombre="Estudiante")
        self.rol_secretaria, _ = Rol.objects.get_or_create(nombre="Secretaría")
        self.rol_admin, _ = Rol.objects.get_or_create(nombre="Administrador")

        self.admin = User.objects.create_superuser("admin_p", "adm@edunova.edu", "AdminPass123")
        self.admin.perfil.rol = self.rol_admin
        self.admin.perfil.save()

    def test_01_configuracion_cuatro_periodos_y_estados(self):
        """Verifica la configuración de los 4 períodos académicos y sus estados dinámicos."""
        hoy = date.today()
        # Período 1 finalizado
        p1 = PeriodoAcademico.objects.create(
            numero=1,
            anio_lectivo=2026,
            fecha_inicio=hoy - timedelta(days=90),
            fecha_fin=hoy - timedelta(days=30),
            porcentaje=25.0
        )
        # Período 2 en curso
        p2 = PeriodoAcademico.objects.create(
            numero=2,
            anio_lectivo=2026,
            fecha_inicio=hoy - timedelta(days=10),
            fecha_fin=hoy + timedelta(days=40),
            porcentaje=25.0
        )
        # Período 3 pendiente
        p3 = PeriodoAcademico.objects.create(
            numero=3,
            anio_lectivo=2026,
            fecha_inicio=hoy + timedelta(days=50),
            fecha_fin=hoy + timedelta(days=100),
            porcentaje=25.0
        )
        # Período 4 cerrado manualmente
        p4 = PeriodoAcademico.objects.create(
            numero=4,
            anio_lectivo=2026,
            fecha_inicio=hoy + timedelta(days=110),
            fecha_fin=hoy + timedelta(days=160),
            porcentaje=25.0,
            cerrado=True
        )

        self.assertEqual(p1.estado, "Finalizado")
        self.assertEqual(p2.estado, "En Curso")
        self.assertEqual(p3.estado, "Pendiente")
        self.assertEqual(p4.estado, "Cerrado")

    def test_02_validacion_fechas_periodo_invalido(self):
        """Verifica que fecha_fin menor que fecha_inicio arroje ValidationError."""
        hoy = date.today()
        p_invalido = PeriodoAcademico(
            numero=1,
            anio_lectivo=2027,
            fecha_inicio=hoy,
            fecha_fin=hoy - timedelta(days=5),
            porcentaje=25.0
        )
        with self.assertRaises(ValidationError):
            p_invalido.clean()

    def test_03_advertencia_cruce_fechas_periodos(self):
        """Verifica la detección de períodos que se cruzan en fechas."""
        hoy = date.today()
        PeriodoAcademico.objects.create(
            numero=1,
            anio_lectivo=2028,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=30),
            porcentaje=25.0
        )
        PeriodoAcademico.objects.create(
            numero=2,
            anio_lectivo=2028,
            fecha_inicio=hoy + timedelta(days=15),
            fecha_fin=hoy + timedelta(days=45),
            porcentaje=25.0
        )
        cruces = PeriodoAcademico.validar_cruces(anio='2028')
        self.assertTrue(len(cruces) > 0, "Debe advertir sobre el cruce con el Período 1")

    def test_04_creacion_cuenta_estudiante_con_documento_como_usuario_y_clave(self):
        """
        Verifica que al registrar un estudiante, el username sea el documento,
        la contraseña inicial sea el documento, y se pueda autenticar de inmediato.
        """
        doc = "1098765432"
        # Simular creación de cuenta según la convención EduNova
        user = User.objects.create_user(
            username=doc,
            first_name="Camila",
            last_name="Torres",
            email="camila.torres@edunova.edu"
        )
        user.set_password(doc)
        user.save()

        user.perfil.rol = self.rol_estudiante
        user.perfil.tipo_documento = "TI"
        user.perfil.numero_documento = doc
        user.perfil.save()

        matricula = Matricula.objects.create(
            ficha=self.ficha,
            aprendiz=user,
            grado_escolar="10",
            seccion="A"
        )

        # Autenticación con documento como usuario y clave
        auth_user = authenticate(username=doc, password=doc)
        self.assertIsNotNone(auth_user, "El estudiante debe poder autenticarse con su documento como usuario y clave.")
        self.assertEqual(auth_user.perfil.rol.nombre, "Estudiante")
        self.assertEqual(auth_user.matriculas_academicas.first().ficha.codigo_ficha, "10-A")

    def test_05_bloqueo_calificaciones_cuando_periodo_esta_cerrado(self):
        """Verifica que el docente no pueda modificar notas si el período está cerrado."""
        hoy = date.today()
        periodo_cerrado = PeriodoAcademico.objects.create(
            numero=1,
            anio_lectivo=2026,
            fecha_inicio=hoy - timedelta(days=60),
            fecha_fin=hoy - timedelta(days=10),
            cerrado=True
        )

        client = Client()
        client.force_login(self.docente)

        # POST a guardar calificaciones para período cerrado
        response = client.post(reverse('calificaciones_docente'), {
            'action': 'guardar_notas',
            'periodo': 'Periodo 1',
            'carga_id': self.carga.id,
            f'nota_{self.docente.id}': '4.5'
        })
        # Debe redirigir con mensaje de error sin modificar nada
        self.assertEqual(response.status_code, 302)
        self.assertIn("tab=planilla", response.url)
