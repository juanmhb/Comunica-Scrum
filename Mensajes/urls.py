from django.urls import  path
from .views import *
from . import  views
from django.contrib.auth.decorators import login_required

app_name = 'Mensajes'

urlpatterns = [
# -------------------------------- Refinamiento del product backlog -----------------------------
    # path('', views.index, name='index'),
    path('listaRefinamiento', login_required(listaRefinamientoProductBL), name='listaRefinamiento'),
    # path('crearRefinamiento/<id>', login_required(crear_Refinamiento), name='crearRefinamiento'), obsoleto
    path('crearRefinamiento/', login_required(crear_Refinamiento), name='crearRefinamiento'),
    path('editarMensaje/<int:pk>', ActualizarMensaje.as_view(), name='editarMensaje'),
    path('eliminarMensaje/<id>', login_required(eliminar_Mensaje), name='eliminarMensaje'),

    # Asistentes Evento SCRUM
    # path('crearAsistente/', login_required(crear_Asistente), name='crearAsistente'),
    path('crearAsistente/<id>', login_required(crear_Asistente), name='crearAsistente'),
    path('listaAsistentes/<id>', login_required(lista_asistentes_por_mensaje), name='listaAsistentes'),
    path('editarAsistente/<int:pk>', ActualizarAsistente.as_view(), name='editarAsistente'),
    path('eliminarAsistente/<id>', login_required(eliminar_Asistente), name='eliminarAsistente'),

    # Historias de usuario, Refinamiento del product backlog, product owner
    path('listaHistoriasBL/<id_Mensaje>', login_required(listaHistoriaUsuariosBL), name='listaHistoriasBL'), # Refinamiento BL
    path('editarHistoriaBL/<int:pk>', ActualizarHistoriaUsuarioBL.as_view(), name='editarHistoriaBL'), # Refinamiento BL
    path('refinarHistoriaBL/<int:id>/<int:id_Mensaje>/', login_required(historiasRefinada), name='refinarHistoriaBL'), # Refinar historia BL
    path('cancelarHistoriaBL/<id>/', login_required(cancelarHistoria), name='cancelarHistoriaBL'), # Cancelar historia general
    path('cancelarHistoriaRef/<id>/', login_required(cancelarHistoriaBL), name='cancelarHistoriaRef'), # Cancelar historia refinadada BL
    # Planeacion Sprint
    path('listaHistoriasPlaneacionSprint/<id>/', login_required(listaHistoriaUsuariosPlaneacionSprint), name='listaHistoriasPlaneacionSprint'), # Planeacion Sprint
    path('agregarHistoriaPS/<id>/', login_required(historiasEnSprint), name='agregarHistoriaPS'), # En sprint
    path('editarHistoriaPlaneacionSprint/<int:pk>', ActualizarHistoriaUsuarioPlaneacionSprint.as_view(), name='editarHistoriaPlaneacionSprint'), # Planeacion Sprint
    path('cancelarHistoriaPlaneacion/<id>/', login_required(cancelarHistoria2), name='cancelarHistoriaPlaneacion'), # Cancelar historia general
    path('cancelarHistoriaPS/<id>/', login_required(cancelarHistoriaPS), name='cancelarHistoriaPS'), # Cancelar historia refinadada BL
    path('listaHUdivididas/<id>/', login_required(listaHUdivididas), name='listaHUdivididas'), # HU divididas

    # Plantilla generada para refinamiento
    path('vistaRefinamiento/<id>', login_required(vistaRefinamiento), name='vistaRefinamiento'),
    path('refinamientoPDF/<id>', login_required(plantillaRefinamiento), name='refinamientoPDF'),

    # Enviar mensaje product BL
    path('enviarMensaje/<id>', login_required(enviar_mensaje), name='enviarMensaje'),
    # path('mi_vistaChafa/', views.mi_vistaChafa, name='mi_vistaChafa'),

    # Recibir mensajes Refinamiento del product backlog
    path('recibirMensajeScrumMaster/', login_required(mensajes_recibidosScrumMaster), name='recibirMensajeScrumMaster'), # Scrum Master
    path('archivosRefinamientoSM/<id>', login_required(archivosRecibidosRefinamientoSM), name='archivosRefinamientoSM'), # archivos refinamiento Scrum Master
    path('recibirMensajeEmpleado/', login_required(mensajes_recibidosEmpleado), name='recibirMensajeEmpleado'), # Empleado
    path('archivosRefinamientoEmpleado/<id>', login_required(archivosRecibidosRefinamientoEmpleado), name='archivosRefinamientoEmpleado'), # archivos refinamiento Empleado

    # Mensajes de Retroalimentacion, refinamiento
    path('retroAProductOwner/<id>/', login_required(mensajes_RetroAlimentacion), name='retroAProductOwner'), # Product Owner
    path('enviarRetroAProductOwner/<id>/', login_required(enviar_mensajeBL), name='enviarRetroAProductOwner'), # Product Owner
    path('vistaRetroAProductOwner/<id>/', login_required(vistaRetroAlimentacionBL), name='vistaRetroAProductOwner'), # Product Owner
    path('retroAScrumMaster/<id>', login_required(enviar_mensajeRetroScrumMaster), name='retroAScrumMaster'), # Scrum Master
    
    path('retroAliScrumMasterBL/<id>', login_required(mensajes_recibidosRetroScrumMaster), name='retroAliScrumMasterBL'), # Srum Master
    path('retroAliEmpleado/<id>', login_required(enviar_mensajeRetroEmpleado), name='retroAliEmpleado'), # Empleado
    
    path('retroAliEmpleadoBL/<id>', login_required(mensajes_recibidosRetroEmpleado), name='retroAliEmpleadoBL'), # Empleado

    # Plantilla generada para el mensaje de retroalimentacion
    path('plantillaRetroBL/<id>/', login_required(plantillaRetroAlimentacionBL), name='plantillaRetroBL'),

# ----------------------------------------- Planeacion Sprint --------------------------------------
    # Planeacion Sprint, Product Owner
    path('vistaPlaneacionSprint/<id>/', views.vistaPlaneacionSprint, name='vistaPlaneacionSprint'), # Beta
    path('listaPlaneacionSprint/',login_required(listaPlaneacionSprint), name='listaPlaneacionSprint'),
    # path('crearPlaneacionSprint/<id>', login_required(crear_PlaneacionSprint), name='crearPlaneacionSprint'), # Opcion 1, obsoleto
    path('crearPlaneacionSprint/', login_required(crear_PlaneacionSprint5), name='crearPlaneacionSprint'),
    path('editarPlaneacionSprint/<int:pk>', ActualizarReunionPlaneacionSprint.as_view(), name='editarPlaneacionSprint'),
    path('eliminarPlaneacionSprint/<id>', login_required(eliminar_PlaneacionSprint), name='eliminarPlaneacionSprint'),

    # Asistentes Planeacion Sprint, Product owner
    path('crearAsistentePlaneacion/<id>', login_required(crear_Asistente_Planeacion), name='crearAsistentePlaneacion'), # BETA
    path('listaAsistentesPlaneacion/<id>', login_required(lista_asistentes_por_planeacion), name='listaAsistentesPlaneacion'),
    path('editarAsistentePlaneacion/<int:pk>', ActualizarAsistentePlaneacion.as_view(), name='editarAsistentePlaneacion'),
    path('eliminarAsistentePlaneacion/<id>', login_required(eliminar_AsistentePlaneacion), name='eliminarAsistentePlaneacion'),

    # Renderizar planeacion del sprint a PDF, product owner
    path('plantillaPlaneacionSprint/<id>/', login_required(plantillaPlaneacionSprint), name='plantillaPlaneacionSprint'),

    # Enviar mensaje de Planeacion del Sprint, Product Owner
    path('enviarMensajePlaneacion/<id>', login_required(enviar_mensaje_Planeacion), name='enviarMensajePlaneacion'),
    path('enviarRetroPlaneacion/<id>/', login_required(enviar_mensajePS), name='enviarRetroPlaneacion'), # Contestacion

    # Recibir mensaje de retralimentacion de planeacion del sprint, product owner
    path('retroPlaneacionSprintP/', login_required(mensajes_RetroAlimentacionPlaneacion), name='retroPlaneacionSprintP'), # Product Owner

    # Recibir mensajes Reunion de planeacion del sprint, Scrum Master
    path('mensajePlaneacionScrumMaster/', login_required(listaPlaneacionSprintScrumMaster), name='mensajePlaneacionScrumMaster'), # Scrum Master

    # Mensajes de Retroalimentacion, planeacion del sprint, Scrum master
    path('retroAPlaneacionScrumMaster/<id>', login_required(enviar_mensajeRetroPlaSprintScrumMaster), name='retroAPlaneacionScrumMaster'),
    path('retroAliScrumMasterPlaneacion/<id>', login_required(mensajes_PlaneacionRetroScrumMaster), name='retroAliScrumMasterPlaneacion'), # Srum Master

    # Recibir mensajes Reunion de planeacion del sprint, Empleado
    path('mensajePlaneacionEmpleado/', login_required(listaPlaneacionSprintEmpleado), name='mensajePlaneacionEmpleado'),
    path('archivosPlaneacionEmpleado/<id>', login_required(archivosRecibidosPlaneacionEmpleado), name='archivosPlaneacionEmpleado'), # archivos planeacion

    # Mensajes de Retroalimentacion, planeacion del sprint, Empleado
    path('retroAPlaneacionEmpleado/<id>', login_required(enviar_mensajeRetroPlaSprintEmpleado), name='retroAPlaneacionEmpleado'), #  en caso de seleccionar "No comprendido" en la interfaz principal
    path('retroAliEmpleadoPlaneacion/<id>', login_required(mensajes_PlaneacionRetroEmpleado), name='retroAliEmpleadoPlaneacion'),

    # Plantilla generada para el mensaje de retroalimentacion
    path('plantillaRetroPS/<id>/', login_required(plantillaRetroAlimentacionPS), name='plantillaRetroPS'),

# -------------------------------------- REUNION DE REVISIÓN DEL SPRINT -----------------------------------------------------
    path('vistaRevisionSprint/<id>/', login_required(vistaRevisionSprint), name='vistaRevisionSprint'),
    path('listaRevisionSprint/',login_required(listaRevisionSprint), name='listaRevisionSprint'),
    path('editarRevisionSprint/<int:pk>', ActualizarRevision.as_view(), name='editarRevisionSprint'),
    path('eliminarRevisionSprint/<id>', login_required(eliminar_revision), name='eliminarRevisionSprint'),
    # Sub lista Sprint
    path('subListaRevisionSprint/', login_required(subListaRevisionSprint), name='subListaRevisionSprint'),
    path('crearSubRevisionSprint/<id>/', login_required(crear_RevisionSprint), name='crearSubRevisionSprint'),

    # Asistentes Planeacion Sprint, Product owner
    path('crearAsistenteRevision/<id>', login_required(crear_Asistente_Revision), name='crearAsistenteRevision'),
    path('listaAsistentesRevision/<id>', login_required(lista_asistentes_por_revision), name='listaAsistentesRevision'),
    path('editarAsistenteRevision/<int:pk>', ActualizarAsistenteRevision.as_view(), name='editarAsistenteRevision'),
    path('eliminarAsistenteRevision/<id>', login_required(eliminar_asistente_revision), name='eliminarAsistenteRevision'),

    # Enviar mensaje de Revision del Sprint, Product Owner
    path('enviarMensajeRevision/<id>', login_required(enviar_mensaje_Revision), name='enviarMensajeRevision'),
    path('enviarRetroRevision/<id>/', login_required(enviar_mensajeRS), name='enviarRetroRevision'), # Contestacion

    # Recibir mensaje de retralimentacion de revisión del sprint, product owner
    path('retroRevisionSprint/', login_required(mensajes_RetroAlimentacionRevision), name='retroRevisionSprint'),

    # Renderizado a PDF
    path('plantillaRevisionSprint/<id>/', login_required(PlantillaRevisionSprint), name='plantillaRevisionSprint'),

    # Recibir mensajes Reunion de revision del sprint, Scrum Master
    path('mensajeRevisionScrumMaster/', login_required(listaRevisionSprintScrumMaster), name='mensajeRevisionScrumMaster'), # Scrum Master
    path('archivosPlaneacionSM/<id>', login_required(archivosRecibidosPlaneacionSM), name='archivosPlaneacionSM'), # archivos planeacion
    path('archivosRevisionSM/<id>', login_required(archivosRecibidosRevisionSM), name='archivosRevisionSM'), # archivos revision

    # Mensajes de Retroalimentacion, planeacion del sprint, Scrum master
    path('retroARevisionScrumMaster/<id>', login_required(enviar_mensajeRetroRevisionSprintSM), name='retroARevisionScrumMaster'),
    path('retroAliScrumMasterRevision/<id>', login_required(mensajes_RevisionRetroScrumMaster), name='retroAliScrumMasterRevision'),

    # Recibir mensajes Reunion de revision del sprint, Empleado
    path('mensajeRevisionEmpleado/', login_required(listaRevisionSprintEmpleado), name='mensajeRevisionEmpleado'),
    path('archivosRevisionEmpleado/<id>', login_required(archivosRecibidosRevisionEmpleado), name='archivosRevisionEmpleado'), # archivos Revision

    # Mensajes de Retroalimentacion, planeacion del sprint, Empleado
    path('retroARevisionEmpleado/<id>', login_required(enviar_mensajeRetroRevisionSprintEmpleado), name='retroARevisionEmpleado'),
    path('retroAliEmpleadoRevision/<id>', login_required(mensajes_RevisionRetroEmpleado), name='retroAliEmpleadoRevision'),

    # Plantilla generada para el mensaje de retroalimentacion
    path('plantillaRetroRS/<id>/', login_required(plantillaRetroAlimentacionRS), name='plantillaRetroRS'),

# -------------------------------------- REUNION DE RETROSPECTIVA DEL SPRINT -----------------------------------------------------
    path('vistaRestrospectiva/<id>/', login_required(vistaRetrospectivaSprint), name='vistaRestrospectiva'),
    path('listaRetrospectivaSprint/',login_required(listaRetrospectivaSprint), name='listaRetrospectivaSprint'),
    path('editarRetrospectiva/<int:pk>', ActualizarRetrospectiva.as_view(), name='editarRetrospectiva'),
    path('eliminarRetrospectiva/<id>', login_required(eliminar_retrospectiva), name='eliminarRetrospectiva'),
    # Sub lista Sprint
    path('subListaRetrospectivaSprint/', login_required(subListaRetrospectivaSprint), name='subListaRetrospectivaSprint'),
    path('crearRetrospectivaSprint/<id>/', login_required(crear_RetrospectivaSprint), name='crearRetrospectivaSprint'),

    # Asistentes Retrospectiva Sprint, Product owner
    path('crearAsistenteRetrospectiva/<id>', login_required(crear_Asistente_Retrospectiva), name='crearAsistenteRetrospectiva'),
    path('listaAsistentesRetrospectiva/<id>', login_required(lista_asistentes_por_retrospectiva), name='listaAsistentesRetrospectiva'),
    path('editarAsistenteRetrospectiva/<int:pk>', ActualizarAsistenteRetrospectiva.as_view(), name='editarAsistenteRetrospectiva'),
    path('eliminarAsistenteRetrospectiva/<id>', login_required(eliminar_asistente_retrospectiva), name='eliminarAsistenteRetrospectiva'),

    # Enviar mensaje de Retrospectiva del Sprint, Product Owner
    path('enviarMensajeRetrospectiva/<id>', login_required(enviar_mensaje_Retrospectiva), name='enviarMensajeRetrospectiva'),
    path('enviarRetroRetroRetrospectiva/<id>/', login_required(enviar_mensaje_RetroRetrospectiva), name='enviarRetroRetroRetrospectiva'), # Contestacion

    # Recibir mensaje de retralimentacion de retrospectiva del sprint, product owner
    path('retroRetrospectivaSprint/', login_required(mensajes_RetroAlimentacionRetrospectiva), name='retroRetrospectivaSprint'),

    # Renderizado a PDF
    path('plantillaRetrospectivaSprint/<id>/', login_required(plantillaRetrospectivaSprint), name='plantillaRetrospectivaSprint'),

    # Recibir mensajes Reunion de retrospectiva del sprint, Scrum Master
    path('mensajeRetrospectivaScrumMaster/', login_required(listaRetrospectivaSprintSM), name='mensajeRetrospectivaScrumMaster'), # Scrum Master
    path('archivosRetrospectivaSM/<id>', login_required(archivosRecibidosRetrospectivaSM), name='archivosRetrospectivaSM'), # archivos retrospectiva
    
    # Mensajes de Retroalimentacion, retrospectiva del sprint, Scrum master
    path('retroARetrospectivaSM/<id>', login_required(enviar_mensajeRetrospectivaSM), name='retroARetrospectivaSM'),
    path('retroAliScrumMasterRetrospectiva/<id>', login_required(mensajes_RetrospectivaRetroSM), name='retroAliScrumMasterRetrospectiva'),

    # Comentarios/reflexiones - retrospectiva sprint - Scrum Master
    path('retrospectivaComentariosSM/<id>/', login_required(crear_Comentarios_RetrospectivaSM), name='retrospectivaComentariosSM'),

    # Recibir mensajes Reunion de retrospectiva del sprint, Empleado
    path('mensajeRetrospectivaEmpleado/', login_required(listaRetrospectivaSprintEmpleado), name='mensajeRetrospectivaEmpleado'),
    path('archivosRetrospectivaEmpleado/<id>', login_required(archivosRecibidosRetrospectivaEmpleado), name='archivosRetrospectivaEmpleado'), # archivos retrospectiva

    # Mensajes de Retroalimentacion, retrospectiva del sprint, Empleado
    path('retroARetrospectivaEmpleado/<id>', login_required(enviar_mensajeRetrospectivaEmpleado), name='retroARetrospectivaEmpleado'),
    path('retroAliEmpleadoRetrospectiva/<id>', login_required(mensajes_RetrospectivaRetroEmpleado), name='retroAliEmpleadoRetrospectiva'),

    # Comentarios/reflexiones - retrospectiva sprint - Empleado
    path('retrospectivaComentariosEmpleado/<id>/', login_required(crear_Comentarios_Retrospectiva_Empleado), name='retrospectivaComentariosEmpleado'),

    # Plantilla generada para el mensaje de retroalimentacion
    path('plantillaRetroRestrospectiva/<id>/', login_required(plantillaRetroAlimentacionRestrospectiva), name='plantillaRetroRestrospectiva'),

# ------------------------------------------------ Reunión Diaria ------------------------------------------------------------------
    path('listaReunionDiaria/',login_required(listaReunionDiaria), name='listaReunionDiaria'),
    path('editarReunionDiaria/<int:pk>', ActualizarReunionDiaria.as_view(), name='editarReunionDiaria'),
    path('eliminarReunionDiaria/<id>', login_required(eliminar_reunion_diaria), name='eliminarReunionDiaria'),
    # Sub lista Sprint
    path('subListaReunionDiaria/', login_required(subListaReunionDiaria), name='subListaReunionDiaria'),
    path('crearReunionDiaria/<id>/', login_required(crear_Reunion_Diaria), name='crearReunionDiaria'),

    # Asistentes Reunion Diaria, Product owner
    path('crearAsistenteReunionDiaria/<id>', login_required(crear_Asistente_Reunion_Diaria), name='crearAsistenteReunionDiaria'),
    path('listaAsistentesReunionDiaria/<id>', login_required(lista_asistentes_por_reunion_diaria), name='listaAsistentesReunionDiaria'),
    path('editarAsistenteReunionDiaria/<int:pk>', ActualizarAsistenteReunionDiaria.as_view(), name='editarAsistenteReunionDiaria'),
    path('eliminarAsistenteReunionDiaria/<id>', login_required(eliminar_asistente_reunion_Diaria), name='eliminarAsistenteReunionDiaria'),

    # Enviar mensaje de Reunion Diaria, Product Owner
    path('enviarMensajeReunionDiaria/<id>', login_required(enviar_mensaje_Reunion_Diaria), name='enviarMensajeReunionDiaria'),
    path('enviarRetroRetroReunionDiaria/<id>/', login_required(enviar_Retro_Reunion_Diaria), name='enviarRetroRetroReunionDiaria'), # Contestacion

    # Recibir mensaje de retralimentacion de la reunion diaria, product owner
    path('retroReunionDiaria/', login_required(mensajes_RetroAlimentacionReunionDiaria), name='retroReunionDiaria'),

    # Vista y renderizado PDF
    path('vistaReunionDiaria/<id>/', login_required(vistaReunionDiaria), name='vistaReunionDiaria'),
    path('plantillaReunionDiaria/<id>/', login_required(plantillaReunionDiaria), name='plantillaReunionDiaria'),
    path('reunionDiariaScrumMaster/', login_required(lista_reunion_diariaScrumMaster), name='reunionDiariaScrumMaster'), # Obsoleto
    path('reunionDiariaEmpleado/', login_required(lista_reunion_diariaEmpleado), name='reunionDiariaEmpleado'), # Obsoleto

     # Recibir mensajes Reunion Diaria del sprint, Scrum Master
    path('mensajeReunionDiaria/', login_required(listaReunionDiariaSM), name='mensajeReunionDiaria'), # Scrum Master
    path('archivosReunionDiariaSM/<id>', login_required(archivosReunionDiariaSM), name='archivosReunionDiariaSM'), # archivos reunion diaria

    # Mensajes de Retroalimentacion, reunion diaria, Scrum master
    path('retroAReunionDiariaSM/<id>', login_required(enviar_mensajeReunionDiariaSM), name='retroAReunionDiariaSM'),
    path('retroAliReunionDiariaSM/<id>', login_required(mensajes_Retro_Reunion_Diaria_SM), name='retroAliReunionDiariaSM'),

    # Comentarios/reflexiones - reunion diaria - Scrum Master
    path('reunionDiariaSM/<id>/', login_required(crear_Comentarios_Reunion_Diaria_SM), name='reunionDiariaSM'),

     # Recibir mensajes Reunion de reunion diaria, Empleado
    path('mensajesReunionDiariaEmpleado/', login_required(listaReunionDiariaEmpleado), name='mensajesReunionDiariaEmpleado'),
    path('archivosReunionDiariaEmpleado/<id>', login_required(archivosReunionDiariaEmpleado), name='archivosReunionDiariaEmpleado'), # archivos retrospectiva

    # Comentarios/reflexiones - reunion diaria - Empleado
    path('reunionDiariaEmpleado/<id>/', login_required(crear_Comentarios_Reunion_Diaria_Empleado), name='reunionDiariaEmpleado'),

    # Mensajes de Retroalimentacion, reunion diaria, Empleado
    path('retroAReunionDiariaEmpleado/<id>', login_required(enviar_mensajeReunionDiariaEmpleado), name='retroAReunionDiariaEmpleado'),
    path('retroAliReunionDiariaEmpleado/<id>', login_required(mensajes_Retro_Reunion_Diaria_Empleado), name='retroAliReunionDiariaEmpleado'),

    # Plantilla generada para el mensaje de retroalimentacion
    path('plantillaRetroReunionDiaria/<id>/', login_required(plantillaRetroAlimentacionReunionDiaria), name='plantillaRetroReunionDiaria'),

    # --------------------------------------- Plantillas pendientes -------------------------------------

    # Historias HU (Historias de usaurio divididas)
    path('vistaHistoriasHU', views.vistaHistoriasHU, name='vistaHistoriasHU'), # Beta
    path('plantillaHistoriasHU', login_required(plantillaHistoriasHU), name='plantillaHistoriasHU'), # Beta

    # mensaje de la Ejecución del Sprint
    path('vistaEjecucionSprint/<id_ReunionDiaria>/', views.vistaEjecucionSprint, name='vistaEjecucionSprint'), # Beta

    # --------------------------------------- Mensajes comprendidos (mover segun sea el caso) ----------------------
    # Mensajes comprendidos - Refinamiento
    path('mensajeComprendidoSM/<int:id>/', login_required(actualizarRetroStatusCorrectoScrumMaster), name='mensajeComprendidoSM'), # Scrum Master
    path('mensajeComprendidoEmpleado/<int:id>/', login_required(actualizarRetroStatusCorrectoEmpleado), name='mensajeComprendidoEmpleado'), # Empleado
    path('mensajeRetroComprendidoSM/<int:id>/', login_required(actualizarRetroBLStatusCorrectoScrumMaster), name='mensajeRetroComprendidoSM'), # Scrum Master
    path('mensajeRetroComprendidoEmpleado/<int:id>/', login_required(actualizarRetroBLStatusCorrectoEmpleado), name='mensajeRetroComprendidoEmpleado'), # Empleado

    # Mensajes comprendidos - Planeacion Sprint
    path('mensajeComprendidoSM2/<int:id>/', login_required(actualizarRetroStatusCorrectoScrumMaster2), name='mensajeComprendidoSM2'), # Scrum Master
    path('mensajeRetroComprendidoSM2/<int:id>/', login_required(actualizarRetroBLStatusCorrectoScrumMaster2), name='mensajeRetroComprendidoSM2'), # Scrum Master
    path('mensajeComprendidoEmpleado2/<int:id>/', login_required(actualizarRetroStatusCorrectoEmpleado2), name='mensajeComprendidoEmpleado2'), # Empleado
    path('mensajeRetroComprendidoEmpleado2/<int:id>/', login_required(actualizarRetroPSStatusCorrectoEmpleado2), name='mensajeRetroComprendidoEmpleado2'), # Empleado

    # Mensajes comprendidos - Revisión Sprint 
    path('mensajeComprendidoSM3/<int:id>/', login_required(actualizarStatusCorrectoScrumMaster), name='mensajeComprendidoSM3'), # Scrum Master
    path('mensajeRetroComprendidoSM3/<int:id>/', login_required(actualizarRetroRevisionStatusCorrectoSM), name='mensajeRetroComprendidoSM3'), # Scrum Master
    path('mensajeComprendidoRevisionEmpleado/<int:id>/', login_required(actualizarRetroStatusCorrectoEmpleadoRevision), name='mensajeComprendidoRevisionEmpleado'), # Empleado
    path('mensajeRetroComprendidoRevisionEmpleado/<int:id>/', login_required(actualizarRetroPSStatusCorrectoEmpleadoRevision), name='mensajeRetroComprendidoRevisionEmpleado'), # Empleado

    # Mensajes comprendidos - Retrospectiva del Sprint
    path('mensajeComprendidoSM4/<int:id>/', login_required(statusCorrectoRetrospectiva), name='mensajeComprendidoSM4'), # Scrum Master
    path('mensajeRetroComprendidoSM4/<int:id>/', login_required(actualizarRetroRetrospectivaStatusCorrectoSM), name='mensajeRetroComprendidoSM4'), # Scrum Master
    path('mensajeComprendidoSM5/<int:id>/', login_required(statusCorrectoRetrospectivaEmpleado), name='mensajeComprendidoSM5'), # Empleado
    path('mensajeRetroComprendidoEmpleado4/<int:id>/', login_required(actualizarRetroRetrospectivaStatusCorrectoEmpleado), name='mensajeRetroComprendidoEmpleado4'), # Empleado

    # Mensajes comprendidos - Reunion Diaria
    path('mensajeComprendidoSM6/<int:id>/', login_required(statusCorrectoReunionDiariaSM), name='mensajeComprendidoSM6'), # Scrum Master
    path('mensajeRetroComprendidoSM6/<int:id>/', login_required(actualizarRetroReunionDiariaStatusCorrectoSM), name='mensajeRetroComprendidoSM6'), # Scrum Master
    path('mensajeComprendidoEmpleado6/<int:id>/', login_required(statusCorrectoReunionDiariaEmpleado), name='mensajeComprendidoEmpleado6'), # Empleado
    path('mensajeRetroComprendidoEmpleado6/<int:id>/', login_required(actualizarRetroReunionDiariaStatusCorrectoEmpleado), name='mensajeRetroComprendidoEmpleado6'), # Empleado

    # -------------------------------------- Sección de archivos ----------------------------------------
    # Archivos
    path('descargar_archivo/<int:id>/',login_required(descargar_archivo), name='descargar_archivo'),
    path('guardarArchivo/',login_required(cargar_documento), name='guardarArchivo'),
    path('guardarArchivoID/<id>/',login_required(cargar_documentoConID), name='guardarArchivoID'), # Refinamiento BL
    path('guardarArchivoIDPS/<id>/',login_required(cargar_documentoConIDPS), name='guardarArchivoIDPS'), # Plneacion del Sprint
    path('guardarArchivoIDRS/<id>/',login_required(cargar_documentoConIDRS), name='guardarArchivoIDRS'), # Revision del Sprint
    path('guardarArchivoIDRetroSprint/<id>/',login_required(cargar_documentoConIDRetroSprint), name='guardarArchivoIDRetroSprint'), # Retrospectiva del Sprint
    path('guardarArchivoIDReunionDiaria/<id>/',login_required(cargar_documentoConIDReunionDiaria), name='guardarArchivoIDReunionDiaria'), # Reunion Diaria

    # Borrar archivos por reunion
    path('borrarArchivoID/<id>/',login_required(eliminar_archivo_refinamiento), name='borrarArchivoID'), # Refinamiento 
    path('borrarArchivoPS/<id>/',login_required(eliminar_archivo_planeacion), name='borrarArchivoPS'), # Planeación del Sprint
    path('borrarArchivoRS/<id>/',login_required(eliminar_archivo_revision), name='borrarArchivoRS'), # Revisión del Sprint
    path('borrarArchivoRetroS/<id>/',login_required(eliminar_archivo_retrospectiva), name='borrarArchivoRetroS'), # Retrospectiva del Sprint
    path('borrarArchivoRD/<id>/',login_required(eliminar_archivo_reunion_diaria), name='borrarArchivoRD'), # Revisión del Sprint

    # -------------------------------------- ALGORITMOS BETA (No borrar) ---------------------------------
    path('enviarMensajes/<id>', login_required(enviar_mensaje2), name='enviarMensajes'), # original
    path('test/', views.testPais, name='test'),
    # path('crearReunionDiaria/<id>/', views.crearReunionDiaria, name='crearReunionDiaria'),
    path('ejecucionSprint/<int:id_ReunionDiaria>', login_required(vistaEjecucionSprintID), name='ejecucionSprint'), # Vista de la ejecucion del sprint

    #path('MensajePantalla/<int:pk>', login_required(enviar_mensaje2), name = 'MensajePantalla'),


    # Editar asistente por mensaje, Scrum Master, Refinamiento 
    path('asistente_RefinamientoSM/<id>', login_required(lista_asistentes_por_usuarioRef_SM), name='asistente_RefinamientoSM'),
    path('editarAsistenteScrumMasterRef/<int:pk>', ActualizarAsistenteScrumMasterRef.as_view(), name='editarAsistenteScrumMasterRef'),
    # Editar asistente por mensaje, Scrum Master, Planeacion 
    path('asistente_PlaneacionSM/<id>', login_required(lista_asistentes_por_usuarioPS_SM), name='asistente_PlaneacionSM'),
    path('editarAsistenteScrumMasterPS/<int:pk>', ActualizarAsistenteScrumMasterPS.as_view(), name='editarAsistenteScrumMasterPS'),
    # Editar asistente por mensaje, Scrum Master, Revision
    path('asistente_RevisionSM/<id>', login_required(lista_asistentes_revision_SM), name='asistente_RevisionSM'),
    path('editarAsistenteRevisionSM/<int:pk>', ActualizarAsistenteRevisionSM.as_view(), name='editarAsistenteRevisionSM'),
    # Editar asistente por mensaje, Scrum Master, Retrospectiva
    path('asistente_RetrospectivaSM/<id>', login_required(lista_asistentes_retrospectiva_SM), name='asistente_RetrospectivaSM'),
    path('editarAsistenteRetrospectivaSM/<int:pk>', ActualizarAsistenteRetrospectivaSM.as_view(), name='editarAsistenteRetrospectivaSM'),
    # Editar asistente por mensaje, Scrum Master, Reunion Diaria
    path('asistente_Reunion_Diaria/<id>', login_required(lista_asistentes_reunion_diaria_SM), name='asistente_Reunion_Diaria'),
    path('editarAsistenteReunionDiariaSM/<int:pk>', ActualizarAsistenteReunionDiaria.as_view(), name='editarAsistenteReunionDiariaSM'),
    # Editar asistente por mensaje, Empleado, Refinamiento 
    path('asistente_RefinamientoEmpleado/<id>', login_required(lista_asistentes_por_usuarioRef_Empleado), name='asistente_RefinamientoEmpleado'),
    path('editarAsistenteEmpleadoRef/<int:pk>', ActualizarAsistenteEmpleadoRef.as_view(), name='editarAsistenteEmpleadoRef'),
    # Editar asistente por mensaje, Empleado, Planeacion 
    path('asistente_PlaneacionEmpleado/<id>', login_required(lista_asistentes_por_usuarioPS_Empleado), name='asistente_PlaneacionEmpleado'), # Beta
    path('editarAsistenteEmpleadoPS/<int:pk>', ActualizarAsistenteEmpleadoPS.as_view(), name='editarAsistenteEmpleadoPS'),
    # Editar asistente por mensaje, Empleado, Revision
    path('asistente_RevisionEmpleado/<id>', login_required(lista_asistentes_revision_Empleado), name='asistente_RevisionEmpleado'),
    path('editarAsistenteRevisionEmpleado/<int:pk>', ActualizarAsistenteRevisionEmpleado.as_view(), name='editarAsistenteRevisionEmpleado'),
    # Editar asistente por mensaje, Empleado, Retrospectiva
    path('asistente_RetrospectivaEmpleado/<id>', login_required(lista_asistentes_retrospectiva_Empleado), name='asistente_RetrospectivaEmpleado'),
    path('editarAsistenteRetrospectivaEmpleado/<int:pk>', ActualizarAsistenteRetrospectivaEmpleado.as_view(), name='editarAsistenteRetrospectivaEmpleado'),
    # Editar asistente por mensaje, Empleado, Reunion Diaria
    path('asistente_ReunionDiaria_Empleado/<id>', login_required(lista_asistentes_reunion_diaria_Empleado), name='asistente_ReunionDiaria_Empleado'),
    path('editarAsistenteReunionDiariaEmpleado/<int:pk>', ActualizarAsistenteReunionDiariaEmpleado.as_view(), name='editarAsistenteReunionDiariaEmpleado'),

    # Sub lista Planeacion Sprint, Product Owner
    path('subListaSprint/', login_required(subListaPlaneacionSprint), name='subListaSprint'), # Beta
    path('crearSubPlaneacionSprint/<id>/', login_required(crear_PlaneacionSprint6), name='crearSubPlaneacionSprint'), # Beta
    path('actualizarPlaneacionSprint/<id>/', login_required(actualizar_ReunionPlaneacion), name='actualizarPlaneacionSprint'), # Beta

    # Comentarios - Beta
    path('crearComentarioPlaneacionSM/<id>/', login_required(crear_ComentarioScrumMasterPlaneacion), name='crearComentarioPlaneacionSM'),
    path('crearComentarioRevisionSM/<id>/', login_required(crear_ComentarioScrumMasterRevision), name='crearComentarioRevisionSM'),
    path('crearComentarioPlaneacionEmpleado/<id>/', login_required(crear_ComentarioEmpleadoPlaneacion), name='crearComentarioPlaneacionEmpleado'),
    path('crearComentarioRevisionEmpleado/<id>/', login_required(crear_ComentarioEmpleadoRevision), name='crearComentarioRevisionEmpleado'),
]