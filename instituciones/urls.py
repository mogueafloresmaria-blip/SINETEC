from django.urls import path
from . import views

urlpatterns = [
    # Instituciones / Colegios
    path('', views.lista_instituciones, name='instituciones_lista'),
    path('nueva/', views.crear_institucion, name='instituciones_crear'),
    path('<int:pk>/', views.detalle_institucion, name='instituciones_detalle'),
    path('<int:pk>/editar/', views.editar_institucion, name='instituciones_editar'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado_institucion, name='instituciones_cambiar_estado'),
    path('<int:pk>/eliminar/', views.eliminar_institucion, name='instituciones_eliminar'),

    # Contactos Institucionales
    path('contactos/', views.contactos_lista, name='contactos_lista'),
    path('contactos/nuevo/', views.contacto_crear, name='contacto_crear'),
    path('contactos/<int:pk>/editar/', views.contacto_editar, name='contacto_editar'),
    path('contactos/<int:pk>/eliminar/', views.contacto_eliminar, name='contacto_eliminar'),

    # Observaciones y Antecedentes
    path('observaciones/', views.observaciones_lista, name='observaciones_lista'),
    path('observaciones/nueva/', views.observacion_crear, name='observacion_crear'),
    path('observaciones/<int:pk>/editar/', views.observacion_editar, name='observacion_editar'),
    path('observaciones/<int:pk>/eliminar/', views.observacion_eliminar, name='observacion_eliminar'),
]
