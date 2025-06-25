from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
# from .forms import *
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View,TemplateView, ListView, UpdateView, CreateView, DeleteView, FormView
import requests

from Mensajes.forms import *
from Mensajes.models import *
from Scrum.models import *

from .utils import render_to_pdf
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q, F
from django.db import transaction
from django.contrib import messages
import time
from datetime import datetime
from django.contrib.auth import login, logout, authenticate
from django.db.models import Sum
import random
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import get_object_or_404
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.text import slugify
import calendar
import matplotlib.pyplot as plt
import io
from Scrum.utils.burndown import construir_pdf_burndown

# ----------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Reunión de Refinamiento del Product Backlog ---------------------------------------
# Lista Refinamiento
def listaRefinamientoProductBL(request):
    if request.user.is_authenticated:
        usuario = request.user.id
        empleado = Empleado.objects.get(Usuario=usuario)
        # Obtener los proyectos en los que el empleado participa
        proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)

        if request.user.usuarioempleado.Roles.NombreRol == 'Product Owner':
            #mensajes = Mensaje.objects.filter(Q(Emisor=empleado) & Q(EventoScrum="2") & Q(Proyecto__in=proyectos))
            mensajes = Mensaje.objects.filter(Q(EventoScrum="2") & Q(Proyecto__in=proyectos))

        #mensajes2 = m_RefinamientoProductBL.objects.filter(Q(Emisor=empleado) & Q(Proyecto__in=proyectos))
        #asistentes = AsistentesEventosScrum.objects.all()
        data = {
            #'form':mensajes2,
            'form2':mensajes,
            #'form3':asistentes
        }

        user = request.user

        if user is not None:
            login(request, user)
            # Redirecciona al usuario dependiendo de su rol
            if user.usuarioempleado.Roles.NombreRol == 'Product Owner':
                return render(request, 'Mensajes/ProductOwner/listaRefinamientoBL.html', data)
            else:
                # si el usuario no es Product Owner se mostrara el siguiente mensaje
                return HttpResponse("No eres Product Owner")
        else:
        # Usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    else: 
        return HttpResponseRedirect(reverse('Scrum:Logout'))

# @transaction.atomic
# def crear_Refinamiento(request):
#     usuario = request.user
#     empleado = Empleado.objects.get(Usuario=usuario)

#     if request.method == 'POST':
#         form = MensajeForms(request.POST, user=request.user)
#         if form.is_valid():

#             # Obtener datos del formulario o de donde sea necesario
#             descripcion = form.cleaned_data['Descripcion']
#             fecha_hora = form.cleaned_data['FechaHora']
#             proyecto = form.cleaned_data['Proyecto']
#             ref = m_EventoScrum.objects.get(pk=2)

#             # Crear instancia de Mensaje
#             mensaje = Mensaje.objects.create(
#                 Descripcion=descripcion,
#                 FechaHora=fecha_hora,
#                 Emisor=empleado,
#                 Proyecto=proyecto,
#                 EventoScrum=ref,
#                 # Asignar otras relaciones según sea necesario
#             )

#             # Crear instancia de m_RefinamientoProductBL
#             planificacion = m_RefinamientoProductBL.objects.create(
#                 Emisor=empleado,
#                 FechaHora=fecha_hora,
#                 Mensaje=mensaje,
#                 Proyecto=proyecto,
#                 # Asignar otras relaciones según sea necesario
#             )

#         # Redirigir a alguna página de éxito o hacer lo que necesites
#         return redirect('Mensajes:listaRefinamiento')
#     else:
#         form = MensajeForms(user=request.user)
#     return render(request, 'Mensajes/ProductOwner/crearRefinamientoBL.html', {'form': form})

def registrar_asistentes_y_receptores(proyecto, sprint, mensaje, evento, emisor):
    """
    Crea automáticamente los asistentes y receptores para un mensaje de evento Scrum.

    Args:
        proyecto (Proyecto): Proyecto asociado.
        sprint (Sprint or None): Sprint asociado (puede ser None).
        mensaje (Mensaje): El mensaje del evento.
        evento (m_EventoScrum): Tipo de evento Scrum.
        emisor (Empleado): Empleado que emite el mensaje.
    """
    empleados_activos = EmpleadoProyecto.objects.filter(
        Proyecto=proyecto,
        Status="1"
    ).select_related("Empleado", "Empleado__Roles")

    for ep in empleados_activos:
        empleado = ep.Empleado

        # Asistente
        AsistentesEventosScrum.objects.create(
            Proyecto=proyecto,
            EventoScrum=evento,
            Mensaje=mensaje,
            Usuario=empleado,
            Rol=empleado.Roles,
            Status="1",  # Obligatorio
            TipoAsistencia="S"
        )

        # Receptor
        MensajeReceptor.objects.create(
            Proyecto=proyecto,
            Mensaje=mensaje,
            Receptor=empleado,
            EventoScrum=evento,
            Emisor=emisor,
            Sprint=sprint,
        )


@transaction.atomic
def crear_Refinamiento(request):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    if request.method == 'POST':
        form = MensajeForms(request.POST, user=request.user)
        if form.is_valid():
            descripcion = form.cleaned_data['Descripcion']
            fecha_hora = form.cleaned_data['FechaHora']
            proyecto = form.cleaned_data['Proyecto']
            ref = m_EventoScrum.objects.get(pk=2)  # Refinamiento

            # Crear el mensaje principal (reunión)
            mensaje = Mensaje.objects.create(
                Descripcion=descripcion,
                FechaHora=fecha_hora,
                Emisor=empleado,
                Proyecto=proyecto,
                EventoScrum=ref,
            )

            # Crear instancia de refinamiento del Product Backlog
            m_RefinamientoProductBL.objects.create(
                Emisor=empleado,
                FechaHora=fecha_hora,
                Mensaje=mensaje,
                Proyecto=proyecto,
            )

            # # Obtener empleados activos del proyecto
            # empleados_activos = EmpleadoProyecto.objects.filter(
            #     Proyecto=proyecto,
            #     Status="1"  # Activo
            # ).select_related("Empleado", "Empleado__Roles")

            # for ep in empleados_activos:
            #     emp = ep.Empleado

            #     # Crear asistente
            #     AsistentesEventosScrum.objects.create(
            #         Proyecto=proyecto,
            #         EventoScrum=ref,
            #         Mensaje=mensaje,
            #         Usuario=emp,
            #         Rol=emp.Roles,
            #         Status="1",           # Obligatorio
            #         TipoAsistencia="S"    # Síncrona
            #     )

            #     # Crear mensaje receptor
            #     MensajeReceptor.objects.create(
            #         Proyecto=proyecto,
            #         Mensaje=mensaje,
            #         Receptor=emp,
            #         EventoScrum=ref,
            #         Emisor=empleado,
            #         Sprint=None  # Refinamiento no tiene sprint asignado
            #     )
            sp=None
            registrar_asistentes_y_receptores(
                proyecto=proyecto,
                sprint=sp,
                mensaje=mensaje,
                evento=ref,
                emisor=empleado
            )

            return redirect('Mensajes:listaRefinamiento')

    else:
        form = MensajeForms(user=request.user)

    return render(request, 'Mensajes/ProductOwner/crearRefinamientoBL.html', {'form': form})


class ActualizarMensaje(LoginRequiredMixin, UpdateView):
    model = Mensaje
    template_name = 'Mensajes/ProductOwner/editarMensaje.html'
    form_class = UpdateMensajePDF_Forms
    success_url = reverse_lazy('Mensajes:listaRefinamiento')
    def get_form_kwargs(self):
        # Obtener los kwargs del formulario y agregar el usuario autenticado
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
def eliminar_Mensaje(request, id):
    producto = get_object_or_404(Mensaje, id=id)
    producto.delete()
    return redirect(to="Mensajes:listaRefinamiento")

# eliminar_RefinamientoProductB, OBSOLETO
def enviar_mensajeF(request, id):
    # receptor = User.objects.get(id=id)
    usuarios_asistentes = AsistentesEventosScrum.objects.all()
    mensaje = Mensaje.objects.get(pk=id) 

    for usuario in usuarios_asistentes:
            # Aquí puedes personalizar el mensaje según sea necesario
            descripcion = mensaje.Descripcion
            emisor = mensaje.Emisor
            destinatario = usuario.Usuario

    mensaje = AsistentesEventosScrum()

    return render(request, 'Mensajes/ProductOwner/listaRefinamientoBL.html')

# Product Owner, no usar este metodo
def enviar_mensaje(request, id):
    idSms = Mensaje.objects.get(pk=id)
    receptor = User.objects.get(pk=5)

    usuario = request.user.id
    empleado = Empleado.objects.get(Usuario=usuario)

    # usuarios = User.objects.filter(pk=5) 

    if request.method == 'POST':
        # form = MensajeForms(request.POST)
        form = envAsistentesForms(request.POST)
        if form.is_valid():
            # idSms = Mensaje.objects.get(pk=id)
            msm = Mensaje.objects.filter(pk=id)

            for contenido in msm:
                proyecto = contenido.Proyecto
                eventoScrum=contenido.EventoScrum
                mensaje=contenido
                status=contenido.Status
                fecha=contenido.FechaHora
                archivo=contenido.archivo
                
            proyecto = contenido.Proyecto
            descripcion = contenido.Descripcion
            eventoScrum = contenido.EventoScrum
            status = contenido.Status
            fecha = contenido.FechaHora
            archivo = contenido.archivo

            res = AsistentesEventosScrum.objects.filter(Mensaje=idSms)
            # res = AsistentesEventosScrum.objects.all()

            for asistente in res:
                # asistentes=asistente.Usuario
                mensaje = Mensaje(Emisor=empleado, Proyecto=proyecto, Descripcion=descripcion, Status="2", 
                              EventoScrum=eventoScrum, FechaHora=fecha, Destinatario=asistente.Usuario, archivo=archivo)
                mensaje.save()

            return redirect('Scrum:index')  # Redirigir a la página de mensajes enviados
    else:
        form = envAsistentesForms
        form2 = Mensaje.objects.filter(pk=id)
        form3 = AsistentesEventosScrum.objects.filter(Mensaje=idSms)
    return render(request, 'Mensajes/ProductOwner/enviarMensaje.html', {'form': form, 'receptor': receptor, 'form2':form2, 'form3':form3})

# -------------------------------------- Asistentes Evento Scrum - CRUD ---------------------------------------
# Refinamiento BL
def crear_Asistente(request,id):
    # emisor = User.objects.get(id=id)
    # mensajes = Mensaje.objects.all()

    mensajes = Mensaje.objects.filter(pk=id)

    if request.method == 'POST':
        form = AsistentesForms(request.POST)
        if form.is_valid():
            
            for mensaje in mensajes:
                # Crear un AsistentesEventosScrum con los datos del mensaje
                asistente = AsistentesEventosScrum(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum,
                    Mensaje=mensaje,
                            # Usuario=mensaje.Emisor,  # Supongo que el Emisor del mensaje se convierte en el Usuario del Asistente
                )
                
            usuario = form.cleaned_data['Usuario']
            rol = form.cleaned_data['Rol']
            status = form.cleaned_data['Status']
            asistencia = form.cleaned_data['TipoAsistencia']
            proyecto = asistente.Proyecto
            eventoScrum = asistente.EventoScrum
            mensajeid = asistente.Mensaje

            
            mensaje = AsistentesEventosScrum(Usuario=usuario,Rol=rol,Status=status,TipoAsistencia=asistencia, Proyecto=proyecto,
                                             EventoScrum=eventoScrum, Mensaje=mensajeid)
            mensaje.save()
            # asistente.save()
            return redirect('Mensajes:listaRefinamiento')  # Redirigir a la página de mensajes enviados
    else:
        form = AsistentesForms()
    return render(request, 'Mensajes/ProductOwner/crearAsistentes.html', {'form': form})

def lista_asistentes_por_mensaje(request, id):
    # Obtener el mensaje específico por su ID
    mensaje = Mensaje.objects.get(pk=id)

    # Obtener todos los AsistentesEventosScrum asociados a este mensaje
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)

    clave = id

    return render(request, 'Mensajes/ProductOwner/listaAsistentes.html', {'form': asistentes, 'clave':clave})

class ActualizarAsistente(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Mensajes/ProductOwner/editarAsistente.html'
    form_class = AsistentesForms
    success_url = reverse_lazy('Mensajes:listaRefinamiento')

def eliminar_Asistente(request, id):
    producto = get_object_or_404(AsistentesEventosScrum, id=id)
    producto.delete()
    return redirect(to="Mensajes:listaRefinamiento")

# ------------------------------------ Historias de usuario ------------------------------------
# Este apartado solo jala las historias de usuario ya creadas, pero con un status especifico
# solo podemos leer, y editar

# Reunion de refinamiento BL
def listaHistoriaUsuariosBL(request, id_Mensaje):

      # Obtén el mensaje para acceder al proyecto
    mensaje = get_object_or_404(Mensaje, pk=id_Mensaje)  
    proyecto_id = mensaje.Proyecto.id

    historias = HistoriaUsuario.objects.filter(Q(Estatus=1) & Q(Proyecto__id=proyecto_id)) # Estatus=1 -> HU Capturada solo seran llamadas las de estatus "Capturada"

    #refinadas = HistoriaUsuario.objects.filter(Estatus=3) 

    #HU Refinadas que ya están en un mensaje de la reunión de Refinamiento del Product Backlog
    refinadas = HistoriaUsuario.objects.filter(Q(Estatus=3) & Q(MensajeRPBL = id_Mensaje))  # Estatus=3 -> HU Refinada
    data = {
        'form': historias,
        'form2': refinadas,
        'id_Mensaje':id_Mensaje,
    }

    return render(request, 'Mensajes/ProductOwner/listaHistoriasUsuariosBL.html', data)

# Opcion 1
def historiasRefinada(request, id, id_Mensaje):
    ref = EstatusHistoria.objects.get(pk=3) # HU Refinadas
    HU = get_object_or_404(HistoriaUsuario, pk=id)
    HU.Estatus = ref
    #HU.MensajeRPBL = int(id_Mensaje) --> Así marca error
    mensaje = get_object_or_404(Mensaje, pk=id_Mensaje)

    HU.MensajeRPBL = mensaje  # Asignar la instancia del objeto Mensaje
    HU.save()
    
    # return render(request, 'Mensajes/ProductOwner/listaHistoriasUsuariosBL.html')
    return redirect(to="Mensajes:listaHistoriasBL", id_Mensaje=id_Mensaje)

def cancelarHistoria(request, id, id_Mensaje):
    ref = EstatusHistoria.objects.get(pk=2) # 2--> HU Cancelada
    producto = get_object_or_404(HistoriaUsuario, pk=id)
    producto.Estatus = ref
    producto.MensajeRPBL = None
    producto.save()
    
    # return render(request, 'Mensajes/ProductOwner/listaHistoriasUsuariosBL.html')
    return redirect(to="Mensajes:listaHistoriasBL", id_Mensaje=id_Mensaje)

# Cancelara la historia si el usuario cambia de opinion
def cancelarHistoriaBL(request, id, id_Mensaje):
    ref = EstatusHistoria.objects.get(pk=1) #Queda con status = Capturada
    producto = get_object_or_404(HistoriaUsuario, pk=id)
    producto.Estatus = ref
    producto.MensajeRPBL = None
    producto.save()
    
    # return render(request, 'Mensajes/ProductOwner/listaHistoriasUsuariosBL.html')
    return redirect(to="Mensajes:listaHistoriasBL", id_Mensaje=id_Mensaje)


class ActualizarHistoriaUsuarioBL(LoginRequiredMixin, UpdateView):
    model = HistoriaUsuario
    template_name = 'Mensajes/ProductOwner/editarHistoriaBL.html'
    form_class = EditarHistoriaUsuarioBL_Forms
    success_url = reverse_lazy('Mensajes:listaRefinamiento')

# Reunion de planeacion del Sprint
def listaHistoriaUsuariosPlaneacionSprint(request, id): # id del Sprint
    historias = HistoriaUsuario.objects.filter(Q(Estatus=3) & Q(Sprint=id)) # solo seran llamadas las de estatus "Refinadas"
    #sprint = HistoriaUsuario.objects.filter(Q(Estatus=4) & Q(Sprint=id)) # solo seran llamadas las de estatus "En Sprint"
    sprintBl = sprint_Backlog.objects.filter(Sprint=id)
    data = {
        'form': historias,
        #'form2':sprint,
        'sprintbl':sprintBl,
    }

    return render(request, 'Mensajes/ProductOwner/listaHistoriasUsuarioPlaneacionSprint.html', data)

# Agregar historias
def historiasEnSprint(request, id): #id de la HU
    ref = EstatusHistoria.objects.get(pk=4) #HU en Sprint
    producto = get_object_or_404(HistoriaUsuario, pk=id)
    producto.Estatus = ref
    producto.save()

    # Estos datos se extraen de la historia de usuario seleccionada y posteriormente se guardan en el modelo sprint_Backlog
    sprint = producto.Sprint
    # print(f"sprint: {sprint} proyecto: {producto.Sprint.Proyecto}")
    proyecto = producto.Sprint.Proyecto
    historia = producto.id
    id_historia = HistoriaUsuario.objects.get(pk=historia)

    sprintBacklog = sprint_Backlog(Proyecto=proyecto, Sprint=sprint, historiaUsuario=id_historia)
    sprintBacklog.save()
    
    return redirect(to="Mensajes:listaHistoriasPlaneacionSprint", id=sprint.id)

# Esta funcion cambia el estatus de la historia de usuario seleccionada a "Cancelada"
def cancelarHistoria2(request, id):
    ref = EstatusHistoria.objects.get(pk=2) # Estatus cancelada
    producto = get_object_or_404(HistoriaUsuario, pk=id)
    producto.Estatus = ref
    producto.save()
    
    return redirect(to="Mensajes:listaHistoriasPlaneacionSprint", id=producto.sprint.id)

# Cancelara SOLO la historia si el usuario cambia de opinion
#def cancelarHistoriaPS(request, id):
#    ref = EstatusHistoria.objects.get(pk=1)
#    producto = get_object_or_404(HistoriaUsuario, pk=id)
#    producto.Estatus = ref
#    producto.save()

    #sprintBacklog = get_object_or_404(sprint_Backlog, pk=id)
    #sprintBacklog.delete()

#    return redirect(to="Mensajes:listaHistoriasPlaneacionSprint")

# Esta funcion regresa al estatus "Capturada" de la historia de usuario y borra el spring_Backlog seleccionado
def cancelarHistoriaPS(request, id):
    producto = get_object_or_404(sprint_Backlog, pk=id)
    producto.delete()

    id_historia = producto.historiaUsuario.id # id de la historia de usuario proveniente del modelo sprint_Backlog
    ref = EstatusHistoria.objects.get(pk=1) # Estatus "Capturada"
    historia = get_object_or_404(HistoriaUsuario, pk=id_historia)
    historia.Estatus = ref
    #historia.MensajeRPBL = None
    historia.save()

    return redirect(to="Mensajes:listaHistoriasPlaneacionSprint", id=historia.Sprint.id)

class ActualizarHistoriaUsuarioPlaneacionSprint(LoginRequiredMixin, UpdateView):
    model = HistoriaUsuario
    template_name = 'Mensajes/ProductOwner/editarHistoriaPlaneacionSprint.html'
    form_class = EditarHistoriaUsuarioBL_Forms
    def get_success_url(self):
        # Obtener el Sprint relacionado con la HistoriaUsuario
        sprint_id = self.get_object().Sprint.pk
        return reverse_lazy('Mensajes:listaHistoriasPlaneacionSprint', kwargs={'id': sprint_id})
    
#  Historias de usuario divididas
def listaHUdivididas(request,id): #id del Sprint
    # Obtener el Empleado relacionado con el usuario actual
    empleado = request.user.usuarioempleado

    # Obtener los proyectos en los que el empleado participa
    proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)

    dato = HistoriaUsuario.objects.filter(Q(Estatus=5) & Q(Sprint=id) & Q(Proyecto__in=proyectos)) # solo seran llamadas las de estatus 5="Dividida en Tareas"

    data = {
        'form': dato,
        'id_sprint': id
    }

    return render(request, 'Mensajes/ProductOwner/huDivididas.html', data)

# lista de tareas divididas para historia de usuario
def listaTareasHU(request, id):
    # Obtener el mensaje específico por su ID
    mensaje = Mensaje.objects.get(pk=id)

    # Obtener todos los AsistentesEventosScrum asociados a este mensaje
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)

    clave = id

    dato = HistoriaUsuario.objects.filter(Estatus=5) # solo seran llamadas las de estatus "Dividida en Tareas"

    # hu = HistoriaUsuario.objects.filter(pk=id)
    hu = HistoriaUsuario.objects.get(pk=id)
    # tareaAsig = tareaAsignada.objects.filter(HistoriaUsuario=hu)

    data = {
        'form': dato,
        #'tarea':tareaAsig
    }

    return render(request, 'Mensajes/ProductOwner/huDivididas.html', data)

# ----------------------------------- Plantilla Refinamiento BL ----------------------------
def vistaRefinamiento(request, id):
    mensaje = Mensaje.objects.get(pk=id)

    # Obtener todos los AsistentesEventosScrum asociados a este mensaje
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)

    datos2 = HistoriaUsuario.objects.filter(Q(Estatus__in=[3,4,5,6,7,8]) & Q(MensajeRPBL=id)) # 3=Refinadas
    #print(f"HU {datos2[0].HorasEstimadas}")
    datos3 = Mensaje.objects.filter(pk=id)
    data = {
        'form': asistentes,
        'form2': datos2,
        'form3': datos3
    }

    return render(request, 'Mensajes/ProductOwner/plantillaRefinamiento.html', data)

# Renderizar refinamientoBL a PDF
def plantillaRefinamiento(request, id): #id del Mensaje original
    # datos = AsistentesEventosScrum.objects.all()
    #historiasBL = HistoriaUsuario.objects.filter(Q(Estatus=3) & Q(MensajeRPBL=id)) # 3=Refinadas
    historiasBL = HistoriaUsuario.objects.filter( Q(MensajeRPBL=id))
    # datos3 = Mensaje.objects.filter(Emisor=request.user)
    datos4 = Mensaje.objects.filter(pk=id)

    mensaje = Mensaje.objects.get(pk=id)

    # Obtener todos los AsistentesEventosScrum asociados a este mensaje
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)

    data = {
        'form': asistentes,
        'form2': historiasBL,
        'form3': datos4
    }

    pdf = render_to_pdf('Mensajes/ProductOwner/plantillaRefinamiento.html', data)
    return HttpResponse(pdf, content_type='application/pdf')

# Plantilla para el mensaje de retroalimentacion del product backlok
def plantillaRetroAlimentacionBL(request,id): # id del mensaje de Retroalimentación
    # dato = MensajeRetroA.objects.filter(Receptor=request.user)
    dato = MensajeRetroA.objects.filter(pk=id)
    data = {
        'form': dato,
    }

    pdf = render_to_pdf('Mensajes/ProductOwner/plantillaRetroRefinamiento.html', data)
    return HttpResponse(pdf, content_type='application/pdf')

# ----------------------------------- Plantilla Planeacion Sprint ----------------------------
def vistaPlaneacionSprint(request, id):
    #idPlaneacion = m_PlanificacionSprint.objects.get(pk=id)
    # planeacion = m_PlanificacionSprint.objects.filter(pk=id)

    planeacion = Mensaje.objects.filter(pk=id)
    historias = HistoriaUsuario.objects.filter(Estatus=4)
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)
    comentarios = m_Comentarios.objects.filter(Mensaje=mensaje)

    usuario = request.user
    idiomaPais = Empleado.objects.filter(Usuario=usuario)

    # Suma los valores de los objetos
    total_horas = sum(item.HorasEstimadas for item in historias)
    total_dias = total_horas / 24

    # porcentaje = (total_horas * total_dias) / 100
    porcentaje = (total_horas + total_dias) / 2

    data = {
        'form': planeacion,
        'form2': historias,
        'form3': asistentes,
        'idiomaPais':idiomaPais,
        'horas':total_horas,
        'dias':total_dias,
        'porcentaje':porcentaje,
        'comentarios':comentarios
    }

    return render(request, 'Mensajes/ProductOwner/plantillaPlaneacionSprint.html', data)

# Renderizar planeacion del sprint a PDF
def plantillaPlaneacionSprint(request, id): #id del Mensaje
    #idPlaneacion = m_PlanificacionSprint.objects.get(pk=id)
    # planeacion = m_PlanificacionSprint.objects.filter(pk=id)

    # Obtener el Empleado relacionado con el usuario actual
    empleado = request.user.usuarioempleado

    # Obtener los proyectos en los que el empleado participa
    proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)


    planeacion = Mensaje.objects.filter(pk=id)
    sprint =  Mensaje.objects.get(pk=id).Sprint
    objetivo_sprint = sprint.objetivosprint
    #historias = HistoriaUsuario.objects.filter(Q(Proyecto__in=proyectos) & Q(Estatus__in=[4, 5, 6, 7, 8]) & Q(Sprint=sprint)) # 4= HU en Sprint 5=HU Divididas
    historias = HistoriaUsuario.objects.filter(Q(Proyecto__in=proyectos)  & Q(Sprint=sprint)) 
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)
    comentarios = m_Comentarios.objects.filter(Mensaje=mensaje)

    usuario = request.user
    ObjEmp = Empleado.objects.filter(Usuario=usuario)

    # Suma los valores de los objetos
    total_horas = sum(item.HorasEstimadas for item in historias)
    total_dias = total_horas / 8

    data = {
        'form': planeacion,
        'form2': historias,
        'form3': asistentes,
        'ObjEmp':ObjEmp,
        'horas':total_horas,
        'dias':total_dias,
        'comentarios':comentarios,
        'objetivo_sprint': objetivo_sprint,
    }

    # return render(request, 'Mensajes/ProductOwner/plantillaPlaneacionSprint.html', data)
    pdf = render_to_pdf('Mensajes/ProductOwner/plantillaPlaneacionSprint.html', data)
    return HttpResponse(pdf, content_type='application/pdf')

# Plantilla para el mensaje de retroalimentacion del la planeacion del sprint
def plantillaRetroAlimentacionPS(request,id): # id del Mensaje de Retroalimentación
    # dato = MensajeRetroA.objects.filter(Receptor=request.user)
    dato = MensajeRetroA.objects.filter(pk=id)
    data = {
        'form': dato,
    }

    pdf = render_to_pdf('Mensajes/ProductOwner/plantillaRetroPlaneacion.html', data)
    return HttpResponse(pdf, content_type='application/pdf')


# --------------------------------- Mensajes recibidos y Retroalimentacion, EMPLEADO Y SCRUM MASTER, refinamiento ------------------------------------------
#Scrum Master
def mensajes_recibidosScrumMaster(request):
    #def mensajes_recibidosScrumMaster(request,id):
    #empleado = Empleado.objects.get(Usuario=id)

    # mensajes = Mensaje.objects.filter(Destinatario=request.user)
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    # mensajes = Mensaje.objects.filter(Destinatario=empleado)
    # (Receptor=empleado)
    recibidos = MensajeReceptor.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="2"))

    data = {
        'form2':recibidos
    }
    return render(request, 'Mensajes/ScrumMaster/refinamientoScrum.html', data)

def mensajes_recibidosScrumMaster22(request,id):
    # mensajes = Mensaje.objects.filter(Destinatario=request.user)
    empleado = Empleado.objects.get(Usuario=id)
    # mensajes = Mensaje.objects.filter(Destinatario=empleado)
    recibidos = MensajeReceptor.objects.filter(Receptor=empleado)

    # mensajes = Mensaje.objects.all()
    return render(request, 'Mensajes/ScrumMaster/refinamientoScrum.html', {'form2':recibidos})

# Scrum Master
def mensajes_recibidosRetroScrumMaster(request, id):
    # mensajes = Mensaje.objects.filter(Destinatario=request.user)
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    # mensajes = Mensaje.objects.filter(Destinatario=empleado)
    recibidos = MensajeReceptor.objects.filter(Receptor=empleado)

    usuario = request.user

    #retroalimentacion = MensajeRetroA.objects.filter(Receptor=usuario)
    # (Receptor=empleado)
    mensaje = Mensaje.objects.get(pk=id)
    retroalimentacion = MensajeRetroA.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="2") & Q(Mensaje=mensaje))
    msmEnviado = MensajeRetroA.objects.filter(Q(Emisor=empleado) & Q(Contestacion__isnull=True))

    data = {
        'mensajes':retroalimentacion,
        'enviado':msmEnviado
    }

    # mensajes = Mensaje.objects.all()
    return render(request, 'Mensajes/ScrumMaster/retroAlimentacionBL.html', data)

#Scrum Master
def lista_reunion_diariaScrumMaster(request):
    # mensajes = Mensaje.objects.filter(Destinatario=request.user)
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensajes = Mensaje.objects.filter(Destinatario=empleado)
    recibidos = MensajeReceptor.objects.filter(Receptor=empleado)

    return render(request, 'Mensajes/ScrumMaster/reunionDiaria.html', {'form': mensajes, 'form2':recibidos})

# Mensaje retroalimentacion Scrum Master, en caso de seleccionar "No Comprendido"
def enviar_mensajeRetroScrumMaster(request, id):
    # emisor = User.objects.get(id=id)
    em = request.user.id
    emisor = request.user

    # mensajes = Mensaje.objects.filter(pk=id) # usar este metodo en caso de que sea proveniente del modelo "Mensaje"
    mensajes = MensajeReceptor.objects.filter(pk=id)
    if request.method == 'POST':
        form = retroAlimentacion_Forms(request.POST)
        if form.is_valid():

            # usar este metodo en caso de que sea proveniente del modelo "Mensaje"
            #for mensaje in mensajes:
            #    # Crear un MensajeRetroA con los datos del mensaje
            #    dato = MensajeRetroA(
            #        Proyecto=mensaje.Proyecto,
            #        EventoScrum=mensaje.EventoScrum, 
            #        Mensaje=mensaje, # hereda por defecto el id del mensaje
            #        Receptor=mensaje.Emisor, # hereda el emisar del mensaje, NO el del request.user
            #        Emisor=mensaje.Destinatario
            #
            #    )

            # usar este metodo en caso de que sea proveniente del modelo "MensajeReceptor"
            for mensaje in mensajes:
                # Crear un MensajeRetroA con los datos del mensaje
                dato = MensajeRetroA(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum, 
                    Mensaje=mensaje.Mensaje, # hereda por defecto el id del mensaje
                    Receptor=mensaje.Emisor, # hereda el emisar del mensaje, NO el del request.user
                    Emisor=mensaje.Receptor
            
                )
            
            emisorid = dato.Emisor

            proyecto = dato.Proyecto
            eventoScrum = dato.EventoScrum
            mensajeid = dato.Mensaje
            receptorid = dato.Receptor
            descripcion = form.cleaned_data['Descripcion']
            # contenido = form.cleaned_data['Contestacion']
            # status = form.cleaned_data['Status']

            # usar este metodo en caso de que sea proveniente del modelo "Mensaje"
            mensaje = MensajeRetroA(Proyecto=proyecto, EventoScrum=eventoScrum, Mensaje=mensajeid, Receptor=receptorid,
                                   Descripcion=descripcion, Status=5, Emisor=emisorid)
            # Contestacion=contenido, Status=status,
            
            # mensaje = MensajeRetroA(Proyecto=proyecto, Mensaje=mensajeid, Receptor=receptorid,
            #                        Descripcion=descripcion, Contestacion=contenido, Status=status, Emisor=emisor)

            mensaje.save()
            return redirect(to='Mensajes:recibirMensajeScrumMaster')  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacion_Forms()
    return render(request, 'Mensajes/ScrumMaster/retroAlimentacion.html', {'form': form})

