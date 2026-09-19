from django.urls import path
from . import views

urlpatterns = [
    path('fichas/', views.lista_fichas, name='fichas_lista'),
    path('fichas/nueva/', views.crear_ficha, name='fichas_crear'),
    path('fichas/<int:pk>/', views.detalle_ficha, name='fichas_detalle'),
    path('fichas/<int:pk>/editar/', views.editar_ficha, name='ficha_editar'),
    path('fichas/<int:pk>/reporte-pdf/', views.reporte_ficha_pdf, name='ficha_reporte_pdf'),
    path('fichas/<int:pk>/reporte/pdf/', views.reporte_ficha_pdf),
    path('fichas/<int:pk>/reporte-excel/', views.reporte_ficha_excel, name='ficha_reporte_excel'),
    path('fichas/<int:pk>/reporte/excel/', views.reporte_ficha_excel),
    path('fichas/<int:ficha_id>/matricular/', views.matricular_aprendiz, name='fichas_matricular'),
    path('programas/', views.lista_programas, name='programas_lista'),
    path('programas/<int:pk>/', views.detalle_programa, name='programa_detalle'),
    path('certificacion/', views.consulta_certificacion, name='consulta_certificacion'),
    path('horarios/', views.tablero_horarios, name='horarios_tablero'),
    path('horarios/nuevo/', views.crear_horario, name='horario_nuevo'),
    path('horarios/<int:pk>/eliminar/', views.eliminar_horario, name='horario_eliminar'),
]
