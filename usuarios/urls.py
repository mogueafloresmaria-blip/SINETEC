from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('buscar/', views.busqueda_global, name='busqueda_global'),
    path('fichas/', views.fichas, name='fichas'),
    path('estudiantes/', views.estudiantes_lista, name='estudiantes_lista'),
    path('estudiantes/registrar/', views.registrar_aprendiz, name='registrar_aprendiz'),
    path('biblioteca/', views.biblioteca_formacion, name='biblioteca_formacion'),
    path('estudiantes/qr/<uuid:token>/', views.qr_estudiante, name='estudiante_qr'),
    path('estudiantes/<int:pk>/boletin-pdf/', views.boletin_estudiante, name='estudiantes_boletin_pdf'),
    path('estudiantes/<int:pk>/', views.detalle_estudiante, name='estudiante_detalle'),
    path('seguimiento-panel/', views.seguimiento, name='seguimiento'),
    path('calificaciones/', views.calificaciones, name='calificaciones'),
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/evidencias/nueva/', views.crear_evidencia, name='crear_evidencia'),
    path('instructor/evidencias/<int:pk>/revisar/', views.revisar_evidencia, name='revisar_evidencia'),
    path('aprendiz/', views.aprendiz_dashboard, name='aprendiz_dashboard'),
    path('aprendiz/evidencias/<int:pk>/entregar/', views.entregar_evidencia, name='entregar_evidencia'),
    path('coordinacion/', views.coordinador_dashboard, name='coordinador_dashboard'),
    path('alertas/', views.alertas_tempranas, name='alertas_tempranas'),
    path('usuarios/', lambda request: views.modulo_simple(request, 'usuarios/gestion_usuarios.html'), name='gestion_usuarios'),
    path('mensajeria/', views.mensajeria, name='mensajeria'),
]