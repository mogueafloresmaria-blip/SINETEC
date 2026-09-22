from django.test import TestCase, Client
from django.contrib.auth.models import User

class InicioViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='instructor_test',
            email='test@sena.edu.co',
            password='Password123*'
        )

    def test_pagina_inicio_responde_ok(self):
        """Verifica que la URL raíz / responda con código HTTP 200 y use la plantilla home.html"""
        respuesta = self.client.get('/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'home.html')
        self.assertContains(respuesta, 'SINETEC')
        self.assertContains(respuesta, 'Centro de Logística y Promoción Ecoturística')

    def test_login_pantalla_responde_ok(self):
        """Verifica que la pantalla de inicio de sesión cargue correctamente"""
        respuesta = self.client.get('/login/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'login.html')

    def test_dashboard_requiere_login(self):
        """Verifica que /dashboard/ redirija al login si el usuario es anónimo"""
        respuesta = self.client.get('/dashboard/')
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn('/login/', respuesta.url)

    def test_dashboard_sin_perfil_no_falla(self):
        """Verifica que el dashboard renderiza sin asumir que el usuario tiene perfil completo."""
        user_sin_perfil = User.objects.create_user(username='sinperfil', password='Password123*')
        self.client.force_login(user_sin_perfil)
        respuesta = self.client.get('/dashboard/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'dashboard.html')

    def test_vistas_autenticadas_responden_ok(self):
        """Verifica que un usuario autenticado pueda acceder a todos los módulos web"""
        self.client.login(username='instructor_test', password='Password123*')

        # Dashboard
        r_dash = self.client.get('/dashboard/')
        self.assertEqual(r_dash.status_code, 200)
        self.assertTemplateUsed(r_dash, 'dashboard.html')

        # Instituciones
        r_inst = self.client.get('/instituciones/')
        self.assertEqual(r_inst.status_code, 200)
        self.assertTemplateUsed(r_inst, 'instituciones/lista.html')

        # Fichas
        r_fichas = self.client.get('/academico/fichas/')
        self.assertEqual(r_fichas.status_code, 200)
        self.assertTemplateUsed(r_fichas, 'academico/fichas_lista.html')

        # Seguimiento
        r_seg = self.client.get('/seguimiento/')
        self.assertEqual(r_seg.status_code, 200)
        self.assertTemplateUsed(r_seg, 'seguimiento/lista.html')

        # Calificaciones
        r_eval = self.client.get('/evaluaciones/')
        self.assertEqual(r_eval.status_code, 200)
        self.assertTemplateUsed(r_eval, 'evaluaciones/calificar.html')

