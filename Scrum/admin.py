from django.contrib import admin
from .models import *


admin.site.register(EstatusHistoria)
admin.site.register(EstatusTarea)
admin.site.register(EstatusSprint)
admin.site.register(Rol)
admin.site.register(Pais)
admin.site.register(Idioma)
admin.site.register(Empleado)
admin.site.register(JefeProyecto)
admin.site.register(Proyecto)
admin.site.register(EmpleadoProyecto)
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



