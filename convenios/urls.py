from django.urls import path
from . import views

urlpatterns = [
    # Catálogo principal con estadísticas y búsqueda
    path('', views.catalogo_convenios, name='convenios_catalogo'),
    
    # Gestión de Instituciones de Convenio
    path('instituciones/nueva/', views.institucion_crear, name='institucion_convenio_crear'),
    path('instituciones/<int:pk>/', views.institucion_detalle, name='institucion_convenio_detalle'),
    path('instituciones/<int:pk>/editar/', views.institucion_editar, name='institucion_convenio_editar'),
    path('instituciones/<int:pk>/desactivar/', views.institucion_desactivar, name='institucion_convenio_desactivar'),
    
    # Gestión de Convenios SENA
    path('convenio/nuevo/', views.convenio_crear, name='convenio_crear'),
    path('instituciones/<int:institucion_id>/convenio/nuevo/', views.convenio_crear, name='convenio_crear_institucion'),
    path('convenio/<int:pk>/', views.convenio_detalle, name='convenio_detalle'),
    path('convenio/<int:pk>/editar/', views.convenio_editar, name='convenio_editar'),
    path('convenio/<int:pk>/eliminar/', views.convenio_eliminar, name='convenio_eliminar'),
    
    # Gestión de Beneficios del Convenio
    path('convenio/<int:convenio_id>/beneficio/nuevo/', views.beneficio_crear, name='beneficio_crear'),
    path('beneficio/<int:pk>/eliminar/', views.beneficio_eliminar, name='beneficio_eliminar'),

    # Gestión de Documentos
    path('convenio/<int:convenio_id>/documento/subir/', views.documento_subir, name='documento_convenio_subir'),
    path('documento/<int:pk>/descargar/', views.documento_descargar, name='documento_convenio_descargar'),
    path('documento/<int:pk>/eliminar/', views.documento_eliminar, name='documento_convenio_eliminar'),
]
