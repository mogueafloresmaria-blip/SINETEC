from django.urls import path
from . import views

urlpatterns = [
    # Semáforo de Competencias (3 colores: 🟢 Aprobado, 🟡 En proceso, 🔴 Por recuperar)
    path('semaforo/', views.semaforo_competencias, name='semaforo_competencias'),
    path('semaforo/api/actualizar/', views.api_actualizar_semaforo, name='api_actualizar_semaforo'),
    path('semaforo/exportar-excel/', views.exportar_semaforo_excel, name='exportar_semaforo_excel'),
    path('semaforo/exportar/excel/', views.exportar_semaforo_excel),
    path('semaforo/exportar-pdf/', views.exportar_semaforo_pdf, name='exportar_semaforo_pdf'),
    path('semaforo/exportar/pdf/', views.exportar_semaforo_pdf),

    # Sábana de Juicios RAP institucional SENA (A y D)
    path('raps/', views.raps_por_ficha, name='evaluaciones_raps'),
    path('aprendices/', views.aprendices_por_rap, name='evaluaciones_aprendices'),
    path('libreta/<int:pk>/', views.libreta_aprendiz, name='libreta_aprendiz'),
    path('calificar/<int:pk>/', views.calificar_aprendiz, name='calificar_aprendiz'),
    path('exportar-excel/', views.exportar_sabana_excel, name='evaluaciones_exportar_excel'),
    path('exportar-csv/', views.exportar_sabana_csv, name='evaluaciones_exportar_csv'),
    path('exportar-pdf/', views.reporte_rap_pdf, name='evaluaciones_exportar_pdf'),
    path('', views.sabana_calificaciones, name='evaluaciones_calificar'),
    path('cerrar-periodo/<int:ficha_id>/', views.cerrar_periodo_ficha, name='evaluaciones_cerrar_periodo'),
]