# Mensaje de retroalimentacion Scrum Master en caso de seleccionar "Comprendido", correcto
def actualizarRetroStatusCorrectoScrumMaster(request, id):
    em = request.user.id
    status = "2"
    producto = get_object_or_404(MensajeReceptor, pk=id)
    producto.Status = status
    producto.save()
    
    # return render(request, 'Mensajes/ProductOwner/listaHistoriasUsuariosBL.html')
    return redirect(to='Mensajes:recibirMensajeScrumMaster')

# Mensaje de retroalimentacion BL Scrum Master en caso de seleccionar "Comprendido"
def actualizarRetroBLStatusCorrectoScrumMaster(request, id):
    status = "3"
    producto = get_object_or_404(MensajeRetroA, pk=id)
    producto.Status = status
    producto.save()

    msm = producto.Mensaje.id
    
    # return render(request, 'Mensajes/ProductOwner/listaHistoriasUsuariosBL.html')
    return redirect('Mensajes:retroAliScrumMasterBL',msm)

# Listar asistentes por usuario y mensaje, Refinamiento, Scrum Master
def lista_asistentes_por_usuarioRef_SM(request, id):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Q(Usuario=empleado) & Q(EventoScrum="2") & Q(Mensaje=mensaje)) 

    data = {
        'form':asistentes
    }

    return render(request, 'Mensajes/ScrumMaster/listaAsistentesRef.html', data)

# Scrum Master
class ActualizarAsistenteScrumMasterRef(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Mensajes/ScrumMaster/editarAsistentePS.html'
    form_class = AsistentesPlaneacion_Forms
    success_url = reverse_lazy('Mensajes:recibirMensajeScrumMaster')

# Empleado
def mensajes_recibidosEmpleado(request):
    # mensajes = Mensaje.objects.filter(Destinatario=request.user)
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
 
    # Obtener los proyectos en los que el empleado participa
    proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)


    # mensajes = Mensaje.objects.filter(Destinatario=empleado)
    # recibidos = MensajeReceptor.objects.filter(Receptor=empleado)
    #recibidos = MensajeReceptor.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="2") & Q(Proyecto__in=proyectos))
    recibidos = MensajeReceptor.objects.filter(
        Q(Receptor=empleado) & 
        Q(EventoScrum="2") & 
        Q(Proyecto__in=proyectos)
    ).annotate(
        mensaje_fecha_hora=F('Mensaje__FechaHora')  # Relación con el modelo Mensaje
    )

    data = {
        'form2':recibidos
    }

    return render(request, 'Scrum/Empleado/refinamientoScrum.html', data)

# Empleado
def mensajes_recibidosRetroEmpleado(request, id): # id del Mensaje
    # mensajes = Mensaje.objects.filter(Destinatario=request.user)
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    # mensajes = Mensaje.objects.filter(Destinatario=empleado)
    recibidos = MensajeReceptor.objects.filter(Receptor=empleado)

    usuario = request.user

    #retroalimentacion = MensajeRetroA.objects.filter(Receptor=usuario)
    # (Receptor=empleado)
    mensaje = Mensaje.objects.get(pk=id)
    retroalimentacion = MensajeRetroA.objects.filter(Q(Emisor=empleado) & Q(EventoScrum="2") & Q(Mensaje=mensaje))
    msmEnviado = MensajeRetroA.objects.filter(Q(Emisor=empleado) & Q(Contestacion__isnull=True))
    # msmEnviado = MensajeRetroA.objects.filter(Emisor=empleado ,Contestacion__isnull=True) tambien funciona :V
    data = {
        'mensajes':retroalimentacion,
        'enviado':msmEnviado
    }

    # mensajes = Mensaje.objects.all()
    return render(request, 'Scrum/Empleado/retroAlimentacionBL.html', data)

# Empleado, aun no se debe usar
def lista_reunion_diariaEmpleado(request):
    # mensajes = Mensaje.objects.filter(Destinatario=request.user)
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensajes = Mensaje.objects.filter(Destinatario=empleado)
    recibidos = MensajeReceptor.objects.filter(Receptor=empleado)

    return render(request, 'Scrum/Empleado/reunionDiaria.html', {'form': mensajes, 'form2':recibidos})

# Empleado
def enviar_mensajeRetroEmpleado(request, id): #id del Mensaje Receptor
    # emisor = User.objects.get(id=id)
    em = request.user.id
    emisor = request.user

    # mensajes = Mensaje.objects.filter(pk=id) # usar este metodo en caso de que sea proveniente del modelo "Mensaje"
    mensajes = MensajeReceptor.objects.filter(pk=id)
    if request.method == 'POST':
        form = retroAlimentacion_Forms(request.POST)
        if form.is_valid():

            # usar este metodo en caso de que sea proveniente del modelo "Mensaje"
            # for mensaje in mensajes:
                # Crear un MensajeRetroA con los datos del mensaje
            #    dato = MensajeRetroA(
            #        Proyecto=mensaje.Proyecto,
            #        EventoScrum=mensaje.EventoScrum, 
            #        Mensaje=mensaje, # hereda por defecto el id del mensaje
            #        Receptor=mensaje.Emisor, # hereda el emisar del mensaje, NO el del request.user
            #        Emisor=mensaje.Destinatario
            #
            #    )

            # usar este metodo en caso de que sea proveniente del modelo "MensajeReceptor"
            for mensaje in mensajes:
                # Crear un MensajeRetroA con los datos del mensaje
                dato = MensajeRetroA(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum, 
                    Mensaje=mensaje.Mensaje, # hereda por defecto el id del mensaje
                    Receptor=mensaje.Emisor, # hereda el emisar del mensaje, NO el del request.user
                    Emisor=mensaje.Receptor
            
                )
            
            emisorid = dato.Emisor

            proyecto = dato.Proyecto
            eventoScrum = dato.EventoScrum
            mensajeid = dato.Mensaje
            receptorid = dato.Receptor
            descripcion = form.cleaned_data['Descripcion']
            # contenido = form.cleaned_data['Contestacion']
            # status = form.cleaned_data['Status']

            # usar este metodo en caso de que sea proveniente del modelo "Mensaje"
            mensaje = MensajeRetroA(Proyecto=proyecto, EventoScrum=eventoScrum, Mensaje=mensajeid, Receptor=receptorid,
                                   Descripcion=descripcion, Status=5, Emisor=emisorid)
            # Contestacion=contenido, Status=status
            
            # mensaje = MensajeRetroA(Proyecto=proyecto, Mensaje=mensajeid, Receptor=receptorid,
            #                        Descripcion=descripcion, Contestacion=contenido, Status=status, Emisor=emisor)

            mensaje.save()
            return redirect(to='Mensajes:recibirMensajeEmpleado')  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacion_Forms()
    return render(request, 'Scrum/Empleado/retroAlimentacionRefEmpleado.html', {'form': form})



# Mensaje de retroalimentacion Empleado en caso de seleccionar "Comprendido", correcto
def actualizarRetroStatusCorrectoEmpleado(request, id): #id del Mensaje Receptor
    em = request.user.id
    status = "2" # 2 = Mensaje Comprendido
    producto = get_object_or_404(MensajeReceptor, pk=id)
    producto.Status = status
    producto.save()
    
    # return render(request, 'Mensajes/ProductOwner/listaHistoriasUsuariosBL.html')
    return redirect(to='Mensajes:recibirMensajeEmpleado')

# Mensaje de retroalimentacion BL Empleado en caso de seleccionar "Comprendido"
def actualizarRetroBLStatusCorrectoEmpleado(request, id): # id del Mensaje de retroalimentación
    status = "3"  # 3 = "Aclarado y/o Comprendido"
    producto = get_object_or_404(MensajeRetroA, pk=id)
    producto.Status = status
    producto.save()

    msm = producto.Mensaje.id
    
    # return render(request, 'Mensajes/ProductOwner/listaHistoriasUsuariosBL.html')
    return redirect('Mensajes:retroAliEmpleadoBL', msm)

# Listar asistentes por usuario y mensaje, Refinamiento, Scrum Master
def lista_asistentes_por_usuarioRef_Empleado(request, id): #id del Mensaje
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Q(Usuario=empleado) & Q(EventoScrum="2") & Q(Mensaje=mensaje)) 

    data = {
        'form':asistentes
    }

    return render(request, 'Scrum/Empleado/listaAsistentesRef.html', data)

# Scrum Master
class ActualizarAsistenteEmpleadoRef(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Scrum/Empleado/editarAsistentePS.html'
    form_class = AsistentesPlaneacion_Forms
    success_url = reverse_lazy('Mensajes:recibirMensajeEmpleado')

# ---------------------------- Mensajes recibidos y Retroalimentacion, Product Owner, refinamiento ---------------------------------
def mensajes_RetroAlimentacion(request, id):
    if request.user.is_authenticated:
        usuario = request.user
        empleado = Empleado.objects.get(Usuario=usuario)
        #print(f"usuario: {usuario}, empleado: {empleado}, id_mensaje: {id}")
        retroalimentacion = MensajeRetroA.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="2")& Q(Mensaje=id)) 

        user = request.user

        if user is not None:
            login(request, user)
            # Redirecciona al usuario dependiendo de su rol
            if user.usuarioempleado.Roles.NombreRol == 'Product Owner':
                return render(request, 'Mensajes/ProductOwner/retroAlimentacion.html', {'mensajes':retroalimentacion})
            else:
                # si el usuario no es Scrum Master se mostrara el siguiente mensaje
                return HttpResponse("No eres Product Owner")
        else:
        # Usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    else: 
        return HttpResponseRedirect(reverse('Scrum:Logout'))

def vistaRetroAlimentacionBL(request,id):
    # dato = MensajeRetroA.objects.filter(Receptor=request.user)
    dato = MensajeRetroA.objects.filter(pk=id)
    data = {
        'form': dato,
    }

    return render(request, 'Mensajes/ProductOwner/plantillaRetroRefinamiento.html', data)

def enviar_mensajeBL(request, id):
    # emisor = User.objects.get(id=id)
    retroalimentacion = MensajeRetroA.objects.filter(pk=id) # hera el id del mensaje recibido con los datos
    # print(f"Mensaje Retro: {retroalimentacion} Id: {id} ")
    # print(f"Mensaje Original: {retroalimentacion.first().Mensaje.id} ")
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    # mensajes = Mensaje.objects.filter(pk=id) # usar este metodo en caso de que sea proveniente del modelo "Mensaje"
    # mensajes = MensajeReceptor.objects.filter(pk=id)
    # retroali = MensajeRetroA.objects.filter(Emisor=id)

    if request.method == 'POST':
        form = retroAlimentacionBL_Forms(request.POST)
        if form.is_valid():

            for retro in retroalimentacion:
                Descripcion=retro.Descripcion
                Proyecto=retro.Proyecto,
                EventoScrum=retro.EventoScrum, 
                Mensaje=retro.Mensaje, # hereda por defecto el id del mensaje
                Receptor=retro.Emisor, # hereda el emisar del mensaje, NO el del request.user
                Emisor=retro.Receptor
                Status=retro.Status

            proyecto = retro.Proyecto
            eventoScrum = retro.EventoScrum
            mensajeid = retro.Mensaje
            #receptorid = retro.Receptor
            #emisorRetro = retro.Emisor
            descripcion = retro.Descripcion
            contenido = form.cleaned_data['Contestacion']
            # status = form.cleaned_data['Status']
            status = retro.Status

            # MensajeReceptor - MensajeRetroA
            # for mensaje in mensajes:
            #    # Crear un MensajeRetroA con los datos de MensajeReceptor
            #    dato = MensajeRetroA(
            #        Proyecto=mensaje.Proyecto,
            #        Mensaje=mensaje.Mensaje, # hereda por defecto el id del mensaje
            #        Receptor=mensaje.Receptor # hereda el emisar del mensaje, NO el del request.user
            #    
            #    )
            
            emisorid = retro.Emisor

            
            
            idreceptor = retro.Emisor
            idreceptore = retro.Emisor.Usuario.id
            #receptorUser = User.objects.get(pk=retroali)
            #recp = User.objects.filter(Receptor=receptorUser)

            #proyecto = dato.Proyecto
            #eventoScrum = dato.EventoScrum
            #mensajeid = dato.Mensaje
            #receptorid = dato.Receptor
            #descripcion = form.cleaned_data['Descripcion']
            # contenido = form.cleaned_data['Contestacion']
            # status = form.cleaned_data['Status']

            # usar este metodo en caso de que sea proveniente del modelo "Mensaje"
            mensaje = MensajeRetroA(Proyecto=proyecto, EventoScrum=eventoScrum, Mensaje=mensajeid, Receptor=idreceptor,
                                   Descripcion=descripcion, Contestacion=contenido, Status=status, Emisor=empleado)
            # Contestacion=contenido, Status=status, Receptor=receptorid, Emisor=emisorid
            
            # mensaje = MensajeRetroA(Proyecto=proyecto, Mensaje=mensajeid, Receptor=receptorid,
            #                        Descripcion=descripcion, Contestacion=contenido, Status=status, Emisor=emisor)
            MensajeRetroA.objects.filter(id=id).update(Contestacion=contenido)
            #mensaje.save()
            return redirect('Mensajes:retroAProductOwner', id=retroalimentacion.first().Mensaje.id)  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacionBL_Forms()
    return render(request, 'Mensajes/ProductOwner/retroContestacionBL.html', {'form': form})

# --------------------------------- CRUD PDF --------------------------------------------------
def descargar_archivo(request, id):
    # instancia = get_object_or_404(m_Archivos, pk=id)
    # # Aquí se asume que el campo 'archivo' en el modelo es un FileField o similar
    # with instancia.Archivo.open() as f:
    #     response = HttpResponse(f.read(), content_type='application/pdf')  # Cambia el content_type según el tipo de archivo
    # response['Content-Disposition'] = 'attachment; filename="archivo.pdf"'  # Cambia el nombre del archivo según sea necesario

    # Obtiene la instancia del archivo
    instancia = get_object_or_404(m_Archivos, pk=id)
    
    # Convierte los datos binarios en un flujo de BytesIO
    archivo_binario = BytesIO(instancia.ArchivoObj)
    archivo_binario.seek(0)  # Asegura que la lectura comience desde el inicio

    # Crea la respuesta HTTP para la descarga
    response = HttpResponse(archivo_binario.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{instancia.Archivo.name.split("/")[-1]}"'
    
    return response

def cargar_documento_OLD(request):
    #print("Guardar documento: cargar_documento")
    if request.method == 'POST':
        form = Archivos_forms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # return redirect('Mensajes:listaRefinamiento')
            return redirect('Scrum:index')
    else:
        form = Archivos_forms()
    return render(request, 'Mensajes/ProductOwner/guardarArchivo.html', {'form': form})

def cargar_documento(request, evento_scrum): 
    if request.method == 'POST':
        form = Archivos_forms(request.POST, request.FILES, evento_scrum=evento_scrum, user=request.user)
        #form = Archivos_forms(request.POST, request.FILES)
        if form.is_valid():
            archivo_pdf = request.FILES['Archivo']  # Aquí obtenemos el archivo PDF subido
            
            # Leer el contenido del archivo como binario
            archivo_binario = archivo_pdf.read()
            
            # Guardar tanto el archivo físico como el binario
            nuevo_archivo = form.save(commit=False)  # No guardamos aún, ya que modificaremos `ArchivoObj`
            nuevo_archivo.ArchivoObj = archivo_binario  # Guardamos el archivo en el campo `BinaryField`
            nuevo_archivo.save()  # Ahora guardamos el objeto con el campo binario

            return redirect('Scrum:index')  # Cambia esto a donde quieras redirigir
    else:
        form = Archivos_forms(evento_scrum=evento_scrum, user=request.user)
        #form = Archivos_forms()
    return render(request, 'Mensajes/ProductOwner/guardarArchivo.html', {'form': form})

def cargar_documentoConID(request, id):
    mensajes = Mensaje.objects.filter(pk=id)
    #print("Guardar documento: cargar_documentoConID")
    if request.method == 'POST':
        form = ArchivosID_forms(request.POST, request.FILES)
        if form.is_valid():
        
            for mensaje in mensajes:
                # Crear un AsistentesEventosScrum con los datos del mensaje
                asistente = m_Archivos(
                    Proyecto=mensaje.Proyecto,
                    Mensaje=mensaje,
                )
                
            descripcion = form.cleaned_data['Descripcion']
            archivo = request.FILES['Archivo']
            proyecto = asistente.Proyecto
            mensajeid = asistente.Mensaje

            save = m_Archivos(Descripcion=descripcion, Archivo=archivo, Mensaje=mensajeid ,Proyecto=proyecto)
            save.save()
            # form.save()
            return redirect('Mensajes:listaRefinamiento')
    else:
        form = ArchivosID_forms()
    return render(request, 'Mensajes/ProductOwner/guardarArchivo.html', {'form': form})

def cargar_documentoConIDPS(request, id):
    mensajes = Mensaje.objects.filter(pk=id)

    if request.method == 'POST':
        form = ArchivosID_forms(request.POST, request.FILES)
        if form.is_valid():
        
            for mensaje in mensajes:
                # Crear un AsistentesEventosScrum con los datos del mensaje
                asistente = m_Archivos(
                    Proyecto=mensaje.Proyecto,
                    Mensaje=mensaje,
                )
                
            descripcion = form.cleaned_data['Descripcion']
            archivo = request.FILES['Archivo']
            proyecto = asistente.Proyecto
            mensajeid = asistente.Mensaje

            save = m_Archivos(Descripcion=descripcion, Archivo=archivo, Mensaje=mensajeid ,Proyecto=proyecto)
            save.save()
            # form.save()
            return redirect('Mensajes:listaPlaneacionSprint')
    else:
        form = ArchivosID_forms()
    return render(request, 'Mensajes/ProductOwner/guardarArchivo.html', {'form': form})

def cargar_documentoConIDRS(request, id):
    mensajes = Mensaje.objects.filter(pk=id)

    if request.method == 'POST':
        form = ArchivosID_forms(request.POST, request.FILES)
        if form.is_valid():
        
            for mensaje in mensajes:
                # Crear un AsistentesEventosScrum con los datos del mensaje
                asistente = m_Archivos(
                    Proyecto=mensaje.Proyecto,
                    Mensaje=mensaje,
                )
                
            descripcion = form.cleaned_data['Descripcion']
            archivo = request.FILES['Archivo']
            proyecto = asistente.Proyecto
            mensajeid = asistente.Mensaje

            save = m_Archivos(Descripcion=descripcion, Archivo=archivo, Mensaje=mensajeid ,Proyecto=proyecto)
            save.save()
            # form.save()
            return redirect('Mensajes:listaRevisionSprint')
    else:
        form = ArchivosID_forms()
    return render(request, 'Mensajes/ProductOwner/guardarArchivo.html', {'form': form})

# Retrospectiva del Sprint
def cargar_documentoConIDRetroSprint(request, id):
    mensajes = Mensaje.objects.filter(pk=id)

    if request.method == 'POST':
        form = ArchivosID_forms(request.POST, request.FILES)
        if form.is_valid():
        
            for mensaje in mensajes:
                # Crear un AsistentesEventosScrum con los datos del mensaje
                asistente = m_Archivos(
                    Proyecto=mensaje.Proyecto,
                    Mensaje=mensaje,
                )
                
            descripcion = form.cleaned_data['Descripcion']
            archivo = request.FILES['Archivo']
            proyecto = asistente.Proyecto
            mensajeid = asistente.Mensaje

            save = m_Archivos(Descripcion=descripcion, Archivo=archivo, Mensaje=mensajeid ,Proyecto=proyecto)
            save.save()
            # form.save()
            return redirect('Mensajes:listaRetrospectivaSprint')
    else:
        form = ArchivosID_forms()
    return render(request, 'Mensajes/ProductOwner/guardarArchivo.html', {'form': form})

# Reunion Diaria
def cargar_documentoConIDReunionDiaria(request, id):
    mensajes = Mensaje.objects.filter(pk=id)

    if request.method == 'POST':
        form = ArchivosID_forms(request.POST, request.FILES)
        if form.is_valid():
        
            for mensaje in mensajes:
                # Crear un AsistentesEventosScrum con los datos del mensaje
                asistente = m_Archivos(
                    Proyecto=mensaje.Proyecto,
                    Mensaje=mensaje,
                )
                
            descripcion = form.cleaned_data['Descripcion']
            archivo = request.FILES['Archivo']
            proyecto = asistente.Proyecto
            mensajeid = asistente.Mensaje

            save = m_Archivos(Descripcion=descripcion, Archivo=archivo, Mensaje=mensajeid ,Proyecto=proyecto)
            save.save()
            # form.save()
            return redirect('Mensajes:listaReunionDiaria')
    else:
        form = ArchivosID_forms()
    return render(request, 'Mensajes/ProductOwner/guardarArchivo.html', {'form': form})



# -----------------------------------------------------------------------------------------------------------------------
# -------------------------------------- Reunion de planeacion del sprint, Product Owner -------------------------------
# Lista planeacion sprint, sin parametros
def listaPlaneacionSprint(request):
    if request.user.is_authenticated:
        # Obtener el Empleado relacionado con el usuario actual
        #empleado = request.user.usuarioempleado
        usuario = request.user
        empleado = Empleado.objects.get(Usuario=usuario)

        # Obtener los proyectos en los que el empleado participa
        proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)
        if usuario.usuarioempleado.Roles.NombreRol == 'Product Owner' :
            #mensajes = Mensaje.objects.filter(Q(Emisor=empleado) & Q(EventoScrum="3") & Q(Proyecto__in=proyectos)) # Reunión de Planeación del Sprint
            mensajes = Mensaje.objects.filter(Q(EventoScrum="3") & Q(Proyecto__in=proyectos)) # Reunión de Planeación del Sprint
        #asistentes = AsistentesEventosScrum.objects.all()
        #planeaciacionSprint = m_PlanificacionSprint.objects.all()

        data = {
        #'form': planeaciacionSprint,
        'form2':mensajes,
        #'form3':asistentes
        }

        user = request.user

        if user is not None:
            login(request, user)
            # Redirecciona al usuario dependiendo de su rol
            if user.usuarioempleado.Roles.NombreRol == 'Product Owner':
                # print(f"Usuario.id PO: {usuario }, empleado: {empleado}, user: {request.user}" )
                # print(f"Mensajes PO: {mensajes}")
                # print(f"asistentes PO: {asistentes}")
                return render(request, 'Mensajes/ProductOwner/listaPlaneacionSprint.html', data)
            else:
                # si el usuario no es Scrum Master se mostrara el siguiente mensaje
                return HttpResponse("No eres Product Owner")
        else:
        # Usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    else: 
        return HttpResponseRedirect(reverse('Scrum:Logout'))

# Muestra una lista de los sprints disponibles para heredar sus datos
def subListaPlaneacionSprint(request):
    # Obtener el Empleado relacionado con el usuario actual
    empleado = request.user.usuarioempleado

    # Obtener los proyectos en los que el empleado participa
    proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)

    # Filtrar los sprints de esos proyectos con el estatus 3, 4 o 5
    sprints = Sprint.objects.filter(
        Proyecto__in=proyectos,
        Estatus__pk__in=[1, 3] # 1= Creado, 3=En ejecución
    )
    #sprint = Sprint.objects.all()

    data = {
        'form': sprints
    }

    return render(request, 'Mensajes/ProductOwner/subListaSprint.html', data)

# Opcion 1, sin heredar datos de "Mensaje", obsoleto
def crear_PlaneacionSprint(request, id):
    emisor = User.objects.get(id=id)

    empleado = Empleado.objects.get(Usuario=id)
    mensajes = Mensaje.objects.filter(Destinatario=empleado)

    if request.method == 'POST':
        form = reunionPlaneacionSprint_Forms(request.POST)
        if form.is_valid():
            sprint = form.cleaned_data['Sprint']
            mensaje = form.cleaned_data['Mensaje']
            proyecto = form.cleaned_data['Proyecto']
            fechaHora = form.cleaned_data['FechaHora']
            # archivo = request.FILES['archivo']
            planeacion = m_PlanificacionSprint(FechaHora=fechaHora, Emisor=empleado, Proyecto=proyecto, Mensaje=mensaje, Sprint=sprint)
            planeacion.save()
            return redirect('Mensajes:listaPlaneacionSprint')  # Redirigir a la página de mensajes enviados
    else:
        form = reunionPlaneacionSprint_Forms()
    return render(request, 'Mensajes/ProductOwner/crearPlaneacionSprint.html', {'form': form, 'receptor': emisor})

# Opcion 2, heredando datos de "Mensaje"
def crear_PlaneacionSprint2(request, id):
    emisor = User.objects.get(id=id)

    mensajes = Mensaje.objects.filter(pk=id)

    if request.method == 'POST':
        form = reunionPlaneacionSprint_Forms(request.POST)
        if form.is_valid():

            for mensaje in mensajes:
                dato = m_PlanificacionSprint(
                    Mensaje=mensaje, # hereda por defecto el id del mensaje
                )

            sprint = form.cleaned_data['Sprint']
            mensajeid = dato.Mensaje
            proyecto = form.cleaned_data['Proyecto']
            fechaHora = form.cleaned_data['FechaHora']
            # archivo = request.FILES['archivo']
            planeacion = m_PlanificacionSprint(FechaHora=fechaHora, Emisor=emisor, Proyecto=proyecto, Mensaje=mensajeid, Sprint=sprint)
            planeacion.save()
            return redirect('Mensajes:listaPlaneacionSprint')  # Redirigir a la página de mensajes enviados
    else:
        form = reunionPlaneacionSprint_Forms()
    return render(request, 'Mensajes/ProductOwner/crearPlaneacionSprint.html', {'form': form, 'receptor': emisor})

# Opcion 5: funciona!!!
@transaction.atomic
def crear_PlaneacionSprint5(request):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    if request.method == 'POST':
        form = MensajePlaneacionForms(request.POST)
        if form.is_valid():

            # Obtener datos del formulario o de donde sea necesario
            descripcion = form.cleaned_data['Descripcion']
            fecha_hora = form.cleaned_data['FechaHora']
            sprint = form.cleaned_data['Sprint']
            proyecto = form.cleaned_data['Proyecto']
            ref = m_EventoScrum.objects.get(pk=3)

            # Crear instancia de Mensaje
            mensaje = Mensaje.objects.create(
                Descripcion=descripcion,
                FechaHora=fecha_hora,
                Emisor=empleado,
                Proyecto=proyecto,
                Sprint=sprint,
                EventoScrum=ref,
                # Asignar otras relaciones según sea necesario
            )

            # Crear instancia de m_PlanificacionSprint
            planificacion = m_PlanificacionSprint.objects.create(
                Emisor=empleado,
                FechaHora=fecha_hora,
                Mensaje=mensaje,
                Proyecto=proyecto,
                Sprint=sprint,
                # Asignar otras relaciones según sea necesario
            )

        # Redirigir a alguna página de éxito o hacer lo que necesites
        return redirect('Mensajes:listaPlaneacionSprint')
    else:
        form = MensajePlaneacionForms()
    return render(request, 'Mensajes/ProductOwner/crearPlaneacionSprint.html', {'form': form})

# Opcion 6, heredando datos del modelo Sprint
# @transaction.atomic
# def crear_PlaneacionSprint6(request, id):
#     usuario = request.user
#     empleado = Empleado.objects.get(Usuario=usuario)

#     # sprint = Sprint.objects.filter(pk=id)

#     if request.method == 'POST':
#         form = MensajePlaneacionSprintForms(request.POST)
#         if form.is_valid():

#             # Obtener datos del formulario o de donde sea necesario
#             fecha_hora = form.cleaned_data['FechaHora']
#             # Convertimos la fecha a formato día/mes/año hh:mm
#             FechaHoraFormateada = fecha_hora.strftime('%d/%m/%Y %H:%M')
#             ref = m_EventoScrum.objects.get(pk=3)

#             producto = get_object_or_404(Sprint, pk=id)
#             descripcion = f"{FechaHoraFormateada},  Planeación Sprint. {producto.objetivosprint}"
#             proyecto = producto.Proyecto
#             # sprint = producto.nombresprint

#             sp = Sprint.objects.get(pk=id)

#             # Crear instancia de Mensaje
#             mensaje = Mensaje.objects.create(
#                 Descripcion=descripcion,
#                 FechaHora=fecha_hora,
#                 Emisor=empleado,
#                 Proyecto=proyecto,
#                 Sprint=sp,
#                 EventoScrum=ref,
#                 # Asignar otras relaciones según sea necesario
#             )

#             # Crear instancia de m_PlanificacionSprint
#             planificacion = m_PlanificacionSprint.objects.create(
#                 Emisor=empleado,
#                 FechaHora=fecha_hora,
#                 Mensaje=mensaje,
#                 Proyecto=proyecto,
#                 Sprint=sp,
#                 # Asignar otras relaciones según sea necesario
#             )

#         # Redirigir a alguna página de éxito o hacer lo que necesites
#         return redirect('Mensajes:listaPlaneacionSprint')
#     else:
#         form = MensajePlaneacionSprintForms()
#     return render(request, 'Mensajes/ProductOwner/crearPlaneacionSprint.html', {'form': form})


@transaction.atomic
def crear_PlaneacionSprint6(request, id):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    if request.method == 'POST':
        form = MensajePlaneacionSprintForms(request.POST)
        if form.is_valid():
            fecha_hora = form.cleaned_data['FechaHora']
            FechaHoraFormateada = fecha_hora.strftime('%d/%m/%Y %H:%M')
            ref = m_EventoScrum.objects.get(pk=3)  # Planeación

            producto = get_object_or_404(Sprint, pk=id)
            descripcion = f"{FechaHoraFormateada},  Planeación Sprint. {producto.objetivosprint}"
            proyecto = producto.Proyecto
            sp = producto

            # Crear el mensaje (reunión)
            mensaje = Mensaje.objects.create(
                Descripcion=descripcion,
                FechaHora=fecha_hora,
                Emisor=empleado,
                Proyecto=proyecto,
                Sprint=sp,
                EventoScrum=ref,
            )

            # Crear la planificación como evento específico
            planificacion = m_PlanificacionSprint.objects.create(
                Emisor=empleado,
                FechaHora=fecha_hora,
                Mensaje=mensaje,
                Proyecto=proyecto,
                Sprint=sp,
            )

            # # ✅ Crear asistentes y receptores automáticamente
            # empleados_activos = EmpleadoProyecto.objects.filter(
            #     Proyecto=proyecto,
            #     Status="1"  # Activo
            # ).select_related("Empleado", "Empleado__Roles")

            # for ep in empleados_activos:
            #     emp = ep.Empleado

            #     # Asistente a la reunión
            #     AsistentesEventosScrum.objects.create(
            #         Proyecto=proyecto,
            #         EventoScrum=ref,
            #         Mensaje=mensaje,
            #         Usuario=emp,
            #         Rol=emp.Roles,
            #         Status="1",  # Obligatorio
            #         TipoAsistencia="S"  # Síncrona
            #     )

            #     # Receptor del mensaje
            #     MensajeReceptor.objects.create(
            #         Proyecto=proyecto,
            #         Mensaje=mensaje,
            #         Receptor=emp,
            #         EventoScrum=ref,
            #         Emisor=empleado,
            #         Sprint=sp,
            #     )
            registrar_asistentes_y_receptores(
                proyecto=proyecto,
                sprint=sp,
                mensaje=mensaje,
                evento=ref,
                emisor=empleado
            )

            return redirect('Mensajes:listaPlaneacionSprint')
    else:
        form = MensajePlaneacionSprintForms()

    return render(request, 'Mensajes/ProductOwner/crearPlaneacionSprint.html', {'form': form})

