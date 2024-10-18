from datetime import datetime
from django.db import models
# from Scrum.models import Proyecto, Empleado, Rol
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save, post_save
from Scrum.models import *
# from Scrum.models import HistoriaUsuario, Empleado, Proyecto, Rol, Sprint

# Create your models here.

#=============================Modelos de Mensajes==========================================================

class m_EventoScrum(models.Model):
    Descripcion = models.CharField(max_length=50,blank=True,null=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.Descripcion
    
class Mensaje(models.Model):
    ListaStatus = (
        ("1", "Generado"), 
        ("2", "Enviado"),
        ("3", "Comprendido"),
        ("4", "Cancelado")
        )

    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE)
    # EventoScrum = models.ForeignKey(m_EventoScrum,on_delete=models.CASCADE,blank=True,null=True)
    EventoScrum = models.ForeignKey(m_EventoScrum,on_delete=models.CASCADE, default=2)
    # Emisor = models.ForeignKey(Empleado,on_delete=models.CASCADE)
    Emisor = models.ForeignKey(Empleado,on_delete=models.CASCADE, related_name='MensajeEmisor')
    Descripcion = models.CharField(max_length=400,blank=True,null=True)
    FHCreacion=models.DateTimeField(auto_now_add=True)
    FHUltimaMod=models.DateTimeField(auto_now=True)
    Status = models.CharField(max_length=1,choices=ListaStatus, default='1')
    #Status = models.IntegerField()
    # Extras necesarios
    FechaHora = models.DateTimeField(null=True) # solo se usa una vez
    # Destinatario = models.ForeignKey(Empleado, on_delete=models.CASCADE, blank=True,null=True) # Obsoleto
    archivo = models.ForeignKey('m_Archivos', on_delete=models.CASCADE, blank=True,null=True) # Obsoleto - borrar en la proxima actualizacion
    Sprint = models.ForeignKey(Sprint,on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.Descripcion # + '. ' + self.ListaStatus[int(self.Status)-1][1]
    
class MensajeReceptor(models.Model):
    ListaStatus = (
        ("1", "Recibido"), 
        ("2", "Comprendido"),
        ("3", "NO Comprendido")
        )
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE)
    Mensaje = models.ForeignKey(Mensaje,on_delete=models.CASCADE)
    Receptor = models.ForeignKey(Empleado,on_delete=models.CASCADE)
    FHCreacion=models.DateTimeField(auto_now_add=True)
    FHUltimaMod=models.DateTimeField(auto_now=True)
    Status = models.CharField(max_length=1,choices=ListaStatus, default='1')
    # Extras necesarios
    EventoScrum = models.ForeignKey(m_EventoScrum,on_delete=models.CASCADE, blank=True,null=True) # hereda el id del modelo mensaje
    Emisor = models.ForeignKey(Empleado,on_delete=models.CASCADE, related_name="receptorEmisor",blank=True,null=True) # Hereda el emisor del modelo mensaje
    archivo = models.ForeignKey('m_Archivos',on_delete=models.CASCADE, blank=True,null=True) # Obsoleto - borrar en proxima actualizacion
    Sprint = models.ForeignKey(Sprint,on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return str(self.Mensaje) + '. ' + self.ListaStatus[int(self.Status)-1][1]

class MensajeRetroA(models.Model):
    ListaStatus = (
        ("1", "Generado"), 
        ("2", "Enviado"),
        ("3", "Aclarado y/o Comprendido"),
        ("4", "Cancelado"),
        ("5","No Comprendido")
        )
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE, blank=True,null=True)
    Mensaje = models.ForeignKey(Mensaje,on_delete=models.CASCADE, blank=True,null=True)
    EventoScrum = models.ForeignKey(m_EventoScrum,on_delete=models.CASCADE, blank=True,null=True)
    Emisor = models.ForeignKey(Empleado,on_delete=models.CASCADE, related_name='retroEmisor', blank=True,null=True)
    Descripcion = models.CharField(max_length=400)
    Contestacion = models.CharField(max_length=400, blank=True,null=True)
    FHCreacion=models.DateTimeField(auto_now_add=True)
    FHUltimaMod=models.DateTimeField(auto_now=True)
    Status = models.CharField(max_length=1,choices=ListaStatus, default='1')
    # El receptor recibe la contestacion de este modelo
    Receptor = models.ForeignKey(Empleado,on_delete=models.CASCADE, related_name='retroReceptor' ,blank=True,null=True)
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return str(self.Mensaje) + '. ' + self.ListaStatus[int(self.Status)-1][1]

class m_ConfiguracionMensaje(models.Model):
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE)
    EventoScrum = models.ForeignKey(m_EventoScrum,on_delete=models.CASCADE)
    RolEmisor = models.ForeignKey(Rol,on_delete=models.CASCADE, related_name='RolEmisor',blank=True,null=True)
    RolReceptor = models.ForeignKey(Rol,on_delete=models.CASCADE, related_name='RolReceptor',blank=True,null=True)
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return str(self.Proyecto) + '. ' + str(self.EventoScrum)  + '. ' + str(self.RolEmisor) + ' -> ' + str(self.RolReceptor)

class AsistentesEventosScrum(models.Model):
    TAsistencia = (
        ("S", "Síncrona"), 
        ("A", "Asíncrona")
        )
    TStatus = (
        ("1", "Obligatorio"),
        ("2", "Opcional"),
    )
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE, blank=True,null=True)
    EventoScrum = models.ForeignKey(m_EventoScrum,on_delete=models.CASCADE, blank=True,null=True)
    Mensaje =  models.ForeignKey(Mensaje,on_delete=models.CASCADE, blank=True,null=True)
    FechaHora = models.DateTimeField(auto_now=True)
    # Usuario = models.ForeignKey(User,on_delete=models.CASCADE, blank=True,null=True)
    Usuario = models.ForeignKey(Empleado,on_delete=models.CASCADE, blank=True,null=True)
    Rol = models.ForeignKey(Rol,on_delete=models.CASCADE,blank=True,null=True)
    Status = models.CharField(max_length=1,choices=TStatus, default='1')
    TipoAsistencia = models.CharField(max_length=1,choices=TAsistencia, default='S')
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return str(self.Proyecto) + ' ' + str(self.EventoScrum)

