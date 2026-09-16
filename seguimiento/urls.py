from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_seguimientos, name='seguimiento_lista'),
    path('asistencia/', views.control_asistencia, name='seguimiento_asistencia'),
    path('nuevo/', views.nuevo_seguimiento, name='seguimiento_nuevo'),
    path('<int:pk>/', views.detalle_seguimiento, name='seguimiento_detalle'),
    path('<int:pk>/acta-pdf/', views.descargar_acta_pdf, name='seguimiento_acta_pdf'),
]