# Opcion 1
class ActualizarReunionPlaneacionSprint(LoginRequiredMixin, UpdateView):
    # model = m_PlanificacionSprint
    model = Mensaje
    template_name = 'Mensajes/ProductOwner/editarPlaneacionSprint.html'
    form_class = reunionPlaneacionSprint_Forms
    success_url = reverse_lazy('Mensajes:listaPlaneacionSprint')

# Opcion 2, actualizando dos modelos en una misma funcion
def actualizar_ReunionPlaneacion(request, id):
    # Obtener el usuario que se va a actualizar
    mensaje = Mensaje.objects.get(id=id)

    print(f"mensaje.FechaHora: {mensaje.FechaHora }, id: {id}")
    # Obtener el Empleado relacionado con el usuario actual
    empleado = request.user.usuarioempleado

    # Obtener los proyectos en los que el empleado participa
    list_proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)

    # Filtrar los sprints de esos proyectos con el estatus 3, 4 o 5
    sprints = Sprint.objects.filter(
        Proyecto__in=list_proyectos,
        Estatus__pk__in=[1, 3, 4] # 1=Creado, 3=EN ejecución, 4=Cerrado
    )

    proyectos_empleado = Proyecto.objects.filter(DetalleProyecto__Empleado=empleado.id)

    archivos = m_Archivos.objects.filter(pk=id)

    data = {
        'mensaje':mensaje,
        'proyectos':proyectos_empleado,
        'sprint':sprints,
        'archivos':archivos
    }

    if request.method == 'POST':
        form = reunionPlaneacionSprint_Forms(request.POST)
        # Obtener el nuevo email del formulario
        fecha = request.POST['FechaHora']
        descripcion = request.POST['Descripcion']
        proyecto = request.POST['Proyecto']
        pro = Proyecto.objects.get(pk=proyecto)
        sprint = request.POST['Sprint']
        sp = Sprint.objects.get(pk=sprint)

        # Actualizar los campos solicitados
        mensaje.FechaHora = fecha
        mensaje.Descripcion = descripcion
        mensaje.Proyecto = pro
        mensaje.Sprint = sp

        # Guardar los cambios en la base de datos
        mensaje.save()

        # spSprint = Sprint.objects.get(id=spd)
        spSprint = get_object_or_404(Sprint, pk=sprint)
        spSprint.objetivosprint = descripcion
        spSprint.save()

        # Redirigir a alguna página de éxito o hacer lo que necesites
        return redirect('Mensajes:listaPlaneacionSprint')
    else:
        form = reunionPlaneacionSprint_Forms()
    # Renderizar el template con el formulario de actualización
    return render(request, 'Mensajes/ProductOwner/editarPlaneacionSp.html', data)

def eliminar_PlaneacionSprint(request, id):
    # producto = get_object_or_404(m_PlanificacionSprint, id=id)
    producto = get_object_or_404(Mensaje, id=id)
    producto.delete()
    return redirect(to="Mensajes:listaPlaneacionSprint")

def obtener_contexto_revision_sprint(mensaje, usuario):
    id_Sprint = mensaje.Sprint.id
    id_Proyecto = mensaje.Proyecto.id

    historias = HistoriaUsuario.objects.filter(Q(Sprint=mensaje.Sprint) & Q(Proyecto=mensaje.Proyecto))
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)
    comentarios = m_Comentarios.objects.filter(Mensaje=mensaje)
    empleado = Empleado.objects.filter(Usuario=usuario)
    tareas = Tarea.objects.filter(HistoriaUsuario__in=historias)
    registros = TareaAvance.objects.filter(tarea__in=tareas)

    total_horas_estimadas = sum(t.horasestimadas for t in tareas)
    total_dias_estimados = total_horas_estimadas / 8

    Query = f"""select id, numero_hu, nombre_hu, horasestimadas, horasreales, estatus_id, huaceptada,
        case 
            when horasrestantes = 0 and horasrestantescaptura = 0 and  horasreales = 0 Then horasestimadas
            else horasrestantes
        end as horasrestantes,
        case 
            when horasrestantes = 0 and horasrestantescaptura = 0 and  horasreales = 0 Then horasestimadas
            else horasrestantescaptura
        end as horasrestantescaptura,
        case
            when
                HorasReales = 0 and  HorasRestantes = 0 Then 0.0
            when 
                HorasReales <> 0 and  HorasRestantes = 0 Then 100.0
            else
                ((HorasEstimadas - HorasRestantes) / HorasEstimadas ::float) * 100
        end AS progreso,
		case
            when
                HorasReales = 0 and  HorasRestantesCaptura = 0 Then 0.0
            when 
                HorasReales <> 0 and  HorasRestantesCaptura = 0 Then 100.0
            else
                ((HorasEstimadas - HorasRestantesCaptura) / HorasEstimadas ::float) * 100
        end AS progreso_captura
        from (SELECT hu.id, hu.\"NumeroHU\" AS numero_hu, hu.nombre AS nombre_hu, eh.\"estatus\" AS Estatus_id,  hu.\"HUAceptada\" AS HUAceptada,
            COALESCE(sum(t.\"horasestimadas\"), 0) AS HorasEstimadas,
            COALESCE(sum(ta.\"horasReales\"), 0) AS HorasReales,
            COALESCE(sum(ta.\"horasRestantes\"), 0) AS HorasRestantes,
			COALESCE(sum(ta."horasRestantesCaptura"), 0) AS HorasRestantesCaptura
        FROM public.\"Scrum_historiausuario\" as hu left join public.\"Scrum_tarea\" as t on
        (
            hu.id = t.\"HistoriaUsuario_id\"
        ) left join public.\"Scrum_tareaavance\" as ta on (
            t.id = ta.\"tarea_id\" and
            ta.\"HistoriaUsuario_id\" = hu.id and
            ta.\"horasDedicadas\" = 0
        ) inner join public.\"Scrum_sprint\" as sp on (
            hu.\"Sprint_id\" = sp.id
        ) inner join public."Scrum_estatushistoria" as eh on (
            hu.\"Estatus_id\" = eh.id
        )
        where
        sp.id =  {id_Sprint}  and
        hu.\"Proyecto_id\" = {id_Proyecto} 
        group by hu.id, hu.\"NumeroHU\", hu.nombre, eh.\"estatus\", hu.\"HUAceptada\" 
        order by numero_hu 
        ) as temp""" 
    
    # Consulta RAW
    #tareaAvance = TareaAvance.objects.raw(f"""<TU QUERY AQUÍ CON {id_Sprint} y {id_Proyecto}>""")
    tareaAvance = TareaAvance.objects.raw(Query)

    # Inicializamos una variable para acumular el total
    total_horas_restantes_captura = 0
    total_horas_restantes = 0

    # Iteramos sobre los resultados del queryset
    for tarea in tareaAvance:
        total_horas_restantes_captura += tarea.horasrestantescaptura 
        total_horas_restantes += tarea.horasrestantes

    if registros:
        total_horas_reales = registros.aggregate(total=models.Sum('horasDedicadas'))['total']
    else:
        # Si no hay registros mostrara 0 por default
        total_horas_reales = 0
    total_dias_reales = total_horas_reales/8
    total_dias_restantes = total_horas_restantes/8
    total_dias_restantes_captura = total_horas_restantes_captura/8
    
    if total_horas_reales == 0 and total_horas_restantes == 0:
        avance_sprint = 0
    elif total_horas_reales != 0 and  total_horas_restantes == 0:  
        avance_sprint = 100.0
    else:
        avance_sprint = ((total_horas_estimadas - total_horas_restantes) / total_horas_estimadas) * 100

    if total_horas_reales == 0 and total_horas_restantes_captura == 0:
        avance_sprint_captura = 0
    elif total_horas_reales != 0 and  total_horas_restantes_captura == 0:  
        avance_sprint_captura = 100.0
    else:
        avance_sprint_captura = ((total_horas_estimadas - total_horas_restantes_captura) / total_horas_estimadas) * 100
    
  
    return {
        'tareaAvance': tareaAvance,
        'mensaje': mensaje,
        'asistentes': asistentes,
        'Empleado': empleado,
        'comentarios': comentarios,
        'total_horas_estimadas': total_horas_estimadas,
        'total_horas_reales': total_horas_reales,
        'total_horas_restantes': total_horas_restantes,
        'total_horas_restantes_captura': total_horas_restantes_captura,
        'total_dias_estimados': total_dias_estimados,
        'total_dias_reales': total_dias_reales,
        'total_dias_restantes': total_dias_restantes,
        'total_dias_restantes_captura': total_dias_restantes_captura,
        'avance_sprint': avance_sprint,
        'avance_sprint_captura': avance_sprint_captura,
    }

def obtener_contexto_retrospectiva_sprint(mensaje, usuario):
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)
    comentarios = m_RetrospectivaSprint.objects.filter(Mensaje=mensaje)
    idiomaPais = Empleado.objects.filter(Usuario=usuario)

    return {
        'form': mensaje,
        'form3': asistentes,
        'idiomaPais':idiomaPais,
        'comentarios':comentarios
    }

def obtener_contexto_reunion_diaria(mensaje, usuario):
    #reunionDiaria = Mensaje.objects.filter(pk=id)
    reunionDiaria = Mensaje.objects.filter(pk=mensaje.id)
    #mensaje = Mensaje.objects.get(pk=id)
    sprint_numero = mensaje.Sprint.numerosprint
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)
    comentarios = m_ReunionDiaria.objects.filter(Mensaje=mensaje)

    #usuario = request.user
    idiomaPais = Empleado.objects.filter(Usuario=usuario)

    return {
        'form': reunionDiaria,
        'form2': asistentes,
        'idiomaPais':idiomaPais,
        'comentarios':comentarios,
        'sprint_numero': sprint_numero,
    }

def obtener_contexto_reunion_diaria_esfuerzo(mensaje, usuario):

    # id_Sprint = Mensaje.objects.get(id=id_ReunionDiaria).Sprint.id
    id_Sprint = mensaje.Sprint.id
    # id_Proyecto = Mensaje.objects.get(id=id_ReunionDiaria).Proyecto.id
    id_Proyecto = mensaje.Proyecto.id
    HU = HistoriaUsuario.objects.filter(Q(Sprint_id=id_Sprint) & Q(Proyecto_id = id_Proyecto)) # 4=En Sprint, 5=Divididas, 6=EN progreso (son las mismas que estan dentro del modelo sprint_backlog)

    Query = f"""SELECT t.* 
            FROM public.\"Scrum_tarea\" as t inner join public.\"Scrum_historiausuario\" as hu on
            (t.\"HistoriaUsuario_id\" = hu.id 
            ) inner join public.\"Scrum_sprint\" as sp on (
                hu.\"Sprint_id\" = sp.id
            )
            where
            sp.id = {id_Sprint} and sp.\"Proyecto_id\" = {id_Proyecto}""" 

    tarea = Tarea.objects.raw(Query)
    
    Query = f"""SELECT hu.id AS historia_id, hu.\"NumeroHU\" AS numero_hu, hu.nombre AS nombre_hu, t.id, t.nombre AS nombre_tarea, t.horasestimadas,
            ta.id AS id_tarea_avance, ta.\"horasDedicadas\", ta.\"horasRestantes\", ta.\"horasReales\", sp.\"numerosprint\", hu.\"Estatus_id\",
            ta.dia_1, ta.dia_2, ta.dia_3, ta.dia_4, ta.dia_5, ta.dia_6, ta.dia_7, ta.dia_8, ta.dia_9, ta.dia_10,
            ta.dia_11, ta.dia_12, ta.dia_13, ta.dia_14, ta.dia_15, ta.dia_16, ta.dia_17, ta.dia_18, ta.dia_19, ta.dia_20,
            ta.dia_21, ta.dia_22, ta.dia_23, ta.dia_24, ta.dia_25, ta.dia_26, ta.dia_27, ta.dia_28, ta.dia_29, ta.dia_30, ta.dia_31
            FROM public."Scrum_historiausuario" as hu left join public."Scrum_tarea" as t on
            (
                hu.id = t.\"HistoriaUsuario_id"
            ) left join public.\"Scrum_tareaavance\" as ta on (
                t.id = ta.\"tarea_id\" and
                ta.\"HistoriaUsuario_id\" = hu.id and
                ta.\"horasDedicadas\" = 0
            ) inner join public.\"Scrum_sprint\" as sp on (
                hu.\"Sprint_id\" = sp.id
            )
            where
            sp.id = {id_Sprint} and
            sp.\"Proyecto_id\" = {id_Proyecto}"""
    

    tareaAvance = TareaAvance.objects.raw(Query)
    #print(f"Registro de tareasavance: {len(list(tareaAvance))}, {list(tareaAvance)}")

    msm = Mensaje.objects.filter(pk=mensaje.id)
    # mensaje = get_object_or_404(Mensaje, id=id_ReunionDiaria)
    sprint_id = mensaje.Sprint.id
    dSprint = get_object_or_404(Sprint, id=sprint_id)
    mes = Sprint.objects.filter(pk=sprint_id)

    # Calcular la diferencia en días
    # diferencia_dias = (fecha_limite - fecha_inicio).days
    diferencia_dias = (dSprint.fechafinalsprint - dSprint.fechainiciosprint).days
    numero = diferencia_dias

    # usuario = request.user
    dEmpleado = Empleado.objects.filter(Usuario=usuario)

    fechas = [dSprint.fechainiciosprint + timedelta(days=i) for i in range(diferencia_dias + 1)]
    #print (f"fechas: {fechas}")
    traduccion_meses = {
        "January": "Enero", "February": "Febrero", "March": "Marzo",
        "April": "Abril", "May": "Mayo", "June": "Junio",
        "July": "Julio", "August": "Agosto", "September": "Septiembre",
        "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
    }

    # Crear un diccionario para agrupar días por mes
    meses = {}


    for fecha in fechas:
        #nombre_mes = fecha.strftime('%B')  # Obtener el nombre del mes en español
        nombre_mes = traduccion_meses[fecha.strftime('%B')]
        if nombre_mes not in meses:
            meses[nombre_mes] = 0
        meses[nombre_mes] += 1  # Contar los días en ese mes

    # # Imprimir resultados
    # for mes, cantidad in meses.items():
    #     print(f"Mes: {mes}, Días: {cantidad}")
    # print(f"mes: {meses}")
        

    # Lista para almacenar la matriz
    matriz_avance = []

    # Iteramos sobre los resultados del Query (tareas de avance)
    for tarea in tareaAvance:
        fila = []
        fila.append(tarea.historia_id) #Id de la Historia de Usuario
        fila.append(tarea.id) #Id de la Tarea
        # Iteramos sobre cada fecha del sprint
        for i, fecha in enumerate(fechas, start=1):
            # Comparar la fecha actual con los campos dia_1, dia_2, ..., dia_n
            for j in range(1, 32):
                field_name = f'dia_{j}'
                # Usar getattr para obtener el valor del campo 'dia_n' del query
                valor_dia = getattr(tarea, field_name, '0/0')
                if fecha.day == j:
                    # Si no hay valor (None), agregamos '0/0', sino tomamos el valor del campo
                    if valor_dia is None:
                        fila.append('0/0')
                    else:
                        fila.append(valor_dia)
    
        # Añadir la fila a la matriz
        matriz_avance.append(fila)

    #print (f"matriz_avance: {matriz_avance}")
    return {
            'form': HU,
            'tarea':tarea,
            'avance':tareaAvance,
            'diferencia_dias': diferencia_dias,
            'mensaje': msm, #mensaje,
            'dEmpleado':dEmpleado,
            'mes':mes,
            'fechas':fechas,
            'matriz_avance':matriz_avance,
            'Sprint': dSprint,
            'meses':meses, 
    }


def generar_pdf_y_guardar(mensaje, data, template_path, descripcion_extra="", nombre_extra=""):
    """
    Genera un PDF desde un template y guarda archivo físico + binario en m_Archivos.
    """
    pdf = render_to_pdf(template_path, data)

    if pdf:
        base_desc = f"{mensaje.EventoScrum.Descripcion} - {mensaje.FechaHora.strftime('%Y-%m-%d')}"
        descripcion = f"{base_desc} {descripcion_extra}".strip()
        archivo_nombre = f"{slugify(descripcion)}{nombre_extra}.pdf"

        nuevo_archivo = m_Archivos(
            Descripcion=descripcion,
            Proyecto=mensaje.Proyecto,
            Mensaje=mensaje,
        )
        nuevo_archivo.Archivo.save(archivo_nombre, ContentFile(pdf.getvalue()), save=False)
        nuevo_archivo.ArchivoObj = pdf.getvalue()
        nuevo_archivo.save()

#Nuevo código para el envío de correos (MENSAJES)
def generar_pdf_y_guardar_refinamiento(mensaje, historiasBL, asistentes):
    data = {
        'form': asistentes,
        'form2': historiasBL,
        'form3': [mensaje],
    }
    generar_pdf_y_guardar(
        mensaje,
        data,
        template_path='Mensajes/ProductOwner/plantillaRefinamiento.html'
    )

def generar_pdf_y_guardar_archivo_planeacion(request, mensaje, asistentes):

    empleado = request.user.usuarioempleado
    proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)
    planeacion = Mensaje.objects.filter(pk=mensaje.id)
    sprint = mensaje.Sprint
    objetivo_sprint = sprint.objetivosprint

    historias = HistoriaUsuario.objects.filter(Q(Proyecto__in=proyectos) & Q(Sprint=sprint))
    comentarios = m_Comentarios.objects.filter(Mensaje=mensaje)
    ObjEmp = Empleado.objects.filter(Usuario=request.user)

    total_horas = sum(item.HorasEstimadas for item in historias)
    total_dias = total_horas / 8

    # Parte 1: Planeación Sprint
    data_planeacion = {
        'form': planeacion,
        'form2': historias,
        'form3': asistentes,
        'ObjEmp': ObjEmp,
        'horas': total_horas,
        'dias': total_dias,
        'comentarios': comentarios,
        'objetivo_sprint': objetivo_sprint,
    }
    generar_pdf_y_guardar(
        mensaje=mensaje,
        data=data_planeacion,
        template_path='Mensajes/ProductOwner/plantillaPlaneacionSprint.html'
    )

    # Parte 2: Historias HU divididas
    historias_divididas = HistoriaUsuario.objects.filter(
        Q(Estatus__in=[5, 6, 7, 8, 9]) & Q(Sprint=sprint)
    )
    data_hu = {'form': historias_divididas}

    generar_pdf_y_guardar(
        mensaje=mensaje,
        data=data_hu,
        template_path='Mensajes/ProductOwner/plantillaHistoriasHU.html',
        descripcion_extra='- HU divididas en tareas',
        nombre_extra='-HU-Divididas'
    )

def guardar_burndown_chart(mensaje):
    sprint = mensaje.Sprint
    if sprint:
        pdf_buffer, _ = construir_pdf_burndown(sprint.id)
        fecha_evento = mensaje.FechaHora.strftime("%Y-%m-%d")
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        descripcion = (
            f"Avance del {sprint.nombresprint} - {fecha_evento} - "
            f"FechaActual ({fecha_actual}) en Gráficas de Burndown"
        )
        archivo_nombre = f"{slugify(descripcion)}.pdf"
        archivo_burndown = m_Archivos(
            Descripcion=descripcion,
            Proyecto=mensaje.Proyecto,
            Mensaje=mensaje,
        )
        archivo_burndown.Archivo.save(archivo_nombre, ContentFile(pdf_buffer.getvalue()), save=False)
        archivo_burndown.ArchivoObj = pdf_buffer.getvalue()
        archivo_burndown.save()

def generar_pdf_y_guardar_archivo_revision(request, mensaje, asistentes):
    data = obtener_contexto_revision_sprint(mensaje, request.user)
    generar_pdf_y_guardar(
        mensaje=mensaje,
        data=data,
        template_path='Mensajes/ProductOwner/plantillaRevisionSprint.html',
        descripcion_extra='',
        nombre_extra=''
    )
     #  Burndown Chart del Sprint (como archivo binario)
    guardar_burndown_chart(mensaje)
 

def generar_pdf_y_guardar_archivo_retrospectiva(request, mensaje, asistentes):
    data = obtener_contexto_retrospectiva_sprint(mensaje, request.user)
    generar_pdf_y_guardar(
        mensaje=mensaje,
        data=data,
        template_path='Mensajes/ProductOwner/plantillaRetrospectivaSprint.html',
        descripcion_extra='',
        nombre_extra=''
    )

def generar_pdf_y_guardar_archivo_reunion_diaria(request, mensaje, asistentes):

    #Parte 1
    data = obtener_contexto_reunion_diaria(mensaje, request.user)
    generar_pdf_y_guardar(
        mensaje=mensaje,
        data=data,
        template_path='Mensajes/ProductOwner/plantillaReuniondDiaria.html',
        descripcion_extra='',
        nombre_extra=''
    )
    
    #Parte 2
    data = obtener_contexto_reunion_diaria_esfuerzo(mensaje, request.user)

    generar_pdf_y_guardar(
        mensaje=mensaje,
        data=data,
        template_path='Mensajes/ProductOwner/plantillaEjecucion2.html',
        descripcion_extra='Esfuerzo_dedicado',
        nombre_extra=''
    )   
     # Parte 3 - Burndown Chart del Sprint (como archivo binario)
    guardar_burndown_chart(mensaje)
 
    # sprint = mensaje.Sprint  # ⚠️ Asegúrate de que el mensaje tenga relación al Sprint
    # if sprint:
    #     pdf_buffer, sprint_obj = construir_pdf_burndown(sprint.id)
    #     # descripcion = f"{mensaje.EventoScrum.Descripcion} - {mensaje.FechaHora.strftime('%Y-%m-%d')} - Burndown"
    #     descripcion = f" Avance del {sprint.nombresprint} - {mensaje.FechaHora.strftime('%Y-%m-%d')} - FechaActual ({datetime.now().strftime("%Y-%m-%d")}) en Gráficas de Burndown"
    #     archivo_nombre = f"{slugify(descripcion)}.pdf"
    #     archivo_burndown = m_Archivos(
    #         Descripcion=descripcion,
    #         Proyecto=mensaje.Proyecto,
    #         Mensaje=mensaje,
    #     )
    #     archivo_burndown.Archivo.save(archivo_nombre, ContentFile(pdf_buffer.getvalue()), save=False)
    #     archivo_burndown.ArchivoObj = pdf_buffer.getvalue()
    #     archivo_burndown.save()

def enviar_mensaje_evento_scrum(request, id, Accion, template_name, redirect_url, evento_id):
    mensaje = get_object_or_404(Mensaje, pk=id)
    usuario = request.user.id
    empleado = Empleado.objects.get(Usuario=usuario)
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)

    if request.method == 'POST':
        form = envAsistentesForms(request.POST)
        if form.is_valid():
            if Accion == 2:
                mensaje.Status = 2
                mensaje.FHUltimaMod = datetime.now()
                mensaje.save()

            proyecto = mensaje.Proyecto
            eventoScrum = mensaje.EventoScrum
            sprint = mensaje.Sprint
            fecha = mensaje.FechaHora
            DescripcionEventoScrum = eventoScrum.Descripcion
            NombreProyecto = proyecto.nombreproyecto
            if evento_id == 2: #Refinamiento
                fecha = m_RefinamientoProductBL.objects.get(Mensaje=id).FechaHora
            FechaHoraReunion = fecha
            #print(f"FechaHoraReunion: {FechaHoraReunion}")

            for asistente in asistentes:
                mensajeReceptor = MensajeReceptor(
                    Proyecto=proyecto,
                    Mensaje=mensaje,
                    Receptor=asistente.Usuario,
                    EventoScrum=eventoScrum,
                    Emisor=empleado,
                    FHCreacion=fecha,
                    Status="1",
                    Sprint=sprint
                )
                if Accion == 1:
                    mensajeReceptor.save()

            destinatarios = ", ".join([f"{a.Usuario.Usuario.email}" for a in asistentes])
            Archivos = m_Archivos.objects.filter(Mensaje=mensaje)
            asunto = f"{DescripcionEventoScrum} {FechaHoraReunion.strftime('%d/%m/%Y %H:%M')}"
            cuerpo = (
                f"Ceremonia: {DescripcionEventoScrum}\\nProyecto: {NombreProyecto}\\n"
                f"Reunión: {FechaHoraReunion.strftime('%d/%m/%Y %H:%M')}\\nDescripción: {mensaje.Descripcion}"
            )
            email = EmailMessage(subject=asunto, body=cuerpo, from_email=request.user.email, to=destinatarios.split(","))

            for arch in Archivos:
                archivo_binario = BytesIO(arch.ArchivoObj)
                email.attach(arch.Archivo.name, archivo_binario.read(), 'application/pdf')

            if Accion == 2:
                email.send()

            time.sleep(2)
            return redirect(redirect_url)

    else:
        if mensaje.Status in ['2', '3', '4']: # 2 = enviado, 3 = comprendido, 4 = Cancelado
            messages.success(request, 'El mensaje ya fue enviado o cancelado.')
            return render(request, 'Scrum/MensajePantalla.html', {'mensaje': mensaje, 'Ruta': redirect_url})

        if mensaje.ArchivosGenerados is not True and evento_id == 2: #evento_id=Refinamiento
            historiasBL = HistoriaUsuario.objects.filter(MensajeRPBL=id)
            generar_pdf_y_guardar_refinamiento(mensaje, historiasBL, asistentes)
        if mensaje.ArchivosGenerados is not True and evento_id == 3: #evento_id=Planeación
            generar_pdf_y_guardar_archivo_planeacion(request, mensaje, asistentes)
        if mensaje.ArchivosGenerados is not True and evento_id == 4: #evento_id=Reunión Diaria
            generar_pdf_y_guardar_archivo_reunion_diaria(request, mensaje, asistentes)            
        if mensaje.ArchivosGenerados is not True and evento_id == 5: #evento_id=Revisión
            generar_pdf_y_guardar_archivo_revision(request, mensaje, asistentes)
        if mensaje.ArchivosGenerados is not True and evento_id == 6: #evento_id=Retrospectiva
            generar_pdf_y_guardar_archivo_retrospectiva(request, mensaje, asistentes)
            
        mensaje.ArchivosGenerados = True
        mensaje.save()

        form = envAsistentesForms
        form2 = Mensaje.objects.filter(pk=id)
        form3 = asistentes
        archivos = m_Archivos.objects.filter(Mensaje=mensaje)

        return render(request, template_name, {
            'form': form, 'form2': form2, 'form3': form3, 'archivos': archivos
        })


# Vistas específicas

def enviar_mensaje2(request, id, Accion):
    from .models import m_RefinamientoProductBL
    return enviar_mensaje_evento_scrum(
        request, id, Accion,
        template_name='Mensajes/ProductOwner/enviarMensaje.html',
        redirect_url='/listaRefinamiento',
        evento_id = 2 # Reunión de Refinamiento del Product BL
    )

def enviar_mensaje_Planeacion(request, id, Accion):
    from .models import m_PlanificacionSprint
    return enviar_mensaje_evento_scrum(
        request, id, Accion,
        template_name='Mensajes/ProductOwner/enviarMensajePlaneacion.html',
        redirect_url='/listaPlaneacionSprint',
        evento_id = 3 # Reunión de Planeación del Sprint
    )

def enviar_mensaje_Revision(request, id, Accion):
    return enviar_mensaje_evento_scrum(
        request, id, Accion,
        template_name='Mensajes/ProductOwner/enviarMensajeRevision.html',
        redirect_url='/listaRevisionSprint',
        evento_id = 5 # Reunión del Cierre/Revisión del Sprint
    )

def enviar_mensaje_Retrospectiva(request, id, Accion):
    return enviar_mensaje_evento_scrum(
        request, id, Accion,
        template_name='Mensajes/ProductOwner/enviarMensajeRetrospectiva.html',
        redirect_url='/listaRetrospectivaSprint',
        evento_id = 6 # Reunión de Retrospectiva del Sprint
    )

def enviar_mensaje_Reunion_Diaria(request, id, Accion):
    return enviar_mensaje_evento_scrum(
        request, id, Accion,
        template_name='Mensajes/ProductOwner/enviarMensajeReunionDiaria.html',
        redirect_url='/listaReunionDiaria',
        evento_id = 4  # Reunión Diaria
    )
# Product Owner
# def enviar_mensaje_Planeacion(request, id, Accion):
#     # mensaje = Mensaje.objects.filter(pk=id) 
#     msm = Mensaje.objects.get(pk=id)
#     usuario = request.user.id
#     empleado = Empleado.objects.get(Usuario=usuario)
#     if request.method == 'POST':
#         form = envAsistentesForms(request.POST)
#         if form.is_valid():
#             mensajeid = msm
#             proyecto = msm.Proyecto
#             eventoScrum = msm.EventoScrum
#             status = msm.Status
#             fecha = msm.FechaHora
#             archivo = msm.archivo
#             sprint = msm.Sprint
#             DescripcionEventoScrum = msm.EventoScrum.Descripcion
#             FechaHoraReunion = m_PlanificacionSprint.objects.get(Mensaje=id).FechaHora #contenido.m_RefinamientoProductBL.FechaHora
#             NombreProyecto = msm.Proyecto.nombreproyecto
#             if Accion == 2:
#                 #Actualiza el status del mensaje enviado
#                 msm.Status = 2 #Enviado
#                 msm.FHUltimaMod = datetime.now()
#                 msm.save() #Actualiza  la BD

#             res = AsistentesEventosScrum.objects.filter(Mensaje=msm)
#             Destinatarios = ""
#             for asistente in res:
#                 mensaje = MensajeReceptor(Proyecto=proyecto, Mensaje=mensajeid, Receptor=asistente.Usuario, EventoScrum=eventoScrum, 
#                                           Emisor=empleado ,FHCreacion=fecha,Status="1", archivo=archivo, Sprint=sprint)
#                 if Accion == 1:
#                     mensaje.save() #Guarda la Información en la BD "Mensajes_mensajereceptor" por cada uno de los destinatarios
#                 Destinatarios = Destinatarios + str(asistente.Usuario.Usuario.email) + ', ' 
                
#             Destinatarios = Destinatarios[:-2] #Elimina la última coma y espacio
   
#             #Inicia Envía el correo
#             Archivos = m_Archivos.objects.filter(Mensaje=msm)
#             #ArchivosAdjuntos=""

#             #Envío de correo
#             FechaHoraFormateada = FechaHoraReunion.strftime('%d/%m/%Y %H:%M')
#             asunto = DescripcionEventoScrum +  ' ' +  str(FechaHoraFormateada) #'Reunión de Planificación del Sprint'
#             Remitente = request.user.email
#             CuerpoMensaje = "Ceremonia: " + DescripcionEventoScrum + '\r\n Proyecto: ' + NombreProyecto + '\r\n' + 'Reunión: ' +  str(FechaHoraFormateada) #'Reunión de Planifiación del Sprint
#             ListaDestinatarios = Destinatarios.split(",")
#             email = EmailMessage(
#                 subject=asunto,
#                 body=CuerpoMensaje,
#                 from_email=Remitente,  
#                 to=ListaDestinatarios,
#             )   
#             for arch in Archivos:
#                  # Convertimos el contenido binario del archivo a un objeto BytesIO
#                 archivo_binario = BytesIO(arch.ArchivoObj)

#                 # Adjuntar el archivo al correo con el nombre original del archivo
#                 email.attach(arch.Archivo.name, archivo_binario.read(), 'application/pdf')
#                 #email.attach_file(str(arch.Archivo))
#             if Accion == 2:
#                 email.send()
#             #Fin Envío del correo

#             time.sleep(2) # 2 segundos de espera, mientras se lee el mensaje de verficacion
#             return redirect('Mensajes:listaPlaneacionSprint')  # Redirigir a la página de mensajes enviados
#     else:
#         if msm.Status == '2': #El mensaje ya fue enviado
#             #print(f"idSms.Status2 : {msm.Status} ")
#             # Obtener el mensaje
#             MensajeAviso = get_object_or_404(Mensaje, pk=id)
#             # Mandar un mensaje que será mostrado en el template
#             messages.success(request, 'El mensaje ya fue enviado.')
#             # Renderizar el template y pasar los datos necesarios
#             return render(request, 'Scrum/MensajePantalla.html', {'mensaje': MensajeAviso, 'Ruta': '/listaPlaneacionSprint'})

