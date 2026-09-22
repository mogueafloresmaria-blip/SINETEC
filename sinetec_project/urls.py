from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from usuarios import views as views_usuarios

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),
    path('instituciones/', include('instituciones.urls')),
    path('academico/', include('academico.urls')),
    path('seguimiento/', include('seguimiento.urls')),
    path('evaluaciones/', include('evaluaciones.urls')),
    path('convenios/', include('convenios.urls')),
    path('login/', views_usuarios.custom_login_view, name='login_short'),
    path('accounts/login/', views_usuarios.custom_login_view, name='login'),
    path('accounts/logout/', views_usuarios.custom_logout_view, name='logout'),
    path('logout/', views_usuarios.custom_logout_view, name='logout_short'),
]

handler403 = 'usuarios.views.error_403_view'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)