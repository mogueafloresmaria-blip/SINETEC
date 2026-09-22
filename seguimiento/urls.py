from django.urls import path
from . import views

urlpatterns = [
    # Bitácoras formativas y pedagógicas (existente)
    path('', views.lista_seguimientos, name='seguimiento_lista'),
    path('asistencia/', views.control_asistencia, name='seguimiento_asistencia'),
    path('asistencia/sesion-qr/<int:ficha_id>/', views.proyectar_qr_sesion, name='seguimiento_qr_sesion'),
    path('asistencia/marcar-sesion/<int:ficha_id>/', views.marcar_asistencia_sesion, name='marcar_asistencia_sesion'),
    path('nuevo/', views.nuevo_seguimiento, name='seguimiento_nuevo'),
    path('<int:pk>/', views.detalle_seguimiento, name='seguimiento_detalle'),
    path('<int:pk>/editar/', views.editar_seguimiento, name='seguimiento_editar'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado_seguimiento, name='cambiar_estado_seguimiento'),
    path('<int:pk>/eliminar/', views.eliminar_seguimiento, name='seguimiento_eliminar'),
    path('<int:pk>/subir-evidencia/', views.subir_evidencia_seguimiento, name='subir_evidencia_seguimiento'),
    path('<int:pk>/eliminar-evidencia/', views.eliminar_evidencia_seguimiento, name='eliminar_evidencia_seguimiento'),
    path('<int:pk>/acta-pdf/', views.descargar_acta_pdf, name='seguimiento_acta_pdf'),

    # Secretaría (existente)
    path('secretaria/', views.secretaria_bandeja, name='secretaria_bandeja'),
    path('secretaria/solicitud/nueva/', views.nueva_solicitud, name='nueva_solicitud'),
    path('secretaria/solicitud/<int:pk>/', views.secretaria_detalle, name='secretaria_detalle'),
    path('secretaria/solicitud/<int:pk>/cambiar-estado/', views.cambiar_estado_solicitud, name='cambiar_estado_solicitud'),
    path('secretaria/mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),

    # Seguimientos Administrativos e Interinstitucionales
    path('administrativo/', views.seguimientos_administrativos_lista, name='seguimientos_admin_lista'),
    path('administrativo/nuevo/', views.seguimiento_admin_crear, name='seguimiento_admin_crear'),
    path('administrativo/<int:pk>/editar/', views.seguimiento_admin_editar, name='seguimiento_admin_editar'),
    path('administrativo/<int:pk>/cambiar-estado/', views.seguimiento_admin_cambiar_estado, name='seguimiento_admin_cambiar_estado'),
    path('administrativo/<int:pk>/eliminar/', views.seguimiento_admin_eliminar, name='seguimiento_admin_eliminar'),

    # Calendario y Agenda Institucional
    path('calendario/', views.calendario_administrativo, name='calendario_administrativo'),
    path('calendario/evento/nuevo/', views.evento_calendario_crear, name='evento_calendario_crear'),
    path('calendario/evento/<int:pk>/eliminar/', views.evento_calendario_eliminar, name='evento_calendario_eliminar'),

    # Biblioteca Documental Administrativa (Repositorio Digital)
    path('documentos/', views.documentos_admin_lista, name='documentos_admin_lista'),
    path('documentos/subir/', views.documento_admin_subir, name='documento_admin_subir'),
    path('documentos/<int:pk>/descargar/', views.documento_admin_descargar, name='documento_admin_descargar'),
    path('documentos/<int:pk>/eliminar/', views.documento_admin_eliminar, name='documento_admin_eliminar'),
]