#         form = envAsistentesForms
#         form2 = Mensaje.objects.filter(pk=id)
#         form3 = AsistentesEventosScrum.objects.filter(Mensaje=msm)
#         #idmensaje = Mensaje.objects.get(pk=id)
#         archivos = m_Archivos.objects.filter(Mensaje=msm)
#     return render(request, 'Mensajes/ProductOwner/enviarMensajePlaneacion.html', {'form': form, 'form2':form2, 'form3':form3, 'archivos':archivos})

def enviar_mensaje_Planeacion_OLD(request, id):
    # mensaje = Mensaje.objects.filter(pk=id) 
    idSms = Mensaje.objects.get(pk=id)
    receptor = User.objects.get(pk=5)
    # emisor = request.user

    usuario = request.user.id
    empleado = Empleado.objects.get(Usuario=usuario)

    # usuarios = User.objects.filter(pk=5) 

    if request.method == 'POST':
        # form = MensajeForms(request.POST)
        form = envAsistentesForms(request.POST)
        if form.is_valid():
            # idSms = Mensaje.objects.get(pk=id)
            msm = Mensaje.objects.filter(pk=id)

            for contenido in msm:
                proyecto = contenido.Proyecto
                eventoScrum=contenido.EventoScrum
                mensaje=contenido
                status=contenido.Status
                fecha=contenido.FechaHora
                archivo=contenido.archivo
                sprint=contenido.Sprint

            #proyecto = contenido.Proyecto
            #descripcion = contenido.Descripcion
            #eventoScrum = contenido.EventoScrum
            #status = contenido.Status
                
            mensajeid = contenido
            proyecto = contenido.Proyecto
            eventoScrum = contenido.EventoScrum
            status = contenido.Status
            fecha = contenido.FechaHora
            archivo = contenido.archivo
            sprint = contenido.Sprint

            res = AsistentesEventosScrum.objects.filter(Mensaje=idSms)

            for asistente in res:
                # mensaje = Mensaje(Emisor=empleado, Proyecto=proyecto, Descripcion=descripcion, Status="2", 
                #               EventoScrum=eventoScrum, FechaHora=fecha, Destinatario=asistente.Usuario, archivo=archivo)
                mensaje = MensajeReceptor(Proyecto=proyecto, Mensaje=mensajeid, Receptor=asistente.Usuario, EventoScrum=eventoScrum, 
                                          Emisor=empleado ,FHCreacion=fecha,Status="1", archivo=archivo, Sprint=sprint)
                mensaje.save()

            time.sleep(2) # 2 segundos de espera, mientras se lee el mensaje de verficacion
            return redirect('Mensajes:listaPlaneacionSprint')  # Redirigir a la página de mensajes enviados
    else:
        form = envAsistentesForms
        form2 = Mensaje.objects.filter(pk=id)
        form3 = AsistentesEventosScrum.objects.filter(Mensaje=idSms)
        idmensaje = Mensaje.objects.get(pk=id)
        archivos = m_Archivos.objects.filter(Mensaje=idmensaje)
    return render(request, 'Mensajes/ProductOwner/enviarMensajePlaneacion.html', {'form': form, 'receptor': receptor, 'form2':form2, 'form3':form3, 'archivos':archivos})


# ------------- Asistentes Evento Scrum para Planeacion Sprint, Product Owner -----------------------------
# OBSOLETO
def crear_Asistente_PlaneacionF(request,id):
    # mensajes = Mensaje.objects.filter(pk=id)
    mensajes = m_PlanificacionSprint.objects.filter(pk=id)

    evento = m_EventoScrum.objects.filter(pk=4)

    if request.method == 'POST':
        form = AsistentesForms(request.POST)
        if form.is_valid():
            
            for mensaje in mensajes:
                # Crear un AsistentesEventosScrum con los datos del mensaje
                asistente = AsistentesEventosScrum(
                    Proyecto=mensaje.Proyecto,
                    # EventoScrum=mensaje.EventoScrum,
                    Mensaje=mensaje.Mensaje,
                            # Usuario=mensaje.Emisor, 
                )

            for evn in evento:
                astro = AsistentesEventosScrum(
                    EventoScrum=astro.EventoScrum
                )
                
            usuario = form.cleaned_data['Usuario']
            rol = form.cleaned_data['Rol']
            status = form.cleaned_data['Status']
            asistencia = form.cleaned_data['TipoAsistencia']
            proyecto = asistente.Proyecto
            eventoScrum = asistente.EventoScrum
            mensajeid = asistente.Mensaje
            ev = astro.EventoScrum

            
            mensaje = AsistentesEventosScrum(Usuario=usuario,Rol=rol,Status=status,TipoAsistencia=asistencia, Proyecto=proyecto,
                                            EventoScrum=ev ,Mensaje=mensajeid)
            # ,EventoScrum=4
            mensaje.save()
            # asistente.save()
            return redirect('Mensajes:listaPlaneacionSprint')  # Redirigir a la página de mensajes enviados
    else:
        form = AsistentesForms()
    return render(request, 'Mensajes/ProductOwner/listaAsistentesPlaneacion.html', {'form': form})

def crear_Asistente_Planeacion(request,id):
    # emisor = User.objects.get(id=id)
    # mensajes = Mensaje.objects.all()

    mensajes = Mensaje.objects.filter(pk=id)

    if request.method == 'POST':
        form = AsistentesForms(request.POST)
        if form.is_valid():
            
            for mensaje in mensajes:
                # Crear un AsistentesEventosScrum con los datos del mensaje
                asistente = AsistentesEventosScrum(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum,
                    Mensaje=mensaje,
                            # Usuario=mensaje.Emisor,  # Supongo que el Emisor del mensaje se convierte en el Usuario del Asistente
                )
                
            usuario = form.cleaned_data['Usuario']
            rol = form.cleaned_data['Rol']
            status = form.cleaned_data['Status']
            asistencia = form.cleaned_data['TipoAsistencia']
            proyecto = asistente.Proyecto
            eventoScrum = asistente.EventoScrum
            mensajeid = asistente.Mensaje

            
            mensaje = AsistentesEventosScrum(Usuario=usuario,Rol=rol,Status=status,TipoAsistencia=asistencia, Proyecto=proyecto,
                                             EventoScrum=eventoScrum, Mensaje=mensajeid)
            mensaje.save()
            # asistente.save()
            return redirect('Mensajes:listaPlaneacionSprint')  # Redirigir a la página de mensajes enviados
    else:
        form = AsistentesForms()
    return render(request, 'Mensajes/ProductOwner/crearAsistentes.html', {'form': form})


def lista_asistentes_por_planeacion(request, id):
    # Obtener el mensaje específico por su ID
    # mensaje = m_PlanificacionSprint.objects.get(pk=id)
    mensaje = Mensaje.objects.get(pk=id)

    # Obtener todos los AsistentesEventosScrum asociados a este mensaje
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)

    clave = id

    return render(request, 'Mensajes/ProductOwner/listaAsistentesPlaneacion.html', {'form': asistentes, 'clave':clave})

class ActualizarAsistentePlaneacion(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Mensajes/ProductOwner/editarAsistente.html'
    form_class = AsistentesForms
    success_url = reverse_lazy('Mensajes:listaPlaneacionSprint')

def eliminar_AsistentePlaneacion(request, id):
    producto = get_object_or_404(AsistentesEventosScrum, id=id)
    producto.delete()
    return redirect(to="Mensajes:listaPlaneacionSprint")

# Plantilla para el mensaje de retroalimentacion de la revision del sprint
def plantillaRetroAlimentacionRS(request,id): # id del Mensaje de retroalimentación
    # dato = MensajeRetroA.objects.filter(Receptor=request.user)
    dato = MensajeRetroA.objects.filter(pk=id)
    data = {
        'form': dato,
    }

    pdf = render_to_pdf('Mensajes/ProductOwner/plantillaRetroRevision.html', data)
    return HttpResponse(pdf, content_type='application/pdf')

# ------------- Retroalimentacion de la Reunion de Planeacion del Sprint, Product Owner --------------
def mensajes_RetroAlimentacionPlaneacion(request, id): #id del Mensaje
    if request.user.is_authenticated:
        usuario = request.user
        empleado = Empleado.objects.get(Usuario=usuario)
        #retroalimentacion = MensajeRetroA.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="3")) 
        retroalimentacion = MensajeRetroA.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="3")& Q(Mensaje=id)) 

        user = request.user

        if user is not None:
            login(request, user)
            # Redirecciona al usuario dependiendo de su rol
            if user.usuarioempleado.Roles.NombreRol == 'Product Owner':
                return render(request, 'Mensajes/ProductOwner/retroAlimentacionPlaneacion.html', {'mensajes':retroalimentacion})
            else:
                # si el usuario no es Product Owner se mostrara el siguiente mensaje
                return HttpResponse("No eres Product Owner")
        else:
        # Usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    else: 
        return HttpResponseRedirect(reverse('Scrum:Logout'))

# Retroalimentación de la Reunión de Planeación del Sprint, contestacion
def enviar_mensajePS(request, id): #id del mensaje de retroalimentación
    retroalimentacion = MensajeRetroA.objects.filter(pk=id) # era el id del mensaje recibido con los datos
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    if request.method == 'POST':
        #Toma de base el modelo MensajeRetroA, el formulario retroAlimentacionBL_Forms es válido para la retroalimentación de todas las ceremonias 
        form = retroAlimentacionBL_Forms(request.POST) 
        if form.is_valid():
            Respuesta = form.cleaned_data['Contestacion']
            MensajeRetroA.objects.filter(id=id).update(Contestacion=  Respuesta )
            #--
            mensaje_retroa = MensajeRetroA.objects.get(pk=id)
            mensaje_id = mensaje_retroa.Mensaje.id  # Obtienes el id del Mensaje relacionado
            # 
            #--
            #return redirect('Mensajes:retroPlaneacionSprintP')  # Redirigir a la página de mensajes enviados
            return redirect('Mensajes:retroPlaneacionSprintP', id=mensaje_id)  # Redirigir a la página de mensajes enviados
        
    else:
        form = retroAlimentacionBL_Forms()
    return render(request, 'Mensajes/ProductOwner/retroContestacionBL.html', {'form': form})


# ------------- Reunion de Planeación del Sprint, Scrum Master, Mensajes recibidos -------------------------
def listaPlaneacionSprintScrumMaster(request):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    # mensajes = Mensaje.objects.filter(Q(Emisor=empleado) & Q(EventoScrum="3")) 
    mensajes = MensajeReceptor.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="3")) 


    data = {
        'form2':mensajes,
    }

    return render(request, 'Mensajes/ScrumMaster/listaPlaneacionSprint.html', data)

# Mensaje de recibido Scrum Master en caso de seleccionar "Comprendido", correcto
def actualizarRetroStatusCorrectoScrumMaster2(request, id):
    em = request.user.id
    status = "2"
    producto = get_object_or_404(MensajeReceptor, pk=id)
    producto.Status = status
    producto.save()
    msm = producto.Mensaje.id
    
    # return render(request, 'Mensajes/ProductOwner/listaHistoriasUsuariosBL.html')
    return redirect(to='Mensajes:mensajePlaneacionScrumMaster')

# Mensaje de retroalimentacion BL Scrum Master en caso de seleccionar "Comprendido"
def actualizarRetroBLStatusCorrectoScrumMaster2(request, id):
    status = "3"
    producto = get_object_or_404(MensajeRetroA, pk=id)
    producto.Status = status
    producto.save()

    msm = producto.Mensaje.id
    
    return redirect('Mensajes:retroAliScrumMasterPlaneacion', msm)

# Mensaje de retroalimentacion BL Scrum Master en caso de seleccionar "No Comprendido" en la interfaz principal de Reunión de Planeación del Sprint
def enviar_mensajeRetroPlaSprintScrumMaster(request, id):
    # emisor = User.objects.get(id=id)
    em = request.user.id
    emisor = request.user

    # mensajes = Mensaje.objects.filter(pk=id) # usar este metodo en caso de que sea proveniente del modelo "Mensaje"
    mensajes = MensajeReceptor.objects.filter(pk=id)
    if request.method == 'POST':
        form = retroAlimentacion_Forms(request.POST)
        if form.is_valid():

            # usar este metodo en caso de que sea proveniente del modelo "MensajeReceptor"
            for mensaje in mensajes:
                # Crear un MensajeRetroA con los datos del mensaje
                dato = MensajeRetroA(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum, 
                    Mensaje=mensaje.Mensaje, # hereda por defecto el id del mensaje
                    Receptor=mensaje.Emisor, # hereda el emisar del mensaje, NO el del request.user
                    Emisor=mensaje.Receptor,
                    # Sprint=mensaje.Sprint,
            
                )
            
            emisorid = dato.Emisor

            proyecto = dato.Proyecto
            eventoScrum = dato.EventoScrum
            mensajeid = dato.Mensaje
            receptorid = dato.Receptor
            descripcion = form.cleaned_data['Descripcion']
            # sprint = dato.Sprint
            # contenido = form.cleaned_data['Contestacion']
            # status = form.cleaned_data['Status']

            mensaje = MensajeRetroA(Proyecto=proyecto, EventoScrum=eventoScrum, Mensaje=mensajeid, Receptor=receptorid,
                                   Descripcion=descripcion, Status=5, Emisor=emisorid)

            mensaje.save()
            return redirect(to='Mensajes:mensajePlaneacionScrumMaster')  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacion_Forms()
    return render(request, 'Mensajes/ScrumMaster/retroAlimentacion.html', {'form': form})

def mensajes_PlaneacionRetroScrumMaster(request, id):
    # mensajes = Mensaje.objects.filter(Destinatario=request.user)
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    # mensajes = Mensaje.objects.filter(Destinatario=empleado)
    recibidos = MensajeReceptor.objects.filter(Receptor=empleado)

    usuario = request.user

    #retroalimentacion = MensajeRetroA.objects.filter(Receptor=usuario)
    # (Receptor=empleado)
    mensaje = Mensaje.objects.get(pk=id)
    retroalimentacion = MensajeRetroA.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="3") & Q(Mensaje=mensaje))
    msmEnviado = MensajeRetroA.objects.filter(Q(Emisor=empleado) & Q(Contestacion__isnull=True))

    data = {
        'mensajes':retroalimentacion,
        'enviado':msmEnviado
    }

    # mensajes = Mensaje.objects.all()
    return render(request, 'Mensajes/ScrumMaster/retroAlimentacionPlaneacion.html', data)

# ------------- Reunion de Planeación del Sprint, Empleado, Mensajes recibidos -------------------------
def listaPlaneacionSprintEmpleado(request):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    # Obtener los proyectos en los que el empleado participa
    proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)

    #mensajes = MensajeReceptor.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="3")& Q(Proyecto__in=proyectos)) # 3=Reunion de Planeación del Sprint
    mensajes = MensajeReceptor.objects.filter(
        Q(Receptor=empleado) & 
        Q(EventoScrum="3") &  # 3=Reunion de Planeación del Sprint
        Q(Proyecto__in=proyectos)
    ).annotate(
        mensaje_fecha_hora=F('Mensaje__FechaHora')  # Relación con el modelo Mensaje
    )
    data = {
        'form2':mensajes,
    }

    return render(request, 'Scrum/Empleado/listaPlaneacionSprint.html', data)

# Mensaje de recibido Empleado en caso de seleccionar "Comprendido", correcto
def actualizarRetroStatusCorrectoEmpleado2(request, id): # id del Mensaje receptor
    status = "2"
    producto = get_object_or_404(MensajeReceptor, pk=id)
    producto.Status = status
    producto.save()
    
    return redirect(to='Mensajes:mensajePlaneacionEmpleado')

# Mensaje de retroalimentacion Empleado en caso de seleccionar "Comprendido"
def actualizarRetroPSStatusCorrectoEmpleado2(request, id): # id del Mensaje de Retroalimentación
    status = "3" # Status=3 --> Aclarado y/o Comprendido
    producto = get_object_or_404(MensajeRetroA, pk=id)
    producto.Status = status
    producto.save()

    msm = producto.Mensaje.id
    
    return redirect('Mensajes:retroAliEmpleadoPlaneacion', msm)

# Mensaje de retroalimentacion Empleado en caso de seleccionar "No Comprendido" en la interfaz principal de Reunión de Planeación del Sprint
def enviar_mensajeRetroPlaSprintEmpleado(request, id): # id del Mensaje Receptor
    # mensajes = Mensaje.objects.filter(pk=id) # usar este metodo en caso de que sea proveniente del modelo "Mensaje"
    mensajes = MensajeReceptor.objects.filter(pk=id)

    if request.method == 'POST':
        form = retroAlimentacion_Forms(request.POST)
        if form.is_valid():

            # usar este metodo en caso de que sea proveniente del modelo "MensajeReceptor"
            for mensaje in mensajes:
                # Crear un MensajeRetroA con los datos del mensaje
                dato = MensajeRetroA(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum, 
                    Mensaje=mensaje.Mensaje, # hereda por defecto el id del mensaje
                    Receptor=mensaje.Emisor, # hereda el emisar del mensaje, NO el del request.user
                    Emisor=mensaje.Receptor,
                    # Sprint=mensaje.Sprint,
            
                )
            
            emisorid = dato.Emisor

            proyecto = dato.Proyecto
            eventoScrum = dato.EventoScrum
            mensajeid = dato.Mensaje
            receptorid = dato.Receptor
            descripcion = form.cleaned_data['Descripcion']

            mensaje = MensajeRetroA(Proyecto=proyecto, EventoScrum=eventoScrum, Mensaje=mensajeid, Receptor=receptorid,
                                   Descripcion=descripcion, Status=5, Emisor=emisorid) # Status=5 --> No Comprendido

            mensaje.save()
            return redirect(to='Mensajes:mensajePlaneacionEmpleado')  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacion_Forms()
    return render(request, 'Scrum/Empleado/retroAlimentacionPS.html', {'form': form})

def mensajes_PlaneacionRetroEmpleado(request, id): # id del Mensaje Original
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    # (Receptor=empleado)
    mensaje = Mensaje.objects.get(pk=id) 
    #print(f"Mensaje: {mensaje}")
    retroalimentacion = MensajeRetroA.objects.filter(Q(Emisor=empleado) & Q(EventoScrum="3") & Q(Mensaje=mensaje))
    #msmEnviado = MensajeRetroA.objects.filter(Q(Emisor=empleado) & Q(Contestacion__isnull=True))

    data = {
        'mensajes':retroalimentacion,
        #'enviado':msmEnviado
    }

    # mensajes = Mensaje.objects.all()
    return render(request, 'Scrum/Empleado/retroAlimentacionPlaneacion.html', data)

# ------------------------------------- Comentarios y Asistentes - Planeacion Sprint -  Scrum Master -------------------------
# Crear comentarios para Planeacion Sprint, Scrum Master
def crear_ComentarioScrumMasterPlaneacion(request,id):
    mensajes = Mensaje.objects.filter(pk=id) # Recibe el id del mensaje origen
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    if request.method == 'POST':
        form = comentarios_Forms(request.POST)
        if form.is_valid():
            
            for mensaje in mensajes:
                # Crear un comentario con los datos del mensaje
                comentario = m_Comentarios(
                    EventoScrum=mensaje.EventoScrum,
                    Mensaje=mensaje,
                )
                
            comentarios = form.cleaned_data['Comentarios']
            mensaje_id = comentario.Mensaje
            evento = comentario.EventoScrum
            
            mensaje = m_Comentarios(Comentarios=comentarios, Mensaje=mensaje_id, Emisor=empleado, EventoScrum=evento)
            mensaje.save()
            # asistente.save()
            return redirect('Mensajes:mensajePlaneacionScrumMaster')  # Redirigir a la página de mensajes enviados
    else:
        form = comentarios_Forms()
    return render(request, 'Mensajes/ScrumMaster/crear_Comentario.html', {'form': form})

# BETA - Listar asistentes por usuario y mensaje, Planeacion, Scrum Master
def lista_asistentes_por_usuarioPS_SM(request, id):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    # Obtener el mensaje específico por su ID
    # mensaje = Mensaje.objects.get(pk=id)

    # Obtener todos los AsistentesEventosScrum asociados a este mensaje
    # (Q(Receptor=empleado) & Q(EventoScrum="3")) 
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Q(Usuario=empleado) & Q(EventoScrum="3") & Q(Mensaje=mensaje)) 

    data = {
        'form':asistentes
    }

    return render(request, 'Mensajes/ScrumMaster/listaAsistentesPS.html', data)

# Scrum Master
class ActualizarAsistenteScrumMasterPS(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Mensajes/ScrumMaster/editarAsistentePS.html'
    form_class = AsistentesPlaneacion_Forms
    success_url = reverse_lazy('Mensajes:mensajePlaneacionScrumMaster')



# ------------------------------------- Comentarios y Asistentes - Planeacion Sprint -  Empleado -------------------------
# def crear_ComentarioEmpleadoPlaneacion_Old(request,id): # id del Mensaje
#     mensajes = Mensaje.objects.filter(pk=id) # Recibe el id del mensaje origen
#     usuario = request.user
#     empleado = Empleado.objects.get(Usuario=usuario)

#     if request.method == 'POST':
#         form = comentarios_Forms(request.POST)
#         if form.is_valid():
            
#             for mensaje in mensajes:
#                 # Crear un comentario con los datos del mensaje
#                 comentario = m_Comentarios(
#                     EventoScrum=mensaje.EventoScrum,
#                     Mensaje=mensaje,
#                 )
                
#             comentarios = form.cleaned_data['Comentarios']
#             mensaje_id = comentario.Mensaje
#             evento = comentario.EventoScrum
            
#             mensaje = m_Comentarios(Comentarios=comentarios, Mensaje=mensaje_id, Emisor=empleado, EventoScrum=evento)
#             mensaje.save()
#             # asistente.save()
#             return redirect('Mensajes:mensajePlaneacionEmpleado')  # Redirigir a la página de mensajes enviados
#     else:
#         form = comentarios_Forms()
#     return render(request, 'Scrum/Empleado/crear_Comentario.html', {'form': form})
# ------------------------------------- Comentarios y Asistentes - Planeacion Sprint -  Empleado -------------------------
def crear_ComentarioEmpleadoPlaneacion(request, id):  # id del Mensaje
    mensajes = Mensaje.objects.filter(pk=id)  # Recibe el id del mensaje origen
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    # Obtener el comentario existente asociado al mensaje (si existe)
    comentario_existente = None
    if mensajes.exists():
        comentario_existente = m_Comentarios.objects.filter(Mensaje=mensajes.first(), Emisor=empleado).first()

    if request.method == 'POST':
        # Si existe un comentario, se edita; de lo contrario, se crea uno nuevo
        if comentario_existente:
            form = comentarios_Forms(request.POST, instance=comentario_existente)
        else:
            form = comentarios_Forms(request.POST)

        if form.is_valid():
            comentario = form.save(commit=False)  # No guarda todavía
            if not comentario_existente:  # Solo añade estos datos si es un nuevo comentario
                comentario.Mensaje = mensajes.first()
                comentario.EventoScrum = mensajes.first().EventoScrum
                comentario.Emisor = empleado
            comentario.save()  # Guarda el comentario
            return redirect('Mensajes:mensajePlaneacionEmpleado')  # Redirige a otra vista
    else:
        # Inicializar el formulario con datos existentes o vacío
        if comentario_existente:
            form = comentarios_Forms(instance=comentario_existente)
        else:
            form = comentarios_Forms()

    return render(request, 'Scrum/Empleado/crear_Comentario.html', {'form': form})

# BETA - Listar asistentes por usuario y mensaje, Planeacion, Empleado
def lista_asistentes_por_usuarioPS_Empleado(request, id): # id del Mensaje Original
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    # Obtener el mensaje específico por su ID
    # mensaje = Mensaje.objects.get(pk=id)

    # Obtener todos los AsistentesEventosScrum asociados a este mensaje
    # (Q(Receptor=empleado) & Q(EventoScrum="3")) 
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Q(Usuario=empleado) & Q(EventoScrum="3") & Q(Mensaje=mensaje)) 

    data = {
        'form':asistentes
    }

    return render(request, 'Scrum/Empleado/listaAsistentesPS.html', data)

# Empleado
class ActualizarAsistenteEmpleadoPS(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Scrum/Empleado/editarAsistentePS.html'
    form_class = AsistentesPlaneacion_Forms
    success_url = reverse_lazy('Mensajes:mensajePlaneacionEmpleado')


# -----------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------- REUNION DE REVISION DEL SPRINT, Product Owner --------------------------------
# Listar registros de revison sprint
def listaRevisionSprint(request):
    if request.user.is_authenticated:
        usuario = request.user
        #empleado = Empleado.objects.get(Usuario=usuario)
        #mensajes = Mensaje.objects.filter(Q(Emisor=empleado) & Q(EventoScrum="5")) # 5= Reunión del Cierre del Sprint


        # Obtener el Empleado relacionado con el usuario actual
        empleado = request.user.usuarioempleado

        # Obtener los proyectos en los que el empleado participa
        proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)

        #Filtra los mensajes de las ceremonias de Cierre del Sprint, relacionados a un proyecto determinado
        if usuario.usuarioempleado.Roles.NombreRol == 'Product Owner' :
            #mensajes = Mensaje.objects.filter(Q(Emisor=empleado) & Q(EventoScrum="5") & Q(Proyecto__in=proyectos)) # 5= Reunión del Cierre del Sprint
            mensajes = Mensaje.objects.filter(Q(EventoScrum="5") & Q(Proyecto__in=proyectos)) # 5= Reunión del Cierre del Sprint


        #asistentes = AsistentesEventosScrum.objects.all()

        #planeaciacionSprint = m_PlanificacionSprint.objects.all()

        data = {
        'form2':mensajes,
        #'form3':asistentes
        }

        #user = request.user

        if usuario is not None:
            login(request, usuario)
            # Redirecciona al usuario dependiendo de su rol
            if usuario.usuarioempleado.Roles.NombreRol == 'Product Owner':
                return render(request, 'Mensajes/ProductOwner/listaRevisionSprint.html', data)
            else:
                # si el usuario no es Scrum Master se mostrara el siguiente mensaje
                return HttpResponse("No eres Product Owner")
        else:
        # Usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    else: 
        return HttpResponseRedirect(reverse('Scrum:Logout'))

# Muestra una lista de los sprints disponibles para heredar sus datos
def subListaRevisionSprint(request):
    #sprint = Sprint.objects.all()
    # Obtener el Empleado relacionado con el usuario actual
    empleado = request.user.usuarioempleado

    # Obtener los proyectos en los que el empleado participa
    proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)

    # Filtrar los sprints de esos proyectos con el estatus 1 y 3
    sprint = Sprint.objects.filter(
        Proyecto__in=proyectos,
        Estatus__pk__in=[1, 3] # 1=Creado, 3=EN ejecución
    )

    data = {
        'form': sprint
    }

    return render(request, 'Mensajes/ProductOwner/subListaRevisionSprint.html', data)

# # Crear revision del sprint heredando datos del modelo Sprint
# @transaction.atomic
# def crear_RevisionSprint(request, id): #id del Sprint
#     usuario = request.user
#     empleado = Empleado.objects.get(Usuario=usuario)

#     if request.method == 'POST':
#         form = MensajeRevisionSprintForms(request.POST)
#         if form.is_valid():

#             # Obtener datos del formulario o de donde sea necesario
#             fecha_hora = form.cleaned_data['FechaHora']
#             FechaHoraFormateada = fecha_hora.strftime('%d/%m/%Y %H:%M')
#             ref = m_EventoScrum.objects.get(pk=5) # Cierre del sprint 

#             producto = get_object_or_404(Sprint, pk=id)
#             descripcion = f"{FechaHoraFormateada},  Revisión Sprint. {producto.objetivosprint}"
#             #descripcion = producto.objetivosprint
#             proyecto = producto.Proyecto
#             # sprint = producto.nombresprint

#             sp = Sprint.objects.get(pk=id)

#             # Crear instancia de Mensaje
#             mensaje = Mensaje.objects.create(
#                 Descripcion=descripcion,
#                 FechaHora=fecha_hora,
#                 Emisor=empleado,
#                 Proyecto=proyecto,
#                 Sprint=sp,
#                 EventoScrum=ref,
#                 # Asignar otras relaciones según sea necesario
#             )

#             # Crear instancia de m_cierreSprint
#             revision = m_CierreSprint.objects.create(
#                 Emisor=empleado,
#                 FechaHora=fecha_hora,
#                 Mensaje=mensaje,
#                 Proyecto=proyecto,
#                 Sprint=sp,
#                 # Asignar otras relaciones según sea necesario
#             )

#         # Redirigir a alguna página de éxito o hacer lo que necesites
#         return redirect('Mensajes:listaRevisionSprint')
#     else:
#         form = MensajeRevisionSprintForms()
#     return render(request, 'Mensajes/ProductOwner/crearRevisionSprint.html', {'form': form})


@transaction.atomic
def crear_RevisionSprint(request, id):  # id del Sprint
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    if request.method == 'POST':
        form = MensajeRevisionSprintForms(request.POST)
        if form.is_valid():
            fecha_hora = form.cleaned_data['FechaHora']
            FechaHoraFormateada = fecha_hora.strftime('%d/%m/%Y %H:%M')
            ref = m_EventoScrum.objects.get(pk=5)  # Revisión Sprint

            producto = get_object_or_404(Sprint, pk=id)
            descripcion = f"{FechaHoraFormateada},  Revisión Sprint. {producto.objetivosprint}"
            proyecto = producto.Proyecto
            sp = producto

            # Crear el mensaje
            mensaje = Mensaje.objects.create(
                Descripcion=descripcion,
                FechaHora=fecha_hora,
                Emisor=empleado,
                Proyecto=proyecto,
                Sprint=sp,
                EventoScrum=ref,
            )

            # Crear el registro de revisión
            m_CierreSprint.objects.create(
                Emisor=empleado,
                FechaHora=fecha_hora,
                Mensaje=mensaje,
                Proyecto=proyecto,
                Sprint=sp,
            )

            # # ✅ Crear asistentes y receptores automáticamente
            # empleados_activos = EmpleadoProyecto.objects.filter(
            #     Proyecto=proyecto,
            #     Status="1"
            # ).select_related("Empleado", "Empleado__Roles")

            # for ep in empleados_activos:
            #     emp = ep.Empleado

            #     # Crear asistente
            #     AsistentesEventosScrum.objects.create(
            #         Proyecto=proyecto,
            #         EventoScrum=ref,
            #         Mensaje=mensaje,
            #         Usuario=emp,
            #         Rol=emp.Roles,
            #         Status="1",  # Obligatorio
            #         TipoAsistencia="S"  # Síncrona
            #     )

            #     # Crear receptor del mensaje
            #     MensajeReceptor.objects.create(
            #         Proyecto=proyecto,
            #         Mensaje=mensaje,
            #         Receptor=emp,
            #         EventoScrum=ref,
            #         Emisor=empleado,
            #         Sprint=sp,
            #     )
            registrar_asistentes_y_receptores(
                proyecto=proyecto,
                sprint=sp,
                mensaje=mensaje,
                evento=ref,
                emisor=empleado
            )


            return redirect('Mensajes:listaRevisionSprint')

    else:
        form = MensajeRevisionSprintForms()

    return render(request, 'Mensajes/ProductOwner/crearRevisionSprint.html', {'form': form})

