from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Libro, PerfilUsuario, Prestamo


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'autor', 'año_publicacion', 
        'cantidad_stock', 'cantidad_disponible', 'disponible'
    ]
    list_filter = ['año_publicacion', 'autor']
    search_fields = ['titulo', 'autor']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información del Libro', {
            'fields': ('titulo', 'autor', 'año_publicacion')
        }),
        ('Stock', {
            'fields': ('cantidad_stock',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'


class CustomUserAdmin(UserAdmin):
    inlines = (PerfilUsuarioInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['user', 'rol', 'fecha_creacion']
    list_filter = ['rol', 'fecha_creacion']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = [
        'libro', 'usuario', 'fecha_prestamo', 
        'fecha_devolucion', 'esta_activo', 'dias_prestado'
    ]
    list_filter = ['fecha_prestamo', 'fecha_devolucion']
    search_fields = ['libro__titulo', 'usuario__username']
    readonly_fields = ['fecha_prestamo']
    
    fieldsets = (
        ('Información del Préstamo', {
            'fields': ('usuario', 'libro')
        }),
        ('Fechas', {
            'fields': ('fecha_prestamo', 'fecha_devolucion')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editando objeto existente
            return self.readonly_fields + ('usuario', 'libro')
        return self.readonly_fields


# Personalizar el sitio de administración
admin.site.site_header = "Administración - Sistema de Biblioteca"
admin.site.site_title = "Biblioteca Admin"
admin.site.index_title = "Gestión de Biblioteca"