from io import BytesIO

from openpyxl import Workbook
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from instituciones.models import InstitucionEducativa
from usuarios.models import PerfilUsuario
from .models import ProgramaFormacion, Competencia, ResultadoAprendizaje, Ficha, Matricula


class AcademicoModelTest(TestCase):
    def setUp(self):
        self.colegio = InstitucionEducativa.objects.create(
            codigo_dane="147001000123",
            nombre="I.E. Técnica Departamental de Ciénaga",
            municipio="Ciénaga"
        )
        self.programa = ProgramaFormacion.objects.create(
            codigo_programa="228106",
            denominacion="Técnico en Sistemas",
            version="102"
        )
        self.instructor = User.objects.create_user(
            username="instructor_carlos",
            first_name="Carlos",
            last_name="Martínez"
        )
        self.ficha = Ficha.objects.create(
            codigo_ficha="2501234",
            programa=self.programa,
            institucion=self.colegio,
            instructor_lider=self.instructor,
            fecha_inicio="2026-02-01",
            fecha_fin="2027-11-30"
        )
        self.aprendiz = User.objects.create_user(
            username="aprendiz_juan",
            first_name="Juan",
            last_name="Pérez"
        )

    def test_creacion_ficha_y_matricula_valida(self):
        """Verifica la vinculación de un aprendiz a una ficha en grado 10° (RN-007)"""
        matricula = Matricula.objects.create(
            ficha=self.ficha,
            aprendiz=self.aprendiz,
            grado_escolar="10"
        )
        self.assertEqual(matricula.ficha.codigo_ficha, "2501234")
        self.assertEqual(matricula.estado_formacion, "En Formacion")
        self.assertEqual(matricula.grado_escolar, "10")

    def test_regla_rn002_no_duplicar_matricula_en_misma_ficha(self):
        """Verifica que un aprendiz no pueda matricularse dos veces en la misma ficha (RN-002)"""
        Matricula.objects.create(
            ficha=self.ficha,
            aprendiz=self.aprendiz,
            grado_escolar="10"
        )
        # Intentar matricular al mismo aprendiz nuevamente en la misma ficha
        with self.assertRaises(IntegrityError):
            Matricula.objects.create(
                ficha=self.ficha,
                aprendiz=self.aprendiz,
                grado_escolar="10"
            )

    def test_importar_aprendices_desde_csv(self):
        contenido = (
            'tipo_documento,numero_documento,nombres,apellidos,correo,grado_escolar\n'
            'TI,1002003004,Ana,Lopez,ana@example.com,10\n'
        )
        archivo = SimpleUploadedFile('aprendices.csv', contenido.encode('utf-8'), content_type='text/csv')
        cliente = self.client
        cliente.force_login(self.instructor)

        response = cliente.post(
            f'/academico/fichas/{self.ficha.id}/matricular/',
            {'accion': 'importar', 'archivo': archivo},
        )

        self.assertRedirects(response, f'/academico/fichas/{self.ficha.id}/')
        perfil = PerfilUsuario.objects.get(numero_documento='1002003004')
        self.assertEqual(perfil.usuario.email, 'ana@example.com')
        self.assertTrue(Matricula.objects.filter(ficha=self.ficha, aprendiz=perfil.usuario).exists())

    def test_importar_aprendices_desde_xlsx(self):
        libro = Workbook()
        hoja = libro.active
        hoja.append(['tipo_documento', 'numero_documento', 'nombres', 'apellidos', 'correo', 'grado_escolar'])
        hoja.append(['CC', '1002003005', 'Luis', 'Perez', 'luis@example.com', '11'])
        contenido = BytesIO()
        libro.save(contenido)
        archivo = SimpleUploadedFile(
            'aprendices.xlsx', contenido.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        self.client.force_login(self.instructor)

        response = self.client.post(
            f'/academico/fichas/{self.ficha.id}/matricular/',
            {'accion': 'importar', 'archivo': archivo},
        )

        self.assertRedirects(response, f'/academico/fichas/{self.ficha.id}/')
        self.assertTrue(PerfilUsuario.objects.filter(numero_documento='1002003005').exists())

    def test_importacion_con_documento_duplicado_no_crea_registros(self):
        contenido = (
            'tipo_documento,numero_documento,nombres,apellidos,correo,grado_escolar\n'
            'TI,1002003006,Primero,Aprendiz,uno@example.com,10\n'
            'TI,1002003006,Segundo,Aprendiz,dos@example.com,11\n'
        )
        archivo = SimpleUploadedFile('duplicados.csv', contenido.encode('utf-8'), content_type='text/csv')
        self.client.force_login(self.instructor)

        response = self.client.post(
            f'/academico/fichas/{self.ficha.id}/matricular/',
            {'accion': 'importar', 'archivo': archivo},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(PerfilUsuario.objects.filter(numero_documento='1002003006').exists())
        self.assertContains(response, 'repetido en el archivo')