class ActualizarRevision(LoginRequiredMixin, UpdateView):
    model = Mensaje
    template_name = 'Mensajes/ProductOwner/editarRevisionSprint.html'
    form_class = UpdateMensajePDF_Forms
    success_url = reverse_lazy('Mensajes:listaRevisionSprint')

    def get_form_kwargs(self):
        # Obtener los kwargs del formulario y agregar el usuario autenticado
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

def eliminar_revision(request, id):
    producto = get_object_or_404(Mensaje, id=id)
    producto.delete()
    return redirect(to="Mensajes:listaRevisionSprint")

# Product Owner
# def enviar_mensaje_Revision(request, id, Accion):

#     msm = Mensaje.objects.get(pk=id)
#     usuario = request.user.id
#     empleado = Empleado.objects.get(Usuario=usuario)

#     if request.method == 'POST':
#         form = envAsistentesForms(request.POST)
#         if form.is_valid():
#             mensajeid = msm
#             proyecto = msm.Proyecto
#             eventoScrum = msm.EventoScrum
#             status = msm.Status
#             fecha = msm.FechaHora
#             archivo = msm.archivo
#             sprint = msm.Sprint
#             DescripcionEventoScrum = msm.EventoScrum.Descripcion
#             FechaHoraReunion = msm.FechaHora
#             NombreProyecto = msm.Proyecto.nombreproyecto

#             if Accion == 2:
#                 #Actualiza el status del mensaje enviado
#                 msm.Status = 2 #Enviado
#                 msm.FHUltimaMod = datetime.now()
#                 msm.save() #Actualiza  la BD

#             res = AsistentesEventosScrum.objects.filter(Mensaje=msm)
#             Destinatarios = ""

#             #res = AsistentesEventosScrum.objects.filter(Mensaje=idSms)

#             for asistente in res:
#                 mensaje = MensajeReceptor(Proyecto=proyecto, Mensaje=mensajeid, Receptor=asistente.Usuario, EventoScrum=eventoScrum, 
#                                           Emisor=empleado ,FHCreacion=fecha,Status="1", archivo=archivo, Sprint=sprint)
#                 if Accion == 1:
#                     mensaje.save() #Guarda la Información en la BD "Mensajes_mensajereceptor" por cada uno de los destinatarios
#                 Destinatarios = Destinatarios + str(asistente.Usuario.Usuario.email) + ', ' 

#             Destinatarios = Destinatarios[:-2] #Elimina la última coma y espacio
   
#             #Inicia Envía el correo
#             Archivos = m_Archivos.objects.filter(Mensaje=msm)
#             #ArchivosAdjuntos=""

#             #Envío de correo
#             FechaHoraFormateada = FechaHoraReunion.strftime('%d/%m/%Y %H:%M')
#             asunto = DescripcionEventoScrum +  ' ' +  str(FechaHoraFormateada) #'Reunión de Revisión del Sprint'
#             Remitente = request.user.email
#             CuerpoMensaje = "Ceremonia: " + DescripcionEventoScrum + '\r\n Proyecto: ' + NombreProyecto + '\r\n' + 'Reunión: ' +  str(FechaHoraFormateada) #'Reunión de Revisión del Sprint
#             ListaDestinatarios = Destinatarios.split(",")
#             email = EmailMessage(
#                 subject=asunto,
#                 body=CuerpoMensaje,
#                 from_email=Remitente,  
#                 to=ListaDestinatarios,
#             )   
#             for arch in Archivos:
#                  # Convertimos el contenido binario del archivo a un objeto BytesIO
#                 archivo_binario = BytesIO(arch.ArchivoObj)

#                 # Adjuntar el archivo al correo con el nombre original del archivo
#                 email.attach(arch.Archivo.name, archivo_binario.read(), 'application/pdf')
#             if Accion == 2:
#                 email.send()
#             #Fin Envío del correo

#             time.sleep(2)
#             return redirect('Mensajes:listaRevisionSprint')  # Redirigir a la página de mensajes enviados
#     else:
#         if msm.Status == '2': #El mensaje ya fue enviado

#             # Obtener el mensaje
#             MensajeAviso = get_object_or_404(Mensaje, pk=id)
#             # Mandar un mensaje que será mostrado en el template
#             messages.success(request, 'El mensaje ya fue enviado.')
#             # Renderizar el template y pasar los datos necesarios
#             return render(request, 'Scrum/MensajePantalla.html', {'mensaje': MensajeAviso, 'Ruta': '/listaRevisionSprint'})

#         form = envAsistentesForms
#         form2 = Mensaje.objects.filter(pk=id)
#         form3 = AsistentesEventosScrum.objects.filter(Mensaje=msm)
#         archivos = m_Archivos.objects.filter(Mensaje=msm)
#     return render(request, 'Mensajes/ProductOwner/enviarMensajeRevision.html', {'form': form, 'form2':form2, 'form3':form3, 'archivos':archivos})

# ------------- Retroalimentacion de la Reunion de Revisión del Sprint, Product Owner --------------
def mensajes_RetroAlimentacionRevision(request, id): #id del Mensaje
    if request.user.is_authenticated:
        usuario = request.user
        empleado = Empleado.objects.get(Usuario=usuario)
        #retroalimentacion = MensajeRetroA.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="5")) 
        retroalimentacion = MensajeRetroA.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="5")& Q(Mensaje=id)) 

        user = request.user

        if user is not None:
            login(request, user)
            # Redirecciona al usuario dependiendo de su rol
            if user.usuarioempleado.Roles.NombreRol == 'Product Owner':
                return render(request, 'Mensajes/ProductOwner/retroalimentacionRevision.html', {'mensajes':retroalimentacion})
            else:
                # si el usuario no es Product Owner se mostrara el siguiente mensaje
                return HttpResponse("No eres Product Owner")
        else:
        # Usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    else: 
        return HttpResponseRedirect(reverse('Scrum:Logout'))

# Retroalimentación de la Reunión de Revisión del Sprint, contestacion
def enviar_mensajeRS(request, id): #id del Mensaje de Retroalimentación
    mensaje_retroa = MensajeRetroA.objects.get(pk=id)
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    if request.method == 'POST':
        form = retroAlimentacionBL_Forms(request.POST)
        if form.is_valid():
            Respuesta = form.cleaned_data['Contestacion']
            MensajeRetroA.objects.filter(id=id).update(Contestacion=  Respuesta )
            mensaje_id = mensaje_retroa.Mensaje.id  # Obtienes el id del Mensaje relacionado
            return redirect('Mensajes:retroRevisionSprint', id=mensaje_id)  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacionBL_Forms()
    return render(request, 'Mensajes/ProductOwner/retroContestacionBL.html', {'form': form})

# ------------------------------- Asistentes - Planeacion Sprint ---------------------------------------------
def lista_asistentes_por_revision(request, id):
    # Obtener el mensaje específico por su ID
    mensaje = Mensaje.objects.get(pk=id)

    # Obtener todos los AsistentesEventosScrum asociados a este mensaje
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)

    clave = id

    return render(request, 'Mensajes/ProductOwner/listaAsistentesRevision.html', {'form': asistentes, 'clave':clave})

def crear_Asistente_Revision(request,id): #id del Mensaje
    mensajes = Mensaje.objects.filter(pk=id)

    if request.method == 'POST':
        form = AsistentesForms(request.POST)
        if form.is_valid():
            
            for mensaje in mensajes:
                # Crear un AsistentesEventosScrum con los datos del mensaje
                asistente = AsistentesEventosScrum(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum,
                    Mensaje=mensaje,
                )
                
            usuario = form.cleaned_data['Usuario']
            rol = form.cleaned_data['Rol']
            status = form.cleaned_data['Status']
            asistencia = form.cleaned_data['TipoAsistencia']
            proyecto = asistente.Proyecto
            eventoScrum = asistente.EventoScrum
            mensajeid = asistente.Mensaje

            
            mensaje = AsistentesEventosScrum(Usuario=usuario,Rol=rol,Status=status,TipoAsistencia=asistencia, Proyecto=proyecto,
                                             EventoScrum=eventoScrum, Mensaje=mensajeid)
            mensaje.save()
            return redirect('Mensajes:listaRevisionSprint')
    else:
        form = AsistentesForms()
    return render(request, 'Mensajes/ProductOwner/crearAsistentes.html', {'form': form})

class ActualizarAsistenteRevision(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Mensajes/ProductOwner/editarAsistente.html'
    form_class = AsistentesForms
    success_url = reverse_lazy('Mensajes:listaRevisionSprint')

def eliminar_asistente_revision(request, id): # id del modelo AsistentesEventosScrum
    producto = get_object_or_404(AsistentesEventosScrum, id=id)
    producto.delete()
    return redirect(to="Mensajes:listaRevisionSprint")


# ----------------------------------- Plantilla Revision Sprint ----------------------------------------
def vistaRevisionSprint(request, id):
    planeacion = Mensaje.objects.filter(pk=id)
    historias = HistoriaUsuario.objects.filter(Q(Estatus=4) | Q(Estatus=5) | Q(Estatus=6) | Q(Estatus=7))
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)
    comentarios = m_Comentarios.objects.filter(Mensaje=mensaje)

    usuario = request.user
    idiomaPais = Empleado.objects.filter(Usuario=usuario)

    # Suma los valores de los objetos
    total_horas = sum(item.HorasEstimadas for item in historias)
    total_dias = total_horas / 24

    # porcentaje = (total_horas * total_dias) / 100
    porcentaje = (total_horas + total_dias) / 2

    # Total de horas de tareas
    tareas = Tarea.objects.all()
    total_tareas = sum(item.horasestimadas for item in tareas)
    tareas_dias = total_tareas / 24

    num = random.randint(1, 16)
    registros = TareaAvance.objects.all()
    if registros:
        suma = registros.aggregate(total=models.Sum('horasDedicadas'))['total']
        diasReales = suma / 24
        # Si la historia esta en progreso, se muestra el siguiente calculo
        # (horas_reales * horas_estimadas) * 100
        enProgreso = (suma / total_tareas) * 100
    else:
        # Si no hay registros mostrara 0 por default
        suma = 0
        diasReales = 0
        enProgreso = 0

    data = {
        'form': planeacion,
        'form2': historias,
        'form3': asistentes,
        'idiomaPais':idiomaPais,
        'horas':total_horas,
        'dias':total_dias,
        'porcentaje':porcentaje,
        'comentarios':comentarios,
        'total_tareas':total_tareas,
        'dias_tareas':tareas_dias,
        'suma':suma,
        'registros': registros,
        'reales':diasReales,
        'progreso':enProgreso,

    }
    return render(request, 'Mensajes/ProductOwner/plantillaRevisionSprint.html', data)



def PlantillaRevisionSprint(request, id):
    mensaje = Mensaje.objects.get(pk=id)
    contexto = obtener_contexto_revision_sprint(mensaje, request.user)
    pdf = render_to_pdf('Mensajes/ProductOwner/plantillaRevisionSprint.html', contexto)
    return HttpResponse(pdf, content_type='application/pdf')


def plantillaRetrospectivaSprint(request, id): #id del Mensaje
    mensaje = Mensaje.objects.get(pk=id)
    contexto = obtener_contexto_retrospectiva_sprint(mensaje, request.user)
    pdf = render_to_pdf('Mensajes/ProductOwner/plantillaRetrospectivaSprint.html', contexto)
    return HttpResponse(pdf, content_type='application/pdf')

def plantillaReunionDiaria(request, id): #id del Mensaje
    mensaje = Mensaje.objects.get(pk=id)
    contexto = obtener_contexto_reunion_diaria(mensaje, request.user)

    pdf = render_to_pdf('Mensajes/ProductOwner/plantillaReuniondDiaria.html', contexto)
    return HttpResponse(pdf, content_type='application/pdf')

def vistaEjecucionSprintID(request, id_ReunionDiaria): #id del Mensaje
    mensaje = Mensaje.objects.get(pk=id_ReunionDiaria)  
    contexto = obtener_contexto_reunion_diaria_esfuerzo(mensaje, request.user)

    pdf = render_to_pdf('Mensajes/ProductOwner/plantillaEjecucion2.html', contexto)
    # return render(request, 'Mensajes/ProductOwner/plantillaEjecucion2.html', contexto)
    return HttpResponse(pdf, content_type='application/pdf')

# def PlantillaRevisionSprint(request, id): #id del Mensaje
#     #planeacion = Mensaje.objects.filter(pk=id)
#     mensaje = Mensaje.objects.get(pk=id)
#     id_Sprint = mensaje.Sprint.id
#     id_Proyecto = mensaje.Proyecto.id
#     # Status de las HU
#     # 4	"En Sprint"
#     # 5	"Dividida en Tareas"
#     # 6	"En Progreso"
#     # 7	"Completada"
#     # 8	"Aceptada"
#     # 9 "Incompleta"
#     #historias = HistoriaUsuario.objects.filter(Q(Sprint = mensaje.Sprint) & Q(Estatus__in=[4, 5, 6, 7, 8, 9]))
#     historias = HistoriaUsuario.objects.filter(Q(Sprint = mensaje.Sprint) & Q(Proyecto=mensaje.Proyecto))
   
#     asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)
#     comentarios = m_Comentarios.objects.filter(Mensaje=mensaje)

#     usuario = request.user
#     empleado = Empleado.objects.filter(Usuario=usuario)

#     # Filtra las tareas asociadas a las historias de usuario filtradas anteriormente
#     tareas = Tarea.objects.filter(HistoriaUsuario__in=historias)

#     total_horas_estimadas = sum(item.horasestimadas for item in tareas)
#     total_dias_estimados = total_horas_estimadas/8

#     # Filtra los registros de TareaAvance asociados a esas tareas
#     registros = TareaAvance.objects.filter(tarea__in=tareas)

#     Query = f"""select id, numero_hu, nombre_hu, horasestimadas, horasreales, estatus_id, huaceptada,
#         case 
#             when horasrestantes = 0 and horasrestantescaptura = 0 and  horasreales = 0 Then horasestimadas
#             else horasrestantes
#         end as horasrestantes,
#         case 
#             when horasrestantes = 0 and horasrestantescaptura = 0 and  horasreales = 0 Then horasestimadas
#             else horasrestantescaptura
#         end as horasrestantescaptura,
#         case
#             when
#                 HorasReales = 0 and  HorasRestantes = 0 Then 0.0
#             when 
#                 HorasReales <> 0 and  HorasRestantes = 0 Then 100.0
#             else
#                 ((HorasEstimadas - HorasRestantes) / HorasEstimadas ::float) * 100
#         end AS progreso,
# 		case
#             when
#                 HorasReales = 0 and  HorasRestantesCaptura = 0 Then 0.0
#             when 
#                 HorasReales <> 0 and  HorasRestantesCaptura = 0 Then 100.0
#             else
#                 ((HorasEstimadas - HorasRestantesCaptura) / HorasEstimadas ::float) * 100
#         end AS progreso_captura
#         from (SELECT hu.id, hu.\"NumeroHU\" AS numero_hu, hu.nombre AS nombre_hu, eh.\"estatus\" AS Estatus_id,  hu.\"HUAceptada\" AS HUAceptada,
#             COALESCE(sum(t.\"horasestimadas\"), 0) AS HorasEstimadas,
#             COALESCE(sum(ta.\"horasReales\"), 0) AS HorasReales,
#             COALESCE(sum(ta.\"horasRestantes\"), 0) AS HorasRestantes,
# 			COALESCE(sum(ta."horasRestantesCaptura"), 0) AS HorasRestantesCaptura
#         FROM public.\"Scrum_historiausuario\" as hu left join public.\"Scrum_tarea\" as t on
#         (
#             hu.id = t.\"HistoriaUsuario_id\"
#         ) left join public.\"Scrum_tareaavance\" as ta on (
#             t.id = ta.\"tarea_id\" and
#             ta.\"HistoriaUsuario_id\" = hu.id and
#             ta.\"horasDedicadas\" = 0
#         ) inner join public.\"Scrum_sprint\" as sp on (
#             hu.\"Sprint_id\" = sp.id
#         ) inner join public."Scrum_estatushistoria" as eh on (
#             hu.\"Estatus_id\" = eh.id
#         )
#         where
#         sp.id =  {id_Sprint}  and
#         hu.\"Proyecto_id\" = {id_Proyecto} 
#         group by hu.id, hu.\"NumeroHU\", hu.nombre, eh.\"estatus\", hu.\"HUAceptada\" 
#         order by numero_hu 
#         ) as temp""" 
#         #    hu.\"Estatus_id\" in (4,5,6,7,8)
#         #%id_Sprint %id_Proyecto
#     tareaAvance = TareaAvance.objects.raw(Query)

#     # Inicializamos una variable para acumular el total
#     total_horas_restantes_captura = 0
#     total_horas_restantes = 0

#     # Iteramos sobre los resultados del queryset
#     for tarea in tareaAvance:
#         total_horas_restantes_captura += tarea.horasrestantescaptura 
#         total_horas_restantes += tarea.horasrestantes

#     if registros:
#         total_horas_reales = registros.aggregate(total=models.Sum('horasDedicadas'))['total']
#         #total_horas_restantes = registros.aggregate(total=models.Sum('horasRestantes'))['total']
#         #total_horas_restantes = registros.filter(horasDedicadas=0).aggregate(total=Sum('horasRestantes'))['total']
#     else:
#         # Si no hay registros mostrara 0 por default
#         total_horas_reales = 0
#         #total_horas_restantes = 0
#     total_dias_reales = total_horas_reales/8
#     total_dias_restantes = total_horas_restantes/8
#     total_dias_restantes_captura = total_horas_restantes_captura/8
    
#     if total_horas_reales == 0 and total_horas_restantes == 0:
#         avance_sprint = 0
#     elif total_horas_reales != 0 and  total_horas_restantes == 0:  
#         avance_sprint = 100.0
#     else:
#         avance_sprint = ((total_horas_estimadas - total_horas_restantes) / total_horas_estimadas) * 100

#     if total_horas_reales == 0 and total_horas_restantes_captura == 0:
#         avance_sprint_captura = 0
#     elif total_horas_reales != 0 and  total_horas_restantes_captura == 0:  
#         avance_sprint_captura = 100.0
#     else:
#         avance_sprint_captura = ((total_horas_estimadas - total_horas_restantes_captura) / total_horas_estimadas) * 100
    
#     data = {
#         'tareaAvance': tareaAvance,
#         'mensaje': mensaje,
#         'asistentes': asistentes,
#         'Empleado':empleado,
#         'total_horas_estimadas': total_horas_estimadas,
#         'total_horas_reales': total_horas_reales,
#         'total_horas_restantes':total_horas_restantes,
#         'total_horas_restantes_captura':total_horas_restantes_captura,
#         'total_dias_estimados':total_dias_estimados,
#         'total_dias_reales':total_dias_reales,
#         'total_dias_restantes':total_dias_restantes,
#         'total_dias_restantes_captura':total_dias_restantes_captura,
#         'avance_sprint':avance_sprint,
#         'avance_sprint_captura':avance_sprint_captura,
#         'comentarios':comentarios,
#     }

#     pdf = render_to_pdf('Mensajes/ProductOwner/plantillaRevisionSprint.html', data)
#     return HttpResponse(pdf, content_type='application/pdf')


# ------------------------------------------- Reunion de Revison del Sprint, Scrum Master ------------------------------------------------
# Recibir Mensajes de revision
def listaRevisionSprintScrumMaster(request):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensajes = MensajeReceptor.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="5")) 
    asistentes = AsistentesEventosScrum.objects.all()
    # archivos = m_Archivos.objects.filter(Mensaje=)

    data = {
        'form2':mensajes,
        'form3':asistentes
    }

    return render(request, 'Mensajes/ScrumMaster/listaRevisionSprint.html', data)

# Listar asistentes por usuario y mensaje, Revision, Scrum Master
def lista_asistentes_revision_SM(request, id):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Q(Usuario=empleado) & Q(EventoScrum="5") & Q(Mensaje=mensaje)) 

    data = {
        'form':asistentes
    }

    return render(request, 'Mensajes/ScrumMaster/listaAsistentesRS.html', data)

class ActualizarAsistenteRevisionSM(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Mensajes/ScrumMaster/editarAsistentePS.html'
    form_class = AsistentesPlaneacion_Forms
    success_url = reverse_lazy('Mensajes:mensajeRevisionScrumMaster')

# Crear comentarios para Revision Sprint
def crear_ComentarioScrumMasterRevision(request,id):
    mensajes = Mensaje.objects.filter(pk=id) # Recibe el id del mensaje origen
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    if request.method == 'POST':
        form = comentarios_Forms(request.POST)
        if form.is_valid():
            
            for mensaje in mensajes:
                # Crear un comentario con los datos del mensaje
                comentario = m_Comentarios(
                    EventoScrum=mensaje.EventoScrum,
                    Mensaje=mensaje,
                )
                
            comentarios = form.cleaned_data['Comentarios']
            mensaje_id = comentario.Mensaje
            evento = comentario.EventoScrum
            
            mensaje = m_Comentarios(Comentarios=comentarios, Mensaje=mensaje_id, Emisor=empleado, EventoScrum=evento)
            mensaje.save()
            # asistente.save()
            return redirect('Mensajes:mensajeRevisionScrumMaster')  # Redirigir a la página de mensajes enviados
    else:
        form = comentarios_Forms()
    return render(request, 'Mensajes/ScrumMaster/crear_Comentario.html', {'form': form})

# Mensaje de recibido Scrum Master en caso de seleccionar "Comprendido"
def actualizarStatusCorrectoScrumMaster(request, id):
    status = "2"
    producto = get_object_or_404(MensajeReceptor, pk=id)
    producto.Status = status
    producto.save()
    
    return redirect(to='Mensajes:mensajeRevisionScrumMaster')

# Mensaje de retroalimentacion Scrum Master en caso de seleccionar "Comprendido"
def actualizarRetroRevisionStatusCorrectoSM(request, id):
    status = "3"
    producto = get_object_or_404(MensajeRetroA, pk=id)
    producto.Status = status
    producto.save()

    msm = producto.Mensaje.id
    
    return redirect('Mensajes:retroAliScrumMasterRevision', msm)

# Mensaje de retroalimentacion Scrum Master en caso de seleccionar "No Comprendido" en la interfaz principal de Reunión de Revisión del Sprint
def enviar_mensajeRetroRevisionSprintSM(request, id):
    mensajes = MensajeReceptor.objects.filter(pk=id)

    if request.method == 'POST':
        form = retroAlimentacion_Forms(request.POST)
        if form.is_valid():

            for mensaje in mensajes:
                # Crear un MensajeRetroA con los datos del mensaje
                dato = MensajeRetroA(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum, 
                    Mensaje=mensaje.Mensaje, # hereda por defecto el id del mensaje
                    Receptor=mensaje.Emisor, # hereda el emisar del mensaje, NO el del request.user
                    Emisor=mensaje.Receptor,
                    # Sprint=mensaje.Sprint,
            
                )
            
            emisorid = dato.Emisor

            proyecto = dato.Proyecto
            eventoScrum = dato.EventoScrum
            mensajeid = dato.Mensaje
            receptorid = dato.Receptor
            descripcion = form.cleaned_data['Descripcion']

            mensaje = MensajeRetroA(Proyecto=proyecto, EventoScrum=eventoScrum, Mensaje=mensajeid, Receptor=receptorid,
                                   Descripcion=descripcion, Status=5, Emisor=emisorid)

            mensaje.save()
            return redirect(to='Mensajes:mensajeRevisionScrumMaster')  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacion_Forms()
    return render(request, 'Mensajes/ScrumMaster/retroAlimentacion.html', {'form': form})

def mensajes_RevisionRetroScrumMaster(request, id):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    recibidos = MensajeReceptor.objects.filter(Receptor=empleado)

    mensaje = Mensaje.objects.get(pk=id)
    retroalimentacion = MensajeRetroA.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="5") & Q(Mensaje=mensaje))
    msmEnviado = MensajeRetroA.objects.filter(Q(Emisor=empleado) & Q(Contestacion__isnull=True))

    data = {
        'mensajes':retroalimentacion,
        'enviado':msmEnviado
    }

    return render(request, 'Mensajes/ScrumMaster/retroAlimentacionRevision.html', data)

# ------------------------------------------- Reunion de Revison del Sprint, Empleado ------------------------------------------------
# Recibir Mensajes de revision
def listaRevisionSprintEmpleado(request):
    # usuario = request.user
    # empleado = Empleado.objects.get(Usuario=usuario)

    # Obtener el Empleado relacionado con el usuario actual
    empleado = request.user.usuarioempleado

    # Obtener los proyectos en los que el empleado participa
    proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)


    #mensajes = MensajeReceptor.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="5") & Q(Proyecto__in=proyectos)) 
    #asistentes = AsistentesEventosScrum.objects.all()
    mensajes = MensajeReceptor.objects.filter(
        Q(Receptor=empleado) & 
        Q(EventoScrum="5") & #Reunión de  revisión del sprint
        Q(Proyecto__in=proyectos)
    ).annotate(
        mensaje_fecha_hora=F('Mensaje__FechaHora')  # Relación con el modelo Mensaje
    )
    data = {
        'form2':mensajes,
        #'form3':asistentes
    }

    return render(request, 'Scrum/Empleado/listaRevisionSprint.html', data)

# Listar asistentes por usuario y mensaje, Revision, Scrum Master
def lista_asistentes_revision_Empleado(request, id): # id del Mensaje Original
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Q(Usuario=empleado) & Q(EventoScrum="5") & Q(Mensaje=mensaje)) 

    data = {
        'form':asistentes
    }

    return render(request, 'Scrum/Empleado/listaAsistentesRS.html', data)

class ActualizarAsistenteRevisionEmpleado(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Scrum/Empleado/editarAsistentePS.html'
    form_class = AsistentesPlaneacion_Forms
    success_url = reverse_lazy('Mensajes:mensajeRevisionEmpleado')

# Crear comentarios para Revision Sprint
# def crear_ComentarioEmpleadoRevision_Old(request,id): # id del Mensaje Original
#     mensajes = Mensaje.objects.filter(pk=id) # Recibe el id del mensaje origen
#     usuario = request.user
#     empleado = Empleado.objects.get(Usuario=usuario)

#     if request.method == 'POST':
#         form = comentarios_Forms(request.POST)
#         if form.is_valid():
            
#             for mensaje in mensajes:
#                 # Crear un comentario con los datos del mensaje
#                 comentario = m_Comentarios(
#                     EventoScrum=mensaje.EventoScrum,
#                     Mensaje=mensaje,
#                 )
                
#             comentarios = form.cleaned_data['Comentarios']
#             mensaje_id = comentario.Mensaje
#             evento = comentario.EventoScrum
            
#             mensaje = m_Comentarios(Comentarios=comentarios, Mensaje=mensaje_id, Emisor=empleado, EventoScrum=evento)
#             mensaje.save()
#             # asistente.save()
#             return redirect('Mensajes:mensajeRevisionEmpleado')  # Redirigir a la página de mensajes enviados
#     else:
#         form = comentarios_Forms()
#     return render(request, 'Scrum/Empleado/crear_Comentario.html', {'form': form})
    
def crear_ComentarioEmpleadoRevision(request, id):  # id del Mensaje
    mensajes = Mensaje.objects.filter(pk=id)  # Recibe el id del mensaje origen
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    # Obtener el comentario existente asociado al mensaje (si existe)
    comentario_existente = None
    if mensajes.exists():
        comentario_existente = m_Comentarios.objects.filter(Mensaje=mensajes.first(), Emisor=empleado).first()

    if request.method == 'POST':
        # Si existe un comentario, se edita; de lo contrario, se crea uno nuevo
        if comentario_existente:
            form = comentarios_Forms(request.POST, instance=comentario_existente)
        else:
            form = comentarios_Forms(request.POST)

        if form.is_valid():
            comentario = form.save(commit=False)  # No guarda todavía
            if not comentario_existente:  # Solo añade estos datos si es un nuevo comentario
                comentario.Mensaje = mensajes.first()
                comentario.EventoScrum = mensajes.first().EventoScrum
                comentario.Emisor = empleado
            comentario.save()  # Guarda el comentario
            return redirect('Mensajes:mensajeRevisionEmpleado')  # Redirige a otra vista
    else:
        # Inicializar el formulario con datos existentes o vacío
        if comentario_existente:
            form = comentarios_Forms(instance=comentario_existente)
        else:
            form = comentarios_Forms()

    return render(request, 'Scrum/Empleado/crear_Comentario.html', {'form': form})


# Mensaje de recibido Empleado en caso de seleccionar "Comprendido", correcto
def actualizarRetroStatusCorrectoEmpleadoRevision(request, id): # id del Mensaje Receptor
    status = "2" # Comprendido 
    producto = get_object_or_404(MensajeReceptor, pk=id)
    producto.Status = status
    producto.save()
    
    return redirect('Mensajes:mensajeRevisionEmpleado')

# Mensaje de retroalimentacion Empleado en caso de seleccionar "Comprendido"
def actualizarRetroPSStatusCorrectoEmpleadoRevision(request, id): # id del Mensaje de Retroalimentación
    status = "3" # Aclarado y/o Comprendido
    producto = get_object_or_404(MensajeRetroA, pk=id)
    producto.Status = status
    producto.save()

    msm = producto.Mensaje.id
    
    return redirect('Mensajes:retroAliEmpleadoRevision', msm)

# Mensaje de retroalimentacion Empleado en caso de seleccionar "No Comprendido" en la interfaz principal de Reunión de Revisión del Sprint
def enviar_mensajeRetroRevisionSprintEmpleado(request, id): # id del Mensaje Receptor
    mensajes = MensajeReceptor.objects.filter(pk=id)

    if request.method == 'POST':
        form = retroAlimentacion_Forms(request.POST)
        if form.is_valid():

            for mensaje in mensajes:
                # Crear un MensajeRetroA con los datos del mensaje
                dato = MensajeRetroA(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum, 
                    Mensaje=mensaje.Mensaje, # hereda por defecto el id del mensaje
                    Receptor=mensaje.Emisor, # hereda el emisar del mensaje, NO el del request.user
                    Emisor=mensaje.Receptor,
                    # Sprint=mensaje.Sprint,
            
                )
            
            emisorid = dato.Emisor

            proyecto = dato.Proyecto
            eventoScrum = dato.EventoScrum
            mensajeid = dato.Mensaje
            receptorid = dato.Receptor
            descripcion = form.cleaned_data['Descripcion']

            mensaje = MensajeRetroA(Proyecto=proyecto, EventoScrum=eventoScrum, Mensaje=mensajeid, Receptor=receptorid,
                                   Descripcion=descripcion, Status=5, Emisor=emisorid) #  Status=5 --> No Comprendido

            mensaje.save()
            return redirect(to='Mensajes:mensajeRevisionEmpleado')  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacion_Forms()
    return render(request, 'Scrum/Empleado/retroAlimentacionPS.html', {'form': form})

def mensajes_RevisionRetroEmpleado(request, id): # id del Mensaje original
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    recibidos = MensajeReceptor.objects.filter(Receptor=empleado)
    #print(f"usuario: {usuario}, empleado: {empleado.id}, id_mensaje:  {id}")
    mensaje = Mensaje.objects.get(pk=id)
    retroalimentacion = MensajeRetroA.objects.filter(Q(Emisor=empleado) & Q(EventoScrum="5") & Q(Mensaje=mensaje))
    #msmEnviado = MensajeRetroA.objects.filter(Q(Emisor=empleado) & Q(Contestacion__isnull=True))
    # print(f"retro: {retroalimentacion.count()}")
    # print(f"msmEnviado: {msmEnviado.count()}")
    data = {
        'mensajes':retroalimentacion,
        #'enviado':msmEnviado
    }

    return render(request, 'Scrum/Empleado/retroAlimentacionRevision.html', data)


# ------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ Reunión de Retrospectiva del Sprint -----------------------------
def vistaRetrospectivaSprint(request, id):
    
    retrospectiva = Mensaje.objects.filter(pk=id)
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)
    comentarios = m_RetrospectivaSprint.objects.filter(Mensaje=mensaje)

    usuario = request.user
    idiomaPais = Empleado.objects.filter(Usuario=usuario)

    data = {
        'form': mensaje,
        'form3': asistentes,
        'idiomaPais':idiomaPais,
        'comentarios':comentarios
    }

    return render(request, 'Mensajes/ProductOwner/plantillaRetrospectivaSprint.html', data)

