from django.db import models
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.dispatch import receiver
from colorfield.fields import ColorField
from django.db.models.signals import post_delete, pre_save, post_save
from django.db.models import JSONField


# from Mensajes.models import *

class Idioma(models.Model):
    idioma=models.CharField(max_length=70, null=False)
    descripcion=models.CharField(max_length=200, null=False)
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.idioma


class Pais(models.Model):
    pais=models.CharField(max_length=70, null=False)
    descripcion=models.CharField(max_length=200, null=False)
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.pais

class EstatusHistoria(models.Model):
    estatus= models.CharField(max_length=100,null=False)
    descripcion = models.CharField(max_length=300,null=True,blank=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.estatus



class EstatusTarea(models.Model):
    estatus= models.CharField(max_length=100,null=False)
    descripcion = models.CharField(max_length=300,null=True,blank=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.estatus


class EstatusSprint(models.Model):
    estatus= models.CharField(max_length=100,null=False)
    descripcion = models.CharField(max_length=300,null=True,blank=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.estatus


class Rol(models.Model):
    NombreRol=models.CharField(max_length=45, null=False)
    #roles=models.CharField(max_length=45, null=False)
    #descripcion=models.CharField(max_length=85, null=False)
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.NombreRol

class Empleado(models.Model):
    rfc=models.CharField(max_length=13,null=False, unique=True)
    telefono = models.CharField(blank=True, null=True,max_length=10)
    cedulaprofesional = models.CharField(max_length=8, null=False, unique=True)
    # Roles = models.ManyToManyField(Rol)
    # cuando se registre un empleado, por defecto tendra el rol de Developers
    Roles = models.ForeignKey(Rol, on_delete=models.CASCADE, default=3) 
    Pais = models.ForeignKey(Pais,on_delete=models.CASCADE,null=True)
    Idioma = models.ForeignKey(Idioma,on_delete=models.CASCADE,null=True)
    Usuario= models.OneToOneField(User,related_name='usuarioempleado', on_delete=models.CASCADE,null=True)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.Usuario.first_name +' '+ self.Usuario.last_name


class JefeProyecto(models.Model):
    rfc=models.CharField(max_length=13,null=False, unique=True)
    telefono = models.CharField(blank=True, null=True,max_length=10)
    cedulaprofesional = models.CharField(max_length=8, null=False, unique=True)
    Pais = models.ForeignKey(Pais,on_delete=models.CASCADE,null=True)
    Idioma = models.ForeignKey(Idioma,on_delete=models.CASCADE,null=True)
    Usuario= models.OneToOneField(User,related_name='usuariojefeproyecto', on_delete=models.CASCADE,null=True)
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.Usuario.first_name +' '+ self.Usuario.last_name


class Proyecto(models.Model):
    JefeProyecto = models.ForeignKey(JefeProyecto,on_delete=models.CASCADE,related_name='JefeProyectoProyectos')
    nombreproyecto = models.CharField(max_length=200,null=False, unique=True)
    fechainicio = models.DateField(blank=True,null=False)
    fechafinal = models.DateField(blank=True,null=False)
    objetivo = models.CharField(max_length=1000,null=True,blank=True)
    impacto = models.CharField(max_length=1000,null=True,blank=True)
    homologacionvision = models.CharField(max_length=1000,null=True,blank=True)


    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.nombreproyecto 


class EmpleadoProyecto(models.Model):
    Empleado = models.ForeignKey(Empleado,on_delete=models.CASCADE,null=True, related_name='DetalleEmpleado')
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE,null=True, related_name='DetalleProyecto')

    class Meta:
        ordering = ['pk']


# class ProductBacklog(models.Model):
#     Proyecto = models.OneToOneField(Proyecto, on_delete=models.CASCADE)
#     fechaelavoracion = models.DateField(null=True)
#     ultimaactualizacion = models.DateField(null=True)

#     class Meta:
#         ordering = ['pk']

#     def __str__(self):
#         return self.Proyecto.nombreproyecto
        



class Sprint(models.Model):
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE, related_name='ProyectoSprints')
    Estatus = models.ForeignKey(EstatusSprint,on_delete=models.CASCADE,related_name='EstatusSprints')
    nombresprint = models.CharField(max_length=200,null=False)
    fechainiciosprint = models.DateField(null=False)
    fechafinalsprint = models.DateField(null=True,blank=True)
    numerosprint = models.IntegerField(null=False)
    objetivosprint = models.CharField(max_length=400,null=False)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.nombresprint

from Mensajes.models import Mensaje

class HistoriaUsuario(models.Model):
    ListaCriterio = (
        ("1", "Si"), 
        ("2", "No"),
        )
    ListaPrioridad = (
        ("1", "Alta"), 
        ("2", "Media"),
        ("3", "Baja"),
        )
    # ProductBacklog = models.ForeignKey(ProductBacklog,on_delete=models.CASCADE, related_name='BacklogHistorias')
    Estatus = models.ForeignKey(EstatusHistoria,on_delete=models.CASCADE,related_name='EstatusHistoriasUsuarios')
    nombre =  models.CharField(max_length=200,null=False)
    NumeroHU = models.CharField(max_length=10,null=True)
    fechacreacion = models.DateField(null=False)
    ultimaactualizacion = models.DateField(blank=True,null=True)
    descripcion = models.CharField(max_length=1000,null=False)
    HorasEstimadas = models.IntegerField(null=True, blank=True)
    Prioridad = models.CharField(max_length=1,choices=ListaPrioridad,null=True, blank=True)
    # Prioridad = models.IntegerField(null=True, blank=True)
    CriteriosAceptacion = models.CharField(max_length=400,null=True, blank=True)
    #CriteriosAceptacion = models.CharField(max_length=1,choices=ListaCriterio,null=True, blank=True)
    MensajeRPBL = models.ForeignKey(Mensaje,  on_delete=models.CASCADE,null=True, blank=True  )
    # tereas_asignadas = models.BooleanField(null=True)
    tereasasignadas = models.BooleanField(default=False)
    Sprint = models.ForeignKey(Sprint,on_delete=models.CASCADE,null=True, blank=True, related_name='SprintHistoriasUsuario')
    Proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True, blank=True, related_name='ProyectoHistoriasUsuario')

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.nombre