class m_RefinamientoProductBL(models.Model):
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE)
    Mensaje =  models.ForeignKey(Mensaje,on_delete=models.CASCADE)
    # Mensaje =  models.OneToOneField(Mensaje, on_delete=models.CASCADE, primary_key=True)
    Emisor = models.ForeignKey(Empleado,on_delete=models.CASCADE)
    FechaHora = models.DateTimeField(blank=True,null=False)
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return str(self.Proyecto) + '. ' + str(self.Mensaje) + '. Emisor: ' + str(self.Emisor) + '. ' + str(self.FechaHora)
    
class m_Archivos(models.Model):
    Descripcion = models.CharField(max_length=100)
    Archivo = models.FileField(upload_to='documents/')
    Mensaje = models.ForeignKey(Mensaje,on_delete=models.CASCADE, null=True, blank=True)
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.Descripcion
    
class m_ReunionDiaria(models.Model):
    FechaHora = models.DateTimeField(auto_now=True)
    Emisor = models.ForeignKey(Empleado,on_delete=models.CASCADE, null=True, blank=True)
    Mensaje = models.ForeignKey(Mensaje,on_delete=models.CASCADE, null=True, blank=True)
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE, null=True, blank=True)
    Sprint = models.ForeignKey(Sprint,on_delete=models.CASCADE, null=True, blank=True)
    ObstaculosPresentados = models.CharField(max_length=500)
    PlanDiaSiguiente = models.CharField(max_length=500)
    TrabajoRealizadoDiaAnterior = models.CharField(max_length=500)
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.ObstaculosPresentados
    
# ---------- Pendientes --------------------------
class m_PlanificacionSprint(models.Model):
    FechaHora = models.DateTimeField(null=False)
    Emisor = models.ForeignKey(Empleado,on_delete=models.CASCADE, null=True, blank=True)
    Mensaje = models.ForeignKey(Mensaje,on_delete=models.CASCADE, null=True, blank=True)
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE, null=True, blank=True)
    Sprint = models.ForeignKey(Sprint,on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.Emisor
    
class m_HomologacionVision(models.Model):
    FechaHora = models.DateTimeField(null=False)
    Emisor = models.ForeignKey(Empleado,on_delete=models.CASCADE, null=True, blank=True)
    Mensaje = models.ForeignKey(Mensaje,on_delete=models.CASCADE, null=True, blank=True)
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.Emisor

class m_RetrospectivaSprint(models.Model):
    Comentarios = models.CharField(max_length=200)
    FechaHora = models.DateTimeField(auto_now_add=True)
    Emisor = models.ForeignKey(Empleado,on_delete=models.CASCADE, null=True, blank=True)
    Mensaje = models.ForeignKey(Mensaje,on_delete=models.CASCADE, null=True, blank=True)
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE, null=True, blank=True)
    Sprint = models.ForeignKey(Sprint,on_delete=models.CASCADE, null=True, blank=True)
    OportunidadesMejora = models.CharField(max_length=200)
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.Comentarios
    
# Este sera el modelo para revision del sprint
class m_CierreSprint(models.Model):
    FechaHora = models.DateTimeField(null=False)
    Emisor = models.ForeignKey(Empleado,on_delete=models.CASCADE, null=True, blank=True)
    Mensaje = models.ForeignKey(Mensaje,on_delete=models.CASCADE, null=True, blank=True)
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE, null=True, blank=True)
    Sprint = models.ForeignKey(Sprint,on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['pk']

    #def __str__(self):
    #    return self.Emisor

class m_Comentarios(models.Model):
    Comentarios = models.CharField(max_length=200)
    Emisor = models.ForeignKey(Empleado,on_delete=models.CASCADE, null=True, blank=True)
    EventoScrum = models.ForeignKey(m_EventoScrum,on_delete=models.CASCADE, blank=True,null=True)
    Mensaje = models.ForeignKey(Mensaje,on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.Comentarios
    
# Ejecucion del sprint, este modelo es de prueba, pero la logica para el el procedimiento es el mismo
# Este modelo sirve para agregar la hora al dia, segun el sprint a utilizar
class dia_sprint(models.Model):
    sprint = models.ForeignKey(Sprint,on_delete=models.CASCADE)
    dia = models.DateTimeField(null=False)
    horasDedicadas = models.IntegerField(null=False)
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return str(self.sprint) + ', ' + str(self.dia) + ', horas dedicadas: ' + str(self.horasDedicadas)

# Obsoleto
#@receiver(post_save, sender=Mensaje)
#def clonar_mensaje_refinamiento(sender, instance, created, **kwargs):
#    if created:  # Solo actuar si el mensaje ha sido creado (no actualizado)
#        # Crear o actualizar un objeto m_RefinamientoProductBL basado en los datos del mensaje
#        m_RefinamientoProductBL.objects.update_or_create(
#            Proyecto=instance.Proyecto,
#            Mensaje=instance,
#            Emisor=instance.Emisor,
#            defaults={'FechaHora': instance.FechaHora}  # O FHUltimaMod, dependiendo de tus necesidades
#            # FechaHora=instance.FechaHora
#        )

 #========================================Fin Modelos de Mensajes ====================================================
      