# def plantillaRetrospectivaSprint(request, id): #id del Mensaje
#     #print(f"plantillaRetrospectivaSprint id: {id} ")
#     retrospectiva = Mensaje.objects.filter(pk=id)
#     mensaje = Mensaje.objects.get(pk=id)
#     asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)
#     comentarios = m_RetrospectivaSprint.objects.filter(Mensaje=mensaje)

#     usuario = request.user
#     idiomaPais = Empleado.objects.filter(Usuario=usuario)

#     data = {
#         'form': mensaje,
#         'form3': asistentes,
#         'idiomaPais':idiomaPais,
#         'comentarios':comentarios
#     }

#     pdf = render_to_pdf('Mensajes/ProductOwner/plantillaRetrospectivaSprint.html', data)
#     return HttpResponse(pdf, content_type='application/pdf')

# Plantilla para el mensaje de retroalimentacion de la retrospectiva del sprint
def plantillaRetroAlimentacionRestrospectiva(request,id): # id del Mensaje de Retroalimentación

    dato = MensajeRetroA.objects.filter(pk=id)
    data = {
        'form': dato,
    }

    pdf = render_to_pdf('Mensajes/ProductOwner/plantillaRetroRetrospectiva.html', data)
    return HttpResponse(pdf, content_type='application/pdf')

# Listar registros de retrospectiva del sprint
def listaRetrospectivaSprint(request):
    if request.user.is_authenticated:
        usuario = request.user
        empleado = Empleado.objects.get(Usuario=usuario)

        # Obtener los proyectos en los que el empleado participa
        proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)
        if usuario.usuarioempleado.Roles.NombreRol in ['Product Owner', 'Scrum Master']:
            #mensajes = Mensaje.objects.filter(Q(Emisor=empleado) & Q(EventoScrum="6") & Q( Proyecto__in=proyectos,)) # Evento - Retrospectiva Sprint 
            mensajes = Mensaje.objects.filter( Q(EventoScrum="6") & Q( Proyecto__in=proyectos,)) # Evento - Retrospectiva Sprint 
        #asistentes = AsistentesEventosScrum.objects.all()
        #asistentes = AsistentesEventosScrum.objects.filter(Mensaje=idSms)

        data = {
        'form2':mensajes,
        #'form3':asistentes
        }

        user = request.user

        if user is not None:
            login(request, user)
            # Redirecciona al usuario dependiendo de su rol
            #if user.usuarioempleado.Roles.NombreRol == 'Product Owner':
            if user.usuarioempleado.Roles.NombreRol in ['Product Owner', 'Scrum Master']:
                return render(request, 'Mensajes/ProductOwner/listaRetrospectivaSprint.html', data)
            else:
                # si el usuario no es Scrum Master se mostrara el siguiente mensaje
                return HttpResponse("No eres Product Owner")
        else:
        # Usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    else: 
        return HttpResponseRedirect(reverse('Scrum:Logout'))

# Muestra una lista de los sprints disponibles para heredar sus datos
def subListaRetrospectivaSprint(request):
    # Obtener el Empleado relacionado con el usuario actual
    empleado = request.user.usuarioempleado

    # Obtener los proyectos en los que el empleado participa
    proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)

    # Filtrar los sprints de esos proyectos con el estatus 3, 4 o 5
    sprints = Sprint.objects.filter(
        Proyecto__in=proyectos,
        Estatus__pk__in=[1,3] #1=Creado, 3=EN ejecución
    )
    #sprint = Sprint.objects.all()

    data = {
        'form': sprints
    }

    return render(request, 'Mensajes/ProductOwner/subListaRetrospectiva.html', data)

# Crear Retrospectiva del Sprint heredando datos del modelo Sprint
# @transaction.atomic
# def crear_RetrospectivaSprint(request, id): #id del Sprint
#     usuario = request.user
#     empleado = Empleado.objects.get(Usuario=usuario)

#     if request.method == 'POST':
#         form = MensajeRevisionSprintForms(request.POST)
#         if form.is_valid():

#             # Obtener datos del formulario o de donde sea necesario
#             fecha_hora = form.cleaned_data['FechaHora']
#             FechaHoraFormateada = fecha_hora.strftime('%d/%m/%Y %H:%M')
#             ref = m_EventoScrum.objects.get(pk=6) # Evento - Retrospectiva Sprint 

#             producto = get_object_or_404(Sprint, pk=id)
#             descripcion = f"{FechaHoraFormateada},  Retrospectiva Sprint. {producto.objetivosprint}"
#             #descripcion = producto.objetivosprint
#             proyecto = producto.Proyecto
#             # sprint = producto.nombresprint

#             sp = Sprint.objects.get(pk=id)

#             # Crear instancia de Mensaje
#             mensaje = Mensaje.objects.create(
#                 Descripcion=descripcion,
#                 FechaHora=fecha_hora,
#                 Emisor=empleado,
#                 Proyecto=proyecto,
#                 Sprint=sp,
#                 EventoScrum=ref,
#                 # Asignar otras relaciones según sea necesario
#             )

#         # Redirigir a alguna página de éxito o hacer lo que necesites
#         return redirect('Mensajes:listaRetrospectivaSprint')
#     else:
#         form = MensajeRevisionSprintForms()
#     return render(request, 'Mensajes/ProductOwner/crearRetrospectivaSprint.html', {'form': form})
# utils/eventos_scrum.py



@transaction.atomic
def crear_RetrospectivaSprint(request, id):  # id del Sprint
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    if request.method == 'POST':
        form = MensajeRevisionSprintForms(request.POST)
        if form.is_valid():
            fecha_hora = form.cleaned_data['FechaHora']
            FechaHoraFormateada = fecha_hora.strftime('%d/%m/%Y %H:%M')
            ref = m_EventoScrum.objects.get(pk=6)  # Retrospectiva Sprint

            producto = get_object_or_404(Sprint, pk=id)
            descripcion = f"{FechaHoraFormateada},  Retrospectiva Sprint. {producto.objetivosprint}"
            proyecto = producto.Proyecto
            sp = producto

            # Crear el mensaje de la retrospectiva
            mensaje = Mensaje.objects.create(
                Descripcion=descripcion,
                FechaHora=fecha_hora,
                Emisor=empleado,
                Proyecto=proyecto,
                Sprint=sp,
                EventoScrum=ref,
            )

            # #  Crear asistentes y receptores
            # empleados_activos = EmpleadoProyecto.objects.filter(
            #     Proyecto=proyecto,
            #     Status="1"
            # ).select_related("Empleado", "Empleado__Roles")

            # for ep in empleados_activos:
            #     emp = ep.Empleado

            #     # Asistente a la reunión
            #     AsistentesEventosScrum.objects.create(
            #         Proyecto=proyecto,
            #         EventoScrum=ref,
            #         Mensaje=mensaje,
            #         Usuario=emp,
            #         Rol=emp.Roles,
            #         Status="1",  # Obligatorio
            #         TipoAsistencia="S"  # Síncrona
            #     )

            #     # Receptor del mensaje
            #     MensajeReceptor.objects.create(
            #         Proyecto=proyecto,
            #         Mensaje=mensaje,
            #         Receptor=emp,
            #         EventoScrum=ref,
            #         Emisor=empleado,
            #         Sprint=sp,
            #     )
            registrar_asistentes_y_receptores(
                proyecto=proyecto,
                sprint=sp,
                mensaje=mensaje,
                evento=ref,
                emisor=empleado
            )


            return redirect('Mensajes:listaRetrospectivaSprint')

    else:
        form = MensajeRevisionSprintForms()

    return render(request, 'Mensajes/ProductOwner/crearRetrospectivaSprint.html', {'form': form})

class ActualizarRetrospectiva(LoginRequiredMixin, UpdateView):
    model = Mensaje
    template_name = 'Mensajes/ProductOwner/editarRetrospectiva.html'
    form_class = UpdateMensajePDF_Forms
    success_url = reverse_lazy('Mensajes:listaRetrospectivaSprint')

    def get_form_kwargs(self):
        # Obtener los kwargs del formulario y agregar el usuario autenticado
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

def eliminar_retrospectiva(request, id):
    producto = get_object_or_404(Mensaje, id=id)
    producto.delete()
    return redirect(to="Mensajes:listaRetrospectivaSprint")

# def enviar_mensaje_Retrospectiva(request, id, Accion):
#     msm = Mensaje.objects.get(pk=id)
#     usuario = request.user.id
#     empleado = Empleado.objects.get(Usuario=usuario)

#     if request.method == 'POST':
#         form = envAsistentesForms(request.POST)
#         if form.is_valid():
#             mensajeid = msm
#             proyecto = msm.Proyecto
#             eventoScrum = msm.EventoScrum
#             status = msm.Status
#             fecha = msm.FechaHora
#             archivo = msm.archivo
#             sprint = msm.Sprint
#             DescripcionEventoScrum = msm.EventoScrum.Descripcion
#             FechaHoraReunion = msm.FechaHora #m_PlanificacionSprint.objects.get(Mensaje=id).FechaHora 
#             NombreProyecto = msm.Proyecto.nombreproyecto
#             if Accion == 2:
#                 #Actualiza el status del mensaje enviado
#                 msm.Status = 2 #Enviado
#                 msm.FHUltimaMod = datetime.now()
#                 msm.save() #Actualiza  la BD

#             res = AsistentesEventosScrum.objects.filter(Mensaje=msm)
#             Destinatarios = ""

#             for asistente in res:
#                 mensaje = MensajeReceptor(Proyecto=proyecto, Mensaje=mensajeid, Receptor=asistente.Usuario, EventoScrum=eventoScrum, 
#                                           Emisor=empleado ,FHCreacion=fecha,Status="1", archivo=archivo, Sprint=sprint)
#                 if Accion == 1:
#                     mensaje.save() #Guarda la Información en la BD "Mensajes_mensajereceptor" por cada uno de los destinatarios
#                 Destinatarios = Destinatarios + str(asistente.Usuario.Usuario.email) + ', ' 
                
#             Destinatarios = Destinatarios[:-2] #Elimina la última coma y espacio

#             #Inicia Envía el correo
#             Archivos = m_Archivos.objects.filter(Mensaje=msm)
#             #ArchivosAdjuntos=""

#             #Envío de correo
#             FechaHoraFormateada = FechaHoraReunion.strftime('%d/%m/%Y %H:%M')
#             asunto = DescripcionEventoScrum +  ' ' +  str(FechaHoraFormateada) #'Reunión de Retrospectiva'
#             Remitente = request.user.email
#             CuerpoMensaje = "Ceremonia: " + DescripcionEventoScrum + '\r\n Proyecto: ' + NombreProyecto + '\r\n' + 'Reunión: ' +  str(FechaHoraFormateada) #'Reunión de  Retrospectiva
#             ListaDestinatarios = Destinatarios.split(",")
#             email = EmailMessage(
#                 subject=asunto,
#                 body=CuerpoMensaje,
#                 from_email=Remitente,  
#                 to=ListaDestinatarios,
#             )   
#             for arch in Archivos:
#                  # Convertimos el contenido binario del archivo a un objeto BytesIO
#                 archivo_binario = BytesIO(arch.ArchivoObj)

#                 # Adjuntar el archivo al correo con el nombre original del archivo
#                 email.attach(arch.Archivo.name, archivo_binario.read(), 'application/pdf')
#             if Accion == 2:
#                 email.send()
#             #Fin Envío del correo
                
#             time.sleep(2)
#             return redirect('Mensajes:listaRetrospectivaSprint')  # Redirigir a la página de mensajes enviados
#     else:
#         if msm.Status == '2': #El mensaje ya fue enviado
#             # print(f"idSms.Status2 : {msm.Status} ")
#             # Obtener el mensaje
#             MensajeAviso = get_object_or_404(Mensaje, pk=id)
#             # Mandar un mensaje que será mostrado en el template
#             messages.success(request, 'El mensaje ya fue enviado.')
#             # Renderizar el template y pasar los datos necesarios
#             return render(request, 'Scrum/MensajePantalla.html', {'mensaje': MensajeAviso, 'Ruta': '/listaRetrospectivaSprint'})


#         form = envAsistentesForms
#         form2 = Mensaje.objects.filter(pk=id)
#         form3 = AsistentesEventosScrum.objects.filter(Mensaje=msm)
#         idmensaje = Mensaje.objects.get(pk=id)
#         archivos = m_Archivos.objects.filter(Mensaje=idmensaje)
#     return render(request, 'Mensajes/ProductOwner/enviarMensajeRetrospectiva.html', {'form': form, 'form2':form2, 'form3':form3, 'archivos':archivos})

# ------------- Retroalimentacion de la Reunion de Retrospectiva del Sprint, Product Owner --------------
def mensajes_RetroAlimentacionRetrospectiva(request, id): #id del Mensaje
    if request.user.is_authenticated:
        usuario = request.user
        empleado = Empleado.objects.get(Usuario=usuario)
        #retroalimentacion = MensajeRetroA.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="6")) 
        retroalimentacion = MensajeRetroA.objects.filter(Q(EventoScrum="6")& Q(Mensaje=id)) 

        user = request.user

        if user is not None:
            login(request, user)
            # Redirecciona al usuario dependiendo de su rol
            #if user.usuarioempleado.Roles.NombreRol == 'Product Owner':
            if user.usuarioempleado.Roles.NombreRol in ['Product Owner', 'Scrum Master']:
                return render(request, 'Mensajes/ProductOwner/retroalimentacionRetrospectiva.html', {'mensajes':retroalimentacion})
            else:
                # si el usuario no es Product Owner se mostrara el siguiente mensaje
                return HttpResponse("No eres Product Owner")
        else:
        # Usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    else: 
        return HttpResponseRedirect(reverse('Scrum:Logout'))

# Retroalimentación de la Reunión de Revisión del Sprint, contestacion
def enviar_mensaje_RetroRetrospectiva(request, id): #id del Mensaje de Retroalimentación
    mensaje_retroa = MensajeRetroA.objects.get(pk=id)
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    
    if request.method == 'POST':
        form = retroAlimentacionBL_Forms(request.POST)
        if form.is_valid():
            Respuesta = form.cleaned_data['Contestacion']
            MensajeRetroA.objects.filter(id=id).update(Contestacion=  Respuesta )
            mensaje_id = mensaje_retroa.Mensaje.id  # Obtienes el id del Mensaje relacionado
            return redirect('Mensajes:retroRetrospectivaSprint', id=mensaje_id)  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacionBL_Forms()
    return render(request, 'Mensajes/ProductOwner/retroContestacionBL.html', {'form': form})

# ------------------------------- Asistentes - Retrospectiva Sprint ---------------------------------------------
def lista_asistentes_por_retrospectiva(request, id): # id del Mensaje
    # Obtener el mensaje específico por su ID
    mensaje = Mensaje.objects.get(pk=id)

    # Obtener todos los AsistentesEventosScrum asociados a este mensaje
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)

    clave = id

    return render(request, 'Mensajes/ProductOwner/listaAsistentesRetrospectiva.html', {'form': asistentes, 'clave':clave})

def crear_Asistente_Retrospectiva(request,id):
    mensajes = Mensaje.objects.filter(pk=id)

    if request.method == 'POST':
        form = AsistentesForms(request.POST)
        if form.is_valid():
            
            for mensaje in mensajes:
                # Crear un AsistentesEventosScrum con los datos del mensaje
                asistente = AsistentesEventosScrum(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum,
                    Mensaje=mensaje,
                )
                
            usuario = form.cleaned_data['Usuario']
            rol = form.cleaned_data['Rol']
            status = form.cleaned_data['Status']
            asistencia = form.cleaned_data['TipoAsistencia']
            proyecto = asistente.Proyecto
            eventoScrum = asistente.EventoScrum
            mensajeid = asistente.Mensaje

            
            mensaje = AsistentesEventosScrum(Usuario=usuario,Rol=rol,Status=status,TipoAsistencia=asistencia, Proyecto=proyecto,
                                             EventoScrum=eventoScrum, Mensaje=mensajeid)
            mensaje.save()
            return redirect('Mensajes:listaRetrospectivaSprint')
    else:
        form = AsistentesForms()
    return render(request, 'Mensajes/ProductOwner/crearAsistentes.html', {'form': form})

class ActualizarAsistenteRetrospectiva(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Mensajes/ProductOwner/editarAsistente.html'
    form_class = AsistentesForms
    success_url = reverse_lazy('Mensajes:listaRetrospectivaSprint')

def eliminar_asistente_retrospectiva(request, id):
    producto = get_object_or_404(AsistentesEventosScrum, id=id)
    producto.delete()
    return redirect(to="Mensajes:listaRetrospectivaSprint")


# ------------------------------- Reunion de retrospectiva del Sprint - Scrum Master (Mensajes recibidos) ----------------
# Listar registros de retrospectiva del sprint
def listaRetrospectivaSprintSM(request):
    if request.user.is_authenticated:
        usuario = request.user
        empleado = Empleado.objects.get(Usuario=usuario)
        mensajes = MensajeReceptor.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="6")) # Evento - Retrospectiva Sprint
        asistentes = AsistentesEventosScrum.objects.all()

        data = {
            'form2':mensajes,
            'form3':asistentes
        }

        user = request.user

        if user is not None:
            login(request, user)
            # Redirecciona al usuario dependiendo de su rol
            if user.usuarioempleado.Roles.NombreRol == 'Scrum Master':
                return render(request, 'Mensajes/ScrumMaster/listaRetrospectivaSprint.html', data)
            else:
                # si el usuario no es Scrum Master se mostrara el siguiente mensaje
                return HttpResponse("No eres Scrum Master")
        else:
        # Usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    else: 
        return HttpResponseRedirect(reverse('Scrum:Logout'))

def listaRetrospectivaSprintSM_ORIGINAL(request): # No borrar hasta en la proxima actualizacion
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensajes = MensajeReceptor.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="6")) # Evento - Retrospectiva Sprint
    asistentes = AsistentesEventosScrum.objects.all()

    data = {
        'form2':mensajes,
        'form3':asistentes
    }

    return render(request, 'Mensajes/ScrumMaster/listaRetrospectivaSprint.html', data)
    

def archivosRecibidosRetrospectivaSM(request, id):
    mensaje = Mensaje.objects.get(pk=id)
    dato = m_Archivos.objects.filter(Mensaje=mensaje)

    data = {
        'form': dato
    }

    return render(request, 'Mensajes/ScrumMaster/archivosRetrospectiva.html', data)

# Listar asistentes por usuario y mensaje, Retrospectiva, Scrum Master
def lista_asistentes_retrospectiva_SM(request, id):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Q(Usuario=empleado) & Q(EventoScrum="6") & Q(Mensaje=mensaje)) 

    data = {
        'form':asistentes
    }

    return render(request, 'Mensajes/ScrumMaster/listaAsistentesRetrospectiva.html', data)

class ActualizarAsistenteRetrospectivaSM(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Mensajes/ScrumMaster/editarAsistentePS.html'
    form_class = AsistentesPlaneacion_Forms
    success_url = reverse_lazy('Mensajes:mensajeRetrospectivaScrumMaster')

# Crear comentarios para Retrospectiva Sprint
def crear_Comentarios_RetrospectivaSM(request,id):
    mensajes = Mensaje.objects.filter(pk=id) # Recibe el id del mensaje origen
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    if request.method == 'POST':
        form = comentariosRetrospectiva_Forms(request.POST)
        if form.is_valid():
            
            for mensaje in mensajes:
                # Crear un comentario con los datos del mensaje
                comentario = m_RetrospectivaSprint(
                    Proyecto=mensaje.Proyecto,
                    Mensaje=mensaje,
                    Sprint=mensaje.Sprint,
                )
                
            comentarios = form.cleaned_data['Comentarios']
            oportunidades = form.cleaned_data['OportunidadesMejora']
            proyecto = comentario.Proyecto
            sprint = comentario.Sprint
            mensaje_id = comentario.Mensaje
            
            mensaje = m_RetrospectivaSprint(Comentarios=comentarios, Mensaje=mensaje_id, Emisor=empleado, Proyecto=proyecto,
                                            Sprint=sprint, OportunidadesMejora=oportunidades)
            mensaje.save()
            return redirect('Mensajes:mensajeRetrospectivaScrumMaster')  # Redirigir a la página de mensajes enviados
    else:
        form = comentariosRetrospectiva_Forms()
    return render(request, 'Mensajes/ScrumMaster/crear_Comentario.html', {'form': form})

# Mensaje de recibido Scrum Master en caso de seleccionar "Comprendido"
def statusCorrectoRetrospectiva(request, id):
    status = "2"
    producto = get_object_or_404(MensajeReceptor, pk=id)
    producto.Status = status
    producto.save()
    
    return redirect(to='Mensajes:mensajeRetrospectivaScrumMaster')

# Mensaje de retroalimentacion Scrum Master en caso de seleccionar "Comprendido"
def actualizarRetroRetrospectivaStatusCorrectoSM(request, id):
    status = "3"
    producto = get_object_or_404(MensajeRetroA, pk=id)
    producto.Status = status
    producto.save()

    msm = producto.Mensaje.id
    
    return redirect('Mensajes:retroAliScrumMasterRetrospectiva', msm)

# Mensaje de retroalimentacion Scrum Master en caso de seleccionar "No Comprendido" en la interfaz principal de Reunión de Retrospectiva del Sprint
def enviar_mensajeRetrospectivaSM(request, id):
    mensajes = MensajeReceptor.objects.filter(pk=id)

    if request.method == 'POST':
        form = retroAlimentacion_Forms(request.POST)
        if form.is_valid():

            for mensaje in mensajes:
                # Crear un MensajeRetroA con los datos del mensaje
                dato = MensajeRetroA(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum, 
                    Mensaje=mensaje.Mensaje, # hereda por defecto el id del mensaje
                    Receptor=mensaje.Emisor, # hereda el emisar del mensaje, NO el del request.user
                    Emisor=mensaje.Receptor,
                    # Sprint=mensaje.Sprint,
            
                )
            
            emisorid = dato.Emisor

            proyecto = dato.Proyecto
            eventoScrum = dato.EventoScrum
            mensajeid = dato.Mensaje
            receptorid = dato.Receptor
            descripcion = form.cleaned_data['Descripcion']

            mensaje = MensajeRetroA(Proyecto=proyecto, EventoScrum=eventoScrum, Mensaje=mensajeid, Receptor=receptorid,
                                   Descripcion=descripcion, Status=5, Emisor=emisorid)

            mensaje.save()
            return redirect(to='Mensajes:mensajeRetrospectivaScrumMaster')  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacion_Forms()
    return render(request, 'Mensajes/ScrumMaster/retroAlimentacion.html', {'form': form})

def mensajes_RetrospectivaRetroSM(request, id):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    recibidos = MensajeReceptor.objects.filter(Receptor=empleado)

    mensaje = Mensaje.objects.get(pk=id)
    retroalimentacion = MensajeRetroA.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="6") & Q(Mensaje=mensaje))
    msmEnviado = MensajeRetroA.objects.filter(Q(Emisor=empleado) & Q(Contestacion__isnull=True))

    data = {
        'mensajes':retroalimentacion,
        'enviado':msmEnviado
    }

    return render(request, 'Mensajes/ScrumMaster/retroAlimentacionRetrospectiva.html', data)


# ------------------------------- Reunion de retrospectiva del Sprint - Empleado (Mensajes recibidos) ----------------
# Listar registros de retrospectiva del sprint
def listaRetrospectivaSprintEmpleado(request):
    if request.user.is_authenticated:
        usuario = request.user
        empleado = Empleado.objects.get(Usuario=usuario)

        # Obtener los proyectos en los que el empleado participa
        proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)

        #mensajes = MensajeReceptor.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="6") & Q(Proyecto__in=proyectos)) # Evento - Retrospectiva Sprint
        #asistentes = AsistentesEventosScrum.objects.all()
        mensajes = MensajeReceptor.objects.filter(
            Q(Receptor=empleado) & 
            Q(EventoScrum="6") & # Evento - Retrospectiva Sprint
            Q(Proyecto__in=proyectos)
        ).annotate(
            mensaje_fecha_hora=F('Mensaje__FechaHora')  # Relación con el modelo Mensaje
        )
        data = {
            'form2':mensajes,
            #'form3':asistentes
        }
    return render(request, 'Scrum/Empleado/listaRetrospectivaSprint.html', data)
    #     user = request.user

    #     if user is not None:
    #         login(request, user)
    #         # Redirecciona al usuario dependiendo de su rol
    #         if user.usuarioempleado.Roles.NombreRol == 'Developers':
    #             return render(request, 'Scrum/Empleado/listaRetrospectivaSprint.html', data)
    #         else:
    #             # si el usuario no es Developers se mostrara el siguiente mensaje
    #             return HttpResponse("No eres Developer")
    #     else:
    #     # Usuario o contraseña incorrectos
    #         return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    # else: 
    #     return HttpResponseRedirect(reverse('Scrum:Logout'))
    
def archivosRecibidosRetrospectivaEmpleado(request, id): # id del Mensaje Original
    mensaje = Mensaje.objects.get(pk=id)
    dato = m_Archivos.objects.filter(Mensaje=mensaje)

    data = {
        'form': dato
    }

    return render(request, 'Scrum/Empleado/archivosRetrospectiva.html', data)

# Mensaje de retroalimentacion Empleado en caso de seleccionar "Comprendido"
def actualizarRetroRetrospectivaStatusCorrectoEmpleado(request, id): # id del Mensaje de Retroalimentación
    status = "3"  # Aclarado y/o Comprendido
    producto = get_object_or_404(MensajeRetroA, pk=id)
    producto.Status = status
    producto.save()

    msm = producto.Mensaje.id
    
    return redirect('Mensajes:retroAliEmpleadoRetrospectiva', msm)

# Listar asistentes por usuario y mensaje, Retrospectiva, Empleado
def lista_asistentes_retrospectiva_Empleado(request, id): # id del Mensaje original
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Q(Usuario=empleado) & Q(EventoScrum="6") & Q(Mensaje=mensaje)) 

    data = {
        'form':asistentes
    }

    return render(request, 'Scrum/Empleado/listaAsistentesRetrospectiva.html', data)

class ActualizarAsistenteRetrospectivaEmpleado(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Scrum/Empleado/editarAsistentePS.html'
    form_class = AsistentesPlaneacion_Forms
    success_url = reverse_lazy('Mensajes:mensajeRetrospectivaEmpleado')

# Crear comentarios para Retrospectiva Sprint
# def crear_Comentarios_Retrospectiva_Empleado_OLD(request,id): # id del Mensaje original
#     mensajes = Mensaje.objects.filter(pk=id) # Recibe el id del mensaje origen
#     usuario = request.user
#     empleado = Empleado.objects.get(Usuario=usuario)

#     if request.method == 'POST':
#         form = comentariosRetrospectiva_Forms(request.POST)
#         if form.is_valid():
            
#             for mensaje in mensajes:
#                 # Crear un comentario con los datos del mensaje
#                 comentario = m_RetrospectivaSprint(
#                     Proyecto=mensaje.Proyecto,
#                     Mensaje=mensaje,
#                     Sprint=mensaje.Sprint,
#                 )
                
#             comentarios = form.cleaned_data['Comentarios']
#             oportunidades = form.cleaned_data['OportunidadesMejora']
#             proyecto = comentario.Proyecto
#             sprint = comentario.Sprint
#             mensaje_id = comentario.Mensaje
            
#             mensaje = m_RetrospectivaSprint(Comentarios=comentarios, Mensaje=mensaje_id, Emisor=empleado, Proyecto=proyecto,
#                                             Sprint=sprint, OportunidadesMejora=oportunidades)
#             mensaje.save()
#             return redirect('Mensajes:mensajeRetrospectivaEmpleado')  # Redirigir a la página de mensajes enviados
#     else:
#         form = comentariosRetrospectiva_Forms()
#     return render(request, 'Scrum/Empleado/crear_Comentario.html', {'form': form})
    
# Crear comentarios para Retrospectiva Sprint    
def crear_Comentarios_Retrospectiva_Empleado(request, id):  # id del Mensaje original
    mensajes = Mensaje.objects.filter(pk=id)  # Recibe el id del mensaje origen
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    # Buscar si ya existe un comentario para este mensaje
    comentario_existente = None
    if mensajes.exists():
        comentario_existente = m_RetrospectivaSprint.objects.filter(Mensaje=mensajes.first(), Emisor=empleado).first()

    if request.method == 'POST':
        # Si existe un comentario, inicializamos el formulario para editarlo
        if comentario_existente:
            form = comentariosRetrospectiva_Forms(request.POST, instance=comentario_existente)
        else:
            form = comentariosRetrospectiva_Forms(request.POST)

        if form.is_valid():
            comentario = form.save(commit=False)  # No guarda todavía
            if not comentario_existente:  # Solo asigna estos campos si es un nuevo comentario
                comentario.Proyecto = mensajes.first().Proyecto
                comentario.Mensaje = mensajes.first()
                comentario.Sprint = mensajes.first().Sprint
                comentario.Emisor = empleado
            comentario.save()  # Guarda el comentario
            return redirect('Mensajes:mensajeRetrospectivaEmpleado')  # Redirige a otra vista
    else:
        # Inicializar el formulario con los datos existentes o en blanco
        if comentario_existente:
            form = comentariosRetrospectiva_Forms(instance=comentario_existente)
        else:
            form = comentariosRetrospectiva_Forms()

    return render(request, 'Scrum/Empleado/crear_Comentario.html', {'form': form})
# Mensaje de recibido Empleado en caso de seleccionar "Comprendido"
def statusCorrectoRetrospectivaEmpleado(request, id):
    status = "2" # Comprendido
    producto = get_object_or_404(MensajeReceptor, pk=id)
    producto.Status = status
    producto.save()
    
    return redirect(to='Mensajes:mensajeRetrospectivaEmpleado')

# Mensaje de retroalimentacion Empleado en caso de seleccionar "No Comprendido" en la interfaz principal de Reunión de Retrospectiva del Sprint
def enviar_mensajeRetrospectivaEmpleado(request, id): # id del Mensaje Receptor
    mensajes = MensajeReceptor.objects.filter(pk=id)

    if request.method == 'POST':
        form = retroAlimentacion_Forms(request.POST)
        if form.is_valid():

            for mensaje in mensajes:
                # Crear un MensajeRetroA con los datos del mensaje
                dato = MensajeRetroA(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum, 
                    Mensaje=mensaje.Mensaje, # hereda por defecto el id del mensaje
                    Receptor=mensaje.Emisor, # hereda el emisar del mensaje, NO el del request.user
                    Emisor=mensaje.Receptor,
                    # Sprint=mensaje.Sprint,
            
                )
            
            emisorid = dato.Emisor

            proyecto = dato.Proyecto
            eventoScrum = dato.EventoScrum
            mensajeid = dato.Mensaje
            receptorid = dato.Receptor
            descripcion = form.cleaned_data['Descripcion']

            mensaje = MensajeRetroA(Proyecto=proyecto, EventoScrum=eventoScrum, Mensaje=mensajeid, Receptor=receptorid,
                                   Descripcion=descripcion, Status=5, Emisor=emisorid) # Status=5 --> No Comprendido

            mensaje.save()
            return redirect(to='Mensajes:mensajeRetrospectivaEmpleado')  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacion_Forms()
    return render(request, 'Scrum/Empleado/retroAlimentacion.html', {'form': form})

def mensajes_RetrospectivaRetroEmpleado(request, id): # id del Mensaje Original
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensaje = Mensaje.objects.get(pk=id)
    retroalimentacion = MensajeRetroA.objects.filter(Q(Emisor=empleado) & Q(EventoScrum="6") & Q(Mensaje=mensaje))

    data = {
        'mensajes':retroalimentacion,
    }

    return render(request, 'Scrum/Empleado/retroAlimentacionRetrospectiva.html', data)


# --------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------- Reunion Diaria -----------------------------------------------------------------------
# Listar registros de la reunion diaria
def listaReunionDiaria(request):
    if request.user.is_authenticated:
        usuario = request.user
        empleado = Empleado.objects.get(Usuario=usuario)

        # Obtener los proyectos en los que el empleado participa
        proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)
        
        #Filtra los mensajes de las ceremonias de Cierre del Sprint, relacionados a un proyecto determinado
        if usuario.usuarioempleado.Roles.NombreRol in ['Product Owner', 'Scrum Master']:
            #mensajes = Mensaje.objects.filter(Q(Emisor=empleado) & Q(EventoScrum="4") & Q(Proyecto__in=proyectos)) # 4= Reunión Diaria
            mensajes = Mensaje.objects.filter(Q(EventoScrum="4") & Q(Proyecto__in=proyectos)) # 4= Reunión Diaria
       #asistentes = AsistentesEventosScrum.objects.all()
        # 🔥 Agregar todos los Sprints disponibles en esos proyectos
        sprints = Sprint.objects.filter(Proyecto__in=proyectos)

        data = {
        'form2':mensajes,
        'sprints': sprints,
        }

        user = request.user

        if user is not None:
            login(request, user)
            # Redirecciona al usuario dependiendo de su rol
            #if user.usuarioempleado.Roles.NombreRol == 'Product Owner':
            if user.usuarioempleado.Roles.NombreRol in ['Product Owner', 'Scrum Master']:
                return render(request, 'Mensajes/ProductOwner/listaReunionDiaria.html', data)
            else:
                # si el usuario no es Product Owner se mostrara el siguiente mensaje
                return HttpResponse("No eres Product Owner")
        else:
        # Usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    else: 
        return HttpResponseRedirect(reverse('Scrum:Logout'))
    
