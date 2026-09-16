from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Ruta raíz oficial que carga tu portada de inicio
    path('', views.home_view, name='home'),
    
    # Dashboard general y Autenticación corregida (Usa auth_views para evitar TemplateDoesNotExist)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Redirección y paneles por rol institucional
    path('panel/', views.redirect_dashboard, name='redirect_dashboard'),
    path('panel/estudiante/', views.aprendiz_dashboard, name='aprendiz_dashboard'),
    path('panel/instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('panel/coordinador/', views.coordinador_dashboard, name='coordinador_dashboard'),

    # Módulos principales de SINETEC
    path('fichas/', views.fichas_view, name='fichas'),
    path('seguimiento/', views.seguimiento_view, name='seguimiento'),
    path('calificaciones/', views.calificaciones_view, name='calificaciones'),
    path('alertas/', views.alertas_tempranas, name='alertas_tempranas'),
    path('mensajeria/', views.mensajeria_view, name='mensajeria'),
    path('gestion-usuarios/', views.gestion_usuarios, name='gestion_usuarios'),

    # Gestión avanzada de estudiantes y reportes
    path('estudiantes/', views.estudiantes_lista, name='estudiantes_lista'),
    path('estudiantes/qr/<uuid:token>/', views.escanear_estudiante, name='escanear_qr'),
    path('estudiantes/<int:pk>/', views.detalle_estudiante, name='estudiantes_detalle'),
    path('estudiantes/<int:pk>/boletin-pdf/', views.exportar_boletin_pdf, name='estudiantes_boletin_pdf'),
    path('estudiantes/<int:pk>/editar/', views.editar_estudiante, name='estudiantes_editar'),
    path('estudiantes/<int:pk>/eliminar/', views.eliminar_estudiante, name='estudiantes_eliminar'),

    # Evaluaciones
    path('evaluaciones/crear/', views.crear_evidencia, name='crear_evidencia'),
    path('evaluaciones/<int:evidencia_id>/calificar/', views.sabana_calificaciones, name='sabana_calificaciones'),
]