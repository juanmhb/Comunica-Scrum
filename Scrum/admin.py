from django.contrib import admin
from .models import *


admin.site.register(EstatusHistoria)
admin.site.register(EstatusTarea)
admin.site.register(EstatusSprint)
admin.site.register(Rol)
admin.site.register(Pais)
admin.site.register(Idioma)
class EmpleadoAdmin(admin.ModelAdmin):
    # columnas que se verán en la tabla del admin
    list_display = (
        'id',
        'rfc', 'cedulaprofesional', 'telefono',
        'rol',                      # <- nombre legible del Rol
        'usuario_id',               # <- User.id
        'usuario_username',         # <- User.username
        'usuario_first_name',       # <- User.first_name
        'usuario_email',            # <- User.email
    )

    # filtros y búsqueda útiles
    list_filter = ('Roles',)  # puedes agregar 'Pais', 'Idioma' si quieres
    search_fields = (
        'rfc', 'cedulaprofesional', 'telefono',
        'Roles__NombreRol',
        'Usuario__username', 'Usuario__first_name',
        'Usuario__last_name', 'Usuario__email',
    )

    # optimiza queries al traer FK/OneToOne
    list_select_related = ('Usuario', 'Roles')

    # ---------- columnas calculadas ----------
    @admin.display(ordering='Roles__NombreRol', description='Rol')
    def rol(self, obj):
        return getattr(obj.Roles, 'NombreRol', None)

    @admin.display(ordering='Usuario__id', description='User ID')
    def usuario_id(self, obj):
        return getattr(obj.Usuario, 'id', None)

    @admin.display(ordering='Usuario__username', description='Usuario')
    def usuario_username(self, obj):
        return getattr(obj.Usuario, 'username', None)

    @admin.display(ordering='Usuario__first_name', description='Nombre')
    def usuario_first_name(self, obj):
        # si quieres nombre completo: f"{obj.Usuario.first_name} {obj.Usuario.last_name}"
        return getattr(obj.Usuario, 'first_name', None)

    @admin.display(ordering='Usuario__email', description='Email')
    def usuario_email(self, obj):
        return getattr(obj.Usuario, 'email', None)
    
admin.site.register(Empleado, EmpleadoAdmin)
admin.site.register(JefeProyecto)
admin.site.register(Empresa)
admin.site.register(Proyecto)

class EmpleadoProyectoAdmin(admin.ModelAdmin):
    list_display = ('id', 'Empleado', 'Proyecto', 'Status')  # 👈 muestra todos los campos
    list_filter = ('Status', 'Proyecto')  # opcional: agrega filtros en el panel lateral
    search_fields = ('Empleado__nombre', 'Proyecto__nombre')  # opcional: búsqueda
admin.site.register(EmpleadoProyecto, EmpleadoProyectoAdmin)    
# admin.site.register(ProductBacklog)
admin.site.register(HistoriaUsuario)
admin.site.register(Tarea)
admin.site.register(Sprint)
# admin.site.register(SprintBacklog) No funciona y no se puede borrar
admin.site.register(ReunionDiaria)
admin.site.register(Progreso)
admin.site.register(PrioridadTarea)
admin.site.register(TareaAvance)
admin.site.register(sprint_Backlog)



