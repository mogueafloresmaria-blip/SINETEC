from django.urls import path
from . import views

urlpatterns = [
    path('fichas/', views.lista_fichas, name='fichas_lista'),
    path('fichas/nueva/', views.crear_ficha, name='fichas_crear'),
    path('horarios/', views.tablero_horarios, name='horarios_tablero'),
    path('horarios/nuevo/', views.crear_horario, name='horario_nuevo'),
    path('horarios/<int:pk>/eliminar/', views.eliminar_horario, name='horario_eliminar'),
    path('fichas/<int:pk>/', views.detalle_ficha, name='fichas_detalle'),
    path('fichas/<int:ficha_id>/matricular/', views.matricular_aprendiz, name='fichas_matricular'),
]
