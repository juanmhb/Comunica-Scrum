from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, render
from datetime import date
from .forms import *
from django.views.generic import View,TemplateView, ListView, UpdateView, CreateView, DeleteView,FormView
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from datetime import timedelta, date
import logging
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.db.models import Sum
from django.db.models import Max

logger = logging.getLogger(__name__)


def exit(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('/Login')

def index(request):
    if request.user.is_authenticated:

        try:
            jefeproyecto = JefeProyecto.objects.get(Usuario=request.user)
        except JefeProyecto.DoesNotExist:
            try:
                empleado = Empleado.objects.get(Usuario=request.user)
                user = request.user
                print(f"Usuario autenticado: {user.username}")
                print(f"Usuario Rol: {user.usuarioempleado.Roles.NombreRol}")
                if user is not None:
                    login(request, user)
                    # Redirecciona al usuario dependiendo de su rol
                    if user.usuarioempleado.Roles.NombreRol == 'Product Owner':
                        return render(request, 'Mensajes/ProductOwner/base.html')
                    elif user.usuarioempleado.Roles.NombreRol == 'Scrum Master':
                        return render(request, 'Mensajes/ScrumMaster/base.html')
                    elif user.usuarioempleado.Roles.NombreRol == 'Developers':
                        return render(request, 'Scrum/Empleado/base.html')
                    else:
                        return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})
                else:
                # Usuario o contraseña incorrectos
                    return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})
                # return render(request,'Scrum/base.html')
            except Empleado.DoesNotExist:
                return HttpResponseRedirect(reverse('Scrum:Logout'))
            return render(request,'Scrum/Empleado/base.html')
        #print(f"JefeP. Usuario autenticado:")
        return render(request,'Scrum/base.html')
        
    return HttpResponseRedirect(reverse('Scrum:Login'))

def Login(request):
    
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('Scrum:index'))
        
    if request.method=='POST':
        form=AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            nombre_usuario=form.cleaned_data.get("username")
            contra=form.cleaned_data.get("password")
            
            usuario=authenticate(username=nombre_usuario, password=contra)
            if usuario is not None:
                login(request, usuario)
                if usuario.usuarioempleado.Roles.NombreRol == 'Product Owner':
                    return redirect('Scrum:index')
                elif usuario.usuarioempleado.Roles.NombreRol == 'Scrum Master':
                    return redirect('Scrum:index')
                elif usuario.usuarioempleado.Roles.NombreRol == 'Developers':
                    return redirect('Scrum:index')
                else:
                    return redirect('Scrum:index')
            else:
                return render(request, 'Scrum/Login.html',{"form":form})
                # return redirect('Scrum:index')      
        else:
            return render(request, 'Scrum/Login.html',{"form":form})
            # return redirect('Scrum:index')
    else:
        form=AuthenticationForm()
        return render(request, 'Scrum/Login.html',{"form":form})


def Registro(request):
    data = {
        'form': CustomUserCreationForm(),
        'form2':EmpleadoForm(),
        'LOGO_SISTEMA': settings.LOGO_SISTEMA
    }
    if request.method=='POST':
        formulario = CustomUserCreationForm(data = request.POST)
        formularioEmpleado = EmpleadoForm(data = request.POST)
        if formulario.is_valid() and formularioEmpleado.is_valid():
            formulario.save()
            user = authenticate(request, username=formulario.cleaned_data["username"], password=formulario.cleaned_data["password1"])
            try: 
                alumno = Empleado.objects.create(rfc=formularioEmpleado.cleaned_data["rfc"],telefono=formularioEmpleado.cleaned_data["telefono"] ,cedulaprofesional=formularioEmpleado.cleaned_data["cedulaprofesional"],Pais=formularioEmpleado.cleaned_data["Pais"],Idioma=formularioEmpleado.cleaned_data["Idioma"],Usuario=user)
            except 	IntegrityError:
                user.delete()
                return render(request, 'Scrum/registro.html',{'error_message':'Ya Existe El Correo Electronico'})
            # login(request, user)
            return HttpResponseRedirect(reverse('Scrum:index'))
        data['form'] = formulario
        data['form2'] = formularioEmpleado
    return render(request, 'Scrum/registro.html', data)




# ------------------------------------------------------------------CRUD Proyectos----------------------------------------------------------------------
class ListadoProyectos(LoginRequiredMixin, View):
    model = Proyecto
    template_name = 'Scrum/proyectos.html'

    def get_queryset(self):
        return self.model.objects.filter(JefeProyecto__Usuario =self.request.user)
    
    def get_context_data(self, **kwargs):
        contexto = {}
        contexto['proyectos']=self.get_queryset()
        return contexto
    
    def get(self, request, *args, **kwargs):    
        return render(request, self.template_name, self.get_context_data())

