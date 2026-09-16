from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_instituciones, name='instituciones_lista'),
    path('nueva/', views.crear_institucion, name='instituciones_crear'),
    path('<int:pk>/', views.detalle_institucion, name='instituciones_detalle'),
    path('<int:pk>/editar/', views.editar_institucion, name='instituciones_editar'),
]
