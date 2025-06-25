from django.urls import  path
from .views import *
from . import  views
from django.contrib.auth.decorators import login_required

from .views import burndown_sprint

app_name = 'Scrum'

urlpatterns = [
    path('', views.index, name='index'),
    path('Login/',views.Login,name='Login'),
    path('Registro/',views.Registro,name='Registro'),
    path('exit/', views.exit, name='exit'),   

    # URL PROYECTOS 
    path('listar_proyectos/', ListadoProyectos.as_view(), name = 'listar_proyectos'),
    path('listar_proyectos_Empleado/', ListadoProyectosEmpleados.as_view(), name = 'listar_proyectos_Empleado'),
    path('crear_proyectos/', CrearProyecto.as_view(), name='crear_proyectos'),
    path('editar_proyecto/<int:pk>', ActualizarProyecto.as_view() , name = 'editar_proyecto'),
    path('eliminar_proyecto/<int:pk>', EliminarProyecto.as_view() , name = 'eliminar_proyecto'),


    # URL PRODUCTBACKLOG
    path('productbacklog/<int:pk>', login_required(ListadoProductBacklog), name = 'productbacklog'),
    path('crear_historiausuario/<int:pk>/', CrearHistoriaUsuario.as_view(), name = 'crear_historiausuario'),
    path('eliminar_historiausuario/<int:pk>', EliminarHistoriaUsuario.as_view() , name = 'eliminar_historiausuario'),
    path('editar_historiausuario/<int:pk>', ActualizarHistoriaUsuario.as_view() , name = 'editar_historiausuario'),

    path('listar_sprint_Empleado/<int:pk>', login_required(ListadoSprintEmpleados), name = 'listar_sprint_Empleado'),
   

    # URL SPRINT
    path('listar_sprint/<int:pk>', login_required(ListadoSprint), name = 'listar_sprint'),
    path('crear_sprint/<int:pk>/', CrearSprint.as_view(), name = 'crear_sprint'),
    path('eliminar_sprint/<int:pk>', EliminarSprint.as_view() , name = 'eliminar_sprint'),
    path('editar_sprint/<int:pk>', ActualizarSprint.as_view() , name = 'editar_sprint'),
    path('asignarhistorias_sprint/<int:pk>', login_required(AsignarHistoriasSprint), name = 'asignarhistorias_sprint'),
    path('burndown_sprint/<int:sprint_id>/', burndown_sprint, name='burndown_sprint'),
    path('burndown_desarrollador/<int:sprint_id>/', burndown_desarrollador, name='burndown_desarrollador'),

    path('listar_sprint_Historias/<int:pk>', login_required(ListadoSprintHistorias), name = 'listar_sprint_Historias'),
    path('editar_historiausuario_sprint/<int:pk>', ActualizarHistoriaUsuarioSprint.as_view() , name = 'editar_historiausuario_sprint'),
    path('eliminar_historiausuario_sprint/<int:pk>', EliminarHistoriaUsuarioSprint.as_view() , name = 'eliminar_historiausuario_sprint'),
    

    # URL TAREA
   path('listar_tareas/<int:pk>', login_required(ListadoTareas), name = 'listar_tareas'),
   path('crear_tarea/<int:pk>/', CrearTarea.as_view(), name = 'crear_tarea'),
   path('eliminar_tarea/<int:pk>', EliminarTarea.as_view() , name = 'eliminar_tarea'),
   path('editar_tarea/<int:pk>', ActualizarTarea.as_view() , name = 'editar_tarea'),
    
   path('editar_tarea_Empleado/<int:pk>', ActualizarTareaEmpleado.as_view() , name = 'editar_tarea_Empleado'),

    #URL TAREAS AVANCE
    path('tareas_avance/<int:sprint_id>/<int:historia_usuario_id>/', views.tareas_avance, name='tareas_avance'),
    path('actualizar_tarea_avance/<int:pk>/', ActualizarTareaAvance.as_view(), name='actualizar_tarea_avance'),
    path('eliminar_tarea_avance/<int:pk>/', EliminarTareaAvance.as_view(), name='eliminar_tarea_avance'),

    #URL TAREAS SPRINT
    path('listar_tareas_sprint/<int:pk>/', login_required(ListadoTareasSprint), name = 'listar_tareas_sprint'),
    path('crear_tarea_Sprint/<int:pk>/', CrearTareaSprint.as_view(), name = 'crear_tarea_Sprint'),
    path('eliminar_tarea_Sprint/<int:pk>', EliminarTareaSprint.as_view() , name = 'eliminar_tarea_Sprint'),
    path('editar_tarea_Sprint/<int:pk>', ActualizarTareaSprint.as_view() , name = 'editar_tarea_Sprint'),
    path('obtener_empleados_por_rol/<int:rol_id>/', views.obtener_empleados_por_rol, name='obtener_empleados_por_rol'),


    # URL  SPRINTBACKLOG
    path('editar_sprintbacklog/<int:pk>', ActualizarSprintBacklog , name = 'editar_sprintbacklog'),
    path('listar_sprintbacklog/<int:pk>', ListadoSprintBacklogEmpleado.as_view() , name = 'listar_sprintbacklog'),

    
    # Tablero Kanban
    path('tablero_kanban/<int:pk>/', tablero_kanban, name='tablero_kanban'),
    path('actualizar_estado_tarea/<int:tarea_id>/<str:nuevo_estado>/', actualizar_estado_tarea, name='actualizar_estado_tarea'),


    # URL  REUNIONES DIARIAS
    path('listar_reuniones/<int:pk>', login_required(ListadoReuniones), name = 'listar_reuniones'),
    path('listar_reuniones_empleado/<int:pk>', ListadoReunionesEmpleado.as_view(), name = 'listar_reuniones_empleado'),
    path('eliminar_reunion/<int:pk>', EliminarReunionDiaria.as_view() , name = 'eliminar_reunion'),
    path('editar_reunion/<int:pk>', ActualizarReunionDiaria.as_view() , name = 'editar_reunion'),
    path('crear_reunion/<int:pk>/', CrearReunionDiaria.as_view(), name = 'crear_reunion'),
    
    # URL  REUNIONES DIARIAS
    path('listar_progreso/<int:pk>', login_required(ListadoProgreso), name = 'listar_progreso'),
    path('listar_progreso_empleado/<int:pk>', ListadoProgresoEmpleado.as_view() , name = 'listar_progreso_empleado'),
    path('editar_progreso_empleado/<int:pk>', ActualizarProgresoEmpleado.as_view() , name = 'editar_progreso_empleado'),

    # URL  EMPLEADOS
    path('asignar_empleados/<int:pk>', login_required(AsignarEmpleados), name = 'asignar_empleados'),



]