class ListadoProyectosEmpleados(LoginRequiredMixin, View):
    model = Proyecto
    template_name = 'Scrum/Empleado/proyectos.html'

    # print(f"proyectos: {model}")

    def get_queryset(self):
        # print(f"user: {self.request.user}")
        return self.model.objects.filter(DetalleProyecto__Empleado__Usuario =self.request.user)
    
    def get_context_data(self, **kwargs):
        contexto = {}
        if self.request.user.usuarioempleado.Roles.NombreRol == 'Product Owner':
            base_template = "Mensajes/ProductOwner/base.html"
        else:
            base_template = "Scrum/Empleado/base.html"
        contexto['base_template'] = base_template
        contexto['proyectos']=self.get_queryset()
        return contexto
    
    def get(self, request, *args, **kwargs):    
        return render(request, self.template_name, self.get_context_data())


class CrearProyecto(LoginRequiredMixin, CreateView):
    model = Proyecto
    template_name = 'Scrum/registrar_proyecto.html'
    form_class = ProyectoForm
    success_url = reverse_lazy('Scrum:listar_proyetos')

    def form_valid(self, form):
        form.instance.JefeProyecto = JefeProyecto.objects.get(Usuario=self.request.user)
        return super().form_valid(form)


class ActualizarProyecto(LoginRequiredMixin, UpdateView):
    # model = Proyecto
    # template_name = 'Scrum/detalle_proyecto.html'
    # form_class = ProyectoForm
    # success_url = reverse_lazy('Scrum:listar_proyetos')
    model = Proyecto
    template_name = 'Scrum/detalle_proyecto.html'
    form_class = ProyectoForm
    def get_success_url(self):
        usuario_actual = self.request.user

        # print("Ini.jmhb.ProyectoForm" , ProyectoForm,  "Fin.jmhb")
         # print("Ini.jmhb.ProyectoForm.data" , ProyectoForm.as_p,  "Fin.jmhb")
   
        if usuario_actual.usuarioempleado.Roles.NombreRol == 'Project Manager': 
            return reverse_lazy('Scrum:listar_proyectos')
        else:
            return reverse_lazy('Scrum:listar_proyectos_Empleado')

class EliminarProyecto(LoginRequiredMixin, DeleteView):
    model = Proyecto
    success_url = reverse_lazy('Scrum:listar_proyetos')


# ------------------------------------------------------------------CRUD ProductBacklog----------------------------------------------------------------------

