from django.contrib import admin
from .models import *

class MensajeAdmin(admin.ModelAdmin):
    readonly_fields=('FHCreacion','FHUltimaMod',)
    list_display =  ('Proyecto','Descripcion', 'Status',)
    search_fields = ('Proyecto__nombreproyecto',)# Llave foranea + __ + nombre del campo de la tabla principal

class MensajeReceptorAdmin(admin.ModelAdmin):
    readonly_fields=('FHCreacion','FHUltimaMod',)
    list_display =  ('Proyecto','Mensaje', 'Status',)
    search_fields = ('Proyecto__nombreproyecto',)
    
class MensajeRetroAAdmin(admin.ModelAdmin):
    readonly_fields=('FHCreacion','FHUltimaMod',)
    list_display =  ('Proyecto','Descripcion', 'Mensaje', 'Status',)
    search_fields = ('Proyecto__nombreproyecto',)

admin.site.register(Mensaje, MensajeAdmin)
admin.site.register(MensajeReceptor, MensajeReceptorAdmin)
admin.site.register(MensajeRetroA,MensajeRetroAAdmin)
admin.site.register(m_EventoScrum)
admin.site.register(m_ConfiguracionMensaje)
admin.site.register(AsistentesEventosScrum)
admin.site.register(m_RefinamientoProductBL)
admin.site.register(dia_sprint)

# admin.site.register(m_ReunionDiaria) 


