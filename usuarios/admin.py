from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Rol, PerfilUsuario


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name = "Información Institucional / Perfil SINETEC"
    verbose_name_plural = "Información Institucional / Perfil SINETEC"


class UserAdmin(BaseUserAdmin):
    inlines = [PerfilUsuarioInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'obtener_rol', 'obtener_documento', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'perfil__rol')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'perfil__numero_documento')

    def obtener_rol(self, obj):
        return obj.perfil.rol.nombre if hasattr(obj, 'perfil') and obj.perfil.rol else "Sin Rol"
    obtener_rol.short_description = "Rol Institucional"

    def obtener_documento(self, obj):
        return f"{obj.perfil.tipo_documento} {obj.perfil.numero_documento}" if hasattr(obj, 'perfil') else "-"
    obtener_documento.short_description = "Documento"


# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'tipo_documento', 'obtener_nombre_completo', 'rol', 'telefono', 'esta_activo')
    list_filter = ('rol', 'tipo_documento', 'esta_activo')
    search_fields = ('numero_documento', 'usuario__first_name', 'usuario__last_name', 'usuario__email')

    def obtener_nombre_completo(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username
    obtener_nombre_completo.short_description = "Nombre Completo"
