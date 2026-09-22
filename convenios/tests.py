import os
from datetime import timedelta
from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import InstitucionConvenio, ConvenioSENA, DocumentoConvenio


class ConveniosSENATestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser('admin_conv', 'admin_conv@sena.edu.co', 'Admin123*')
        self.usuario_comun = User.objects.create_user('docente_sin_permiso', 'docente@sena.edu.co', 'Pass123*')
        self.hoy = timezone.localdate()

        # 1. Crear institución base
        self.institucion = InstitucionConvenio.objects.create(
            nombre="I.E. Simón Bolívar de Prueba",
            codigo_dane="147001999999",
            departamento="Magdalena",
            municipio="Santa Marta",
            direccion="Calle 10 # 5-20",
            telefono="3001112233",
            correo="simon@prueba.edu.co",
            activo=True
        )

        # 2. Crear convenios con distintos estados automáticos
        # Activo:
        self.conv_activo = ConvenioSENA.objects.create(
            institucion=self.institucion,
            numero_convenio="CONV-ACTIVO-001",
            nombre="Convenio Activo de Articulación",
            tipo_convenio="Articulacion Media Tecnica",
            fecha_inicio=self.hoy - timedelta(days=100),
            fecha_fin=self.hoy + timedelta(days=200),
            responsable="Coordinador SENA"
        )

        # Próximo a vencer (15 días restantes):
        self.conv_proximo = ConvenioSENA.objects.create(
            institucion=self.institucion,
            numero_convenio="CONV-PROXIMO-002",
            nombre="Convenio por Vencer",
            tipo_convenio="Pasantias y Practicas",
            fecha_inicio=self.hoy - timedelta(days=300),
            fecha_fin=self.hoy + timedelta(days=15),
            responsable="Enlace SENA"
        )

        # Vencido (hace 10 días):
        self.conv_vencido = ConvenioSENA.objects.create(
            institucion=self.institucion,
            numero_convenio="CONV-VENCIDO-003",
            nombre="Convenio Expirado",
            tipo_convenio="Marco de Cooperacion",
            fecha_inicio=self.hoy - timedelta(days=400),
            fecha_fin=self.hoy - timedelta(days=10),
            responsable="Enlace SENA"
        )

    def test_01_crear_institucion(self):
        """1. Crear institución educativa vía POST."""
        self.client.force_login(self.admin)
        res = self.client.post('/convenios/instituciones/nueva/', {
            'nombre': 'I.E. Nueva Creación',
            'codigo_dane': '147001888888',
            'departamento': 'Magdalena',
            'municipio': 'Ciénaga',
            'direccion': 'Carrera 15 # 20-30',
            'telefono': '3109998877',
            'correo': 'nueva@colegio.edu.co',
        })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(InstitucionConvenio.objects.filter(nombre='I.E. Nueva Creación').exists())

    def test_02_crear_convenio(self):
        """2. Crear convenio SENA asociado a una institución."""
        self.client.force_login(self.admin)
        res = self.client.post('/convenios/convenio/nuevo/', {
            'institucion': self.institucion.pk,
            'numero_convenio': 'CONV-TEST-NEW-99',
            'nombre': 'Convenio de Cooperación Pedagógica',
            'tipo_convenio': 'Especifico',
            'fecha_inicio': self.hoy.strftime('%Y-%m-%d'),
            'fecha_fin': (self.hoy + timedelta(days=365)).strftime('%Y-%m-%d'),
            'responsable': 'Ing. Instructor',
        })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(ConvenioSENA.objects.filter(numero_convenio='CONV-TEST-NEW-99').exists())

    def test_03_ver_institucion_detalle(self):
        """3. Ver página completa de detalle de la institución."""
        self.client.force_login(self.admin)
        res = self.client.get(f'/convenios/instituciones/{self.institucion.pk}/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'I.E. Simón Bolívar de Prueba')
        self.assertContains(res, 'CONV-ACTIVO-001')
        self.assertContains(res, 'Información Institucional')

    def test_04_editar_institucion(self):
        """4. Editar datos institucionales."""
        self.client.force_login(self.admin)
        res = self.client.post(f'/convenios/instituciones/{self.institucion.pk}/editar/', {
            'nombre': 'I.E. Simón Bolívar (Modificada)',
            'codigo_dane': self.institucion.codigo_dane,
            'departamento': 'Magdalena',
            'municipio': 'Santa Marta',
            'direccion': 'Nueva Dirección 123',
        })
        self.assertEqual(res.status_code, 302)
        self.institucion.refresh_from_db()
        self.assertEqual(self.institucion.nombre, 'I.E. Simón Bolívar (Modificada)')

    def test_05_editar_convenio(self):
        """5. Editar datos de un convenio."""
        self.client.force_login(self.admin)
        res = self.client.post(f'/convenios/convenio/{self.conv_activo.pk}/editar/', {
            'institucion': self.institucion.pk,
            'numero_convenio': 'CONV-ACTIVO-001',
            'nombre': 'Convenio Actualizado 2026',
            'tipo_convenio': self.conv_activo.tipo_convenio,
            'fecha_inicio': self.conv_activo.fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': self.conv_activo.fecha_fin.strftime('%Y-%m-%d'),
            'responsable': 'Nuevo Responsable',
        })
        self.assertEqual(res.status_code, 302)
        self.conv_activo.refresh_from_db()
        self.assertEqual(self.conv_activo.nombre, 'Convenio Actualizado 2026')

    def test_06_subir_descargar_y_eliminar_documento(self):
        """6, 7, 8. Subir documento real, descargarlo con FileResponse y eliminarlo."""
        self.client.force_login(self.admin)
        archivo_fake = SimpleUploadedFile(
            "minuta_test.pdf",
            b"%PDF-1.4 Fake test content for legal agreement",
            content_type="application/pdf"
        )
        # Subir
        res_subida = self.client.post(f'/convenios/convenio/{self.conv_activo.pk}/documento/subir/', {
            'nombre': 'Minuta Legal Test',
            'tipo': 'Documento del convenio',
            'archivo': archivo_fake,
            'descripcion': 'Archivo de prueba unitaria',
        })
        self.assertEqual(res_subida.status_code, 302)
        doc = DocumentoConvenio.objects.filter(convenio=self.conv_activo, nombre='Minuta Legal Test').first()
        self.assertIsNotNone(doc)

        # Descargar
        res_descarga = self.client.get(f'/convenios/documento/{doc.pk}/descargar/')
        self.assertEqual(res_descarga.status_code, 200)
        self.assertEqual(res_descarga['Content-Type'], 'application/pdf')

        # Eliminar
        res_eliminar = self.client.post(f'/convenios/documento/{doc.pk}/eliminar/')
        self.assertEqual(res_eliminar.status_code, 302)
        self.assertFalse(DocumentoConvenio.objects.filter(pk=doc.pk).exists())

    def test_07_calculo_automatico_de_estados(self):
        """9. Verificación de cálculo automático de estados sin ingreso manual."""
        self.assertEqual(self.conv_activo.estado, 'Activo')
        self.assertEqual(self.conv_proximo.estado, 'Próximo a vencer')
        self.assertEqual(self.conv_vencido.estado, 'Vencido')

        # Estado manual forzado
        self.conv_activo.estado_manual = 'Suspendido'
        self.assertEqual(self.conv_activo.estado, 'Suspendido')

    def test_08_catalogo_estadisticas_y_busqueda(self):
        """10, 11, 12, 13. Estadísticas extraídas de BD, catálogo de tarjetas y filtros."""
        self.client.force_login(self.admin)
        res = self.client.get('/convenios/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'I.E. Simón Bolívar')
        # Verificar estadísticas en contexto
        self.assertGreaterEqual(res.context['total_instituciones'], 1)
        self.assertGreaterEqual(res.context['total_activos'], 1)
        self.assertGreaterEqual(res.context['total_proximos'], 1)
        self.assertGreaterEqual(res.context['total_vencidos'], 1)

        # Búsqueda por DANE
        res_dane = self.client.get('/convenios/?q=147001999999')
        self.assertEqual(len(res_dane.context['instituciones']), 1)

        # Búsqueda que no coincide
        res_nada = self.client.get('/convenios/?q=InexistenteXYZ1234')
        self.assertEqual(len(res_nada.context['instituciones']), 0)
        self.assertContains(res_nada, 'No se encontraron instituciones')

    def test_09_desactivar_institucion_borrado_logico(self):
        """14. Desactivar institución sin borrar registros de la base de datos."""
        self.client.force_login(self.admin)
        res = self.client.post(f'/convenios/instituciones/{self.institucion.pk}/desactivar/')
        self.assertEqual(res.status_code, 302)
        self.institucion.refresh_from_db()
        self.assertFalse(self.institucion.activo)
        # La institución sigue existiendo en la BD
        self.assertTrue(InstitucionConvenio.objects.filter(pk=self.institucion.pk).exists())

    def test_10_permisos_y_seguridad(self):
        """15. Los usuarios anónimos o sin autorización no pueden crear ni modificar convenios."""
        c_anonimo = Client()
        # Anónimo es redirigido a login
        res_anon = c_anonimo.get('/convenios/')
        self.assertEqual(res_anon.status_code, 302)
        self.assertIn('/login/', res_anon.url)

        # Usuario sin permisos administrativos no puede registrar instituciones
        c_comun = Client()
        c_comun.force_login(self.usuario_comun)
        res_denegado = c_comun.get('/convenios/instituciones/nueva/')
        self.assertEqual(res_denegado.status_code, 403)