# Muestra una lista de los sprints disponibles para heredar sus datos
def subListaReunionDiaria(request):
    # Obtener el Empleado relacionado con el usuario actual
    empleado = request.user.usuarioempleado

    # Obtener los proyectos en los que el empleado participa
    proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)

    # Filtrar los sprints de esos proyectos con el estatus 3, 4 o 5
    sprints = Sprint.objects.filter(
        Proyecto__in=proyectos,
        Estatus__pk__in=[1, 3] # 1=Creado, 3=En ejecución
    )
    #sprint = Sprint.objects.all()

    data = {
        'form': sprints
    }

    return render(request, 'Mensajes/ProductOwner/subListaReunionDiaria.html', data)

# Crear Reunion Diaria heredando datos del modelo Sprint
# @transaction.atomic
# def crear_Reunion_Diaria(request, id): # id del Sprint
#     usuario = request.user
#     empleado = Empleado.objects.get(Usuario=usuario)

#     if request.method == 'POST':
#         form = MensajeRevisionSprintForms(request.POST)
#         if form.is_valid():

#             # Obtener datos del formulario o de donde sea necesario
#             fecha_hora = form.cleaned_data['FechaHora']
#             FechaHoraFormateada = fecha_hora.strftime('%d/%m/%Y %H:%M')
#             ref = m_EventoScrum.objects.get(pk=4) # Evento - Reunion Diaria

#             producto = get_object_or_404(Sprint, pk=id)
#             #descripcion = producto.objetivosprint
#             descripcion = f"{FechaHoraFormateada},  Reunión Diaria. {producto.objetivosprint}"
#             proyecto = producto.Proyecto
#             # sprint = producto.nombresprint

#             sp = Sprint.objects.get(pk=id)

#             # Crear instancia de Mensaje
#             mensaje = Mensaje.objects.create(
#                 Descripcion=descripcion,
#                 FechaHora=fecha_hora,
#                 Emisor=empleado,
#                 Proyecto=proyecto,
#                 Sprint=sp,
#                 EventoScrum=ref,
#                 # Asignar otras relaciones según sea necesario
#             )

#         # Redirigir a alguna página de éxito o hacer lo que necesites
#         return redirect('Mensajes:listaReunionDiaria')
#     else:
#         form = MensajeRevisionSprintForms()
#     return render(request, 'Mensajes/ProductOwner/crearReunionDiaria.html', {'form': form})


# Crear Reunion Diaria heredando datos del modelo Sprint
# @transaction.atomic
# def crear_Reunion_Diaria(request, id):  # id del Sprint
#     usuario = request.user
#     empleado = Empleado.objects.get(Usuario=usuario)
#     ref = m_EventoScrum.objects.get(pk=4)  # Evento - Reunion Diaria
#     sprint = get_object_or_404(Sprint, pk=id)
#     proyecto = sprint.Proyecto

#     if request.method == 'POST':
#         form = MensajeRevisionSprintForms(request.POST)
#         if form.is_valid():
#             crear_todas = form.cleaned_data.get('crear_todas')
#             fecha_hora = form.cleaned_data['FechaHora']

#             if crear_todas:
#                 # Crear todas las reuniones entre inicio y fin del sprint, ignorando fines de semana
#                 current_date = sprint.fechainiciosprint
#                 end_date = sprint.fechafinalsprint

#                 while current_date <= end_date:
#                     if current_date.weekday() < 5:  # 0 = lunes, 6 = domingo
#                         fecha_datetime = datetime.combine(current_date, fecha_hora.time())
#                         descripcion = f"{fecha_datetime.strftime('%d/%m/%Y %H:%M')}, Reunión Diaria. {sprint.objetivosprint}"
                        
#                         Mensaje.objects.create(
#                             Descripcion=descripcion,
#                             FechaHora=fecha_datetime,
#                             Emisor=empleado,
#                             Proyecto=proyecto,
#                             Sprint=sprint,
#                             EventoScrum=ref
#                         )
#                     current_date += timedelta(days=1)

#             else:
#                 # Crear solo una reunión
#                 fecha_formateada = fecha_hora.strftime('%d/%m/%Y %H:%M')
#                 descripcion = f"{fecha_formateada}, Reunión Diaria. {sprint.objetivosprint}"

#                 Mensaje.objects.create(
#                     Descripcion=descripcion,
#                     FechaHora=fecha_hora,
#                     Emisor=empleado,
#                     Proyecto=proyecto,
#                     Sprint=sprint,
#                     EventoScrum=ref
#                 )

#             return redirect('Mensajes:listaReunionDiaria')
#     else:
#         form = MensajeRevisionSprintForms()

#     return render(request, 'Mensajes/ProductOwner/crearReunionDiaria.html', {'form': form})

# Crear Reunion Diaria heredando datos del modelo Sprint
@transaction.atomic
def crear_Reunion_Diaria(request, id):  # id del Sprint
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    ref = m_EventoScrum.objects.get(pk=4)  # Evento - Reunión Diaria
    sprint = get_object_or_404(Sprint, pk=id)
    proyecto = sprint.Proyecto

    if request.method == 'POST':
        form = MensajeReunionDiariaForms(request.POST)
        if form.is_valid():
            crear_todas = form.cleaned_data.get('crear_todas')
            fecha_hora = form.cleaned_data['FechaHora']

            def asignar_asistentes(mensaje):
                empleados_activos = EmpleadoProyecto.objects.filter(
                    Proyecto=proyecto,
                    Status="1"  # Activo
                ).select_related("Empleado", "Empleado__Roles")

                for ep in empleados_activos:
                    AsistentesEventosScrum.objects.create(
                        Proyecto=mensaje.Proyecto,
                        EventoScrum=mensaje.EventoScrum,
                        Mensaje=mensaje,
                        Usuario=ep.Empleado,
                        Rol=ep.Empleado.Roles,
                        Status="1",  # Obligatorio
                        TipoAsistencia="S"  # Síncrona
                    )

                    # Crear MensajeReceptor
                    MensajeReceptor.objects.create(
                        Proyecto=mensaje.Proyecto,
                        Mensaje=mensaje,
                        Receptor=ep.Empleado,
                        Status="1",  # Recibido
                        EventoScrum=mensaje.EventoScrum,
                        Emisor=mensaje.Emisor,
                        Sprint=mensaje.Sprint
                    )

            if crear_todas:
                current_date = sprint.fechainiciosprint
                end_date = sprint.fechafinalsprint

                while current_date <= end_date:
                    if current_date.weekday() < 5:  # Lunes a viernes
                        fecha_datetime = datetime.combine(current_date, fecha_hora.time())
                        descripcion = f"{fecha_datetime.strftime('%d/%m/%Y %H:%M')}, Reunión Diaria. {sprint.objetivosprint}"
                        
                        mensaje = Mensaje.objects.create(
                            Descripcion=descripcion,
                            FechaHora=fecha_datetime,
                            Emisor=empleado,
                            Proyecto=proyecto,
                            Sprint=sprint,
                            EventoScrum=ref
                        )

                        # Crear asistentes
                        asignar_asistentes(mensaje)

                    current_date += timedelta(days=1)


            else:
                fecha_formateada = fecha_hora.strftime('%d/%m/%Y %H:%M')
                descripcion = f"{fecha_formateada}, Reunión Diaria. {sprint.objetivosprint}"

                mensaje = Mensaje.objects.create(
                    Descripcion=descripcion,
                    FechaHora=fecha_hora,
                    Emisor=empleado,
                    Proyecto=proyecto,
                    Sprint=sprint,
                    EventoScrum=ref
                )
                # Crear asistentes
                asignar_asistentes(mensaje)


            return redirect('Mensajes:listaReunionDiaria')

    else:
        form = MensajeReunionDiariaForms()

    return render(request, 'Mensajes/ProductOwner/crearReunionDiaria.html', {'form': form})


class ActualizarReunionDiaria(LoginRequiredMixin, UpdateView):
    model = Mensaje
    template_name = 'Mensajes/ProductOwner/editarReunionDiaria.html'
    form_class = UpdateMensajePDF_Forms
    success_url = reverse_lazy('Mensajes:listaReunionDiaria')

    def get_form_kwargs(self):
        # Obtener los kwargs del formulario y agregar el usuario autenticado
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    

def eliminar_reunion_diaria(request, id): # id del Mensaje
    producto = get_object_or_404(Mensaje, id=id)
    producto.delete()
    return redirect(to="Mensajes:listaReunionDiaria")

# def enviar_mensaje_Reunion_Diaria(request, id, Accion):
#     msm = Mensaje.objects.get(pk=id)
#     usuario = request.user.id
#     empleado = Empleado.objects.get(Usuario=usuario)


#     if request.method == 'POST':
#         form = envAsistentesForms(request.POST)
#         if form.is_valid():
#             #msm = Mensaje.objects.filter(pk=id)
#             mensajeid = msm
#             proyecto = msm.Proyecto
#             eventoScrum = msm.EventoScrum
#             status = msm.Status
#             fecha = msm.FechaHora
#             archivo = msm.archivo
#             sprint = msm.Sprint
#             DescripcionEventoScrum = msm.EventoScrum.Descripcion
#             FechaHoraReunion = msm.FechaHora #m_PlanificacionSprint.objects.get(Mensaje=id).FechaHora 
#             NombreProyecto = msm.Proyecto.nombreproyecto
#             if Accion == 2:
#                 #Actualiza el status del mensaje enviado
#                 msm.Status = 2 #Enviado
#                 msm.FHUltimaMod = datetime.now()
#                 msm.save() #Actualiza  la BD

#             res = AsistentesEventosScrum.objects.filter(Mensaje=msm)
#             Destinatarios = ""

#             res = AsistentesEventosScrum.objects.filter(Mensaje=msm)
#             Destinatarios = ""
#             for asistente in res:
#                 mensaje = MensajeReceptor(Proyecto=proyecto, Mensaje=mensajeid, Receptor=asistente.Usuario, EventoScrum=eventoScrum, 
#                                           Emisor=empleado ,FHCreacion=fecha,Status="1", archivo=archivo, Sprint=sprint)
#                 if Accion == 1:
#                     mensaje.save() #Guarda la Información en la BD "Mensajes_mensajereceptor" por cada uno de los destinatarios
#                 Destinatarios = Destinatarios + str(asistente.Usuario.Usuario.email) + ', ' 
                
#             Destinatarios = Destinatarios[:-2] #Elimina la última coma y espacio
   
#             #Inicia Envía el correo
#             Archivos = m_Archivos.objects.filter(Mensaje=msm)
#             #ArchivosAdjuntos=""

#             #Envío de correo
#             FechaHoraFormateada = FechaHoraReunion.strftime('%d/%m/%Y %H:%M')
#             asunto = DescripcionEventoScrum +  ' ' +  str(FechaHoraFormateada) #'Reunión Diaria'
#             Remitente = request.user.email
#             CuerpoMensaje = "Ceremonia: " + DescripcionEventoScrum + '\r\n Proyecto: ' + NombreProyecto + '\r\n' + 'Reunión: ' +  str(FechaHoraFormateada) #'Reunión diaria
#             ListaDestinatarios = Destinatarios.split(",")
#             email = EmailMessage(
#                 subject=asunto,
#                 body=CuerpoMensaje,
#                 from_email=Remitente,  
#                 to=ListaDestinatarios,
#             )   
#             for arch in Archivos:
#                  # Convertimos el contenido binario del archivo a un objeto BytesIO
#                 archivo_binario = BytesIO(arch.ArchivoObj)

#                 # Adjuntar el archivo al correo con el nombre original del archivo
#                 email.attach(arch.Archivo.name, archivo_binario.read(), 'application/pdf')
#                 #email.attach_file(str(arch.Archivo))
#             if Accion == 2:
#                 email.send()
#             #Fin Envío del correo

#             time.sleep(2)
#             #return redirect('Mensajes:listaRetrospectivaSprint')  # Redirigir a la página de mensajes enviados
#             return redirect('Mensajes:listaReunionDiaria') 
#     else:
#         if msm.Status == '2': #El mensaje ya fue enviado
#             #print(f"idSms.Status2 : {msm.Status} ")
#             # Obtener el mensaje
#             MensajeAviso = get_object_or_404(Mensaje, pk=id)
#             # Mandar un mensaje que será mostrado en el template
#             messages.success(request, 'El mensaje ya fue enviado.')
#             # Renderizar el template y pasar los datos necesarios
#             return render(request, 'Scrum/MensajePantalla.html', {'mensaje': MensajeAviso, 'Ruta': '/listaReunionDiaria'})


#         form = envAsistentesForms
#         form2 = Mensaje.objects.filter(pk=id)
#         form3 = AsistentesEventosScrum.objects.filter(Mensaje=msm)
#         idmensaje = Mensaje.objects.get(pk=id)
#         archivos = m_Archivos.objects.filter(Mensaje=idmensaje)
#     return render(request, 'Mensajes/ProductOwner/enviarMensajeReunionDiaria.html', {'form': form,  'form2':form2, 'form3':form3, 'archivos':archivos})

# ------------- Retroalimentacion de la Reunion Diaria, Product Owner --------------
def mensajes_RetroAlimentacionReunionDiaria(request, id): # id del Mensaje original
    if request.user.is_authenticated:
        usuario = request.user
        empleado = Empleado.objects.get(Usuario=usuario)
        #retroalimentacion = MensajeRetroA.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="4")) 
        retroalimentacion = MensajeRetroA.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="4")& Q(Mensaje=id)) 

        user = request.user

        if user is not None:
            login(request, user)
            # Redirecciona al usuario dependiendo de su rol
            #if user.usuarioempleado.Roles.NombreRol == 'Product Owner':
            if user.usuarioempleado.Roles.NombreRol in ['Product Owner', 'Scrum Master']:
                return render(request, 'Mensajes/ProductOwner/retroalimentacionReunionDiaria.html', {'mensajes':retroalimentacion})
            else:
                # si el usuario no es Product Owner se mostrara el siguiente mensaje
                return HttpResponse("No eres Product Owner")
        else:
        # Usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    else: 
        return HttpResponseRedirect(reverse('Scrum:Logout'))

# Retroalimentación de la Reunión Diaria, contestacion
def enviar_Retro_Reunion_Diaria(request, id): # id del Mensaje de retroalimentación
    retroalimentacion = MensajeRetroA.objects.filter(pk=id) # era el id del mensaje recibido con los datos
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    if request.method == 'POST':
        form = retroAlimentacionBL_Forms(request.POST)
        if form.is_valid():
            Respuesta = form.cleaned_data['Contestacion']
            MensajeRetroA.objects.filter(id=id).update(Contestacion=  Respuesta )
            #--
            mensaje_retroa = MensajeRetroA.objects.get(pk=id)
            mensaje_id = mensaje_retroa.Mensaje.id  # Obtienes el id del Mensaje relacionado
            # 
            #--
            return redirect('Mensajes:retroReunionDiaria', id=mensaje_id )  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacionBL_Forms()
    return render(request, 'Mensajes/ProductOwner/retroContestacionBL.html', {'form': form})

# Plantilla para el mensaje de retroalimentacion de la retrospectiva del sprint
def plantillaRetroAlimentacionReunionDiaria(request,id): # id del Mensaje de Retroalimentación
    # dato = MensajeRetroA.objects.filter(Receptor=request.user)
    dato = MensajeRetroA.objects.filter(pk=id)
    data = {
        'form': dato,
    }

    pdf = render_to_pdf('Mensajes/ProductOwner/plantillaRetroReunionDiaria.html', data)
    return HttpResponse(pdf, content_type='application/pdf')

# ----------- Asistentes Evento Scrum - Reunion Diaria -------------------------------
def lista_asistentes_por_reunion_diaria(request, id): # id del Mensaje
    # Obtener el mensaje específico por su ID
    mensaje = Mensaje.objects.get(pk=id)

    # Obtener todos los AsistentesEventosScrum asociados a este mensaje
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)

    clave = id

    return render(request, 'Mensajes/ProductOwner/listaAsistentesReunionDiaria.html', {'form': asistentes, 'clave':clave})

def crear_Asistente_Reunion_Diaria(request,id): # id del Mensaje
    mensajes = Mensaje.objects.filter(pk=id)

    if request.method == 'POST':
        form = AsistentesForms(request.POST)
        if form.is_valid():
            
            for mensaje in mensajes:
                # Crear un AsistentesEventosScrum con los datos del mensaje
                asistente = AsistentesEventosScrum(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum,
                    Mensaje=mensaje,
                )
                
            usuario = form.cleaned_data['Usuario']
            rol = form.cleaned_data['Rol']
            status = form.cleaned_data['Status']
            asistencia = form.cleaned_data['TipoAsistencia']
            proyecto = asistente.Proyecto
            eventoScrum = asistente.EventoScrum
            mensajeid = asistente.Mensaje

            
            mensaje = AsistentesEventosScrum(Usuario=usuario,Rol=rol,Status=status,TipoAsistencia=asistencia, Proyecto=proyecto,
                                             EventoScrum=eventoScrum, Mensaje=mensajeid)
            mensaje.save()
            return redirect('Mensajes:listaReunionDiaria')
    else:
        form = AsistentesForms()
    return render(request, 'Mensajes/ProductOwner/crearAsistentes.html', {'form': form})

class ActualizarAsistenteReunionDiariaPO(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Mensajes/ProductOwner/editarAsistente.html'
    form_class = AsistentesForms
    success_url = reverse_lazy('Mensajes:listaReunionDiaria')
    # def get_success_url(self):
    #     # Extraer el id desde self.kwargs
    #     mensaje_id = self.kwargs['pk']
    #     # Usar el id para generar la URL
    #     print(f"mensaje_id: {mensaje_id}")
    #     return reverse_lazy('Mensajes:listaAsistentesReunionDiaria', kwargs={'id': mensaje_id})
    #success_url = reverse_lazy('Mensajes:listaAsistentesReunionDiaria')

def eliminar_asistente_reunion_Diaria(request, id):
    producto = get_object_or_404(AsistentesEventosScrum, id=id)
    producto.delete()
    return redirect(to="Mensajes:listaReunionDiaria")

# ------------------- Vista y plantilla PDF, Reunion Diaria, product owner ------------------------
def vistaReunionDiaria(request, id):
    reunionDiaria = Mensaje.objects.filter(pk=id)
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)
    comentarios = m_ReunionDiaria.objects.filter(Mensaje=mensaje)

    usuario = request.user
    idiomaPais = Empleado.objects.filter(Usuario=usuario)

    data = {
        'form': reunionDiaria,
        'form2': asistentes,
        'idiomaPais':idiomaPais,
        'comentarios':comentarios
    }

    return render(request, 'Mensajes/ProductOwner/plantillaReuniondDiaria.html', data)

# def plantillaReunionDiaria(request, id): #id del Mensaje original
#     reunionDiaria = Mensaje.objects.filter(pk=id)
#     mensaje = Mensaje.objects.get(pk=id)
#     sprint_numero = mensaje.Sprint.numerosprint
#     asistentes = AsistentesEventosScrum.objects.filter(Mensaje=mensaje)
#     comentarios = m_ReunionDiaria.objects.filter(Mensaje=mensaje)

#     usuario = request.user
#     idiomaPais = Empleado.objects.filter(Usuario=usuario)

#     data = {
#         'form': reunionDiaria,
#         'form2': asistentes,
#         'idiomaPais':idiomaPais,
#         'comentarios':comentarios,
#         'sprint_numero': sprint_numero,
#     }

#     pdf = render_to_pdf('Mensajes/ProductOwner/plantillaReuniondDiaria.html', data)
#     return HttpResponse(pdf, content_type='application/pdf')


# ------------------------------- Reunion Diaria - Scrum Master (Mensajes recibidos) ----------------
# Listar registros de reunion diaria
def listaReunionDiariaSM(request):
    if request.user.is_authenticated:
        usuario = request.user
        empleado = Empleado.objects.get(Usuario=usuario)
        mensajes = MensajeReceptor.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="4")) # Evento - Retrospectiva Diaria
        asistentes = AsistentesEventosScrum.objects.all()

        data = {
            'form2':mensajes,
            'form3':asistentes
        }

        user = request.user

        if user is not None:
            login(request, user)
            # Redirecciona al usuario dependiendo de su rol
            if user.usuarioempleado.Roles.NombreRol == 'Scrum Master':
                return render(request, 'Mensajes/ScrumMaster/listaReunionDiaria.html', data)
            else:
                # si el usuario no es Scrum Master se mostrara el siguiente mensaje
                return HttpResponse("No eres Scrum Master")
        else:
        # Usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    else: 
        return HttpResponseRedirect(reverse('Scrum:Logout'))
    
def archivosReunionDiariaSM(request, id):
    mensaje = Mensaje.objects.get(pk=id)
    dato = m_Archivos.objects.filter(Mensaje=mensaje)

    data = {
        'form': dato
    }

    return render(request, 'Mensajes/ScrumMaster/archivosReunionDiaria.html', data)

# Listar asistentes por usuario y mensaje, Retrospectiva, Scrum Master
def lista_asistentes_reunion_diaria_SM(request, id):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Q(Usuario=empleado) & Q(EventoScrum="4") & Q(Mensaje=mensaje)) 

    data = {
        'form':asistentes
    }

    return render(request, 'Mensajes/ScrumMaster/listaAsistentesReunionDiaria.html', data)

class ActualizarAsistenteReunionDiariaSM(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Mensajes/ScrumMaster/editarAsistentePS.html'
    form_class = AsistentesPlaneacion_Forms
    success_url = reverse_lazy('Mensajes:mensajeReunionDiaria')

# Crear comentarios para Reunion Diaria
def crear_Comentarios_Reunion_Diaria_SM(request,id):
    mensajes = Mensaje.objects.filter(pk=id) # Recibe el id del mensaje origen
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)

    if request.method == 'POST':
        form = reunionDiaria_Forms(request.POST)
        if form.is_valid():
            
            for mensaje in mensajes:
                # Crear un comentario con los datos del mensaje
                comentario = m_ReunionDiaria(
                    Proyecto=mensaje.Proyecto,
                    Mensaje=mensaje,
                    Sprint=mensaje.Sprint,
                )
                
            obstaculos = form.cleaned_data['ObstaculosPresentados']
            plan = form.cleaned_data['PlanDiaSiguiente']
            trabajoRealizado = form.cleaned_data['TrabajoRealizadoDiaAnterior']
            proyecto = comentario.Proyecto
            sprint = comentario.Sprint
            mensaje_id = comentario.Mensaje
            
            mensaje = m_ReunionDiaria(ObstaculosPresentados=obstaculos, Mensaje=mensaje_id, Emisor=empleado, Proyecto=proyecto,
                                            Sprint=sprint, PlanDiaSiguiente=plan, TrabajoRealizadoDiaAnterior=trabajoRealizado)
            mensaje.save()
            return redirect('Mensajes:mensajeReunionDiaria')  # Redirigir a la página de mensajes enviados
    else:
        form = reunionDiaria_Forms()
    return render(request, 'Mensajes/ScrumMaster/crear_Comentario.html', {'form': form})

# Mensaje de recibido Scrum Master en caso de seleccionar "Comprendido"
def statusCorrectoReunionDiariaSM(request, id):
    status = "2"
    producto = get_object_or_404(MensajeReceptor, pk=id)
    producto.Status = status
    producto.save()
    
    return redirect(to='Mensajes:mensajeReunionDiaria')

# Mensaje de retroalimentacion Scrum Master en caso de seleccionar "Comprendido"
def actualizarRetroReunionDiariaStatusCorrectoSM(request, id):
    status = "3"
    producto = get_object_or_404(MensajeRetroA, pk=id)
    producto.Status = status
    producto.save()

    msm = producto.Mensaje.id
    
    return redirect('Mensajes:retroAliReunionDiariaSM', msm)

# Mensaje de retroalimentacion Scrum Master en caso de seleccionar "No Comprendido" en la interfaz principal de Reunión de Retrospectiva del Sprint
def enviar_mensajeReunionDiariaSM(request, id):
    mensajes = MensajeReceptor.objects.filter(pk=id)

    if request.method == 'POST':
        form = retroAlimentacion_Forms(request.POST)
        if form.is_valid():

            for mensaje in mensajes:
                # Crear un MensajeRetroA con los datos del mensaje
                dato = MensajeRetroA(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum, 
                    Mensaje=mensaje.Mensaje, # hereda por defecto el id del mensaje
                    Receptor=mensaje.Emisor, # hereda el emisar del mensaje, NO el del request.user
                    Emisor=mensaje.Receptor,
                    # Sprint=mensaje.Sprint,
            
                )
            
            emisorid = dato.Emisor

            proyecto = dato.Proyecto
            eventoScrum = dato.EventoScrum
            mensajeid = dato.Mensaje
            receptorid = dato.Receptor
            descripcion = form.cleaned_data['Descripcion']

            mensaje = MensajeRetroA(Proyecto=proyecto, EventoScrum=eventoScrum, Mensaje=mensajeid, Receptor=receptorid,
                                   Descripcion=descripcion, Status=5, Emisor=emisorid)

            mensaje.save()
            return redirect(to='Mensajes:mensajeReunionDiaria')  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacion_Forms()
    return render(request, 'Mensajes/ScrumMaster/retroAlimentacion.html', {'form': form})

def mensajes_Retro_Reunion_Diaria_SM(request, id):
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    recibidos = MensajeReceptor.objects.filter(Receptor=empleado)

    mensaje = Mensaje.objects.get(pk=id)
    retroalimentacion = MensajeRetroA.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="4") & Q(Mensaje=mensaje))
    msmEnviado = MensajeRetroA.objects.filter(Q(Emisor=empleado) & Q(Contestacion__isnull=True))

    data = {
        'mensajes':retroalimentacion,
        'enviado':msmEnviado
    }

    return render(request, 'Mensajes/ScrumMaster/retroAlimentacionReunioDiaria.html', data)


# ------------------------------- Reunion diaria - Empleado (Mensajes recibidos) ----------------
# Listar registros de retrospectiva del sprint
def listaReunionDiariaEmpleado(request):
    if request.user.is_authenticated:
        usuario = request.user
        empleado = Empleado.objects.get(Usuario=usuario)

        # Obtener los proyectos en los que el empleado participa
        proyectos = EmpleadoProyecto.objects.filter(Empleado=empleado).values_list('Proyecto', flat=True)
        # 🔥 Agregar todos los Sprints disponibles en esos proyectos
        sprints = Sprint.objects.filter(Proyecto__in=proyectos)

        #mensajes = MensajeReceptor.objects.filter(Q(Receptor=empleado) & Q(EventoScrum="4")& Q(Proyecto__in=proyectos)) # Evento - Reunion diaria
        mensajes = MensajeReceptor.objects.filter(
            Q(Receptor=empleado) & 
            Q(EventoScrum="4") & 
            Q(Proyecto__in=proyectos)
        ).annotate(
            mensaje_fecha_hora=F('Mensaje__FechaHora')  # Relación con el modelo Mensaje
        )
        data = {
            'form2':mensajes,
            'sprints': sprints,
        }

        user = request.user

        if user is not None:
            login(request, user)
            # Redirecciona al usuario dependiendo de su rol
            # if user.usuarioempleado.Roles.NombreRol == 'Developers':
            if user.usuarioempleado.Roles.NombreRol in ['Developers','Scrum Master']:
                return render(request, 'Scrum/Empleado/listaReunionDiaria.html', data)
            else:
                # si el usuario no es Developers se mostrara el siguiente mensaje
                return HttpResponse("No eres Developer")
        else:
        # Usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})

    else: 
        return HttpResponseRedirect(reverse('Scrum:Logout'))
    
def archivosReunionDiariaEmpleado(request, id): # id del Mensaje original
    mensaje = Mensaje.objects.get(pk=id)
    dato = m_Archivos.objects.filter(Mensaje=mensaje)

    data = {
        'form': dato
    }

    return render(request, 'Scrum/Empleado/archivosReunionDiaria.html', data)

# Mensaje de retroalimentacion Scrum Master en caso de seleccionar "Comprendido"
def actualizarRetroReunionDiariaStatusCorrectoEmpleado(request, id): # id del Mensaje de retroalimentación
    status = "3" #Aclarado y/o Comprendido
    producto = get_object_or_404(MensajeRetroA, pk=id)
    producto.Status = status
    producto.save()

    msm = producto.Mensaje.id
    
    return redirect('Mensajes:retroAliReunionDiariaEmpleado', msm)

# Listar asistentes por usuario y mensaje, Retrospectiva, Scrum Master
def lista_asistentes_reunion_diaria_Empleado(request, id): # id del Mensaje Original
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensaje = Mensaje.objects.get(pk=id)
    asistentes = AsistentesEventosScrum.objects.filter(Q(Usuario=empleado) & Q(EventoScrum="4") & Q(Mensaje=mensaje)) 

    data = {
        'form':asistentes
    }

    return render(request, 'Scrum/Empleado/listaAsistentesReunionDiaria.html', data)

class ActualizarAsistenteReunionDiariaEmpleado(LoginRequiredMixin, UpdateView):
    model = AsistentesEventosScrum
    template_name = 'Scrum/Empleado/editarAsistentePS.html'
    form_class = AsistentesPlaneacion_Forms
    success_url = reverse_lazy('Mensajes:mensajesReunionDiariaEmpleado')

# Crear comentarios para Reunion Diaria
# def crear_Comentarios_Reunion_Diaria_Empleado_OLD(request,id): # id del Mensaje original
#     mensajes = Mensaje.objects.filter(pk=id) # Recibe el id del mensaje origen
#     usuario = request.user
#     empleado = Empleado.objects.get(Usuario=usuario)

#     if request.method == 'POST':
#         form = reunionDiaria_Forms(request.POST)
#         if form.is_valid():
            
