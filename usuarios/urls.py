from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('buscar/', views.busqueda_global, name='busqueda_global'),
    path('fichas/', views.fichas, name='fichas'),
    path('estudiantes/', views.estudiantes_lista, name='estudiantes_lista'),
    path('estudiantes/qr/<uuid:token>/', views.qr_estudiante, name='estudiante_qr'),
    path('estudiantes/<int:pk>/boletin-pdf/', views.boletin_estudiante, name='estudiantes_boletin_pdf'),
    path('estudiantes/<int:pk>/', views.detalle_estudiante, name='estudiante_detalle'),
    path('seguimiento-panel/', views.seguimiento, name='seguimiento'),
    path('calificaciones/', views.calificaciones, name='calificaciones'),
    path('alertas/', lambda request: views.modulo_simple(request, 'usuarios/alertas_tempranas.html'), name='alertas_tempranas'),
    path('usuarios/', lambda request: views.modulo_simple(request, 'usuarios/gestion_usuarios.html'), name='gestion_usuarios'),
    path('mensajeria/', lambda request: views.modulo_simple(request, 'mensajeria.html'), name='mensajeria'),
]