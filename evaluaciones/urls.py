from django.urls import path
from . import views

urlpatterns = [
    path('raps/', views.raps_por_ficha, name='evaluaciones_raps'),
    path('aprendices/', views.aprendices_por_rap, name='evaluaciones_aprendices'),
    path('exportar-excel/', views.exportar_sabana_excel, name='evaluaciones_exportar_excel'),
    path('exportar-pdf/', views.reporte_rap_pdf, name='evaluaciones_exportar_pdf'),
    path('', views.sabana_calificaciones, name='evaluaciones_calificar'),
    path('cerrar-periodo/<int:ficha_id>/', views.cerrar_periodo_ficha, name='evaluaciones_cerrar_periodo'),
]