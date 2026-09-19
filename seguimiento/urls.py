from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_seguimientos, name='seguimiento_lista'),
    path('asistencia/', views.control_asistencia, name='seguimiento_asistencia'),
    path('nuevo/', views.nuevo_seguimiento, name='seguimiento_nuevo'),
    path('<int:pk>/', views.detalle_seguimiento, name='seguimiento_detalle'),
    path('<int:pk>/acta-pdf/', views.descargar_acta_pdf, name='seguimiento_acta_pdf'),
    path('secretaria/', views.secretaria_bandeja, name='secretaria_bandeja'),
    path('secretaria/solicitud/nueva/', views.nueva_solicitud, name='nueva_solicitud'),
    path('secretaria/solicitud/<int:pk>/', views.secretaria_detalle, name='secretaria_detalle'),
    path('secretaria/solicitud/<int:pk>/cambiar-estado/', views.cambiar_estado_solicitud, name='cambiar_estado_solicitud'),
    path('secretaria/mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
]