class PrioridadTarea(models.Model):
    prioridad = models.CharField(max_length=100,null=False)
    colors =  models.CharField(max_length=100,null=False)

    class Meta:
        ordering = ['pk']
        
    def __str__(self):
        return str(self.prioridad) 


class Tarea(models.Model):
    HistoriaUsuario = models.ForeignKey(HistoriaUsuario,on_delete=models.CASCADE, related_name='HistoriaTareas')
    Rol = models.ForeignKey(Rol,on_delete=models.CASCADE, related_name='RolTareas')
    Estatus = models.ForeignKey(EstatusTarea,on_delete=models.CASCADE,related_name='EstatusTareas')
    Prioridad = models.ForeignKey(PrioridadTarea,on_delete=models.CASCADE,related_name='PrioridadTareas')
    fechainicioplaneado= models.DateField(blank=True,null=True)
    nombre =  models.CharField(max_length=200,null=False)
    fechainicioreal= models.DateField(blank=True,null=True)
    fechafinalplaneado= models.DateField(blank=True,null=True)
    fechafinalreal = models.DateField(blank=True,null=True)
    horasestimadas = models.IntegerField(null=False)
    # horasreales = models.IntegerField(null=True)
    

    Empleado = models.ForeignKey(Empleado,on_delete=models.CASCADE, null=True, blank=True) # Extra necesario
    Proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, null=True, blank=True, related_name='ProyectoTareas')
    
    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.nombre
    
    

class TareaAvance(models.Model):
    HistoriaUsuario = models.ForeignKey(HistoriaUsuario, on_delete=models.CASCADE, related_name='HistoriaTareasAvance', null=True, blank=True)
    #fechaAvance= models.DateField(auto_now=True)
    fechaAvance= models.DateField(null=False)
    horasDedicadas = models.IntegerField(null=False)
    horasRestantes = models.IntegerField(blank=True, null=True)
    horasReales = models.IntegerField(null=False, default=0)
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='tareaAvance', null=True, blank=True)
    dia_1 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_2 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_3 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_4 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_5 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_6 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_7 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_8 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_9 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_10 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_11 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_12 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_13 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_14 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_15 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_16 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_17 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_18 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_19 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_20 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_21 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_22 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_23 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_24 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_25 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_26 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_27 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_28 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_29 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_30 = models.CharField(max_length=5, blank=True, default='0/0')
    dia_31 = models.CharField(max_length=5, blank=True, default='0/0')


class Tareas_kanban(models.Model):
    horasDedicadas = models.IntegerField(null=False)
    horasRestantes = models.IntegerField(default=0)
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='tareas_kanban', null=True, blank=True)
    estado = models.CharField(max_length=50, choices=[
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Completada', 'Completada')
    ])

    class Meta:
        ordering = ['pk']

   
   
# modelo actualizado
class sprint_Backlog(models.Model):
    Proyecto = models.ForeignKey(Proyecto,on_delete=models.CASCADE)
    Sprint = models.ForeignKey(Sprint,on_delete=models.CASCADE, null=True, blank=True)
    historiaUsuario = models.ForeignKey(HistoriaUsuario,on_delete=models.CASCADE)

    class Meta:
        ordering = ['pk']