def ListadoProductBacklog(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    Estatus = list(EstatusHistoria.objects.all())[0]
    # jmhb HistoriasProductBacklog = HistoriaUsuario.objects.filter(Proyecto__pk=pk, Estatus=Estatus)
    HistoriasProductBacklog = HistoriaUsuario.objects.filter(Proyecto__pk=pk)
    pkBacklog = HistoriaUsuario.objects.filter(Proyecto__pk=pk).first()  # Usamos .first() en lugar de .get() para evitar errores si no hay coincidencias
    return render(request, 'Scrum/gestion_proyectos.html', {
        'HistoriasProductBacklog': HistoriasProductBacklog,
        'pkBacklog': pkBacklog,
        'pk': pk,
        'proyecto': proyecto
    })


# ------------------------------------------------------------------CRUD Historias de Usuario----------------------------------------------------------------------

class CrearHistoriaUsuario(LoginRequiredMixin, CreateView):
    model = HistoriaUsuario
    template_name = 'Scrum/registrar_HistriasUsuarios.html'
    form_class = HistoriaUsuarioForm
    # success_url = reverse_lazy('Scrum:listar_proyectos')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        form.instance.Proyecto = Proyecto.objects.get(pk=self.kwargs['pk'])
        #Obtiene el número máximo de la HU, basado en un proyecto particular
        max_valor = HistoriaUsuario.objects.filter(Proyecto=self.kwargs['pk']).aggregate(Max('NumeroHU'))
        print(f"Valor Máximo HU: {max_valor}")
        if max_valor['NumeroHU__max'] is None: 
            SiguienteHU = 'HU001'
        else:
            SiguienteHU = max_valor['NumeroHU__max'][-3:] #Obtiene los 3 'ultimos dígitos
            SiguienteHU = 'HU' + str(int(SiguienteHU) + 1).rjust(3,'0') #Rellena con CEROS 0

        #print(f"Valor Máximo HU2: {SiguienteHU}")
        form.instance.NumeroHU = SiguienteHU
        form.instance.Estatus = list(EstatusHistoria.objects.all())[0]
        return super().form_valid(form)

    def get_success_url(self):
         return reverse('Scrum:productbacklog', kwargs={'pk': self.kwargs['pk']})


class EliminarHistoriaUsuario(LoginRequiredMixin, DeleteView):
    model = HistoriaUsuario
    # success_url = reverse_lazy('Scrum:listar_proyetos')

    def get_success_url(self):
         return reverse('Scrum:productbacklog', kwargs={'pk': self.object.Proyecto.pk})


class ActualizarHistoriaUsuario(LoginRequiredMixin, UpdateView):
    model = HistoriaUsuario
    template_name = 'Scrum/detalle_historiausuario.html'
    form_class = HistoriaUsuarioForm
 
    def get_success_url(self):
         return reverse('Scrum:productbacklog', kwargs={'pk': self.object.Proyecto.pk})
    

    
class ActualizarHistoriaUsuarioSprint(LoginRequiredMixin, UpdateView):
    model = HistoriaUsuario
    template_name = 'Scrum/detalle_historiausuario_sprint.html'
    form_class = HistoriaUsuarioForm
 
    def get_success_url(self):
          return reverse('Scrum:listar_sprint_Historias', kwargs={'pk': self.object.Sprint.pk})
    
class EliminarHistoriaUsuarioSprint(LoginRequiredMixin, DeleteView):
    model = HistoriaUsuario
    # success_url = reverse_lazy('Scrum:listar_proyetos')

    def get_success_url(self):
         return reverse('Scrum:listar_sprint_Historias', kwargs={'pk': self.object.Sprint.pk})

# ------------------------------------------------------------------CRUD Sprint----------------------------------------------------------------------

def ListadoSprint(request, pk):
    Sprints = Sprint.objects.filter(Proyecto__pk=pk)
    # pkBacklog= ProductBacklog.objects.get(Proyecto__pk=pk)
    return render(request,'Scrum/gestion_sprint.html', {'Sprints': Sprints,'pk':pk})

def ListadoSprintEmpleados(request, pk):
    Sprints = Sprint.objects.filter(Proyecto__pk=pk,SprintSprintBacklogs__Empleado__Usuario=request.user)
    # pkBacklog= ProductBacklog.objects.get(Proyecto__pk=pk)
    return render(request,'Scrum/Empleado/gestion_sprint.html', {'Sprints': list(set(Sprints)),'pk':pk})

def ListadoSprintHistorias(request, pk):
    sprint = get_object_or_404(Sprint, pk=pk)
    HistoriasProductBacklog = HistoriaUsuario.objects.filter(Sprint__pk=pk)
    pkProyecto = sprint.Proyecto.pk

    return render(request, 'Scrum/gestion_proyectos.html', {
        'HistoriasProductBacklog': HistoriasProductBacklog,
        'pk': pkProyecto,
        'Sprint': sprint
    })

class CrearSprint(LoginRequiredMixin,CreateView):
    model = Sprint
    template_name = 'Scrum/registrar_sprint.html'
    form_class = SprintForm
    # success_url = reverse_lazy('Scrum:listar_proyectos')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs['pk']
        return context

    def form_valid(self,form):
        form.instance.Proyecto= Proyecto.objects.get(pk=self.kwargs['pk'])
        # print(pk)
        form.instance.Estatus = list(EstatusSprint.objects.all())[0]
        return super().form_valid(form)

    def get_success_url(self):
         return reverse('Scrum:listar_sprint', kwargs={'pk': self.kwargs['pk']})


class EliminarSprint(LoginRequiredMixin, DeleteView):
    model = Sprint
    # success_url = reverse_lazy('Scrum:listar_proyetos')

    def get_success_url(self):
         return reverse('Scrum:listar_sprint', kwargs={'pk': self.object.Proyecto.pk})


class ActualizarSprint(LoginRequiredMixin, UpdateView):
    model = Sprint
    template_name = 'Scrum/detalle_sprint.html'
    form_class = SprintForm
 
    def get_success_url(self):
         return reverse('Scrum:listar_sprint', kwargs={'pk': self.object.Proyecto.pk})


def AsignarHistriasSprint(request, pk):
    sprint = get_object_or_404(Sprint, pk=pk)
    pkProyecto = sprint.Proyecto
    form = SprintHistoriasUsuarioForm(pk=pkProyecto.pk)
    
    if request.method == 'POST':
        form = SprintHistoriasUsuarioForm(data=request.POST, pk=pkProyecto.pk)
        if form.is_valid():
            listH = request.POST.getlist("Historias")
            try:
                status = EstatusHistoria.objects.all()
                for historia_id in listH:
                    updateHistoria = get_object_or_404(HistoriaUsuario, pk=historia_id)
                    updateHistoria.Sprint = sprint
                    updateHistoria.Estatus = status[1]
                    updateHistoria.save()
            except IntegrityError:
                return render(request, 'ingles/registro.html', {'error_message': 'Ya Existe El Correo Electronico'})
            return HttpResponseRedirect(reverse('Scrum:listar_sprint', kwargs={'pk': pkProyecto.pk}))
    
    data = {
        'form': form,
        'pk': pk
    }
    return render(request, 'Scrum/AsignarHistorias.html', data)

# ------------------------------------------------------------------CRUD Tarea----------------------------------------------------------------------

def ListadoTareas(request, pk):
    try:
        
        historia_usuario = HistoriaUsuario.objects.get(pk=pk)
       
        Tareas = Tarea.objects.filter(HistoriaUsuario=historia_usuario)
        pkProyecto = historia_usuario.Proyecto.pk if historia_usuario.Proyecto else None

        context = {
            'Tareas': Tareas,
            'pk': pkProyecto,
            'historia_usuario' : historia_usuario
        }

        return render(request, 'Scrum/gestion_tareas.html', context)

    except HistoriaUsuario.DoesNotExist:
        return render(request, 'Scrum/gestion_tareas.html', {'error': 'La historia de usuario no existe'})


@login_required
def ListadoTareasSprint(request, pk): #Listado de las tareas de una HU específica
    try:
        historia_usuario = HistoriaUsuario.objects.get(pk=pk)
        tareas = Tarea.objects.filter(HistoriaUsuario__pk=pk)
        proyecto_pk = historia_usuario.Proyecto.pk if historia_usuario.Proyecto else None
        sprint_pk = historia_usuario.Sprint.pk if historia_usuario.Sprint else None

        context = {
            'Tareas': tareas,
            'historia_usuario': historia_usuario,
            'pk': proyecto_pk,  # Esto es para el projectbacklog
            'Sprint': True,
            'pksprint': sprint_pk
        }
        return render(request, 'Scrum/gestion_tareas_sprint.html', context)
    except HistoriaUsuario.DoesNotExist:
        return HttpResponseNotFound("Historia de Usuario no encontrada")
    

def obtener_datos_tareas(historia_usuario):
    tareas = Tarea.objects.filter(HistoriaUsuario=historia_usuario)
    datos_tareas = []

    for tarea in tareas:
        tarea_avances = TareaAvance.objects.filter(tarea=tarea)

        for tarea_avance in tarea_avances:
            sprint = tarea_avance.HistoriaUsuario.sprint_backlog_set.first().Sprint if tarea_avance.HistoriaUsuario and tarea_avance.HistoriaUsuario.sprint_backlog_set.exists() else None
            datos_tareas.append({
                'tarea': tarea.nombre,
                'fecha_avance': tarea_avance.fechaAvance,
                'horas_dedicadas': tarea_avance.horasDedicadas,
                'horas_restantes': tarea_avance.horasRestantes,
                'sprint': sprint.nombre if sprint else 'N/A'
            })

    return datos_tareas


@login_required
def tareas_avance(request, sprint_id=None, historia_usuario_id=None):
    #print("jmhb, tareas avance2")
    if sprint_id is not None and historia_usuario_id is not None:
        try:
            historia_usuario = HistoriaUsuario.objects.get(pk=historia_usuario_id)
            tareas = Tarea.objects.filter(HistoriaUsuario__pk=historia_usuario_id)
            sprint = Sprint.objects.get(pk=sprint_id)
            proyecto_pk = historia_usuario.Proyecto.pk if historia_usuario.Proyecto else None
            sprint_pk = sprint.pk if sprint else None

            # Calcular los días hábiles del sprint
            fechainicio = sprint.fechainiciosprint
            fechafin = sprint.fechafinalsprint or date.today()
              
            # Asegurarse de que la fecha de inicio no sea después de la fecha de fin
            if fechainicio > fechafin:
                raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")

            # Calcular la diferencia de días entre las dos fechas, devuelve un objeto timedelta que contiene el número total de días entre ambas fechas
            delta = fechafin - fechainicio

            # Generar una lista de fechas de los días hábiles (excluyendo fines de semana), desde la fecha de inicio hasta la fecha final del Sprint
            dias_habiles = [fechainicio + timedelta(days=i) for i in range(delta.days + 1)
                            if (fechainicio + timedelta(days=i)).weekday() < 5]

            # Imprimir o usar el número de días hábiles
            #print(f"Días hábiles del sprint: {len(dias_habiles)}, dias_habiles: {dias_habiles}")

            # Obtener registros de TareaAvance para cada tarea y cada día hábil
            datos_tareas = []
            for tarea in tareas:
                tarea_avances = TareaAvance.objects.filter(
                    HistoriaUsuario=historia_usuario,
                    tarea=tarea
                )

                if tarea_avances.exists():
                    tarea_avance = tarea_avances.first()
                else:
                    tarea_avance = TareaAvance.objects.create(
                        HistoriaUsuario=historia_usuario,
                        tarea=tarea,
                        horasDedicadas=0,
                        horasRestantes=tarea.horasestimadas,
                        fechaAvance=timezone.now().date()
                    )

                avances = []
                horas_reales = tarea_avance.horasReales if tarea_avance else 0
                
                for dia in dias_habiles:
                    field_name = f'dia_{dia.day}'
                    
                   
                    avance = getattr(tarea_avance, field_name, '0/0')
                    #print(f"Avance: {avance}, field_name: {field_name}")
                    avances.append(avance)
                
                datos_tareas.append({
                    'nombre': tarea.nombre,
                    'horas_estimadas': tarea.horasestimadas,
                    'horas_reales': horas_reales,
                    'avances': avances,
                    'tarea_avance_pk': tarea_avance.pk if tarea_avance else None,
                })
                #print(f"datos_tareas: {datos_tareas}")
            context = {
                'Tareas': datos_tareas,
                'historia_usuario': historia_usuario,
                'pk': proyecto_pk,
                'Sprint': True,
                'pksprint': sprint_pk,
                'dias_habiles': dias_habiles,
            }

            return render(request, 'Scrum/tareas_avance.html', context)

        except HistoriaUsuario.DoesNotExist:
            return HttpResponseBadRequest("La Historia de Usuario especificada no existe.")

    else:
        return HttpResponseBadRequest("Se requieren tanto sprint_id como historia_usuario_id para esta vista.")


class ActualizarTareaAvance(LoginRequiredMixin, UpdateView):
    model = TareaAvance
    form_class = TareaAvanceForm
    template_name = 'Scrum/detalle_tarea_avance.html'

    def form_valid(self, form):
        # Primero, guarda los cambios en el registro actual
        response = super().form_valid(form)
        
        lista_dias_horas = form.cleaned_data['lista_dias_horas']
        #Obtiene todos registros en base
        tarea_avance_id = self.kwargs.get('pk', None)
        Tarea=TareaAvance.objects.get(pk=tarea_avance_id)
        tarea_id = Tarea.tarea_id
        self.ModTarAv = TareaAvance.objects.filter(tarea_id=tarea_id)
        

        HayRegistro = False
        for dia, horas_dedicadas, horas_restantes in lista_dias_horas:
            if horas_dedicadas != 0:
                for tareaAv in self.ModTarAv:
                    if tareaAv.fechaAvance == dia: # Se deben actualizar las horas dedicadas en la BD del registro en cuestión
                        tareaAv.horasDedicadas = horas_dedicadas
                        tareaAv.save() #Actualiza  la BD, de los registros que ya están en la BD
                        HayRegistro = True
                if not HayRegistro: #Se agrega el registro
                    new_instance = form.save(commit=False)
                    new_instance.id = None
                    new_instance.horasDedicadas = horas_dedicadas
                    new_instance.fechaAvance = dia
                    new_instance.save()
                HayRegistro = False
        # Redirige a la vista que muestra el listado de tareas sin el duplicado
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tarea_avance'] = self.object
        return context

    def get_success_url(self):
        tarea = self.object.tarea
        return reverse_lazy('Scrum:tareas_avance', kwargs={'sprint_id': tarea.HistoriaUsuario.Sprint.pk, 'historia_usuario_id': tarea.HistoriaUsuario.pk})
    
class EliminarTareaAvance(LoginRequiredMixin, DeleteView):
    model = TareaAvance
    def get_success_url(self):
         return reverse('Scrum:tareas_avance', kwargs={'pk': self.object.HistoriaUsuario.pk})
    
              
class CrearTarea(LoginRequiredMixin,CreateView):
    model = Tarea
    template_name = 'Scrum/registrar_tarea.html'
    form_class = TareaForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs['pk']
        return context

    def form_valid(self,form):
        form.instance.HistoriaUsuario= HistoriaUsuario.objects.get(pk=self.kwargs['pk'])
        form.instance.Proyecto= form.instance.HistoriaUsuario.Proyecto #HistoriaUsuario.Proyecto #.objects.get(pk=self.kwargs['pk'])
        # print(pk)
        print(list(EstatusTarea.objects.all())[0])
        form.instance.Estatus = list(EstatusTarea.objects.all())[0] # Tarea=pendiente
        return super().form_valid(form)

    def get_success_url(self):
         return reverse('Scrum:listar_tareas', kwargs={'pk': self.object.HistoriaUsuario.pk})



class CrearTareaSprint(LoginRequiredMixin, CreateView):
    model = Tarea
    template_name = 'Scrum/registrar_tarea_sprint.html'
    form_class = TareaForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']  
        context['pksprint'] = self.kwargs.get('pksprint', None)  
        return context

    def form_valid(self, form):
        try:
            # Obtener la Historia de Usuario asociada
            historia_usuario = HistoriaUsuario.objects.get(pk=self.kwargs['pk'])
            form.instance.HistoriaUsuario = historia_usuario
            form.instance.Estatus = EstatusTarea.objects.first()

            # Guardar la tarea sin empleados ni proyecto todavía
            tarea = form.save(commit=False)
            tarea.Proyecto = historia_usuario.Proyecto  # Asigna el proyecto relacionado

            # Asignar el empleado seleccionado, si hay alguno
            empleado = form.cleaned_data.get('Empleado')
            if empleado:
                tarea.Empleado = empleado
            else:
                tarea.Empleado = None

            tarea.save()  # Guardar la tarea con toda la información

            # Imprimir el contenido de cleaned_data para depuración
            print("Cleaned Data:", form.cleaned_data)

            return super().form_valid(form)
        except HistoriaUsuario.DoesNotExist:
            return HttpResponseNotFound("Historia de Usuario no encontrada")

    def get_success_url(self):
        return reverse_lazy('Scrum:listar_tareas_sprint', kwargs={'pk': self.kwargs['pk']})

    def get_form(self, form_class=None):
        form = super(CrearTareaSprint, self).get_form(form_class)
        if self.request.method == 'POST':
            rol_id = self.request.POST.get('Rol')
            if rol_id:
                form.fields['Empleado'].queryset = Empleado.objects.filter(Roles_id=rol_id)
            else:
                form.fields['Empleado'].queryset = Empleado.objects.none()
        else:
            # Inicialmente, no mostrar ningún empleado
            form.fields['Empleado'].queryset = Empleado.objects.none()
        return form




def obtener_empleados_por_rol(request, rol_id):
    empleados = Empleado.objects.filter(Roles_id=rol_id).select_related('Usuario').values('id', 'Usuario__first_name', 'Usuario__last_name')
    empleados_list = [{'id': emp['id'], 'nombre': f"{emp['Usuario__first_name']} {emp['Usuario__last_name']}"} for emp in empleados]
    return JsonResponse({'empleados': empleados_list})


class EliminarTarea(LoginRequiredMixin, DeleteView):
    model = Tarea
    def get_success_url(self):
         return reverse('Scrum:listar_tareas', kwargs={'pk': self.object.HistoriaUsuario.pk})


class EliminarTareaSprint(LoginRequiredMixin, DeleteView):
    model = Tarea
    def get_success_url(self):
         return reverse('Scrum:listar_tareas_sprint', kwargs={'pk': self.object.HistoriaUsuario.pk})


class ActualizarTarea(LoginRequiredMixin, UpdateView):
    model = Tarea
    template_name = 'Scrum/detalle_tarea.html'
    form_class = TareaForm
 
    def get_success_url(self):
         return reverse('Scrum:listar_tareas', kwargs={'pk': self.object.HistoriaUsuario.pk})

class ActualizarTareaSprint(LoginRequiredMixin, UpdateView):
    model = Tarea
    template_name = 'Scrum/detalle_tarea_sprint.html'
    form_class = TareaForm

    def get_success_url(self):
        return reverse_lazy('Scrum:listar_tareas_sprint', kwargs={'pk': self.object.HistoriaUsuario.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()  # Asegúrate de que la instancia está siendo pasada
        return kwargs

    

    
class ActualizarTareaEmpleado(LoginRequiredMixin, UpdateView):
    model = Tarea
    template_name = 'Scrum/Empleado/detalle_tarea.html'
    form_class = TareaEmpleadoForm
 
    def get_success_url(self):
         return reverse('Scrum:listar_sprintbacklog', kwargs={'pk': self.object.HistoriaUsuario.Sprint.pk})
    

# ----------------------------------------------------------------- TABLERO KANBAN -------------------------------------------------------------------------

@login_required
def tablero_kanban(request, pk):
    try:
        historia_usuario = HistoriaUsuario.objects.get(pk=pk)
        tareas = Tarea.objects.filter(HistoriaUsuario__pk=pk)

        for tarea in tareas:
            tarea_kanban, created = Tareas_kanban.objects.get_or_create(
                tarea=tarea,
                defaults={'estado': 'Pendiente', 'horasDedicadas': 0}  
            )
            if created:
                tarea_kanban.save()

        for tarea_kanban in Tareas_kanban.objects.filter(tarea__HistoriaUsuario__pk=pk):
            ultimo_avance = TareaAvance.objects.filter(
                tarea=tarea_kanban.tarea, HistoriaUsuario=historia_usuario
            ).order_by('-fechaAvance').first()
            
            if ultimo_avance:
                tarea_kanban.horasDedicadas = ultimo_avance.horasDedicadas
                tarea_kanban.horasRestantes = ultimo_avance.horasRestantes
            else:
                tarea_kanban.horasDedicadas = 0
                tarea_kanban.horasRestantes = 0
            
            tarea_kanban.save()

        tareas_kanban = Tareas_kanban.objects.filter(tarea__HistoriaUsuario__pk=pk)
        total_horas_dedicadas = sum(tarea_kanban.horasDedicadas for tarea_kanban in tareas_kanban)

        proyecto_pk = historia_usuario.Proyecto.pk if historia_usuario.Proyecto else None
        sprint_pk = historia_usuario.Sprint.pk if historia_usuario.Sprint else None

        context = {
            'tareas': tareas_kanban,
            'historia_usuario': historia_usuario,
            'pk': proyecto_pk,
            'Sprint': True,
            'pksprint': sprint_pk,
            'total_horas_dedicadas': total_horas_dedicadas
        }
        return render(request, 'Scrum/tablero_kanban.html', context)
    except HistoriaUsuario.DoesNotExist:
        return HttpResponseNotFound("Historia de Usuario no encontrada")



@csrf_exempt
@login_required
def actualizar_estado_tarea(request, tarea_id, nuevo_estado):
    if request.method == 'PUT':
        if nuevo_estado not in ['Pendiente', 'En Proceso', 'Completada']:
            return JsonResponse({'success': False, 'message': 'Estado no válido'}, status=400)

        try:
            tarea = Tareas_kanban.objects.get(pk=tarea_id)
        except Tareas_kanban.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Tarea no encontrada'}, status=404)

        tarea.estado = nuevo_estado
        tarea.save()

        if nuevo_estado == 'Completada':
            hoy = timezone.now().date()

            # Obtener el último registro de avance de tarea
            tarea_avances = TareaAvance.objects.filter(
                tarea=tarea.tarea,
                HistoriaUsuario=tarea.tarea.HistoriaUsuario
            ).order_by('-fechaAvance')

            if tarea_avances.exists():
                # Obtener el último registro (más reciente)
                tarea_avance = tarea_avances.first()
                fecha_avance_dia = hoy.day  

                
                dia_field_name = f'dia_{fecha_avance_dia}'

                # Verificar si el campo existe en el modelo 
                if hasattr(tarea_avance, dia_field_name):
                    
                    horas_restantes = tarea.horasRestantes
                    tarea.horasDedicadas += horas_restantes
                    tarea.horasRestantes = 0

                    # Actualizar el campo del día actual
                    setattr(tarea_avance, dia_field_name, f'{horas_restantes}/0')
                else:
                    return JsonResponse({'success': False, 'message': 'Campo de día no encontrado'}, status=400)
                
                tarea_avance.fechaAvance = hoy
                tarea_avance.horasDedicadas = tarea.horasDedicadas
                tarea_avance.horasRestantes = 0
                tarea_avance.save()
                print("Se ha actualizado un registro existente en la tabla TareaAvance.")  # Mensaje de confirmación

            else:
                # Si no existe ningún registro, crear uno nuevo
                horas_restantes = tarea.horasRestantes
                tarea.horasDedicadas += horas_restantes
                tarea.horasRestantes = 0

                TareaAvance.objects.create(
                    tarea=tarea.tarea,
                    HistoriaUsuario=tarea.tarea.HistoriaUsuario,
                    horasDedicadas=tarea.horasDedicadas,
                    horasRestantes=0,
                    fechaAvance=hoy,
                    **{f'dia_{hoy.day}': f'{horas_restantes}/0'}
                )
           
            print("Se ha creado un nuevo registro en la tabla TareaAvance.")  # Mensaje de confirmación

            
            tarea.save()
            
        return JsonResponse({'success': True, 'taskId': f'task-{tarea.id}'})

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)






# ------------------------------------------------------------------CRUD SprintBacklog----------------------------------------------------------------------



# class ActualizarSprintBacklog(LoginRequiredMixin, UpdateView):
#     model = SprintBacklog
#     template_name = 'Scrum/detalle_sprintbacklog.html'
#     form_class = SprintBacklogForm(pk=8)


#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["pk"] = self.kwargs['pk']
#         return context

#     def get_success_url(self):
#          return reverse('Scrum:listar_tareas_sprint', kwargs={'pk': self.object.Tarea.HistoriaUsuario.pk})


def ActualizarSprintBacklog(request,pk):
    # proyecto = Proyecto.objects.get(pk=pk)
    data = {
        'form': SprintBacklogForm(pk=8),
        'pk':pk
    }
    if request.method=='POST':
        formulario = EmpleadoProyectoForm(data = request.POST,pk=8)
        # if formulario.is_valid():
        sprintbacklog=SprintBacklog.objects.get(pk=pk)
        print(request.POST['Empleado'])
        sprintbacklog.Empleado = Empleado.objects.get(pk=request.POST['Empleado'])
        sprintbacklog.save()
        return HttpResponseRedirect( reverse('Scrum:listar_tareas_sprint',kwargs={'pk': sprintbacklog.Tarea.HistoriaUsuario.pk}))

    return render(request, 'Scrum/detalle_sprintbacklog.html', data)


class ListadoSprintBacklogEmpleado(LoginRequiredMixin, View):
    model = SprintBacklog
    template_name = 'Scrum/Empleado/gestion_tareas.html'

    def get_queryset(self):
        return self.model.objects.filter(Empleado__Usuario =self.request.user,Tarea__HistoriaUsuario__Sprint__pk=self.kwargs['pk']).order_by('Sprint')
    
    def get_context_data(self, **kwargs):
        contexto = {}
        contexto['Tareas']=self.get_queryset()
        contexto['pk']=Sprint.objects.get(pk=self.kwargs['pk']).Proyecto.pk
        return contexto
    
    def get(self, request, *args, **kwargs):    
        return render(request, self.template_name, self.get_context_data())


# ------------------------------------------------------------------CRUD  Reuniones Diarias----------------------------------------------------------------------

def ListadoReuniones(request, pk):
    ReunionesDiarias = ReunionDiaria.objects.filter(Sprint__pk=pk)
    pkProyecto = Sprint.objects.get(pk=pk).Proyecto.pk
    return render(request,'Scrum/gestion_reuniondiaria.html', {'ReunionesDiarias': ReunionesDiarias,'pk':pkProyecto,'pkSprint':pk})


class ListadoReunionesEmpleado(LoginRequiredMixin, View):
    model = ReunionDiaria
    template_name = 'Scrum/Empleado/gestion_reuniondiaria.html'

    def get_queryset(self):
        return self.model.objects.filter(Sprint__pk=self.kwargs['pk']).order_by('Sprint')
    
    def get_context_data(self, **kwargs):
        contexto = {}
        contexto['ReunionesDiarias']=self.get_queryset()
        contexto['pk']=Sprint.objects.get(pk=self.kwargs['pk']).Proyecto.pk
        contexto['pkSprint']=self.kwargs['pk']
        return contexto
    
    def get(self, request, *args, **kwargs):    
        return render(request, self.template_name, self.get_context_data())

class EliminarReunionDiaria(LoginRequiredMixin, DeleteView):
    model = ReunionDiaria

    def get_success_url(self):
         return reverse('Scrum:listar_reuniones', kwargs={'pk': self.object.Sprint.pk})


class ActualizarReunionDiaria(LoginRequiredMixin, UpdateView):
    model = ReunionDiaria
    template_name = 'Scrum/detalle_reuniondiaria.html'
    form_class = ReunionDiariaForm
 
    def get_success_url(self):
         return reverse('Scrum:listar_reuniones', kwargs={'pk': self.object.Sprint.pk})


class CrearReunionDiaria(LoginRequiredMixin,CreateView):
    model = ReunionDiaria
    template_name = 'Scrum/crear_reuniondiaria.html'
    form_class = ReunionDiariaForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs['pk']
        return context

    def form_valid(self,form):
        form.instance.Sprint= Sprint.objects.get(pk=self.kwargs['pk'])
        today = date.today()        
        form.instance.fecha = today
        return super().form_valid(form)

    def get_success_url(self):
         return reverse('Scrum:listar_reuniones', kwargs={'pk': self.object.Sprint.pk})


# ------------------------------------------------------------------CRUD  Progreso----------------------------------------------------------------------
def ListadoProgreso(request, pk):
    list_progreso = Progreso.objects.filter(ReunionDiaria__pk=pk)
    return render(request,'Scrum/detalle_reunionprogreso.html', {'list_progreso': list_progreso,'pk':pk})


class ListadoProgresoEmpleado(LoginRequiredMixin, View):
    model = Progreso
    template_name = 'Scrum/Empleado/gestion_progreso.html'

    def get_queryset(self):
        return self.model.objects.filter(ReunionDiaria__pk=self.kwargs['pk'],SprintBacklog__Empleado__Usuario=self.request.user)
    
    def get_context_data(self, **kwargs):
        contexto = {}
        Reunion = ReunionDiaria.objects.get(pk=self.kwargs['pk'])
        contexto['list_progreso']=self.get_queryset()
        contexto['pk']=Reunion.Sprint.Proyecto.pk
        contexto['pksprint']=Reunion.Sprint.pk
        return contexto
    
    def get(self, request, *args, **kwargs):    
        return render(request, self.template_name, self.get_context_data())



class ActualizarProgresoEmpleado(LoginRequiredMixin, UpdateView):
    model = Progreso
    template_name = 'Scrum/Empleado/detalle_progreso.html'
    form_class = ProgresoEmpleadoForm
 
    def get_success_url(self):
         return reverse('Scrum:listar_progreso_empleado', kwargs={'pk': self.object.ReunionDiaria.pk})



# ------------------------------------------------------------------CRUD  Empleado----------------------------------------------------------------------

def AsignarEmpleados(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    
    # Obtener empleados asignados y disponibles
    assigned_employees = Empleado.objects.filter(DetalleEmpleado__Proyecto=proyecto)
    available_employees = Empleado.objects.exclude(DetalleEmpleado__Proyecto=proyecto)
    
    data = {
        'form': EmpleadoProyectoForm(pk=proyecto.pk),
        'pk': pk,
        'assigned_employees': assigned_employees,
        'available_employees': available_employees
    }
    
    if request.method == 'POST':
        formulario = EmpleadoProyectoForm(data=request.POST, pk=proyecto.pk)
        if formulario.is_valid():
            listE = request.POST.getlist("EmpleadoProyecto")
            try:
                for empleado in listE:
                    object_empleado = Empleado.objects.get(pk=empleado)
                    EmpleadoProyecto.objects.create(Empleado=object_empleado, Proyecto=proyecto)
            except IntegrityError:
                return render(request, 'Scrum/Asignar_empleados.html', {'error_message': 'Ya Existe El Correo Electronico'})
            return HttpResponseRedirect(reverse('Scrum:listar_proyetos'))

    return render(request, 'Scrum/Asignar_empleados.html', data)