#             for mensaje in mensajes:
#                 # Crear un comentario con los datos del mensaje
#                 comentario = m_ReunionDiaria(
#                     Proyecto=mensaje.Proyecto,
#                     Mensaje=mensaje,
#                     Sprint=mensaje.Sprint,
#                 )
                
#             obstaculos = form.cleaned_data['ObstaculosPresentados']
#             plan = form.cleaned_data['PlanDiaSiguiente']
#             trabajoRealizado = form.cleaned_data['TrabajoRealizadoDiaAnterior']
#             proyecto = comentario.Proyecto
#             sprint = comentario.Sprint
#             mensaje_id = comentario.Mensaje
            
#             mensaje = m_ReunionDiaria(ObstaculosPresentados=obstaculos, Mensaje=mensaje_id, Emisor=empleado, Proyecto=proyecto,
#                                             Sprint=sprint, PlanDiaSiguiente=plan, TrabajoRealizadoDiaAnterior=trabajoRealizado)
#             mensaje.save()
#             return redirect('Mensajes:mensajesReunionDiariaEmpleado')  # Redirigir a la página de mensajes enviados
#     else:
#         form = reunionDiaria_Forms()
#     return render(request, 'Scrum/Empleado/crear_Comentario.html', {'form': form})
def crear_Comentarios_Reunion_Diaria_Empleado(request,id): # id del Mensaje original
    mensajes = Mensaje.objects.filter(pk=id) # Recibe el id del mensaje origen
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    # Busca si ya existe un comentario para este mensaje
    comentario_existente = None
    if mensajes.exists():
        #comentario_existente = m_ReunionDiaria.objects.filter(Mensaje=mensajes.first()).first()
        comentario_existente = m_ReunionDiaria.objects.filter(
            Mensaje=mensajes.first(),
            Emisor = empleado
            #Emisor__Usuario=request.user
        ).first()
    if request.method == 'POST':
        if comentario_existente:  # Si existe, se edita
            form = reunionDiaria_Forms(request.POST, instance=comentario_existente)
        else:  # Si no, se crea un nuevo comentario
            form = reunionDiaria_Forms(request.POST)

        if form.is_valid():
            comentario = form.save(commit=False)  # No guarda todavía
            comentario.Proyecto = mensajes.first().Proyecto
            comentario.Mensaje = mensajes.first()
            comentario.Sprint = mensajes.first().Sprint
            comentario.Emisor = empleado
            comentario.save()  # Guarda el formulario junto con los datos adicionales
            return redirect('Mensajes:mensajesReunionDiariaEmpleado')  # Redirigir a la página de mensajes enviados
    else:
        # Inicializa el formulario con los datos existentes o en blanco
        if comentario_existente:
            form = reunionDiaria_Forms(instance=comentario_existente)
        else:
            form = reunionDiaria_Forms()

    return render(request, 'Scrum/Empleado/crear_Comentario.html', {'form': form})
    
def listado_comentarios_reunion_diaria(request,id): # id del Mensaje original
        # Obtener todas las entradas de m_ReunionDiaria
    reuniones = m_ReunionDiaria.objects.filter(Mensaje__id=id)
    mensaje = get_object_or_404(Mensaje, pk=id) # Recibe el id del mensaje origen
    fecha_hora = mensaje.FechaHora
    # print(f"Mensaje__id: {id}")
    return render(request, 'Scrum/Empleado/ListadoComentariosReunionDiaria.html', {'reuniones': reuniones, 'fecha_hora': fecha_hora})
    #return redirect('Mensajes:mensajesReunionDiariaEmpleado')  # Redirigir a la página de mensajes enviados

# Mensaje de recibido Scrum Master en caso de seleccionar "Comprendido"
def statusCorrectoReunionDiariaEmpleado(request, id): #id del Mensaje Receptor
    status = "2" #Comprendido
    producto = get_object_or_404(MensajeReceptor, pk=id)
    producto.Status = status
    producto.save()
    
    return redirect(to='Mensajes:mensajesReunionDiariaEmpleado')

# Mensaje de retroalimentacion Empleado en caso de seleccionar "No Comprendido" en la interfaz principal de Reunión de Retrospectiva del Sprint
def enviar_mensajeReunionDiariaEmpleado(request, id): # id del Mensaje del Receptor
    mensajes = MensajeReceptor.objects.filter(pk=id)

    if request.method == 'POST':
        form = retroAlimentacion_Forms(request.POST)
        if form.is_valid():

            for mensaje in mensajes:
                # Crear un MensajeRetroA con los datos del mensaje
                dato = MensajeRetroA(
                    Proyecto=mensaje.Proyecto,
                    EventoScrum=mensaje.EventoScrum, 
                    Mensaje=mensaje.Mensaje, # hereda por defecto el id del mensaje
                    Receptor=mensaje.Emisor, # hereda el emisar del mensaje, NO el del request.user
                    Emisor=mensaje.Receptor,
                    # Sprint=mensaje.Sprint,
            
                )
            
            emisorid = dato.Emisor

            proyecto = dato.Proyecto
            eventoScrum = dato.EventoScrum
            mensajeid = dato.Mensaje
            receptorid = dato.Receptor
            descripcion = form.cleaned_data['Descripcion']

            mensaje = MensajeRetroA(Proyecto=proyecto, EventoScrum=eventoScrum, Mensaje=mensajeid, Receptor=receptorid,
                                   Descripcion=descripcion, Status=5, Emisor=emisorid) # Status=5 --> No Comprendido

            mensaje.save()
            return redirect(to='Mensajes:mensajesReunionDiariaEmpleado')  # Redirigir a la página de mensajes enviados
    else:
        form = retroAlimentacion_Forms()
    return render(request, 'Scrum/Empleado/retroAlimentacion.html', {'form': form})

def mensajes_Retro_Reunion_Diaria_Empleado(request, id): # id del Mensaje original
    usuario = request.user
    empleado = Empleado.objects.get(Usuario=usuario)
    mensaje = Mensaje.objects.get(pk=id)
    #print(f"usuario: {usuario}, empleado: {empleado}, mensaje_id: {id}, ")
    retroalimentacion = MensajeRetroA.objects.filter(Q(Emisor=empleado) & Q(EventoScrum="4") & Q(Mensaje=mensaje))

    data = {
        'mensajes':retroalimentacion,
    }

    return render(request, 'Scrum/Empleado/retroAlimentacionReunioDiaria.html', data)

# ------------------------------------------------ Experimentos y plantillas (No borrar)------------------------------------------------
# Eliminar archivos dentro de la sección de mensaje
def eliminar_archivo_refinamiento(request, id):
    producto = get_object_or_404(m_Archivos, id=id)
    producto.delete()
    msm = producto.Mensaje.id
    return redirect("Mensajes:enviarMensajes", msm, "1")

def eliminar_archivo_planeacion(request, id):
    producto = get_object_or_404(m_Archivos, id=id)
    producto.delete()
    msm = producto.Mensaje.id
    return redirect("Mensajes:enviarMensajePlaneacion", msm, "1")

def eliminar_archivo_revision(request, id):
    producto = get_object_or_404(m_Archivos, id=id)
    producto.delete()
    msm = producto.Mensaje.id
    return redirect("Mensajes:enviarMensajeRevision", msm, "1")

def eliminar_archivo_retrospectiva(request, id):
    producto = get_object_or_404(m_Archivos, id=id)
    producto.delete()
    msm = producto.Mensaje.id
    return redirect("Mensajes:enviarMensajeRetrospectiva", msm, "1")

def eliminar_archivo_reunion_diaria(request, id):
    producto = get_object_or_404(m_Archivos, id=id)
    producto.delete()
    msm = producto.Mensaje.id
    return redirect("Mensajes:enviarMensajeReunionDiaria", msm, "1")


# Pruebas para ver el pais del empleado
def testPais(request):
    # dato = m_ReunionDiaria.objects.all()
    dato2 = AsistentesEventosScrum.objects.all()
    #dato = MensajeRetroA.objects.filter(Receptor=request.user)
    #dato = MensajeRetroA.objects.filter(pk=id)
    data = {
        # 'form': dato,
        'form2':dato2
    }

    return render(request, 'Mensajes/ScrumMaster/pruebas.html', data)

# Lista de archivos disponibles para Revision del sprint - Scrum Master
def archivosRecibidosRevisionSM(request, id):
    mensaje = Mensaje.objects.get(pk=id)
    dato = m_Archivos.objects.filter(Mensaje=mensaje)

    data = {
        'form': dato
    }

    return render(request, 'Mensajes/ScrumMaster/archivosRevision.html', data)

# Lista de archivos disponibles para Planeacion del sprint - Scrum Master
def archivosRecibidosPlaneacionSM(request, id):
    mensaje = Mensaje.objects.get(pk=id)
    dato = m_Archivos.objects.filter(Mensaje=mensaje)

    data = {
        'form': dato
    }

    return render(request, 'Mensajes/ScrumMaster/archivosPlaneacion.html', data)

# Lista de archivos disponibles para Refinamiento del product backlog - Scrum Master
def archivosRecibidosRefinamientoSM(request, id):
    mensaje = Mensaje.objects.get(pk=id)
    dato = m_Archivos.objects.filter(Mensaje=mensaje)

    data = {
        'form': dato
    }

    return render(request, 'Mensajes/ScrumMaster/archivosRefinamiento.html', data)

# Lista de archivos disponibles para Refinamiento del product backlog - Empleado
def archivosRecibidosRefinamientoEmpleado(request, id):
    mensaje = Mensaje.objects.get(pk=id)
    dato = m_Archivos.objects.filter(Mensaje=mensaje)

    data = {
        'form': dato
    }

    return render(request, 'Scrum/Empleado/archivosRefinamiento.html', data)

# Lista de archivos disponibles para Planeacion del sprint - Empleado
def archivosRecibidosPlaneacionEmpleado(request, id): # id del Mensaje
    mensaje = Mensaje.objects.get(pk=id)
    dato = m_Archivos.objects.filter(Mensaje=mensaje)

    data = {
        'form': dato
    }

    return render(request, 'Scrum/Empleado/archivosPlaneacion.html', data)

# Lista de archivos disponibles para Revision del sprint - Empleado
def archivosRecibidosRevisionEmpleado(request, id): # id del Mensaje
    mensaje = Mensaje.objects.get(pk=id)
    dato = m_Archivos.objects.filter(Mensaje=mensaje)

    data = {
        'form': dato
    }

    return render(request, 'Scrum/Empleado/archivosRevision.html', data)

#def vistaHistoriasHU(request, id_sprint):
#def vistaHistoriasHU(request):
    # dato = MensajeRetroA.objects.filter(Receptor=request.user)
    #dato = MensajeRetroA.objects.filter(pk=id)
    #dato = HistoriaUsuario.objects.filter(Q(Estatus=4) & Q(Sprint=id_sprint)) # EN Sprint
    #dato = HistoriaUsuario.objects.filter(Estatus=4) # EN Sprint
    # dato = HistoriaUsuario.objects.all()
    #tarea = Tarea.objects.all()
    # hu = HistoriaUsuario.objects.filter(pk=id)
    # hu = HistoriaUsuario.objects.get(pk=id)
    # tarea = tareaAsignada.objects.filter(pk=2)
    # tarea = tareaAsignada.objects.all()

    # data = {
    #     'form': dato,
    #     #'tarea':tarea
    # }

    # return render(request, 'Mensajes/ProductOwner/plantillaHistoriasHU.html', data)

def plantillaHistoriasHU(request, id_sprint):
    dato = HistoriaUsuario.objects.filter(Q(Estatus__in= [5,6,7,8,9]) & Q(Sprint=id_sprint)) #HU 5= Divididas en Tareas, 6=EN progreso, 7= Completada, 8=Aceptada, 9=Incompleta
    #tarea = Tarea.objects.all()

    data = {
        'form': dato,
        #'tarea':tarea
    }

    pdf = render_to_pdf('Mensajes/ProductOwner/plantillaHistoriasHU.html', data)
    return HttpResponse(pdf, content_type='application/pdf')

def vistaEjecucionSprint(request, id_ReunionDiaria):
    #dato = HistoriaUsuario.objects.filter(Estatus=4) # En Sprint (son las mismas que estan dentro del modelo sprint_backlog)
    id_Sprint = ReunionDiaria.objects.get(id=id_ReunionDiaria).Sprint.id
    dato = HistoriaUsuario.objects.filter(Q(Sprint_id=id_Sprint) & Q(Estatus__in=[4, 5, 6])) # 4=En Sprint, 5=Divididas, 6=EN progreso (son las mismas que estan dentro del modelo sprint_backlog)
    tarea = Tarea.objects.all()
    tareaAvance = TareaAvance.objects.all()

    evento = get_object_or_404(Sprint, id=id_Sprint)

    # fecha_inicio = datetime.strptime('2023-05-01', '%Y-%m-%d')
    #fecha_limite = datetime.strptime('2023-05-17', '%Y-%m-%d')

    # Calcular la diferencia en días
    # diferencia_dias = (fecha_limite - fecha_inicio).days
    diferencia_dias = (evento.fechafinalsprint - evento.fechainiciosprint).days
    numero = diferencia_dias

    # sprintbacklog = sprint_Backlog.objects.all()

    data = {
        'form': dato,
        'tarea':tarea,
        'avance':tareaAvance,
        'diferencia_dias': diferencia_dias,
        # 'sprintbl': sprintbacklog
    }

    return render(request, 'Mensajes/ProductOwner/plantillaEjecucion.html', data)

# def vistaEjecucionSprintID(request, id_ReunionDiaria):
#     #dato = HistoriaUsuario.objects.filter(Estatus=4) # En Sprint (son las mismas que estan dentro del modelo sprint_backlog)
#     #modelo ReunionDiaria ?
#     id_Sprint = Mensaje.objects.get(id=id_ReunionDiaria).Sprint.id
#     id_Proyecto = Mensaje.objects.get(id=id_ReunionDiaria).Proyecto.id

#     #HU = HistoriaUsuario.objects.filter(Q(Sprint_id=id_Sprint) & Q(Estatus__in=[4, 5, 6])) # 4=En Sprint, 5=Divididas, 6=EN progreso (son las mismas que estan dentro del modelo sprint_backlog)
#     HU = HistoriaUsuario.objects.filter(Q(Sprint_id=id_Sprint) & Q(Proyecto_id = id_Proyecto)) # 4=En Sprint, 5=Divididas, 6=EN progreso (son las mismas que estan dentro del modelo sprint_backlog)

#     #dato = HistoriaUsuario.objects.filter(Estatus=4) # En Sprint (son las mismas que estan dentro del modelo sprint_backlog)
#     Query = f"""SELECT t.* 
#             FROM public.\"Scrum_tarea\" as t inner join public.\"Scrum_historiausuario\" as hu on
#             (t.\"HistoriaUsuario_id\" = hu.id 
#             ) inner join public.\"Scrum_sprint\" as sp on (
#                 hu.\"Sprint_id\" = sp.id
#             )
#             where
#             sp.id = {id_Sprint} and sp.\"Proyecto_id\" = {id_Proyecto}""" 
#     #and             hu.\"Estatus_id\" in (4,5,6)
#     tarea = Tarea.objects.raw(Query)
    
#     Query = f"""SELECT hu.id AS historia_id, hu.\"NumeroHU\" AS numero_hu, hu.nombre AS nombre_hu, t.id, t.nombre AS nombre_tarea, t.horasestimadas,
#             ta.id AS id_tarea_avance, ta.\"horasDedicadas\", ta.\"horasRestantes\", ta.\"horasReales\", sp.\"numerosprint\", hu.\"Estatus_id\",
#             ta.dia_1, ta.dia_2, ta.dia_3, ta.dia_4, ta.dia_5, ta.dia_6, ta.dia_7, ta.dia_8, ta.dia_9, ta.dia_10,
#             ta.dia_11, ta.dia_12, ta.dia_13, ta.dia_14, ta.dia_15, ta.dia_16, ta.dia_17, ta.dia_18, ta.dia_19, ta.dia_20,
#             ta.dia_21, ta.dia_22, ta.dia_23, ta.dia_24, ta.dia_25, ta.dia_26, ta.dia_27, ta.dia_28, ta.dia_29, ta.dia_30, ta.dia_31
#             FROM public."Scrum_historiausuario" as hu left join public."Scrum_tarea" as t on
#             (
#                 hu.id = t.\"HistoriaUsuario_id"
#             ) left join public.\"Scrum_tareaavance\" as ta on (
#                 t.id = ta.\"tarea_id\" and
#                 ta.\"HistoriaUsuario_id\" = hu.id and
#                 ta.\"horasDedicadas\" = 0
#             ) inner join public.\"Scrum_sprint\" as sp on (
#                 hu.\"Sprint_id\" = sp.id
#             )
#             where
#             sp.id = {id_Sprint} and
#             sp.\"Proyecto_id\" = {id_Proyecto}"""
    
#             #hu.\"Estatus_id\" in (4,5,6)""" % 

#     tareaAvance = TareaAvance.objects.raw(Query)
#     #print(f"Registro de tareasavance: {len(list(tareaAvance))}, {list(tareaAvance)}")

#     msm = Mensaje.objects.filter(pk=id_ReunionDiaria)
#     mensaje = get_object_or_404(Mensaje, id=id_ReunionDiaria)
#     sprint_id = mensaje.Sprint.id
#     dSprint = get_object_or_404(Sprint, id=sprint_id)
#     mes = Sprint.objects.filter(pk=sprint_id)

#     # Calcular la diferencia en días
#     # diferencia_dias = (fecha_limite - fecha_inicio).days
#     diferencia_dias = (dSprint.fechafinalsprint - dSprint.fechainiciosprint).days
#     numero = diferencia_dias

#     usuario = request.user
#     dEmpleado = Empleado.objects.filter(Usuario=usuario)

#     # sprintbacklog = sprint_Backlog.objects.all()
#     fechas = [dSprint.fechainiciosprint + timedelta(days=i) for i in range(diferencia_dias + 1)]
#     #print (f"fechas: {fechas}")
#     traduccion_meses = {
#         "January": "Enero", "February": "Febrero", "March": "Marzo",
#         "April": "Abril", "May": "Mayo", "June": "Junio",
#         "July": "Julio", "August": "Agosto", "September": "Septiembre",
#         "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
#     }

#     # Crear un diccionario para agrupar días por mes
#     meses = {}


#     for fecha in fechas:
#         #nombre_mes = fecha.strftime('%B')  # Obtener el nombre del mes en español
#         nombre_mes = traduccion_meses[fecha.strftime('%B')]
#         if nombre_mes not in meses:
#             meses[nombre_mes] = 0
#         meses[nombre_mes] += 1  # Contar los días en ese mes

#     # # Imprimir resultados
#     # for mes, cantidad in meses.items():
#     #     print(f"Mes: {mes}, Días: {cantidad}")
#     # print(f"mes: {meses}")
        

#     # Lista para almacenar la matriz
#     matriz_avance = []

#     # Iteramos sobre los resultados del Query (tareas de avance)
#     for tarea in tareaAvance:
#         fila = []
#         fila.append(tarea.historia_id) #Id de la Historia de Usuario
#         fila.append(tarea.id) #Id de la Tarea
#         # Iteramos sobre cada fecha del sprint
#         for i, fecha in enumerate(fechas, start=1):
#             # Comparar la fecha actual con los campos dia_1, dia_2, ..., dia_n
#             for j in range(1, 32):
#                 field_name = f'dia_{j}'
#                 # Usar getattr para obtener el valor del campo 'dia_n' del query
#                 valor_dia = getattr(tarea, field_name, '0/0')
#                 if fecha.day == j:
#                     # Si no hay valor (None), agregamos '0/0', sino tomamos el valor del campo
#                     if valor_dia is None:
#                         fila.append('0/0')
#                     else:
#                         fila.append(valor_dia)
    
#         # Añadir la fila a la matriz
#         matriz_avance.append(fila)

#     #print (f"matriz_avance: {matriz_avance}")
#     data = {
#             'form': HU,
#             'tarea':tarea,
#             'avance':tareaAvance,
#             'diferencia_dias': diferencia_dias,
#             'mensaje':msm,
#             'dEmpleado':dEmpleado,
#             'mes':mes,
#             'fechas':fechas,
#             'matriz_avance':matriz_avance,
#             'Sprint': dSprint,
#             'meses':meses, 
#             # 'dia':diaDedicado
#             # 'sprintbl': sprintbacklog
#     }

#     return render(request, 'Mensajes/ProductOwner/plantillaEjecucion2.html', data)


# def generar_pdf_y_guardar_archivo(mensaje, historiasBL, asistentes):
#     """
#     Genera el PDF del evento de refinamiento y lo guarda en m_Archivos.
#     """
#     data = {
#         'form': asistentes,
#         'form2': historiasBL,
#         'form3': [mensaje],
#     }
#     print(f"generar_pdf_y_guardar_archivo: {mensaje}")
#     pdf = render_to_pdf('Mensajes/ProductOwner/plantillaRefinamiento.html', data)

#     if pdf:
#         descripcion = f"{mensaje.EventoScrum.Descripcion} - {mensaje.FechaHora.strftime('%Y-%m-%d')}"
#         archivo_nombre = f"{slugify(descripcion)}.pdf"

#         nuevo_archivo = m_Archivos(
#             Descripcion=descripcion,
#             Proyecto=mensaje.Proyecto,
#             Mensaje=mensaje,
#         )
#         nuevo_archivo.Archivo.save(archivo_nombre, ContentFile(pdf.getvalue()), save=False)
#         nuevo_archivo.ArchivoObj = pdf.getvalue()
#         nuevo_archivo.save()


# # Product Owner, original
# def enviar_mensaje2(request, id, Accion):
#     idSms = Mensaje.objects.get(pk=id)
#     usuario = request.user.id
#     empleado = Empleado.objects.get(Usuario=usuario)
#     asistentes = AsistentesEventosScrum.objects.filter(Mensaje=idSms)
#     form3 = asistentes
#     if request.method == 'POST':
#         form = envAsistentesForms(request.POST)
#         if form.is_valid():
#             msm = Mensaje.objects.filter(pk=id)
#             mensaje = msm.first()
#             #mensajeid = mensaje
#             proyecto = mensaje.Proyecto
#             eventoScrum = mensaje.EventoScrum
#             #status = mensaje.Status
#             fecha = mensaje.FechaHora
#             #archivo = mensaje.archivo
#             DescripcionEventoScrum = mensaje.EventoScrum.Descripcion
#             FechaHoraReunion = m_RefinamientoProductBL.objects.get(Mensaje=id).FechaHora
#             NombreProyecto = mensaje.Proyecto.nombreproyecto

#             if Accion == 2:
#                 mensaje.Status = 2  # Enviado
#                 mensaje.FHUltimaMod = datetime.now()
#                 mensaje.save()

#             res = AsistentesEventosScrum.objects.filter(Mensaje=idSms)
#             Destinatarios = ""
#             for asistente in res:
#                 mensajeRecep = MensajeReceptor(
#                     Proyecto=proyecto, Mensaje=mensaje, Receptor=asistente.Usuario,
#                     EventoScrum=eventoScrum, Emisor=empleado, FHCreacion=fecha,
#                     Status="1" #, archivo=archivo
#                 )
#                 if Accion == 1:
#                     mensajeRecep.save()
#                 Destinatarios += f"{asistente.Usuario.Usuario.email}, "

#             Destinatarios = Destinatarios.rstrip(', ')
#             Archivos = m_Archivos.objects.filter(Mensaje=idSms)
#             FechaHoraFormateada = FechaHoraReunion.strftime('%d/%m/%Y %H:%M')
#             asunto = f"{DescripcionEventoScrum} {FechaHoraFormateada}"
#             Remitente = request.user.email
#             CuerpoMensaje = (
#                 f"Ceremonia: {DescripcionEventoScrum}\nProyecto: {NombreProyecto}\n"
#                 f"Reunión: {FechaHoraFormateada}\nDescripción: {mensaje.Descripcion}"
#             )
#             ListaDestinatarios = Destinatarios.split(",")

#             email = EmailMessage(subject=asunto, body=CuerpoMensaje, from_email=Remitente, to=ListaDestinatarios)

#             for arch in Archivos:
#                 archivo_binario = BytesIO(arch.ArchivoObj)
#                 email.attach(arch.Archivo.name, archivo_binario.read(), 'application/pdf')

#             if Accion == 2:
#                 email.send()

#             time.sleep(2)
#             return redirect('Mensajes:listaRefinamiento')
#     else:
#         if idSms.Status == '2':
#             MensajeAviso = get_object_or_404(Mensaje, pk=id)
#             messages.success(request, 'El mensaje ya fue enviado.')
#             return render(request, 'Scrum/MensajePantalla.html', {'mensaje': MensajeAviso, 'Ruta': '/listaRefinamiento'})
        
#         if idSms.ArchivosGenerados is not True:
#             # ✅ Obtener datos necesarios para generar el PDF
#             historiasBL = HistoriaUsuario.objects.filter(MensajeRPBL=id)
#             # ✅ Generar y guardar el PDF en m_Archivos
#             generar_pdf_y_guardar_archivo(idSms, historiasBL, asistentes)
#             idSms.ArchivosGenerados = True
#             idSms.save()#(update_fields=["ArchivosGenerados"])

#         form = envAsistentesForms
#         form2 = Mensaje.objects.filter(pk=id)
#         #form3 = AsistentesEventosScrum.objects.filter(Mensaje=idSms)
#         archivos = m_Archivos.objects.filter(Mensaje=idSms)

#     return render(request, 'Mensajes/ProductOwner/enviarMensaje.html', {
#         'form': form,
#         'form2': form2,
#         'form3': form3,
#         'archivos': archivos
#     })
       
# def enviar_mensaje2(request, id, Accion):
#     # mensaje = Mensaje.objects.filter(pk=id) 
#     idSms = Mensaje.objects.get(pk=id)
#     #IdProyecto = idSms.Proyecto
#     #receptor = User.objects.get(pk=5)
#     # emisor = request.user

#     usuario = request.user.id
#     empleado = Empleado.objects.get(Usuario=usuario)

#     if request.method == 'POST':

#         # form = MensajeForms(request.POST)
#         form = envAsistentesForms(request.POST)
#         if form.is_valid():
#             # idSms = Mensaje.objects.get(pk=id)
#             msm = Mensaje.objects.filter(pk=id)
            
#             contenido = msm.first()
#             mensaje=contenido
#             mensajeid = contenido
#             proyecto = contenido.Proyecto
#             eventoScrum = contenido.EventoScrum
#             status = contenido.Status
#             fecha = contenido.FechaHora
#             archivo = contenido.archivo
#             DescripcionEventoScrum = contenido.EventoScrum.Descripcion
#             FechaHoraReunion = m_RefinamientoProductBL.objects.get(Mensaje=id).FechaHora #contenido.m_RefinamientoProductBL.FechaHora
#             NombreProyecto = contenido.Proyecto.nombreproyecto

#             if Accion == 2:
#                 #Actualiza el status del mensaje enviado
#                 mensaje.Status = 2 #Enviado
#                 mensaje.FHUltimaMod = datetime.now()
#                 mensaje.save() #Actualiza  la BD

#             res = AsistentesEventosScrum.objects.filter(Mensaje=idSms)
#             Destinatarios = ""
#             for asistente in res:
#                 mensajeRecep = MensajeReceptor(Proyecto=proyecto, Mensaje=mensajeid, Receptor=asistente.Usuario, EventoScrum=eventoScrum, 
#                                           Emisor=empleado ,FHCreacion=fecha,Status="1", archivo=archivo)
#                 if Accion == 1:
#                     mensajeRecep.save()
#                 #messages.success(request,"Mensaje enviado con exito")
#                 Destinatarios = Destinatarios + str(asistente.Usuario.Usuario.email) + ', ' #"\"" + str(asistente.Usuario.Usuario.email) +  "\""+ ', '
                
#             Destinatarios = Destinatarios[:-2] #Elimina la última coma y espacio
#             #print(f"Destinatario: {Destinatarios}")

#             #Envía el correo
#             Archivos = m_Archivos.objects.filter(Mensaje=idSms)
#             #ArchivosAdjuntos=""

#             #Envío de correo
#             FechaHoraFormateada = FechaHoraReunion.strftime('%d/%m/%Y %H:%M')
#             asunto = DescripcionEventoScrum +  ' ' +  str(FechaHoraFormateada) #'Reunión de Refinamiento del Product Backlog' #form.cleaned_data['asunto']
#             Remitente = request.user.email
#             #print(f"Remitente: {Remitente}")
#             #destinatario = form.cleaned_data['destinatario']
#             CuerpoMensaje = "Ceremonia: " + DescripcionEventoScrum + '\r\n Proyecto: ' + NombreProyecto + '\r\n' + 'Reunión: ' +  str(FechaHoraFormateada) #'Reunión de Refinamiento del Product Backlog' #form.cleaned_data['mensaje']
#             CuerpoMensaje += '\r\nDescripción: ' +  mensaje.Descripcion
            
#             #archivo = request.FILES.get('archivo', None)
#             #Destinatarios = 'jmhernan@yahoo.com'
#             ListaDestinatarios = Destinatarios.split(",")
#             #print(f"ListaDestinatarios: {ListaDestinatarios}")
#             email = EmailMessage(
#                 subject=asunto,
#                 body=CuerpoMensaje,
#                 from_email=Remitente,  # Remitente
#                 to=ListaDestinatarios,
#             )   
#             for arch in Archivos:
#                 #print(f"archivo: {arch.Archivo}")
#                 #ArchivosAdjuntos = ArchivosAdjuntos  + "'"+str(arch.Archivo)+"'" + ','

#                 # Se convierte el contenido binario del archivo a un objeto BytesIO
#                 archivo_binario = BytesIO(arch.ArchivoObj)
#                  # Adjuntar el archivo al correo con el nombre original del archivo
#                 email.attach(arch.Archivo.name, archivo_binario.read(), 'application/pdf')
#                 #email.attach_file(str(arch.Archivo))
#                 #print(f"archivo: {arch.Archivo}")
#             #ArchivosAdjuntos = ArchivosAdjuntos[:-1]
#             #print(f"archivos adjuntos: {ArchivosAdjuntos}")

#             #email.attach_file(ArchivosAdjuntos)
#             if Accion == 2:
#                 email.send()
#             #messages.success(request,"Mensaje enviado con éxito")
#             #Fin Envío del correo
#             time.sleep(2)
#             return redirect('Mensajes:listaRefinamiento')  # Redirigir a la página de mensajes enviados
#     else:
#         if idSms.Status == '2': #El mensaje ya fue enviado
#             print(f"idSms.Status2 : {idSms.Status} ")
#             # Obtener el mensaje
#             MensajeAviso = get_object_or_404(Mensaje, pk=id)
#             # Mandar un mensaje que será mostrado en el template
#             messages.success(request, 'El mensaje ya fue enviado.')
#             # Renderizar el template y pasar los datos necesarios
#             return render(request, 'Scrum/MensajePantalla.html', {'mensaje': MensajeAviso, 'Ruta': '/listaRefinamiento'})

#             # # Datos que deseas enviar al template del modal
#             # title = "Aviso"
#             # content = "El mensaje ya fue enviado."
            
#             # # Si quieres devolver el HTML del modal
#             # return render(request, 'Scrum/MensajePantalla.html', {'title': title, 'content': content})

        
#         form = envAsistentesForms
#         form2 = Mensaje.objects.filter(pk=id)
#         form3 = AsistentesEventosScrum.objects.filter(Mensaje=idSms)
#         idmensaje = Mensaje.objects.get(pk=id)
#         archivos = m_Archivos.objects.filter(Mensaje=idmensaje)
#     return render(request, 'Mensajes/ProductOwner/enviarMensaje.html', {'form': form, 'form2':form2, 'form3':form3, 'archivos':archivos})