# modelo desactualizado, por alguna razon no se puede borrar...
class SprintBacklog(models.Model):
    Sprint = models.ForeignKey(Sprint,on_delete=models.CASCADE,related_name='SprintSprintBacklogs')
    Tarea = models.ForeignKey(Tarea,on_delete=models.CASCADE,related_name='TareaSprintBacklogs')
    Empleado = models.ForeignKey(Empleado,on_delete=models.CASCADE,related_name='EmpleadoSprintBacklog',null=True)
    observaciones = models.CharField(max_length=1000,null=True)

    class Meta:
        ordering = ['pk']




class ReunionDiaria(models.Model):
    Sprint = models.ForeignKey(Sprint,on_delete=models.CASCADE,related_name='SprintReuniones')
    fecha = models.DateField()
    observaciones = models.CharField(max_length=1000,null=True,blank=True)

    class Meta:
        ordering = ['fecha']
        
    def __str__(self):
        return str(self.fecha) 


class Progreso(models.Model):
    ReunionDiaria = models.ForeignKey(ReunionDiaria,on_delete=models.CASCADE,related_name='ReuniondiariaProgresos')
    SprintBacklog = models.ForeignKey(SprintBacklog,on_delete=models.CASCADE,related_name='SprintBacklogProgresos')
    horasinvertivas = models.IntegerField(null=False)

    class Meta:
        ordering = ['pk']


# @receiver(post_save, sender=Proyecto, dispatch_uid="update_stock_count") 
# def New_ProductBacklog(sender, instance, **kwargs):
    
#     my_objects_ProductPacklog= list(ProductBacklog.objects.filter(Proyecto=instance))
#     if not my_objects_ProductPacklog:
#         productbacklog = ProductBacklog.objects.create(Proyecto=instance)
#         productbacklog.save()

#     post_save.disconnect(New_ProductBacklog, sender=Proyecto)
#     post_save.connect(New_ProductBacklog, sender=Proyecto)


#@receiver(post_save, sender=Tarea, dispatch_uid="update_stock_count") 
#def New_SprintBacklog(sender, instance, **kwargs):
    
#    my_objects_SprintBacklog= list(SprintBacklog.objects.filter(Tarea=instance))
#    if not my_objects_SprintBacklog:
#        sprintbacklog = SprintBacklog.objects.create(Tarea=instance,Sprint=instance.HistoriaUsuario.Sprint)
#        sprintbacklog.save()

#    my_objects_tareas = list(Tarea.objects.filter(Estatus__pk=1,HistoriaUsuario=instance.HistoriaUsuario))
#    if not my_objects_tareas:
#        historiusuario = instance.HistoriaUsuario
#        historiusuario.tereasasignadas = True
#        historiusuario.save()
#    else:
#        historiusuario = instance.HistoriaUsuario
#        historiusuario.tereasasignadas = False
#        historiusuario.save()


#    post_save.disconnect(New_SprintBacklog, sender=Tarea)
#    post_save.connect(New_SprintBacklog, sender=Tarea)


@receiver(post_save, sender=ReunionDiaria, dispatch_uid="update_stock_count") 
def News_Progreso(sender, instance, **kwargs):
    
    my_objects_Progreso= list(Progreso.objects.filter(ReunionDiaria=instance))
    if not my_objects_Progreso:
        list_sprintbacklog = list(SprintBacklog.objects.filter(Tarea__HistoriaUsuario__Sprint=instance.Sprint))
        for sprintbacklog in list_sprintbacklog: 
            progreso = Progreso.objects.create(ReunionDiaria=instance,SprintBacklog=sprintbacklog,horasinvertivas=0)
            progreso.save()

    post_save.disconnect(News_Progreso, sender=ReunionDiaria)
    post_save.connect(News_Progreso, sender=ReunionDiaria)

#@receiver(post_save, sender=SprintBacklog, dispatch_uid="update_stock_count") 
#def Update_SprintBacklog(sender, instance, **kwargs):
    
    # my_objects_SprintBacklog= list(SprintBacklog.objects.filter(Tarea=instance))
    
#    status = EstatusTarea.objects.all()
#    if( instance.Empleado != None) and (instance.Tarea.Estatus != status[1])  :
        # status = EstatusTarea.objects.all()
#        tarea = instance.Tarea
#        tarea.Estatus = status[1]
#        tarea.save()
#        print(instance.Empleado)

#    post_save.disconnect(Update_SprintBacklog, sender=SprintBacklog)
#    post_save.connect(Update_SprintBacklog, sender=SprintBacklog)