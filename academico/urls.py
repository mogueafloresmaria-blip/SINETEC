from django.urls import path
from . import views

urlpatterns = [
    path('fichas/', views.lista_fichas, name='fichas_lista'),
    path('fichas/nueva/', views.crear_ficha, name='fichas_crear'),
    path('fichas/<int:pk>/', views.detalle_ficha, name='fichas_detalle'),
    path('fichas/<int:ficha_id>/matricular/', views.matricular_aprendiz, name='fichas_matricular'),
]
